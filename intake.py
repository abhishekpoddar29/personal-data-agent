"""
intake.py
---------
Step 1: Upload your data to the agent.
Run this FIRST, before chat.py.

Usage:
    python intake.py
    (FastAPI must be running: uvicorn main:app --reload --port 8000)
"""

import os
import sys
import uuid
import requests

BACKEND = os.getenv("API_BASE", "http://localhost:8000")
SESSION_FILE = ".session_id"   # stores the session ID for chat.py to pick up


def check_backend():
    try:
        r = requests.get(f"{BACKEND}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def upload_pdf(path: str) -> bool:
    if not os.path.isfile(path):
        print(f"  File not found: {path}")
        return False
    filename = os.path.basename(path)
    print(f"  Uploading {filename}...")
    with open(path, "rb") as f:
        r = requests.post(
            f"{BACKEND}/upload",
            files={"files": (filename, f, "application/pdf")},
            timeout=30,
        )
    if r.status_code == 201:
        print("  Upload successful.")
        return True
    print(f"  Upload failed: {r.json().get('detail', r.text)}")
    return False


def upload_text(text: str) -> bool:
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        tmp.write(text)
        tmp_path = tmp.name
    print("  Uploading text...")
    with open(tmp_path, "rb") as f:
        r = requests.post(
            f"{BACKEND}/upload",
            files={"files": ("summary.txt", f, "text/plain")},
            timeout=30,
        )
    os.unlink(tmp_path)
    if r.status_code == 201:
        print("  Upload successful.")
        return True
    print(f"  Upload failed: {r.json().get('detail', r.text)}")
    return False


def create_session(session_id: str) -> bool:
    print("  Starting agent session...")
    r = requests.post(
        f"{BACKEND}/chat/start",
        json={"session_id": session_id},
        timeout=30,
    )
    if r.status_code == 201:
        print(f"  Session started: {session_id}")
        return True
    print(f"  Session failed: {r.json().get('detail', r.text)}")
    return False


def main():
    print("\n=== Personal Data Agent — Intake ===\n")

    # Check backend
    if not check_backend():
        print("ERROR: FastAPI backend is not running.")
        print("Start it first with:  uvicorn main:app --reload --port 8000")
        sys.exit(1)
    print("Backend connected.\n")

    # Choose input type
    print("How do you want to provide your data?")
    print("  1. Upload a PDF file")
    print("  2. Paste text / bio / summary")
    choice = input("\nEnter 1 or 2: ").strip()

    uploaded = False

    if choice == "1":
        path = input("\nEnter the full path to your PDF file:\n> ").strip().strip('"')
        uploaded = upload_pdf(path)

    elif choice == "2":
        print("\nPaste your text below.")
        print("When done, type END on a new line and press Enter:")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        text = "\n".join(lines)
        if not text.strip():
            print("No text entered. Exiting.")
            sys.exit(1)
        uploaded = upload_text(text)

    else:
        print("Invalid choice. Run the script again.")
        sys.exit(1)

    if not uploaded:
        print("\nUpload failed. Exiting.")
        sys.exit(1)

    # Create session
    session_id = str(uuid.uuid4())
    if not create_session(session_id):
        print("\nFailed to start session. Exiting.")
        sys.exit(1)

    # Save session ID for chat.py
    with open(SESSION_FILE, "w") as f:
        f.write(session_id)

    print(f"\nAll done! Session saved.")
    print("\nNow run:  python chat.py\n")


if __name__ == "__main__":
    main()