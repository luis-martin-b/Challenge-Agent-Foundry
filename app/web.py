"""
SkyNova Airlines - web chat with the Foundry agent (FastAPI backend + static Apple-style frontend).

Usage:
    python app/web.py            -> http://localhost:8000
Endpoints:
    GET  /                 chat page
    GET  /api/info         agent name, version, model
    POST /api/conversation new conversation -> {"conversation_id": ...}
    POST /api/chat         {"message": "...", "conversation_id": "..."} -> answer, tools, sources, charts
    GET  /api/history              list of saved chats (newest first)
    GET  /api/history/{id}         one chat with all its messages
    DELETE /api/history/{id}       delete a chat
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from skynova_client import ROOT, SkyNovaAgent

STATIC = Path(__file__).parent / "static"
# Chat history: one JSON file per conversation, stored locally (git-ignored)
HISTORY = ROOT / "history"
HISTORY.mkdir(exist_ok=True)
SAFE_ID = re.compile(r"^[A-Za-z0-9_\-]{1,200}$")


def _history_path(conversation_id: str) -> Path:
    if not SAFE_ID.match(conversation_id):
        raise HTTPException(400, "Invalid conversation id")
    return HISTORY / f"{conversation_id}.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _save_turn(conversation_id: str, user_text: str, agent_msg: dict):
    path = _history_path(conversation_id)
    chat = json.loads(path.read_text()) if path.exists() else {
        "id": conversation_id, "title": user_text[:60] + ("…" if len(user_text) > 60 else ""),
        "created": _now(), "messages": []}
    chat["messages"] += [{"role": "user", "text": user_text}, {"role": "agent", **agent_msg}]
    chat["updated"] = _now()
    path.write_text(json.dumps(chat, ensure_ascii=False, indent=1))

# One authenticated client for the whole server; each browser session gets its own Foundry conversation.
agent = SkyNovaAgent()
app = FastAPI(title="SkyNova Agent")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
app.mount("/outputs", StaticFiles(directory=agent.output_dir), name="outputs")


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info():
    return {"agent": agent.agent_name, "version": agent.agent_version, "model": agent.model}


@app.post("/api/conversation")
def new_conversation():
    return {"conversation_id": agent.create_conversation()}


@app.post("/api/chat")
def chat(req: ChatRequest):
    # Plain "def": FastAPI runs it in a thread pool, so the blocking SDK call doesn't freeze the server.
    message = req.message.strip()
    if not message:
        raise HTTPException(400, "Empty message")
    conversation_id = req.conversation_id or agent.create_conversation()
    try:
        reply = agent.ask(message, conversation_id=conversation_id)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"The agent could not answer: {e}") from e

    text = reply.text
    for f in reply.files:
        # The charts are shown as images below the answer, so remove links to them from the text.
        text = re.sub(r"!?\[([^\]]*)\]\(" + re.escape(str(f)) + r"\)", "", text)
        text = text.replace(str(f), f"/outputs/{f.name}")
    agent_msg = {
        "text": text.strip(),
        "tools": [{"kind": t.kind, "name": t.name, "detail": t.detail, "error": bool(t.error)} for t in reply.tools],
        "sources": reply.sources,
        "files": [f"/outputs/{f.name}" for f in reply.files],
    }
    _save_turn(conversation_id, message, agent_msg)
    return {"conversation_id": conversation_id, **agent_msg}


@app.get("/api/history")
def list_history():
    chats = []
    for p in HISTORY.glob("*.json"):
        try:
            c = json.loads(p.read_text())
            chats.append({"id": c["id"], "title": c["title"], "updated": c.get("updated", "")})
        except (json.JSONDecodeError, KeyError):
            continue
    return sorted(chats, key=lambda c: c["updated"], reverse=True)


@app.get("/api/history/{conversation_id}")
def get_history(conversation_id: str):
    path = _history_path(conversation_id)
    if not path.exists():
        raise HTTPException(404, "Chat not found")
    return json.loads(path.read_text())


@app.delete("/api/history/{conversation_id}")
def delete_history(conversation_id: str):
    path = _history_path(conversation_id)
    path.unlink(missing_ok=True)
    try:  # also delete the conversation in Foundry (best effort)
        agent.delete_conversation(conversation_id)
    except Exception:  # noqa: BLE001
        pass
    return {"deleted": conversation_id}


if __name__ == "__main__":
    print(f"SkyNova web app -> http://localhost:8000  (agent {agent.agent_name} v{agent.agent_version})")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
