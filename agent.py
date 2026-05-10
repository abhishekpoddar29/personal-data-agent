"""
agent.py
--------
Wraps the Google Gemini API.

Responsibilities:
  - Configure the Gemini client once at startup (reads GEMINI_API_KEY from .env)
  - Maintain multi-turn chat sessions (session_id → ChatSession)
  - Accept full document context when a session starts
  - Answer follow-up questions using Gemini's built-in conversation memory
"""

import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # reads .env in the project root

# ── Configure Gemini once ──────────────────────────────────────────────────

_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key:
    raise EnvironmentError(
        "GEMINI_API_KEY is missing. "
        "Create a .env file in the project root and add:\n"
        "  GEMINI_API_KEY=your_key_here\n"
        "Get a free key at: https://aistudio.google.com/app/apikey"
    )

genai.configure(api_key=_api_key)

# ── System instruction sent to Gemini ─────────────────────────────────────

_SYSTEM = """You are a personal AI assistant for a specific individual.
You have been given their personal documents and data.
Answer every question on their behalf, drawing only from the provided documents.

Rules:
- Be accurate, concise, and helpful.
- If the answer is clearly in the documents, state it directly.
- If you can reasonably infer something, say so with appropriate confidence.
- If the information is simply not in the documents, say so honestly.
- Never fabricate facts about the person.
"""

# ── Model ──────────────────────────────────────────────────────────────────

_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=_SYSTEM,
)

# ── Session store  (session_id → genai.ChatSession) ───────────────────────

_sessions: dict[str, genai.ChatSession] = {}


# ── Public API ─────────────────────────────────────────────────────────────

def start_session(session_id: str, context: str) -> None:
    """
    Create a new chat session and seed it with the user's document context.

    Args:
        session_id : unique string identifier
        context    : full text of all uploaded documents
    """
    chat = _model.start_chat(history=[])

    # Prime the model with the document context as the very first exchange.
    # Gemini will remember this throughout the session.
    seed = (
        "Here are my personal documents. "
        "Use them to answer any questions I ask you.\n\n"
        f"{context}"
    )
    chat.send_message(seed)  # Gemini acknowledges; we discard that reply
    _sessions[session_id] = chat


def chat(session_id: str, message: str) -> str:
    """
    Send a user message to an existing session and return the reply.

    Args:
        session_id : must exist (call start_session first)
        message    : user's question

    Returns:
        Gemini's answer as a plain string.

    Raises:
        KeyError   if session_id is not found.
    """
    if session_id not in _sessions:
        raise KeyError(f"Session '{session_id}' not found. Start one first.")

    response = _sessions[session_id].send_message(message)
    return response.text


def end_session(session_id: str) -> None:
    """Remove a session from memory (no-op if it doesn't exist)."""
    _sessions.pop(session_id, None)


def active_sessions() -> list[str]:
    """Return all active session IDs."""
    return list(_sessions.keys())