# 🤖 Personal Data Agent

A conversational AI agent that reads your personal documents and answers questions on your behalf. Upload a PDF or paste your bio/resume as text, then chat with an AI that knows you — powered by **Google Gemini**, **FastAPI**, and **Gradio**.

---

## 📸 How It Works

```
You run intake.py
    → Upload PDF or paste text
    → FastAPI extracts and stores the text
    → Gemini session created with your data as context

You run chat.py
    → Gradio chat UI opens in browser
    → Ask anything about yourself
    → Gemini answers using your documents
```

---

## 🗂️ Project Structure

```
personal-agent/
│
├── main.py          ← FastAPI backend (REST API server)
├── agent.py         ← Google Gemini API wrapper
├── file_parser.py   ← PDF and plain text extraction
│
├── intake.py        ← Step 1: upload your data via terminal
├── chat.py          ← Step 2: Gradio chat interface
│
├── .env             ← your secret API key (you create this)
├── requirements.txt ← Python dependencies
└── README.md
```

---

## ⚙️ Prerequisites

- Python **3.10 or higher**
- A **Google Gemini API key** (free) → https://aistudio.google.com/app/apikey

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/personal-agent.git
cd personal-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn[standard] python-multipart PyMuPDF google-generativeai python-dotenv requests gradio
```

### 4. Create your `.env` file

Create a file named `.env` in the project root and add your Gemini API key:

```
GEMINI_API_KEY=your_actual_key_here
```

> ⚠️ Never commit this file. Add `.env` to your `.gitignore`.

### 5. Run the project

You need **three terminals**, all with the venv activated.

**Terminal 1 — Start the FastAPI backend**
```bash
uvicorn main:app --reload --port 8000
```

Wait until you see:
```
INFO: Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2 — Upload your personal data**
```bash
python intake.py
```

Follow the prompts:
```
How do you want to provide your data?
  1. Upload a PDF file
  2. Paste text / bio / summary

Enter 1 or 2:
```

When finished it will print: `Now run: python chat.py`

**Terminal 3 — Start the chat UI**
```bash
python chat.py
```

Open the URL shown (usually **http://localhost:7860**) and start chatting.

---

## 💬 Example Interaction

After uploading a resume PDF:

> **You:** What programming languages do I know?
>
> **Agent:** Based on your resume, you are proficient in Python, JavaScript, and SQL, with additional experience in FastAPI and React.

> **You:** What was my role at my last company?
>
> **Agent:** At Acme Corp, you worked as a Backend Engineer for 4 years, where you built REST APIs and led the migration to a microservices architecture.

---

## 🔧 Supported File Types

| Type | Extensions |
|---|---|
| PDF | `.pdf` |
| Plain text | `.txt` |
| Markdown | `.md`, `.markdown` |

---

## 🛠️ API Reference

FastAPI interactive docs available at **http://localhost:8000/docs** when the backend is running.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload PDF or text files |
| `DELETE` | `/files` | Clear all uploaded files |
| `POST` | `/chat/start` | Start a Gemini chat session |
| `POST` | `/chat/{session_id}` | Send a message, get a reply |
| `DELETE` | `/chat/{session_id}` | End a session |
| `GET` | `/health` | Check backend status |

---

## ⚠️ Important Notes

- **Sessions are in-memory** — if the FastAPI server restarts, run `intake.py` again to create a new session.
- **Always start the backend first** before running `intake.py` or `chat.py`.
- **PDF must be text-based** — scanned/image-only PDFs will return no readable text. Use a text-based PDF.

---

## 🧱 Challenges We Faced

- **PyMuPDF DLL error on Windows** — `ImportError: DLL load failed while importing _extra`. Fixed by installing the Microsoft Visual C++ Redistributable and pinning `PyMuPDF==1.23.8`.

- **Gradio version hell** — Every version of Gradio (4.x, 5.x, 6.x) had different breaking API changes: `css` moved from `gr.Blocks()` to `launch()`, `type` parameter removed from `gr.Chatbot`, `bubble_full_width` removed, `retry_btn` removed. The final fix was dropping `gr.Blocks` entirely and using the simplest possible `gr.ChatInterface(chat).launch()`.

- **`HfFolder` import error** — `gradio==4.44.1` depended on `huggingface-hub` but newer versions of `huggingface-hub` removed `HfFolder`. Solved by installing gradio without version pinning and letting pip resolve dependencies automatically.

- **`gradio-client` conflict** — Manually pinning `gradio-client` always caused dependency resolution failures. Fix: never pin `gradio-client` separately — let `gradio` pull the correct version automatically.

- **Windows localhost binding error** — `ValueError: When localhost is not accessible, a shareable link must be created`. Fixed by using `server_name="0.0.0.0"` in `launch()`.

- **Deprecated Gemini model** — `gemini-1.5-flash` returned a 404 from the API. Updated to `gemini-2.0-flash` in `agent.py`.

- **Session lost after backend restart** — FastAPI stores sessions in memory, so any restart wipes them. The fix is to always keep the backend running and re-run `intake.py` if a session is lost.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| LLM | Google Gemini 2.0 Flash |
| Backend | FastAPI + Uvicorn |
| PDF Parsing | PyMuPDF (fitz) |
| Chat UI | Gradio |
| API Client | google-generativeai |
| Env Management | python-dotenv |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙌 Acknowledgements

Built with [FastAPI](https://fastapi.tiangolo.com/), [Gradio](https://gradio.app/), and [Google Gemini](https://ai.google.dev/).git init
