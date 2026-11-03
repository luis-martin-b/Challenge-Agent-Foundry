"""
SkyNova agent client: shared core used by both the terminal and the web interfaces.

It handles:
  * Authentication with Microsoft Entra ID (DefaultAzureCredential, e.g. `az login`)
  * The connection to the Foundry project and to the agent (Microsoft Foundry SDK: azure-ai-projects)
  * Conversations (multi-turn memory kept server-side by Foundry)
  * Parsing the response: answer text, tools used, knowledge-base citations, charts made by Code Interpreter
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

CITATION_MARKER = re.compile(r"【[^】]*】")
SANDBOX_LINK = re.compile(r"sandbox:/mnt/data/([^\s)\]]+)")


@dataclass
class ToolCall:
    kind: str   # "knowledge" | "code" | "github" | "other"
    name: str
    detail: str = ""
    error: str | None = None


@dataclass
class AgentReply:
    text: str
    tools: list[ToolCall] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    files: list[Path] = field(default_factory=list)


class SkyNovaAgent:
    """Thin wrapper around a Foundry agent, exposed through the OpenAI-compatible Responses API."""

    def __init__(self, endpoint: str | None = None, agent_name: str | None = None, output_dir: Path | None = None):
        self.endpoint = endpoint or os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
        self.agent_name = agent_name or os.environ.get("FOUNDRY_AGENT_NAME", "skynova-customer-care")
        if not self.endpoint:
            raise RuntimeError("FOUNDRY_PROJECT_ENDPOINT is not set. Copy .env.example to .env and fill it in.")
        self.output_dir = output_dir or ROOT / "outputs"
        self.output_dir.mkdir(exist_ok=True)

        # 1) Authentication: DefaultAzureCredential tries env vars, managed identity, Azure CLI (az login), VS Code...
        self._credential = DefaultAzureCredential()
        # 2) Connection to the Foundry project
        self._project = AIProjectClient(endpoint=self.endpoint, credential=self._credential)
        # 3) Check that the agent exists (and that we have permission to use it)
        agent = self._project.agents.get(agent_name=self.agent_name)
        self.agent_version = agent.versions.latest.version
        self.model = agent.versions.latest.definition.get("model", "?")
        # 4) OpenAI-compatible client authenticated with the same Entra ID credential
        self._openai = self._project.get_openai_client()
        self.conversation_id: str | None = None

    # ------------------------------------------------------------------ conversation
    def new_conversation(self) -> str:
        self.conversation_id = self._openai.conversations.create().id
        return self.conversation_id

    def create_conversation(self) -> str:
        """Create a conversation without changing the default one (used by the web app, one per browser session)."""
        return self._openai.conversations.create().id

    def ask(self, message: str, conversation_id: str | None = None) -> AgentReply:
        """Send a message. Without conversation_id, the default conversation of this client is used (terminal)."""
        if conversation_id is None:
            if not self.conversation_id:
                self.new_conversation()
            conversation_id = self.conversation_id
        response = self._openai.responses.create(
            conversation=conversation_id,
            input=message,
            extra_body={"agent_reference": {"name": self.agent_name, "type": "agent_reference"}},
        )
        response = self._handle_approvals(response, conversation_id)
        return self._parse(response)

    def _handle_approvals(self, response, conversation_id: str):
        """If an MCP tool is configured with 'require approval', approve the requests automatically."""
        for _ in range(5):
            requests = [o for o in response.output if o.type == "mcp_approval_request"]
            if not requests:
                return response
            response = self._openai.responses.create(
                conversation=conversation_id,
                input=[{"type": "mcp_approval_response", "approval_request_id": r.id, "approve": True} for r in requests],
                extra_body={"agent_reference": {"name": self.agent_name, "type": "agent_reference"}},
            )
        return response

    # ------------------------------------------------------------------ parsing
    def _parse(self, response) -> AgentReply:
        tools, sources, file_refs, text_parts = [], [], [], []
        for item in response.output:
            if item.type == "mcp_call":
                tools.append(self._describe_tool(item))
                file_refs += self._file_refs_from_output(item.output or "")
            elif item.type == "code_interpreter_call":  # native (non-toolbox) Code Interpreter
                tools.append(ToolCall("code", "code_interpreter"))
            elif item.type == "message":
                for part in item.content:
                    if getattr(part, "type", "") != "output_text":
                        continue
                    text_parts.append(part.text)
                    for ann in part.annotations or []:
                        if ann.type == "url_citation":
                            doc = self._document_name(ann.url)
                            if doc not in sources:
                                sources.append(doc)
                        elif ann.type == "container_file_citation":
                            file_refs.append((ann.container_id, ann.file_id, ann.filename))

        files = self._download(file_refs)
        text = CITATION_MARKER.sub("", "\n".join(text_parts)).strip()
        text = self._relink_sandbox(text, files)
        return AgentReply(text=text, tools=tools, sources=sources, files=files)

    @staticmethod
    def _describe_tool(item) -> ToolCall:
        name = item.name or ""
        args = {}
        try:
            args = json.loads(item.arguments or "{}")
        except json.JSONDecodeError:
            pass
        error = str(item.error) if item.error else None
        if name.startswith("knowledge_base") or (item.server_label or "").startswith("kb-"):
            return ToolCall("knowledge", "knowledge_base_retrieve", error=error)
        if name.startswith("code_interpreter"):
            return ToolCall("code", "code_interpreter", error=error)
        if "___" in name or "issue" in name:
            short = name.split("___")[-1]
            detail = args.get("query") or (f"#{args['issue_number']}" if "issue_number" in args else "")
            if not detail and args.get("labels"):
                detail = "labels=" + ",".join(args["labels"])
            if not detail and args.get("title"):
                detail = args["title"]
            return ToolCall("github", short, detail=str(detail), error=error)
        return ToolCall("other", name, error=error)

    @staticmethod
    def _file_refs_from_output(output: str) -> list[tuple[str, str, str]]:
        """Toolbox Code Interpreter returns file citations as JSON inside the tool output text."""
        refs = []
        for m in re.finditer(r'"file_id":\s*"([^"]+)",\s*"filename":\s*"([^"]+)",\s*"container_id":\s*"([^"]+)"', output):
            refs.append((m.group(3), m.group(1), m.group(2)))
        return refs

    def _download(self, refs: list[tuple[str, str, str]]) -> list[Path]:
        """Download generated files from the Code Interpreter container. Duplicates (same bytes) are skipped."""
        saved, seen = [], {}
        # Code Interpreter returns both an inline preview (cfile_xxx.png) and the named file the code saved.
        # Keep only the named files when there are any; fall back to the previews otherwise.
        refs = list(dict.fromkeys(refs))
        named = [r for r in refs if not r[2].startswith("cfile_")]
        refs = named or refs
        for container_id, file_id, filename in refs:
            try:
                data = self._openai.containers.files.content.retrieve(file_id, container_id=container_id).read()
            except Exception:  # noqa: BLE001 - file may have expired with the container
                continue
            digest = hashlib.sha256(data).hexdigest()
            if digest in seen:
                continue
            path = self.output_dir / Path(filename).name
            if path.exists():
                path = path.with_stem(f"{path.stem}_{file_id[-6:]}")
            path.write_bytes(data)
            seen[digest] = path
            saved.append(path)
        return saved

    @staticmethod
    def _relink_sandbox(text: str, files: list[Path]) -> str:
        """Replace 'sandbox:/mnt/data/x.png' links (only valid in the portal) with the local file path."""
        by_name = {f.name: f for f in files}

        def repl(m):
            local = by_name.get(Path(m.group(1)).name) or (files[0] if files else None)
            return str(local) if local else m.group(0)

        return SANDBOX_LINK.sub(repl, text)

    @staticmethod
    def _document_name(url: str) -> str:
        """Azure AI Search chunk ids contain the source blob URL base64-encoded; decode it to get the PDF name."""
        m = re.search(r"/docs/[^_/]+_([A-Za-z0-9_\-]+?)(\d)_pages_\d+", unquote(url))
        if m:
            try:
                b64, pad = m.group(1), int(m.group(2))
                decoded = base64.urlsafe_b64decode(b64 + "=" * pad).decode()
                return Path(decoded).name
            except Exception:  # noqa: BLE001
                pass
        return "SkyNova knowledge base"

    def close(self):
        self._openai.close()
        self._project.close()
        self._credential.close()
