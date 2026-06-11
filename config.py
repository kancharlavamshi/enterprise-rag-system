import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = "gpt-4o-mini"
EMBED_MODEL = "all-MiniLM-L6-v2"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(DATA_DIR, "documents")
DB_PATH = os.path.join(DATA_DIR, "database", "enterprise.db")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
VECTOR_STORE_PATH = os.path.join(DATA_DIR, "vector_store")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5

# ── Users ──────────────────────────────────────────────────────────────────────
USERS = {
    "alice": {"role": "admin",              "name": "Alice Smith",    "department": "IT"},
    "bob":   {"role": "hr_manager",         "name": "Bob Johnson",    "department": "HR"},
    "carol": {"role": "finance_analyst",    "name": "Carol Williams", "department": "Finance"},
    "dave":  {"role": "engineer",           "name": "Dave Brown",     "department": "Engineering"},
    "eve":   {"role": "compliance_officer", "name": "Eve Davis",      "department": "Legal"},
    "frank": {"role": "employee",           "name": "Frank Miller",   "department": "Sales"},
}

# ── Role → data-source categories ─────────────────────────────────────────────
ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": [
        "hr_docs", "financial_docs", "security_docs", "technical_docs",
        "compliance_docs", "incident_reports", "public",
        "employee_db", "financial_db", "project_db",
        "audit_logs", "system_alerts", "access_logs",
    ],
    "hr_manager": [
        "hr_docs", "employee_db", "project_db", "public",
    ],
    "finance_analyst": [
        "financial_docs", "financial_db", "project_db", "public",
    ],
    "engineer": [
        "technical_docs", "project_db", "system_alerts", "public",
    ],
    "compliance_officer": [
        "compliance_docs", "security_docs", "audit_logs",
        "access_logs", "incident_reports", "public",
    ],
    "employee": [
        "hr_docs", "project_db", "public",
    ],
}

# ── Intent → source categories ─────────────────────────────────────────────────
INTENT_SOURCE_MAP: dict[str, list[str]] = {
    "HR_POLICY":   ["hr_docs", "employee_db"],
    "FINANCIAL":   ["financial_docs", "financial_db"],
    "TECHNICAL":   ["technical_docs", "system_alerts"],
    "COMPLIANCE":  ["compliance_docs", "security_docs"],
    "EMPLOYEE":    ["employee_db", "hr_docs"],
    "INCIDENT":    ["incident_reports", "system_alerts"],
    "AUDIT":       ["audit_logs", "access_logs"],
    "GENERAL":     ["hr_docs", "financial_docs", "technical_docs", "public"],
}

# ── Source → retrieval type ────────────────────────────────────────────────────
VECTOR_CATEGORIES = {
    "hr_docs", "financial_docs", "security_docs", "technical_docs",
    "compliance_docs", "incident_reports", "public",
    "audit_logs", "system_alerts", "access_logs",
}

SQL_CATEGORIES = {"employee_db", "financial_db", "project_db"}
