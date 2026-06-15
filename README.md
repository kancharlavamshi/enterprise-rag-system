# Enterprise RAG Intelligence System

> A production-grade, secure Retrieval-Augmented Generation system over heterogeneous enterprise data silos with strict RBAC, multi-source retrieval, grounded citations, and full explainability.
![overview](https://github.com/kancharlavamshi/enterprise-rag-system/blob/main/enterprise-rag-system.png)
---

## Versions

| Version | Repo | Status | Features |
|---------|------|--------|---------|
| **v1 — Demo** | Public (this repo) | ✅ Live | RAG pipeline, RBAC, multi-source retrieval, citations, explainability |
| **v2 — Production Auth** | Private branch | ✅ Built | + Login, registration, admin email approval, session management |
| **v3 — Security Hardening** | Private branch | ✅ Built | + Rate limiting, session expiry, input sanitization, CORS, security headers |

> 📩 **Want access to v2 or v3?** Open an issue or email `krishnedit3@gmail.com` with your use case.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?logo=openai)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange)
![SQLite](https://img.shields.io/badge/SQLite-Structured%20Data-blue?logo=sqlite)

---

## Architecture

```
User Query (Natural Language)
         │
         ▼
┌─────────────────────┐
│   FastAPI Backend   │  ←── Web UI (static/index.html)
└────────┬────────────┘
         │
┌────────▼────────┐
│   RBAC Auth     │  validates user_id → role → permissions
└────────┬────────┘
         │
┌────────▼────────┐
│ Intent Detector │  GPT-4o-mini classifies query intent
└────────┬────────┘
         │
┌────────▼────────┐
│  Query Router   │  intent × permissions → allowed sources
└───┬────┬────┬───┘
    │    │    │
┌───▼─┐┌─▼──┐┌▼──────┐
│Chroma││SQL ││JSON   │
│ DB  ││lite ││Logs   │
│Docs ││DB  ││Alerts │
└───┬─┘└─┬──┘└┬──────┘
    │     │    │
┌───▼─────▼────▼───┐
│ MultiSource       │  ranked + deduplicated RetrievedChunks
│ Retriever         │
└────────┬──────────┘
         │
┌────────▼──────────┐
│ Answer Generator  │  GPT-4o-mini → grounded answer + citations
└────────┬──────────┘
         │
Response: answer + [SOURCE_N] citations + confidence
        + retrieval_trace + denied_categories
```

---

## Features

- **Multi-source Retrieval** — semantic search (ChromaDB), NL→SQL (SQLite), JSON log search
- **Strict RBAC** — 6 roles × 12 data source categories, enforced at router + vector filter level
- **Grounded Answers** — every claim backed by retrieved context, never hallucinated
- **Inline Citations** — `[SOURCE_N]` markers with source file and category
- **Explainability** — full retrieval trace, relevance scores, confidence level, denied categories
- **Web UI** — clean dark-theme interface with user switcher and retrieval trace explorer

---

## Dataset

### Documents (7 files — `data/documents/`)
| File | Category | Content |
|------|----------|---------|
| `hr_policy.txt` | `hr_docs` | PTO (15-25 days), sick leave, parental leave (16 weeks), remote work, 401k |
| `financial_report_q4_2024.txt` | `financial_docs` | Revenue $45.2M, net income $9M, 2025 dept budgets |
| `security_policy.txt` | `security_docs` | Password policy, data classification, incident response |
| `technical_architecture.txt` | `technical_docs` | 47 microservices, CI/CD, AWS/K8s/Kafka stack |
| `compliance_gdpr.txt` | `compliance_docs` | GDPR rights, retention policies, breach notification |
| `incident_report_sept2024.txt` | `incident_reports` | Credential stuffing attack IR-2024-047 |
| `public_company_overview.txt` | `public` | Company info, leadership, office locations |

### SQL Database (`data/database/enterprise.db`)
| Table | Rows | Content |
|-------|------|---------|
| `employees` | 20 | Name, department, position, salary, hire date |
| `departments` | 5 | Engineering, HR, Finance, Sales, Legal |
| `projects` | 10 | Budget, spent, status, timeline |
| `financial_transactions` | 100 | Date, category, amount, approver |
| `budget_allocations` | 5 | Annual dept budgets vs actual spend |

### JSON Logs (`data/logs/`)
| File | Entries | Content |
|------|---------|---------|
| `audit_log.json` | 50 | User actions, resource access, session IDs |
| `system_alerts.json` | 20 | SIEM/WAF/IDS alerts with severity (LOW→CRITICAL) |
| `access_log.json` | 100 | Login success/failure, IP, MFA, geo |

---

## RBAC Design

| Role | Accessible Sources |
|------|--------------------|
| `admin` | All 12 sources |
| `hr_manager` | hr_docs, employee_db, project_db, public |
| `finance_analyst` | financial_docs, financial_db, project_db, public |
| `engineer` | technical_docs, project_db, system_alerts, public |
| `compliance_officer` | compliance_docs, security_docs, audit_logs, access_logs, incident_reports, public |
| `employee` | hr_docs, project_db, public |

**Demo users:** alice (admin), bob (hr_manager), carol (finance_analyst), dave (engineer), eve (compliance_officer), frank (employee)

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/kancharlavamshi/enterprise-rag-system.git
cd enterprise-rag-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your OpenAI API key
cp .env.example .env
# Edit .env → add your OPENAI_API_KEY

# 4. Generate synthetic data + index vector store (one-time, ~30s)
python setup_data.py

# 5. Start the server
python -m uvicorn app_demo:app --reload --port 8000

# 6. Open the UI
open http://localhost:8000
```

---

## API Reference

### `POST /query`
```json
{
  "user_id": "carol",
  "query": "What was Q4 2024 net income?",
  "max_results": 5
}
```

**Response:**
```json
{
  "user": { "user_id": "carol", "role": "finance_analyst" },
  "intents": ["FINANCIAL"],
  "intent_confidence": 0.95,
  "sources_queried": ["financial_docs", "financial_db"],
  "denied_categories": [],
  "answer": "ACME's net income in Q4 2024 was $9,044,000 [SOURCE_2].",
  "confidence": "HIGH — directly stated in context",
  "citations": "[SOURCE_1] financial_db | SQL\n[SOURCE_2] financial_docs | financial_report_q4_2024.txt",
  "retrieval_trace": [
    { "rank": 1, "source_category": "financial_db", "relevance_score": 0.9, ... }
  ],
  "chunks_used": 2,
  "latency_ms": 6449.7
}
```

### `GET /users` — list all users and their permissions  
### `GET /health` — health check  
### `GET /docs` — Swagger UI

---

## Project Structure

```
enterprise-rag-system/
├── app_demo.py              # FastAPI application — demo version (v1)
├── config.py                # RBAC policies, users, model config
├── setup_data.py            # Synthetic data generation + vector indexing
├── demo.py                  # CLI demo (rich terminal output)
├── requirements.txt
├── .env.example
├── core/
│   ├── auth.py              # RBAC authentication
│   ├── intent.py            # Intent detection (GPT-4o-mini)
│   ├── router.py            # Query routing by intent + permissions
│   ├── retriever.py         # Multi-source retrieval orchestrator
│   └── generator.py         # Answer generation with citations
├── sources/
│   ├── base.py              # RetrievedChunk dataclass
│   ├── pdf_source.py        # ChromaDB vector source
│   ├── sql_source.py        # NL→SQL on SQLite
│   └── json_source.py       # JSON log search
├── static/
│   └── index.html           # Web UI
└── data/
    ├── documents/           # 7 synthetic enterprise text files
    ├── database/            # SQLite DB (enterprise.db)
    └── logs/                # 3 JSON log files
```

---

## Security

### Implemented in v1 (this repo)
| Feature | Details |
|---|---|
| RBAC — two layers | Router blocks denied sources + ChromaDB metadata pre-filter |
| SQL injection prevention | Users never write SQL — GPT-4o-mini generates SELECT-only queries |
| Secrets management | All keys via `.env`, never hardcoded |

### Added in v2 (private)
- [x] Login + registration with password hashing (PBKDF2-SHA256, 100k iterations, unique salt)
- [x] Session cookies — `httponly=True`, `samesite=lax` (CSRF protection)
- [x] Admin approval gate — no user gets access without manual admin approval via email
- [x] Audit log — every query logged with user, timestamp, sources accessed

### Added in v3 (private)
- [x] Login rate limiting — max 5 attempts per IP per minute
- [x] Session expiry — auto-logout after 24 hours
- [x] Input sanitization — XSS stripping on all query inputs
- [x] CORS policy — restrict API calls to allowed origins only
- [x] Security headers — X-Frame-Options, X-Content-Type-Options, CSP
- [x] Account lockout — temporary ban after repeated failed logins

---

## Roadmap

- [ ] HTTPS with SSL/TLS (self-signed for local, Let's Encrypt for cloud)
- [ ] Support for real PDF uploads (PyPDF2 / pdfplumber)
- [ ] Vector store refresh API — re-index without restart
- [ ] Multi-tenancy — isolate data per organisation
- [ ] Chat history — multi-turn conversation memory
- [ ] Export answers as PDF report with citations

