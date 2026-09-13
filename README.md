# gwoe-evidence-finder
Gemeinwohl Evidence Finder

A local, privacy-first tool that reads internal company documents and surfaces source-linked evidence for Gemeinwohl-Matrix topics (human dignity, solidarity & justice, ecological sustainability, transparency & co-determination).

Built as a working prototype for teams preparing a Common Good Balance Sheet — instead of manually searching through documents to find relevant evidence, upload what you already have and let the AI point you to it, with a citation back to the source.

How it works
Upload PDF, Word, or text documents — text is extracted directly in the browser
Pick a topic from the Gemeinwohl-Matrix
Click "Find evidence" — the AI reads your documents and returns relevant excerpts, quoted verbatim, with the source document, a confidence rating, and a short explanation of why each passage is relevant
A human reviewer checks the evidence, discusses it with stakeholders, and writes the final report — this tool finds candidate evidence, it does not write or approve anything itself
Why local, not cloud AI

Company documents can include sensitive supplier, employee, and financial information. This tool runs entirely on your own machine — document text is never sent to an external API. The AI model itself runs locally via Ollama, and all uploaded documents stay in your browser.

Tech stack
Frontend: Plain HTML/CSS/JavaScript — no framework, no build step
Document parsing: pdf.js (PDF) and mammoth.js (Word), both running client-side in the browser
Backend: FastAPI + Uvicorn
AI model: Ollama running an open-weight model (default: Llama 3.1)
Setup

1. Install Ollama and pull a model

bash
# Download from https://ollama.com/download, then:
ollama pull llama3.1

2. Install Python dependencies

bash
pip install fastapi uvicorn httpx --break-system-packages

3. Start the backend

bash
uvicorn backend:app --reload --port 8000

4. Open the frontend Open gwoe_evidence_finder_local.html directly in your browser (double-click it, or open via your browser's File menu). It's a plain local file — no server needed for the frontend itself.

Project structure
├── backend.py                          # FastAPI server, calls Ollama
├── gwoe_evidence_finder_local.html     # Full app with styling
├── gwoe_evidence_finder_lite.html      # Same logic, minimal styling
└── README.md
Limitations (current prototype)
Documents and results are stored in browser localStorage only — not shared between users, not persisted to a real database
Scanned/image-only PDFs can't be read (no OCR yet) — text-based PDFs and Word docs work
Smaller local models are less capable than large cloud models — expect occasional missed evidence or formatting slips
No authentication, multi-user support, or production hosting — this is a working proof of concept, not a deployed system
Status

Working prototype (v1). Next steps under discussion: moving to Hugging Face's Transformers/TGI for more model flexibility, containerizing with Docker, and testing against real Common Good Reports.
