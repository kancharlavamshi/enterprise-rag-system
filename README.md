# Enterprise RAG Intelligence System

> A production-grade, secure Retrieval-Augmented Generation system over heterogeneous enterprise data silos — strict RBAC, multi-source retrieval, grounded citations, and full explainability.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?logo=openai)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange)
![SQLite](https://img.shields.io/badge/SQLite-Structured%20Data-blue?logo=sqlite)

---

## Versions

This project has been built iteratively across 4 versions. **v1 is open-source in this repo.** v2, v3, and v4 are in a private repository — see the access section below.

| Version | What it is |
|---------|-----------|
| **v1 — Demo** | Core RAG pipeline with RBAC, multi-source retrieval, citations, explainability. Fully runnable — instructions below. |
| **v2 — Auth** | Adds real login system — user registration, admin email approval, password hashing, session cookies. |
| **v3 — Security** | Adds rate limiting, session expiry, XSS sanitization, CORS policy, security headers on top of v2. |
| **v4 — RAG Quality** | Adds cross-encoder re-ranking, conversation memory, semantic chunking, RAGAS evaluation on top of v3. |

---

## Run v1 (Demo)

### Prerequisites
- Python 3.9 or higher
- An OpenAI API key (get one at platform.openai.com)
- ~300 MB disk space (ChromaDB + embedding models)

### Step-by-step

```bash
# 1. Clone this repository
git clone https://github.com/kancharlavamshi/enterprise-rag-system.git
cd enterprise-rag-system
```

```bash
# 2. Install dependencies
pip install -r requirements.txt
```

```bash
# 3. Configure your API key
cp .env.example .env
```

Open `.env` and set your key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

```bash
# 4. Generate synthetic enterprise data and index the vector store
# This runs once and takes about 30 seconds
python setup_data.py
```

```bash
# 5. Start the server
python -m uvicorn app_demo:app --reload --port 8000
```

```bash
# 6. Open the app in your browser
open http://localhost:8000
```

### Demo users
The app comes with 6 pre-built demo users. Select any from the dropdown in the UI:

| User | Role | Can access |
|------|------|-----------|
| Alice Smith | admin | Everything — all 12 data sources |
| Bob Johnson | hr_manager | HR docs, employee database, projects |
| Carol Williams | finance_analyst | Financial docs, financial database, projects |
| Dave Brown | engineer | Technical docs, system alerts, projects |
| Eve Davis | compliance_officer | Compliance, security, audit logs, access logs, incidents |
| Frank Miller | employee | HR docs, projects, public info only |

### Try these queries
- `What is the parental leave policy?` (as Bob — HR Manager)
- `What was Q4 2024 net income?` (as Carol — Finance Analyst)
- `Show recent security alerts` (as Alice — Admin)
- `What microservices does ACME use?` (as Dave — Engineer)
- `What happened in the September 2024 incident?` (as Eve — Compliance Officer)
- `How many PTO days do I get?` (as Frank — Employee)

---

## Architecture

```
User Query
    │
    ▼
┌───────────────────┐
│  FastAPI Backend  │  ← Web UI (static/index.html)
└────────┬──────────┘
         │
┌────────▼────────┐
│   RBAC Auth     │  user_id → role → permitted sources
└────────┬────────┘
         │
┌────────▼────────┐
│ Intent Detector │  GPT-4o-mini classifies the query intent
└────────┬────────┘
         │
┌────────▼────────┐
│  Query Router   │  intent × permissions → allowed data sources
└──┬──────┬────┬──┘
   │      │    │
┌──▼──┐ ┌─▼──┐ ┌▼──────┐
│Chroma│ │SQL │ │JSON   │
│ DB  │ │lite│ │Logs   │
│Docs │ │ DB │ │Alerts │
└──┬──┘ └─┬──┘ └┬──────┘
   │       │     │
┌──▼───────▼─────▼──────┐
│  MultiSourceRetriever  │  dedup + rank retrieved chunks
└────────────────────────┘
         │
┌────────▼──────────┐
│  AnswerGenerator  │  GPT-4o-mini → grounded answer + citations
└───────────────────┘
         │
    Response:
    answer + [SOURCE_N] citations + confidence
    + retrieval_trace + denied_categories
```

---

## What v1 Gives You

- **Multi-source Retrieval** — one query searches ChromaDB (documents), SQLite (structured data), and JSON logs simultaneously
- **Strict RBAC** — enforced at two layers: query router blocks denied sources AND ChromaDB metadata pre-filters vectors at retrieval time
- **Grounded Answers** — GPT-4o-mini is instructed to use only retrieved context; every claim has a source
- **Inline Citations** — `[SOURCE_1]`, `[SOURCE_2]` markers in the answer, with a source list at the bottom
- **Retrieval Trace** — expandable panel in the UI shows every chunk retrieved, its source, category, and relevance score
- **Confidence Level** — HIGH / MEDIUM / LOW with reasoning on every response
- **4-Theme UI** — Dark, Light, Ocean, Mocha — switch from the header, persists across sessions

---

## Dataset (Synthetic)

### Documents — `data/documents/`
| File | Category | Contains |
|------|----------|---------|
| `hr_policy.txt` | hr_docs | PTO 15–25 days, parental leave 16 weeks, sick leave, 401k, remote work |
| `financial_report_q4_2024.txt` | financial_docs | Revenue $45.2M, net income $9M, department budgets 2025 |
| `security_policy.txt` | security_docs | Password policy, data classification, incident response SLA |
| `technical_architecture.txt` | technical_docs | 47 microservices, CI/CD, AWS + Kubernetes + Kafka |
| `compliance_gdpr.txt` | compliance_docs | GDPR rights, retention schedules, breach notification |
| `incident_report_sept2024.txt` | incident_reports | Credential stuffing attack IR-2024-047, timeline, remediation |
| `public_company_overview.txt` | public | Company mission, leadership team, office locations |

### SQL — `data/database/enterprise.db`
| Table | Rows | Contains |
|-------|------|---------|
| `employees` | 20 | Name, department, position, salary, hire date |
| `departments` | 5 | Name, head, headcount, location |
| `projects` | 10 | Name, budget, spent, status, timeline |
| `financial_transactions` | 100 | Date, category, amount, approver |
| `budget_allocations` | 5 | Annual budget vs actual per department |

### JSON Logs — `data/logs/`
| File | Entries | Contains |
|------|---------|---------|
| `audit_log.json` | 50 | User actions, resources accessed, session IDs, timestamps |
| `system_alerts.json` | 20 | SIEM/WAF/IDS alerts with severity LOW → CRITICAL |
| `access_log.json` | 100 | Login success/failure, IP, MFA status, geo location |

---

## API

### `POST /query`
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
  "user": { "user_id": "carol", "role": "finance_analyst", "department": "Finance" },
  "intents": ["FINANCIAL"],
  "intent_confidence": 0.95,
  "sources_queried": ["financial_docs", "financial_db"],
  "denied_categories": [],
  "answer": "ACME's net income in Q4 2024 was $9,044,000 [SOURCE_2].",
  "confidence": "HIGH — directly stated in retrieved context",
  "citations": "[SOURCE_1] financial_db | SQL: financial_transactions\n[SOURCE_2] financial_docs | financial_report_q4_2024.txt",
  "retrieval_trace": [
    { "rank": 1, "source_category": "financial_db", "source": "SQL: budget_allocations", "relevance_score": 0.91, "content_preview": "..." }
  ],
  "chunks_used": 4,
  "latency_ms": 1842.3
}
```

### `GET /users` — list all demo users and their permissions
### `GET /health` — service health check
### `GET /docs` — interactive Swagger UI

---

## Project Structure

```
enterprise-rag-system/
├── app_demo.py          # FastAPI application — v1 demo (no auth)
├── config.py            # RBAC role definitions, demo users, model settings
├── setup_data.py        # Generates all synthetic data + indexes ChromaDB
├── demo.py              # CLI version (rich terminal output, no server needed)
├── requirements.txt
├── .env.example
│
├── core/
│   ├── auth.py          # RBAC authenticator — validates user_id → role → permissions
│   ├── intent.py        # Intent detection via GPT-4o-mini
│   ├── router.py        # Maps intent × permissions to allowed data sources
│   ├── retriever.py     # Orchestrates multi-source retrieval + deduplication
│   └── generator.py     # Builds prompt with context + calls GPT-4o-mini
│
├── sources/
│   ├── base.py          # RetrievedChunk dataclass
│   ├── pdf_source.py    # ChromaDB vector search (semantic similarity)
│   ├── sql_source.py    # NL → SQL on SQLite (structured queries)
│   └── json_source.py   # JSON log search (recent alerts, audit events)
│
├── static/
│   └── index.html       # Web UI — user selector, query input, result display, themes
│
└── data/
    ├── documents/        # 7 synthetic enterprise text files
    ├── database/         # enterprise.db (SQLite)
    └── logs/             # audit_log.json, system_alerts.json, access_log.json
```

---

## v2, v3, v4 — Private Repository

The advanced versions are maintained in a private repository. Here is what each adds:

### v2 — Production Authentication
- User registration form (name, email, department, role)
- Admin email approval workflow — admin receives an email with one-click Approve / Reject
- No account is activated until an admin approves it
- Login with email + password (PBKDF2-SHA256, 100,000 iterations)
- Session cookies (`httponly`, `samesite=lax`, 24-hour expiry)
- Authenticated app UI — shows your real approved role, no demo dropdown
- Built with: `auth_db.py` (SQLite sessions), `core/email_service.py` (Gmail SMTP)

### v3 — Security Hardening
- Login rate limiting — 5 failed attempts per IP triggers a 5-minute lockout
- Query rate limiting — max 30 queries per minute per IP
- Server-side session expiry — sessions auto-expire after 24 hours regardless of cookie
- Input sanitization — XSS stripping applied to every user input before processing
- CORS policy — allowed origins locked down via environment variable
- Security headers on every response:
  - `X-Frame-Options: DENY` (clickjacking protection)
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection: 1; mode=block`
  - `Content-Security-Policy`
  - `Strict-Transport-Security` (HSTS)

### v4 — RAG Quality
- **Cross-encoder re-ranking** — retrieved chunks are re-scored by `cross-encoder/ms-marco-MiniLM-L-6-v2` and reordered so the most relevant reach the LLM first
- **Semantic chunking** — documents split at paragraph/sentence boundaries with 1-sentence overlap, preserving meaning better than fixed word-count chunks
- **Conversation memory** — last 5 conversation turns stored per session and passed to the LLM as context, enabling follow-up questions
- **RAGAS evaluation** — `POST /evaluate` endpoint scores any answer on faithfulness, answer relevancy, and context precision
- **Async email** — registration always responds in under 1 second; SMTP runs in a background thread
- **4-theme UI** — Dark / Light / Ocean / Mocha across all pages, persisted in localStorage

---

## Request Access to v2 / v3 / v4

The private repository is available on request for:
- Developers building production RAG systems
- Security engineers evaluating the auth + hardening stack
- Researchers working on RAG quality and evaluation

**Email `krishnedit3@gmail.com`** with your name, use case, and which version you need.

---

## Roadmap

- [ ] HTTPS / SSL with Let's Encrypt for cloud deployment
- [ ] Real PDF uploads (PyPDF2 / pdfplumber)
- [ ] Vector store refresh API — re-index without server restart
- [ ] Multi-tenancy — isolate data per organisation
- [ ] Export answers as PDF report with citations
