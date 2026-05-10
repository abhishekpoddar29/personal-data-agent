"""
main.py
-------
FastAPI backend for the Personal Data Agent.

Endpoints
---------
POST   /upload              Upload one or more files (PDF / TXT / MD)
DELETE /files               Clear all uploaded files

POST   /chat/start          Start a new chat session (seeds Gemini with docs)
POST   /chat/{session_id}   Send a message; returns Gemini's reply
DELETE /chat/{session_id}   End a session

GET    /health              Quick status check
"""

import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import agent
from file_parser import extract_text

# ── App ────────────────────────────────────────────────────────────────────

app = FastAPI(title="Personal Data Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory file store  {file_id: {name, content}} ──────────────────────

_files: dict[str, dict] = {}

# ── Helpers ────────────────────────────────────────────────────────────────

def _build_context() -> str:
    """Concatenate all uploaded file contents into one context string."""
    sections = []
    for meta in _files.values():
        bar = "=" * 60
        sections.append(f"{bar}\nFILE: {meta['name']}\n{bar}\n{meta['content'].strip()}")
    return "\n\n".join(sections)

# ── Pydantic models ────────────────────────────────────────────────────────

class StartRequest(BaseModel):
    session_id: str | None = None   # auto-generated if omitted

class MessageRequest(BaseModel):
    message: str

# ── Routes ─────────────────────────────────────────────────────────────────

@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload(files: list[UploadFile] = File(...)):
    """
    Accept one or more files (PDF, TXT, MD) and store their extracted text.
    Returns a list of {id, name} for each accepted file.
    """
    if not files:
        raise HTTPException(400, "No files provided.")

    uploaded = []
    for f in files:
        name = f.filename or "unnamed"
        raw = await f.read()

        try:
            content = extract_text(raw, name)
        except ValueError as exc:
            raise HTTPException(415, str(exc)) from exc

        fid = str(uuid.uuid4())
        _files[fid] = {"name": name, "content": content}
        uploaded.append({"id": fid, "name": name})

    return {"uploaded": uploaded, "total_files": len(_files)}


@app.delete("/files")
def clear_files():
    """Remove all uploaded files."""
    count = len(_files)
    _files.clear()
    return {"message": f"Cleared {count} file(s)."}


@app.post("/chat/start", status_code=status.HTTP_201_CREATED)
def start_chat(body: StartRequest):
    """
    Create a new Gemini chat session seeded with all uploaded documents.
    Returns the session_id to use in subsequent /chat/{session_id} calls.
    """
    if not _files:
        raise HTTPException(
            400,
            "No files uploaded yet. Upload at least one document first."
        )

    session_id = body.session_id or str(uuid.uuid4())

    if session_id in agent.active_sessions():
        raise HTTPException(409, f"Session '{session_id}' already exists.")

    context = _build_context()

    try:
        agent.start_session(session_id, context)
    except Exception as exc:
        raise HTTPException(502, f"Gemini error: {exc}") from exc

    return {
        "session_id": session_id,
        "files_loaded": len(_files),
    }


@app.post("/chat/{session_id}")
def send_message(session_id: str, body: MessageRequest):
    """
    Send a question to an existing chat session.
    Returns Gemini's answer.
    """
    if not body.message.strip():
        raise HTTPException(400, "Message cannot be empty.")

    try:
        answer = agent.chat(session_id, body.message)
    except KeyError:
        raise HTTPException(404, f"Session '{session_id}' not found.")
    except Exception as exc:
        raise HTTPException(502, f"Gemini error: {exc}") from exc

    return {"session_id": session_id, "answer": answer}


@app.delete("/chat/{session_id}")
def end_chat(session_id: str):
    """End and remove a chat session."""
    if session_id not in agent.active_sessions():
        raise HTTPException(404, f"Session '{session_id}' not found.")
    agent.end_session(session_id)
    return {"message": f"Session '{session_id}' ended."}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "files": len(_files),
        "active_sessions": len(agent.active_sessions()),
    }