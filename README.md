# SmartScribe AI

**AI Text & PDF Summarizer and Simplifier** — built with Python, Streamlit, and Google's Gemini API.

SmartScribe AI turns long articles, essays, research papers, notes, and PDF documents into
clear, faithful summaries — written in original wording, not copy-pasted excerpts. It can also
rewrite difficult material in plain language, explain it the way a tutor would, or distill it
into key takeaways.

---

## Features

- **Paste-and-summarize** text workspace with live word/character counts
- **PDF upload and summarization**, including multi-page and long documents
- **4 processing modes**: Summary, Explain Simply, Student Mode, Key Takeaways
- **Configurable output**: length (Very Short → Detailed), tone (Simple → Professional),
  and format (Paragraph, Bullet Points, Numbered Points)
- **Long-document chunking**: documents are split into logical chunks, summarized
  individually, then combined into one coherent final summary
- **Document Insights**: real, calculated word counts, reduction percentage, and
  estimated reading time saved — nothing fabricated
- **Session history**: revisit earlier results during your session
- **Copy / download** results as `.txt` or `.md`
- **Friendly error handling** for missing/invalid API keys, quota limits, rate limits,
  timeouts, corrupted PDFs, password-protected PDFs, and scanned/image-only PDFs
- **Powered only by Google Gemini** — no OpenAI, Ollama, Hugging Face, or local LLMs

## Demo

Deployed app: `[ADD YOUR STREAMLIT COMMUNITY CLOUD URL HERE AFTER DEPLOYING]`

## Screenshots

Screenshots go in [`assets/`](assets/) — add your own after running the app locally
(see [`assets/README.md`](assets/README.md) for suggested filenames).

## Tech Stack

| Layer          | Technology                              |
|----------------|------------------------------------------|
| UI             | Streamlit                                |
| AI provider    | Google Gemini API (`google-genai` SDK)   |
| PDF extraction | PyMuPDF (`fitz`)                         |
| Language       | Python 3.10+                             |
| Testing        | pytest                                   |
| Config         | python-dotenv (local) / Streamlit Secrets (cloud) |

## Architecture

```
User
  │
  ▼
Streamlit UI            (components/)
  │
  ▼
Application service      (services/summarizer.py)
  │  — decides: single-pass summary, or chunk → map → reduce
  ▼
Text / PDF processing     (services/text_processor.py, services/pdf_service.py)
  │
  ▼
Prompt construction       (prompts/)
  │
  ▼
AI service                (services/ai_service.py)
  │  — the ONLY module that calls Gemini
  ▼
Gemini API
  │
  ▼
Post-processing            (utils/metrics.py → Document Insights)
  │
  ▼
Result UI                  (components/result_view.py)
```

The UI never calls the Gemini API directly. Every request flows
`UI → summarizer → ai_service → Gemini`, which keeps prompt logic, error handling, and
provider-specific code in one place.

## How It Works

1. You paste text or upload a PDF.
2. For PDFs, `services/pdf_service.py` extracts and cleans the text with PyMuPDF, and
   raises a clear, specific error for corrupted files, password-protected files, or
   scanned/image-only PDFs with no extractable text (SmartScribe AI does not perform OCR).
3. `services/text_processor.py` cleans the text and, if it's long, splits it into chunks
   along paragraph (then sentence) boundaries.
4. If the document needed chunking, each chunk is summarized individually
   (`services/ai_service.py`), and the partial summaries are combined into one final,
   coherent summary in a second Gemini call.
5. Every prompt (`prompts/`) explicitly instructs Gemini to write in its own words, preserve
   facts/numbers/names/dates, and avoid adding unsupported information.
6. `services/ai_service.py` requests a structured JSON response (`summary` +
   `key_takeaways`) so the UI can render both sections reliably.
7. `utils/metrics.py` computes real Document Insights (word counts, reduction percentage,
   reading time saved) directly from the original and generated text.
8. The result is shown in the UI, added to session history, and available to copy or
   download.

## Installation

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [VS Code](https://code.visualstudio.com/) with the
  [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- A [Google Gemini API key](https://aistudio.google.com/apikey) (free to create)
- [Git](https://git-scm.com/downloads)

### 1. Get the project into VS Code

If you received this project as a folder, open it directly:

```bash
code smartscribe-ai
```

Or, if it's already a GitHub repository, clone it first:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd smartscribe-ai
code .
```

### 2. Create a virtual environment

Open the **integrated terminal** in VS Code (`` Ctrl+` ``) and run:

**Windows (PowerShell / cmd):**

```bat
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

When VS Code prompts *"We noticed a new virtual environment..."*, click **Select Interpreter**,
or manually pick it via `Ctrl+Shift+P` → **Python: Select Interpreter** → choose the one under
`.venv`.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Gemini API Setup

1. Go to [Google AI Studio](https://aistudio.google.com/apikey).
2. Sign in and click **Create API key**.
3. Copy the generated key — you'll paste it into `.env` in the next step.
4. Review Google's current [Gemini API pricing and rate limits](https://ai.google.dev/gemini-api/docs/pricing).
   Gemini offers free-tier usage, but it is **subject to Google's current quotas and
   policies**, which can change — this project does not assume unlimited or
   permanently free usage, and handles quota/rate-limit errors gracefully in the UI.

## Environment Variables

Copy the example file and fill in your key:

**Windows:**

```bat
copy .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Then edit `.env`:

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash
```

| Variable         | Required | Description                                                                 |
|------------------|----------|-------------------------------------------------------------------------------|
| `GEMINI_API_KEY` | Yes      | Your Gemini API key from Google AI Studio. Never commit this file.           |
| `GEMINI_MODEL`   | No       | Which Gemini model to use. Defaults to `gemini-3.5-flash` if unset. See below. |

**Choosing a model:** Google periodically retires older Gemini models — for example,
`gemini-2.5-flash` and `gemini-2.5-pro` are scheduled to be retired in October 2026.
This project defaults to `gemini-3.5-flash`, a current, actively supported model, but
because the model name lives entirely in `GEMINI_MODEL`, you can switch models at any time
without changing any code. Check
[ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models) for the
current list before deploying, since Google may add or retire model names after this was
written.

`.env` is already excluded via `.gitignore` and is **never** required on Streamlit Community
Cloud — the deployed app reads `GEMINI_API_KEY`/`GEMINI_MODEL` from Streamlit Secrets instead
(see [Streamlit Cloud Deployment](#streamlit-cloud-deployment) below).

## Local Development

With your virtual environment active and `.env` filled in, run:

```bash
streamlit run app.py
```

Streamlit will open the app in your browser, typically at `http://localhost:8501`. The sidebar
shows a **Gemini API · Configured** pill once your key is detected.

## Testing

Unit tests cover text cleaning, chunking, word counts, reading-time and compression
calculations, input validation, and PDF extraction (including corrupted, password-protected,
and blank/scanned PDFs). **No real Gemini API key is required to run the tests** — the AI
service itself is not exercised by the test suite.

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

## GitHub Setup

From the project root, with Git installed:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the URL of an empty repository you've created on
GitHub (e.g. `https://github.com/your-username/smartscribe-ai.git`).

> `.env` and `.streamlit/secrets.toml` are already listed in `.gitignore`, so your API key
> will not be pushed to GitHub as long as you haven't removed those entries.

## Streamlit Cloud Deployment

1. Push the project to GitHub (see above) — Streamlit Community Cloud deploys from a
   GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in.
3. Click **New app**, then select your repository and branch.
4. Set **Main file path** to `app.py`.
5. Before (or after) deploying, open **Advanced settings → Secrets** and add:

   ```toml
   GEMINI_API_KEY = "your_key_here"
   GEMINI_MODEL = "gemini-3.5-flash"
   ```

   This is the cloud equivalent of your local `.env` file — no `.env` file is needed or
   used on Streamlit Cloud.
6. Click **Deploy**. Streamlit Cloud installs `requirements.txt` and starts the app.
7. Once deployed, open the generated URL (`https://your-app-name.streamlit.app`).
8. **Test from another computer or device** (or your phone) by opening that same URL —
   confirm text summarization, PDF upload, and downloads all work without any local files
   or services running on your machine.

If you update `GEMINI_API_KEY` or `GEMINI_MODEL` in Secrets later, reboot the app from the
Streamlit Cloud dashboard (**Manage app → Reboot**) for the change to take effect.

## Security

- API keys are **never** hard-coded, printed, logged, or displayed in the UI — the sidebar
  only ever shows a "Configured / Not configured" status pill.
- `utils/config.py` is the single place that reads `GEMINI_API_KEY` / `GEMINI_MODEL`, from
  Streamlit Secrets first and environment variables second.
- `.gitignore` excludes `.env`, `.streamlit/secrets.toml`, virtual environments, and Python
  caches from version control.
- All Gemini API calls are isolated to `services/ai_service.py` — no other module touches
  the network.

## Project Structure

```
smartscribe-ai/
│
├── app.py                     # Entry point: page config, routing, wiring
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
│
├── .streamlit/
│   └── config.toml            # Theme + server config
│
├── components/                 # Streamlit UI — no Gemini calls here
│   ├── header.py               # Global CSS injection, page titles
│   ├── sidebar.py               # Nav, settings, Gemini status
│   ├── home.py                  # Landing page
│   ├── text_workspace.py        # Summarize Text page
│   ├── pdf_workspace.py         # Summarize PDF page
│   ├── result_view.py           # Shared result rendering + copy/download
│   ├── history_view.py          # Session history page
│   └── about.py                 # About page
│
├── services/                   # Business logic — no Streamlit calls here
│   ├── ai_service.py            # The ONLY module that calls Gemini
│   ├── pdf_service.py           # PyMuPDF extraction + typed errors
│   ├── summarizer.py            # Orchestrates single-pass vs. chunked runs
│   └── text_processor.py        # Cleaning + paragraph/sentence-aware chunking
│
├── prompts/                     # Prompt construction, no API calls
│   ├── summarization.py
│   ├── simplification.py
│   └── takeaways.py
│
├── utils/
│   ├── config.py                # Secrets/env resolution — no keys hard-coded
│   ├── validators.py            # Input validation
│   ├── metrics.py                # Word counts, reading time, compression %
│   ├── helpers.py                # Titles, timestamps, export formatting
│   └── session.py                # st.session_state history management
│
├── tests/                        # pytest — no real Gemini key required
│   ├── test_text_processor.py
│   ├── test_pdf_service.py
│   ├── test_metrics.py
│   └── test_validators.py
│
└── assets/
    ├── style.css                 # Custom design system
    └── README.md                 # Screenshot placeholders
```

## Future Improvements

- Persistent history via a real database (SQLite/Postgres) instead of session state
- Optional OCR pipeline for scanned/image-only PDFs
- Multi-file batch summarization
- User accounts and saved preferences
- Streaming responses for faster perceived performance on long documents

## Resume Description

> Built SmartScribe AI, a full-stack Streamlit application that summarizes and simplifies
> text and PDF documents using Google's Gemini API, with a modular Python architecture
> separating UI, prompt engineering, and AI-service layers.

> Implemented a document-chunking pipeline (map-reduce style) to reliably summarize long
> PDFs beyond a single request's practical size, with paragraph/sentence-aware splitting
> and typed error handling for corrupted, password-protected, and scanned PDFs.

> Designed a configurable prompt system supporting four processing modes (Summary, Explain
> Simply, Student Mode, Key Takeaways) with adjustable length, tone, and output format,
> backed by structured JSON responses and unit tests covering text processing and
> validation logic.

---

Built with Python, Streamlit, and Google Gemini.
