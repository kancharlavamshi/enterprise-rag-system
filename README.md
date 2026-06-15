# Enterprise RAG Intelligence System

> A production-grade, secure Retrieval-Augmented Generation system over heterogeneous enterprise data silos — strict RBAC, multi-source retrieval, grounded citations, and full explainability.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?logo=openai)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange)
![SQLite](https://img.shields.io/badge/SQLite-Structured%20Data-blue?logo=sqlite)

---

## Versions

| Version | Visibility | Status | What it adds |
|---------|-----------|--------|-------------|
| **v1 — Demo** | Public (this repo) | Live | RAG pipeline, RBAC, multi-source retrieval, citations, explainability, 4-theme UI |
| **v2 — Auth** | Private | Built | + Login, registration, admin email approval, session cookies |
| **v3 — Security** | Private | Built | + Rate limiting, session expiry, input sanitization, CORS, security headers |
| **v4 — RAG Quality** | Private | Built | + Cross-encoder re-ranking, conversation memory, RAGAS evaluation, async email |

> v1 is fully runnable from this repo. v2, v3, v4 are private branches.
> Want access? Email `krishnedit3@gmail.com` with your use case.

---

## Quick Start (v1)

```bash
# 1. Clone
git clone https://github.com/kancharlavamshi/enterprise-rag-system.git
cd enterprise-rag-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your OpenAI API key
cp .env.example .env
# Edit .env and set: OPENAI_API_KEY=your_key_here

# 4. Generate synthetic enterprise data + index vector store (one-time, ~30 seconds)
python setup_data.py

# 5. Start the server
python -m uvicorn app_demo:app --reload --port 8000

# 6. Open in browser
open http://localhost:8000
```

Requirements: Python 3.9+, OpenAI API key, ~300 MB disk (ChromaDB + sentence-transformer models)

---

## What Each Version Adds

### v2 — Authentication (private)
Built on top of v1:
- User registration with name, email, department, role selection
- Admin approval via email (Approve / Reject one-click links)
- Login with email + password (PBKDF2-SHA256, 100k iterations)
- Session cookies (httponly, samesite=lax, 24-hour expiry)
- Protected `/app` route — shows your real authenticated role, no demo dropdown
- Run: `python -m uvicorn app:app --reload --port 8000`

### v3 — Security Hardening (private)
Built on top of v2:
- Login rate limiting — max 5 attempts per IP, 5-minute lockout
- Query rate limiting — max 30 queries/min per IP
- Server-side session expiry — auto-logout after 24 hours
- Input sanitization — XSS stripping on all user inputs before processing
- CORS policy — allowed origins configurable via `.env`
- Security headers — X-Frame-Options DENY, X-Content-Type-Options nosniff, X-XSS-Protection, Content-Security-Policy, Strict-Transport-Security
- Run: `python -m uvicorn app_v3:app --reload --port 8000`

### v4 — RAG Quality (private)
Built on top of v3:
- Cross-encoder re-ranking — all retrieved chunks scored by `cross-encoder/ms-marco-MiniLM-L-6-v2` and reordered before the LLM sees them
- Semantic chunking — paragraph/sentence boundary splitting with 1-sentence overlap (replaces fixed word-count chunking)
- Conversation memory — last 5 turns per session passed as context to the LLM, keyed by auth cookie
- RAGAS evaluation — `POST /evaluate` endpoint scores any answer for faithfulness, answer relevancy, and context precision
- Memory clear — `DELETE /memory/{session_id}` clears conversation history on demand
- Async email — registration responds instantly; SMTP runs in a background thread, no 15-second delays
- 4-theme UI across all pages — Dark / Light / Ocean / Mocha, persisted in localStorage
- Run: `python -m uvicorn app_v4:app --reload --port 8000`

---

## Architecture

```
User Query (Natural Language)
         |
         v
+---------------------+
|   FastAPI Backend   |  <-- Web UI (static/index.html)
+--------+------------+
         |
+--------v--------+
|   RBAC Auth     |  user_id -> role -> permitted source categories
+--------+--------+
         |
+--------v--------+
| Intent Detector |  GPT-4o-mini classifies query intent
+--------+--------+
         |
+--------v--------+
|  Query Router   |  intent x permissions -> allowed sources
+---+----+----+---+
    |    |    |
+---v-++--v-++v------+
|Chroma||SQL ||JSON  |
| DB  ||lite ||Logs  |
|Docs ||DB  ||Alerts|
+---+-++--+--++--+---+
    |     |      |
+---v-----v------v------+
| MultiSourceRetriever  |  dedup -> cross-encoder re-rank (v4)
+--------+--------------+
         |
+--------v----------+
| Answer Generator  |  conversation history (v4) + GPT-4o-mini
+--------+----------+
         |
Response: answer + [SOURCE_N] citations + confidence
        + retrieval_trace + denied_categories
```

---

## Features (v1)

- Multi-source Retrieval — semantic search (ChromaDB), NL-to-SQL (SQLite), JSON log search in one query
- Strict RBAC — 6 roles x 12 data source categories, enforced at router level AND ChromaDB metadata pre-filter
- Grounded Answers — every claim backed by retrieved context, never hallucinated
- Inline Citations — [SOURCE_N] markers with source file and category
- Explainability — full retrieval trace, relevance scores, confidence level, denied categories shown in UI
- 4-Theme UI — Dark / Light / Ocean / Mocha, switch from the header

---

## Dataset

### Documents (data/documents/)
| File | Category | Content |
|------|----------|---------|
| hr_policy.txt | hr_docs | PTO (15-25 days), sick leave, parental leave (16 weeks), remote work, 401k |
| financial_report_q4_2024.txt | financial_docs | Revenue $45.2M, net income $9M, 2025 dept budgets |
| security_policy.txt | security_docs | Password policy, data classification, incident response |
| technical_architecture.txt | technical_docs | 47 microservices, CI/CD, AWS/K8s/Kafka stack |
| compliance_gdpr.txt | compliance_docs | GDPR rights, retention policies, breach notification |
| incident_report_sept2024.txt | incident_reports | Credential stuffing attack IR-2024-047 |
| public_company_overview.txt | public | Company info, leadership, office locations |

### SQL Database (data/database/enterprise.db)
| Table | Rows | Content |
|-------|------|---------|
| employees | 20 | Name, department, position, salary, hire date |
| departments | 5 | Engineering, HR, Finance, Sales, Legal |
| projects | 10 | Budget, spent, status, timeline |
| financial_transactions | 100 | Date, category, amount, approver |
| budget_allocations | 5 | Annual dept budgets vs actual spend |

### JSON Logs (data/logs/)
| File | Entries | Content |
|------|---------|---------|
| audit_log.json | 50 | User actions, resource access, session IDs |
| system_alerts.json | 20 | SIEM/WAF/IDS alerts with severity (LOW to CRITICAL) |
| access_log.json | 100 | Login success/failure, IP, MFA, geo |

---

## RBAC Design

| Role | Accessible Sources |
|------|--------------------|
| admin | All 12 sources |
| hr_manager | hr_docs, employee_db, project_db, public |
| finance_analyst | financial_docs, financial_db, project_db, public |
| engineer | technical_docs, project_db, system_alerts, public |
| compliance_officer | compliance_docs, security_docs, audit_logs, access_logs, incident_reports, public |
| employee | hr_docs, project_db, public |

Demo users (v1): alice (admin), bob (hr_manager), carol (finance_analyst), dave (engineer), eve (compliance_officer), frank (employee)

---

## API Reference

### POST /query
```json
{
  "user_id": "carol",
  "query": "What was Q4 2024 net income?",
  "max_results": 5
}
```

Response:
```json
{
  "user": { "user_id": "carol", "role": "finance_analyst" },
  "intents": ["FINANCIAL"],
  "intent_confidence": 0.95,
  "sources_queried": ["financial_docs", "financial_db"],
  "denied_categories": [],
  "answer": "ACME's net income in Q4 2024 was $9,044,000 [SOURCE_2].",
  "confidence": "HIGH -- directly stated in context",
  "citations": "[SOURCE_1] financial_db | SQL\n[SOURCE_2] financial_docs | financial_report_q4_2024.txt",
  "retrieval_trace": [
    { "rank": 1, "source_category": "financial_db", "relevance_score": 0.91 }
  ],
  "chunks_used": 2,
  "latency_ms": 1842.3
}
```

### GET /users — list all users and their permissions
### GET /health — health check
### GET /docs — Swagger UI (auto-generated)

---

## Project Structure

```
enterprise-rag-system/
├── app_demo.py          # v1 — FastAPI demo app (no auth required)
├── config.py            # RBAC roles, users, model config
├── setup_data.py        # Generates synthetic data + indexes ChromaDB
├── requirements.txt
├── .env.example
├── core/
│   ├── auth.py          # RBAC authenticator
│   ├── intent.py        # Intent detection via GPT-4o-mini
│   ├── router.py        # Routes query to allowed sources by role
│   ├── retriever.py     # Orchestrates multi-source retrieval
│   └── generator.py     # Builds prompt + calls GPT-4o-mini
├── sources/
│   ├── base.py          # RetrievedChunk dataclass
│   ├── pdf_source.py    # ChromaDB vector search
│   ├── sql_source.py    # NL to SQL on SQLite
│   └── json_source.py   # JSON log search
├── static/
│   └── index.html       # Web UI with 4-theme switcher
└── data/
    ├── documents/        # 7 synthetic enterprise text files
    ├── database/         # SQLite (enterprise.db)
    └── logs/             # 3 JSON log files
```

---

## Security

### v1 (this repo)
| Feature | How |
|---|---|
| RBAC — two layers | Router blocks denied sources + ChromaDB metadata pre-filter |
| SQL injection prevention | GPT-4o-mini generates SELECT-only queries; no raw user SQL |
| Secrets management | All keys via .env, never hardcoded |

### v2 (private)
- PBKDF2-SHA256 password hashing (100k iterations)
- Admin email approval before any account is activated
- Session tokens stored server-side in SQLite, never exposed to client

### v3 (private)
- Login rate limiting — 5 attempts per IP, 5-minute lockout
- Query rate limiting — 30 queries/min per IP
- Server-side session expiry — 24-hour auto-logout
- Input sanitization — XSS stripping on all inputs
- CORS + security headers (X-Frame-Options, CSP, HSTS)

### v4 (private)
- All of v3, plus registration is always instant (email async, no blocking)

---

## Roadmap

- [ ] HTTPS / SSL with Let's Encrypt for cloud deployment
- [ ] Real PDF uploads (PyPDF2 / pdfplumber)
- [ ] Vector store refresh API — re-index without restart
- [ ] Multi-tenancy — isolate data per organisation
- [ ] Export answers as PDF report with citations
