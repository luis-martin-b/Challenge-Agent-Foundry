"""
SkyNova Airlines - web chat with the Foundry agent (FastAPI backend + static Apple-style frontend).

Usage:
    python app/web.py            -> http://localhost:8000
Endpoints:
    GET  /                 chat page
    GET  /api/info         agent name, version, model
    POST /api/conversation new conversation -> {"conversation_id": ...}
    POST /api/chat         {"message": "...", "conversation_id": "..."} -> answer, tools, sources, charts
"""
import re
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from skynova_client import SkyNovaAgent

STATIC = Path(__file__).parent / "static"

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
    return {
        "conversation_id": conversation_id,
        "text": text.strip(),
        "tools": [{"kind": t.kind, "name": t.name, "detail": t.detail, "error": bool(t.error)} for t in reply.tools],
        "sources": reply.sources,
        "files": [f"/outputs/{f.name}" for f in reply.files],
    }


if __name__ == "__main__":
    print(f"SkyNova web app -> http://localhost:8000  (agent {agent.agent_name} v{agent.agent_version})")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
