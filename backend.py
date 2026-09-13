"""
Gemeinwohl Evidence Finder -- local backend
============================================
Runs entirely on your own machine. No document text ever leaves your
computer -- it goes from this script straight to your local Ollama
instance and back.

set up:
  1. Install Ollama:        https://ollama.com/download
  2. Pull a model:          ollama pull llama3.1
     (mistral or qwen2.5 also work well; smaller = faster, less accurate)
  3. Install Python deps:   pip install fastapi uvicorn httpx --break-system-packages

RUN:
  uvicorn backend:app --reload --port 8000

Then open gwoe_evidence_finder_local.html directly in your browser
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import json
import re

app = FastAPI()

# "CORSMiddlware" function gives permision for HTML file to be opened and call api as backend (localhost:8000) are technically in different origins. 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1"   

#this next part defines what a valid request looks like 
class Document(BaseModel):
    name: str
    text: str


class ExtractRequest(BaseModel):  #ExtractRequest class basically requests three peices of information, a document 
                                  #and each document containing a name and a text, e.g. "hr_policy" for name and "Employees are entitled to..." for text in doc. 

    topic_label: str
    topic_desc: str
    documents: list[Document]


SYSTEM_PROMPT = """You are an evidence-extraction assistant for a Gemeinwohl-Ökonomie \
(Economy for the Common Good) report. Given a set of internal documents and one \
Gemeinwohl-Matrix topic, find passages that provide relevant evidence for that topic.

Rules:
- Only use text that is genuinely present in the documents provided. Never invent \
or paraphrase a quote -- copy it verbatim, in its ORIGINAL language, exactly as \
written in the source document (you may trim to a short excerpt, max ~30 words). \
Do not translate the quote itself -- it must remain an exact, checkable copy of \
the source text.
- If the quote is not already in English, also provide an English translation of \
that exact excerpt in the "translation" field. If the quote is already in English, \
set "translation" to an empty string.
- For each piece of evidence, name which document it came from exactly as given in \
its "DOCUMENT:" label.
- Rate your confidence that this passage is genuinely relevant evidence for the \
topic: "high", "medium", or "low".
- Add one short sentence of reasoning explaining why this passage is relevant. \
Always write the reasoning in ENGLISH, regardless of what language the source \
documents or the quote are in.
- If no relevant evidence exists in the documents, return an empty array.
- Return between 0 and 8 of the strongest pieces of evidence, not everything remotely related.

Respond ONLY with a JSON array, no other text, no markdown fences, in this exact shape:
[{"source": "document name", "quote": "verbatim excerpt in its original language", "translation": "English translation of the quote, or empty string if quote is already English", "confidence": "high", "reasoning": "why this is relevant, written in English"}]
"""


@app.post("/api/extract")
async def extract(req: ExtractRequest):
    doc_block = "\n\n".join(
        f'--- DOCUMENT: "{d.name}" ---\n{d.text}' for d in req.documents
    )
    user_prompt = (
        f"Gemeinwohl topic: {req.topic_label}\n"
        f"Topic description: {req.topic_desc}\n\n{doc_block}"
    )

    payload = {
        "model": MODEL_NAME,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=120) as client:
        try:
            resp = await client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()
        except Exception as e:
            return {"evidence": [], "error": f"Could not reach Ollama: {e}"}

    raw = resp.json().get("message", {}).get("content", "")
    cleaned = re.sub(r"```json|```", "", raw).strip()

    try:
        evidence = json.loads(cleaned)
        if not isinstance(evidence, list):
            evidence = []
    except json.JSONDecodeError:
        evidence = []

    return {"evidence": evidence}


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME}
