# 🏦 LangGraph Banking Chatbot

A production-grade, agentic banking assistant built with **LangGraph**, featuring
fraud detection, sentiment escalation, RAG-powered knowledge retrieval,
multi-turn persistent memory, and automated quality control loops.

---

## Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [RAG Setup](#rag-setup)
- [Graph Flow](#graph-flow)
- [API Reference](#api-reference)
- [Monitoring](#monitoring)
- [License](#license)

---

## Architecture

```
User Message
     │
     ▼
┌─────────────────┐
│   pii_redactor  │  ← Masks card numbers, SSNs, account IDs
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ detect_intent_category│  ← Classifies intent + fraud scoring (0–100)
└──────────┬───────────┘
           │
    ┌──────▼──────┐
    │route_after_ │  score ≥ 80 ──────────────────────┐
    │fraud_score  │                                    │
    └──────┬──────┘                                    │
           │ score < 80                                │
           ▼                                           ▼
┌──────────────────┐                        ┌──────────────────┐
│ fetch_extra_info │  ← ChromaDB RAG        │  human_handoff   │ ──► END
└────────┬─────────┘                        └──────────────────┘
         │                                            ▲
         ▼                                            │
    ┌─────────┐                                       │
    │ planner │  ← Multi-turn MongoDB memory          │
    └────┬────┘                                       │
         │                                            │
         ▼                                            │
   ┌──────────┐                                       │
   │ responder│                                       │
   └─────┬────┘                                       │
         │                                            │
         ▼                                            │
┌─────────────────────┐                               │
│ sentiment_escalator │  compound ≤ −0.6 ─────────────┘
└──────────┬──────────┘
           │ compound > −0.6
           ▼
┌─────────────────────┐
│  route_after_       │
│  sentiment          │
└──────────┬──────────┘
           │
           ▼
┌──────────────────┐
│  latency_guard   │  > 8s ──────────────────────────► human_handoff
└────────┬─────────┘
         │ ≤ 8s
         ▼
┌──────────────────┐
│     critic       │  ← Model rotation: Mistral→Llama3→Qwen
└────────┬─────────┘
         │
  ┌──────▼──────┐
  │route_after_ │  iterations < 3 ──► improve ──► critic
  │   critic    │
  └──────┬──────┘
         │ quality_ok OR iterations ≥ 3
         ▼
    ┌──────────┐
    │ finalize │ ──► END
    └──────────┘
```

---

## Features

| Feature | Description |
|---|---|
| **PII Redaction** | Auto-masks card numbers, SSNs, and account identifiers via regex |
| **Fraud Scoring** | Risk score 0–100; sessions scoring ≥ 80 trigger human handoff |
| **Sentiment Escalation** | VADER compound score ≤ −0.6 routes distressed users to agents |
| **RAG Knowledge Base** | ChromaDB + HuggingFace embeddings for policy/FAQ retrieval |
| **Persistent Memory** | MongoDB stores last 10 turns per `session_id` |
| **Latency Budget** | 8-second hard limit; breaches auto-escalate to human handoff |
| **Critic Loop** | Up to 3 quality-control iterations with LLM model rotation |
| **CRM Webhook** | Diagnostic JSON payload pushed on every human handoff event |

---

## Tech Stack

- **Orchestration:** LangGraph, LangChain
- **LLMs:** Mistral, Llama 3, Qwen (via Ollama / API)
- **Vector Store:** ChromaDB
- **Embeddings:** HuggingFace `sentence-transformers`
- **Sentiment:** `vaderSentiment`
- **Memory:** MongoDB (`pymongo`)
- **Server:** FastAPI + Uvicorn
- **Monitoring:** Structured JSON logging



## Installation

### Prerequisites

- Python 3.10+
- MongoDB running locally or a MongoDB Atlas URI
- Ollama installed (for local LLMs) **or** API keys configured

**1. Clone the repository**

bash
git clone https://github.com/your-org/banking-chatbot.git
cd banking-chatbot

**2. Create and activate a virtual environment**

bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

**3. Install dependencies**

bash
pip install -r requirements.txt

**`requirements.txt`**


langgraph
langchain
langchain-community
fastapi
uvicorn[standard]
pymongo
chromadb
sentence-transformers
vaderSentiment
python-dotenv
httpx

---

## Configuration

Create a `.env` file in the project root:

env
# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB=banking_chatbot
MONGO_COLLECTION=sessions

# CRM Webhook (for human handoff)
CRM_WEBHOOK_URL=https://your-crm.example.com/webhook/escalation

# LLM (if using external API)
OPENAI_API_KEY=sk-...
OLLAMA_BASE_URL=http://localhost:11434

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION=banking_kb

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Latency
LATENCY_BUDGET_SECONDS=8

# Fraud
FRAUD_SCORE_THRESHOLD=80

---

## Running the Server

**Start MongoDB** (if running locally)

bash
mongod --dbpath ./data/db

**Start Ollama** (if using local LLMs)

bash
ollama serve
ollama pull mistral
ollama pull llama3
ollama pull qwen

**Start the FastAPI server**

bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

The API will be available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## RAG Setup

Place your source documents (`.txt`, `.pdf`, `.md`) inside the `docs/` folder,
then run the ingestion pipeline:

bash
python -m app.rag.ingest

This will:

1. Load all documents from `docs/`
2. Split them into chunks (512 tokens, 50 overlap)
3. Embed using `sentence-transformers/all-MiniLM-L6-v2`
4. Persist the vector store to `chroma_db/`

**Verify ingestion**

bash
python - <<'EOF'
from app.rag.retriever import get_retriever
r = get_retriever()
results = r.similarity_search("What is the overdraft policy?", k=3)
for doc in results:
    print(doc.page_content[:200])
    print("---")
EOF

**Re-ingest after adding new documents**

bash
python -m app.rag.ingest --reset

---

## Graph Flow
```
| Step | Node | Routing Logic |
|---|---|---|
| 1 | `pii_redactor` | Always → `detect_intent_category` |
| 2 | `detect_intent_category` | Always → `route_after_fraud_score` |
| 3 | `route_after_fraud_score` | score ≥ 80 → `human_handoff`, else → `fetch_extra_info` |
| 4 | `fetch_extra_info` | Always → `planner` |
| 5 | `planner` | Always → `responder` |
| 6 | `responder` | Always → `sentiment_escalator` |
| 7 | `sentiment_escalator` | Always → `route_after_sentiment` |
| 8 | `route_after_sentiment` | compound ≤ −0.6 → `human_handoff`, else → `latency_guard` |
| 9 | `latency_guard` | > 8s → `human_handoff`, else → `critic` |
| 10 | `critic` | Always → `route_after_critic` |
| 11 | `route_after_critic` | iterations < 3 & not ok → `improve` → `critic`, else → `finalize` |
| 12 | `human_handoff` | Always → `END` |
| 13 | `finalize` | Always → `END` |
```


## API Reference

### `POST /chat`

Send a message and receive a response.

**Request**

json
{
  "session_id": "user_abc123",
  "message": "What is my account balance?"
}

**Response**

json
{
  "session_id": "user_abc123",
  "response": "Your current balance is $2,450.00.",
  "fraud_score": 12,
  "sentiment": 0.34,
  "latency_ms": 1240,
  "escalated": false
}

### `POST /chat/reset`

Clear session memory for a given `session_id`.

json
{ "session_id": "user_abc123" }

### `GET /health`

Returns server and dependency health status.

json
{
  "status": "ok",
  "mongo": "connected",
  "chroma": "connected",
  "ollama": "connected"
}

---

## Monitoring

All nodes emit structured JSON logs:

json
{
  "timestamp": "2026-06-14T10:32:01Z",
  "session_id": "user_abc123",
  "node": "fraud_scorer",
  "fraud_score": 87,
  "action": "human_handoff_triggered",
  "latency_ms": 340
}

To tail logs in production:

bash
uvicorn app.main:app --log-config log_config.json

---

## License

MIT License — see [LICENSE](LICENSE) for details.
`

---

**Notes:**
- Replace `your-org` with your actual GitHub username/org
- The `--reset` flag on `ingest.py` needs to be implemented to wipe and re-create the Chroma collection
- Add a `Dockerfile` and `docker-compose.yml` if you want containerized deployment (let me know and I'll generate those too)