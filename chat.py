"""
chat.py
-------
Step 2: Chat with your Personal Data Agent.
Run AFTER intake.py has uploaded your data.

Usage:
    python chat.py
"""

import os
import requests
import gradio as gr

BACKEND  = os.getenv("API_BASE", "http://localhost:8000")
SESSION_FILE = ".session_id"


def load_session() -> str | None:
    if not os.path.isfile(SESSION_FILE):
        return None
    with open(SESSION_FILE) as f:
        sid = f.read().strip()
    return sid if sid else None


def ask_backend(session_id: str, message: str) -> str:
    try:
        r = requests.post(
            f"{BACKEND}/chat/{session_id}",
            json={"message": message},
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()["answer"]
        return f"Error {r.status_code}: {r.json().get('detail', r.text)}"
    except requests.ConnectionError:
        return "Cannot reach backend. Is FastAPI running on port 8000?"


# Load session on startup
SESSION_ID = load_session()

if not SESSION_ID:
    print("\nERROR: No session found.")
    print("Please run intake.py first to upload your data.\n")


def chat(message: str, history: list) -> str:
    if not SESSION_ID:
        return "No session found. Please run `python intake.py` first to upload your data."
    return ask_backend(SESSION_ID, message)


# ── Launch — exactly as you requested ────────────────────────────────────────
if __name__ == "__main__":
    print(f"\nSession loaded: {SESSION_ID}")
    print("Starting chat UI...\n")
    gr.ChatInterface(chat).launch()