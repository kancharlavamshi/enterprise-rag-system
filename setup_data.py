"""
Run once to generate synthetic enterprise data and populate the vector store + SQLite DB.
Usage: python setup_data.py
"""
from __future__ import annotations
import json
import os
import sqlite3
import sys
import textwrap
from datetime import date, timedelta
import random

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR  = os.path.join(BASE, "data", "documents")
DB_PATH   = os.path.join(BASE, "data", "database", "enterprise.db")
LOGS_DIR  = os.path.join(BASE, "data", "logs")
STORE_DIR = os.path.join(BASE, "data", "vector_store")

for d in (DOCS_DIR, os.path.dirname(DB_PATH), LOGS_DIR, STORE_DIR):
    os.makedirs(d, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# 1. SYNTHETIC DOCUMENTS
# ══════════════════════════════════════════════════════════════════════════════

DOCUMENTS: dict[str, tuple[str, str]] = {
    # filename: (source_category, content)
    "hr_policy.txt": ("hr_docs", textwrap.dedent("""
        ACME CORP HUMAN RESOURCES POLICY MANUAL — v3.2 (2024)

        1. PAID TIME OFF (PTO)
        Full-time employees accrue 15 days of PTO per year for the first 3 years,
        20 days per year from years 4-7, and 25 days per year after 7 years of service.
        PTO requests must be submitted at least 2 weeks in advance via the HR portal.
        Unused PTO up to 5 days may be carried over to the next calendar year.

        2. SICK LEAVE
        Employees receive 10 paid sick days per year. Sick leave does not roll over.
        For absences exceeding 3 consecutive days, a doctor's note is required.
        Short-term disability kicks in after 5 consecutive sick days.

        3. PARENTAL LEAVE
        Primary caregivers receive 16 weeks of fully paid parental leave.
        Secondary caregivers receive 6 weeks of fully paid parental leave.
        Parental leave must be taken within 12 months of the birth or adoption.

        4. REMOTE WORK POLICY
        Employees may work remotely up to 3 days per week with manager approval.
        Fully remote arrangements require VP-level approval and annual review.
        Remote employees must maintain core hours of 10:00 AM – 3:00 PM local time.

        5. PERFORMANCE REVIEW PROCESS
        Reviews are conducted bi-annually in January and July.
        Ratings: Exceeds Expectations (5), Meets Expectations (4), Needs Improvement (3),
        Below Expectations (2), Unsatisfactory (1).
        Employees rated 4 or above are eligible for merit increases.

        6. CODE OF CONDUCT
        Employees must maintain professional behaviour at all times.
        Zero tolerance for harassment, discrimination, or retaliation.
        Conflicts of interest must be disclosed to HR within 30 days of occurrence.
        Violations may result in disciplinary action up to and including termination.

        7. HEALTH BENEFITS
        ACME provides comprehensive medical, dental, and vision coverage.
        Company pays 80% of premiums for individual coverage, 60% for family coverage.
        401(k) plan with 4% employer match up to 6% of employee contribution.
        Annual HSA contribution of $750 for individuals, $1,500 for families.

        8. TRAINING & DEVELOPMENT
        Each employee has an annual L&D budget of $2,500.
        Tuition reimbursement up to $5,000 per year for job-related degrees.
        Mandatory compliance training must be completed by March 31 each year.
    """)),

    "financial_report_q4_2024.txt": ("financial_docs", textwrap.dedent("""
        ACME CORP — Q4 2024 FINANCIAL REPORT (CONFIDENTIAL)

        EXECUTIVE SUMMARY
        ACME Corp delivered strong Q4 2024 results, exceeding guidance on revenue and EPS.

        INCOME STATEMENT (Q4 2024)
        Total Revenue:          $45,200,000
        Cost of Goods Sold:     $18,080,000
        Gross Profit:           $27,120,000   (Gross Margin: 60.0%)
        Operating Expenses:
          Sales & Marketing:     $6,780,000
          Research & Development: $4,520,000
          General & Administrative: $3,614,000
          Total OpEx:            $14,914,000
        EBITDA:                 $12,206,000
        Net Income:             $9,044,000    (Net Margin: 20.1%)

        FULL YEAR 2024
        Revenue:                $162,400,000  (+18% YoY)
        Net Income:             $32,480,000   (+24% YoY)

        DEPARTMENT BUDGETS 2025
        Engineering:            $28,000,000
        Sales & Marketing:      $22,000,000
        Human Resources:         $5,500,000
        Finance:                 $4,200,000
        Legal & Compliance:      $3,800,000
        Operations:              $9,500,000

        CASH & LIQUIDITY
        Cash and equivalents:   $87,600,000
        Total debt:             $12,000,000
        Net cash position:      $75,600,000

        TOP 5 REVENUE STREAMS (Q4 2024)
        1. SaaS subscriptions:  $24,860,000 (55%)
        2. Professional services: $8,136,000 (18%)
        3. Licensing:            $5,424,000 (12%)
        4. Maintenance & support: $4,520,000 (10%)
        5. Other:                $2,260,000  (5%)

        OUTLOOK 2025
        Revenue guidance:       $195,000,000 – $200,000,000
        EBITDA margin target:   28% – 30%
        Headcount growth:       +12% (targeting 650 FTE by year-end)
    """)),

    "security_policy.txt": ("security_docs", textwrap.dedent("""
        ACME CORP INFORMATION SECURITY POLICY — v2.1 (2024)

        1. DATA CLASSIFICATION
        Level 1 – Public: General corporate information, press releases.
        Level 2 – Internal: Standard business operations, non-sensitive.
        Level 3 – Confidential: Customer data, financials, HR records.
        Level 4 – Restricted: Trade secrets, merger plans, legal communications.

        2. ACCESS CONTROL
        Principle of least privilege applies to all system access.
        All privileged accounts require MFA. Service accounts must not be shared.
        Access reviews are conducted quarterly. Dormant accounts deactivated after 90 days.
        Separation of duties required for financial systems above $10,000 approval.

        3. PASSWORD POLICY
        Minimum length: 14 characters. Must include upper, lower, digit, special char.
        Password rotation: every 90 days for privileged accounts, 180 days for standard.
        Password reuse: last 12 passwords may not be reused.
        Account lockout: 5 failed attempts → 30-minute lockout.

        4. INCIDENT RESPONSE
        Severity 1 (Critical): Response within 1 hour. CISO, CTO, CEO notified.
        Severity 2 (High): Response within 4 hours. CISO and department head notified.
        Severity 3 (Medium): Response within 24 hours. Security team notified.
        Severity 4 (Low): Response within 72 hours. Logged and tracked.
        All incidents must be logged in the SIEM and reported to compliance within 72h.

        5. ENCRYPTION STANDARDS
        Data at rest: AES-256. Data in transit: TLS 1.3 minimum.
        Cryptographic keys managed via enterprise HSM. Key rotation: annually.
        End-to-end encryption required for all Restricted data.

        6. THIRD-PARTY VENDOR SECURITY
        All vendors handling Level 3+ data must complete annual security assessments.
        SOC 2 Type II report required before onboarding.
        Right-to-audit clause mandatory in all vendor contracts.
    """)),

    "technical_architecture.txt": ("technical_docs", textwrap.dedent("""
        ACME CORP — TECHNICAL ARCHITECTURE OVERVIEW (2024)

        INFRASTRUCTURE OVERVIEW
        Cloud Provider: AWS (primary), GCP (DR)
        Regions: us-east-1 (primary), us-west-2 (failover)
        Uptime SLA: 99.95% (approximately 4.4 hours downtime/year)

        MICROSERVICES ARCHITECTURE
        Services are containerised (Docker) and orchestrated via Kubernetes (EKS).
        Service mesh: Istio for inter-service communication and mTLS.
        API Gateway: Kong — handles auth, rate limiting, and routing.
        Total microservices: 47 across 6 domains.

        CORE DOMAINS
        1. Identity & Access:  AuthService, RoleService, TokenService
        2. Customer Platform:  AccountService, ProfileService, BillingService
        3. Product Engine:     CatalogService, SearchService, RecommendationService
        4. Data Pipeline:      IngestionService, TransformService, ExportService
        5. Notification Hub:   EmailService, SMSService, WebhookService
        6. Analytics:          MetricsService, ReportService, DashboardService

        CI/CD PIPELINE
        Source control: GitHub Enterprise
        Build: GitHub Actions → Docker build → ECR push
        Deploy: ArgoCD (GitOps) → EKS
        Testing: unit (Jest/pytest), integration (Testcontainers), e2e (Playwright)
        Release cadence: weekly for features, daily for hotfixes.

        DATABASES
        PostgreSQL 15 (RDS) — transactional data
        MongoDB 6 (Atlas) — document storage, event logs
        Redis 7 (ElastiCache) — caching, sessions
        Elasticsearch 8 — search and log aggregation
        Snowflake — data warehouse / analytics

        OBSERVABILITY STACK
        Metrics: Prometheus + Grafana
        Logs: FluentBit → Elasticsearch → Kibana
        Traces: OpenTelemetry → Jaeger
        Alerting: PagerDuty (Sev1/2), Slack (Sev3/4)
        MTTR target: < 30 minutes for Sev1 incidents.

        API STANDARDS
        REST APIs: OpenAPI 3.1 specs mandatory. Versioning via URL path (/v1/, /v2/).
        GraphQL: used by customer-facing portal only.
        Event streaming: Kafka (MSK) for async workflows.
        gRPC: used for internal high-throughput service-to-service calls.
    """)),

    "compliance_gdpr.txt": ("compliance_docs", textwrap.dedent("""
        ACME CORP — GDPR COMPLIANCE FRAMEWORK (2024)

        DATA PROTECTION OFFICER (DPO)
        Name: Margaret Thompson
        Email: dpo@acmecorp.com
        Phone: +1-415-555-0199

        DATA SUBJECT RIGHTS
        Right of Access (Art. 15): Fulfilled within 30 days of request.
        Right to Erasure (Art. 17): Fulfilled within 30 days. Exceptions logged.
        Right to Portability (Art. 20): Data provided in JSON/CSV format.
        Right to Rectification (Art. 16): Corrections within 10 business days.
        Right to Object (Art. 21): Opt-out processed immediately.

        LAWFUL BASIS FOR PROCESSING
        Customer data: Contractual necessity + Consent
        Employee data: Legal obligation + Legitimate interests
        Analytics: Legitimate interests (with opt-out mechanism)
        Marketing: Explicit consent required

        DATA RETENTION POLICY
        Customer account data: Retained 7 years post-account closure.
        Transaction records: Retained 10 years (tax/legal compliance).
        Application logs: Retained 90 days.
        Audit logs: Retained 3 years.
        Marketing data: Retained until consent withdrawn.

        BREACH NOTIFICATION PROCEDURE
        Internal detection to DPO notification: within 1 hour.
        DPO assessment and risk scoring: within 4 hours.
        If high risk, notify supervisory authority (ICO) within 72 hours.
        Notify affected data subjects within 72 hours if high risk to individuals.
        All breaches documented in the breach register regardless of notification outcome.

        INTERNATIONAL DATA TRANSFERS
        EU-US Data Privacy Framework certification maintained.
        Standard Contractual Clauses (SCCs) used for non-Framework transfers.
        Transfer Impact Assessments (TIAs) conducted for high-risk transfers.

        PRIVACY BY DESIGN
        DPIAs mandatory for new processing activities involving sensitive data.
        Data minimisation enforced in all new product features.
        Pseudonymisation applied to analytics datasets.
    """)),

    "incident_report_sept2024.txt": ("incident_reports", textwrap.dedent("""
        ACME CORP — SECURITY INCIDENT REPORT #IR-2024-047
        Classification: CONFIDENTIAL — RESTRICTED ACCESS

        INCIDENT OVERVIEW
        Date Detected:    2024-09-15 02:34 UTC
        Date Contained:   2024-09-15 05:17 UTC
        Severity:         Sev2 (High)
        Type:             Unauthorised Access Attempt
        Status:           Resolved

        SUMMARY
        A credential stuffing attack targeted the customer portal login endpoint.
        Attackers used 14,200 credential pairs obtained from a third-party breach.
        231 accounts were successfully authenticated before detection.
        No data exfiltration confirmed. All affected sessions terminated within 43 minutes.

        TIMELINE
        02:34 — Anomalous login spike detected by Elasticsearch alert rule.
        02:41 — On-call engineer acknowledged PagerDuty alert.
        02:55 — CISO, CTO notified. War-room opened in Slack.
        03:12 — Automated rate limiting deployed; attack traffic reduced 90%.
        03:28 — Affected accounts force-logged-out and passwords invalidated.
        05:17 — Full containment confirmed. Attack traffic ceased.
        09:00 — Post-incident review (PIR) session commenced.

        ROOT CAUSE
        No MFA enforced on legacy customer portal (/portal/v1/login).
        CAPTCHA bypassed using CAPTCHA-solving service.
        Rate limiting on login endpoint was 500 req/min (too permissive).

        REMEDIATION ACTIONS
        [DONE] Deployed CAPTCHA v3 with risk score threshold of 0.7.
        [DONE] Enforced MFA on all portal login paths.
        [DONE] Reduced rate limit to 30 req/min per IP.
        [IN PROGRESS] Force password reset for all 231 affected accounts.
        [PLANNED] Upgrade to /portal/v2 by 2024-11-01 (legacy endpoint decommission).

        IMPACT ASSESSMENT
        Customer accounts compromised: 231 (of 84,500 active)
        Data accessed: Profile pages only (no payment data, no PII beyond email/username)
        Regulatory notification required: Yes — ICO notified 2024-09-17.
        Customer notifications sent: 2024-09-16 (affected users only).

        LESSONS LEARNED
        1. Legacy endpoints must be included in hardening roadmap.
        2. MFA enforcement must be retroactive, not just new accounts.
        3. Credential stuffing detection rules needed in WAF.
    """)),

    "public_company_overview.txt": ("public", textwrap.dedent("""
        ACME CORP — COMPANY OVERVIEW

        Founded: 2011
        Headquarters: San Francisco, CA
        Employees: ~580 (as of 2024)
        CEO: Jonathan Reid
        CTO: Sarah Chen
        CFO: Michael Torres

        MISSION
        Empowering enterprises with intelligent, secure software solutions.

        PRODUCTS
        - AcmePlatform: Core SaaS platform for enterprise data management
        - AcmeInsight: Analytics and business intelligence suite
        - AcmeGuard: Enterprise security and compliance tooling

        OFFICE LOCATIONS
        San Francisco (HQ), New York, London, Singapore, Sydney

        CONTACT
        General:      info@acmecorp.com
        Press:        press@acmecorp.com
        Support:      support@acmecorp.com
        HR/Careers:   careers@acmecorp.com
    """)),
}

# ══════════════════════════════════════════════════════════════════════════════
# 2. SQLITE DATABASE
# ══════════════════════════════════════════════════════════════════════════════

def create_database() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS employees;
    DROP TABLE IF EXISTS departments;
    DROP TABLE IF EXISTS projects;
    DROP TABLE IF EXISTS financial_transactions;
    DROP TABLE IF EXISTS budget_allocations;

    CREATE TABLE departments (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        head_id INTEGER,
        budget REAL,
        headcount INTEGER
    );

    CREATE TABLE employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        position TEXT NOT NULL,
        salary REAL NOT NULL,
        manager_id INTEGER,
        hire_date TEXT NOT NULL,
        email TEXT NOT NULL,
        status TEXT DEFAULT 'active'
    );

    CREATE TABLE projects (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department_id INTEGER,
        budget REAL,
        spent REAL,
        status TEXT,
        start_date TEXT,
        end_date TEXT,
        lead_id INTEGER
    );

    CREATE TABLE financial_transactions (
        id INTEGER PRIMARY KEY,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        department_id INTEGER,
        approved_by TEXT,
        description TEXT
    );

    CREATE TABLE budget_allocations (
        id INTEGER PRIMARY KEY,
        year INTEGER,
        department_id INTEGER,
        allocated REAL,
        spent REAL,
        category TEXT
    );
    """)

    depts = [
        (1, "Engineering",        2,  28_000_000, 180),
        (2, "Human Resources",    8,   5_500_000,  25),
        (3, "Finance",           10,   4_200_000,  18),
        (4, "Sales & Marketing", 14,  22_000_000, 120),
        (5, "Legal & Compliance", 18,  3_800_000,  15),
    ]
    cur.executemany("INSERT INTO departments VALUES (?,?,?,?,?)", depts)

    employees = [
        (1,  "Alice Smith",       "Engineering",       "VP of Engineering",       185_000, None, "2018-03-01", "alice@acmecorp.com"),
        (2,  "Sarah Chen",        "Engineering",       "CTO",                     320_000, None, "2015-07-14", "sarah.chen@acmecorp.com"),
        (3,  "Raj Patel",         "Engineering",       "Senior Software Engineer", 145_000, 1,   "2020-05-20", "raj.patel@acmecorp.com"),
        (4,  "Priya Nair",        "Engineering",       "Software Engineer",        115_000, 1,   "2022-01-10", "priya.nair@acmecorp.com"),
        (5,  "Tom Lee",           "Engineering",       "DevOps Engineer",          130_000, 1,   "2021-08-03", "tom.lee@acmecorp.com"),
        (6,  "Aisha Mohammed",    "Engineering",       "ML Engineer",              155_000, 1,   "2020-11-15", "aisha.m@acmecorp.com"),
        (7,  "Chris Park",        "Engineering",       "Security Engineer",        140_000, 1,   "2019-06-22", "chris.park@acmecorp.com"),
        (8,  "Bob Johnson",       "Human Resources",   "HR Director",              125_000, None, "2017-09-01", "bob@acmecorp.com"),
        (9,  "Linda Torres",      "Human Resources",   "HR Business Partner",       88_000, 8,   "2021-03-14", "linda.t@acmecorp.com"),
        (10, "Carol Williams",    "Finance",           "Finance Manager",          118_000, None, "2019-01-07", "carol@acmecorp.com"),
        (11, "James Wu",          "Finance",           "Senior Accountant",         92_000, 10,  "2020-07-19", "james.wu@acmecorp.com"),
        (12, "Maria Garcia",      "Finance",           "Financial Analyst",         85_000, 10,  "2022-04-11", "maria.g@acmecorp.com"),
        (13, "Michael Torres",    "Finance",           "CFO",                      295_000, None, "2016-02-28", "michael.t@acmecorp.com"),
        (14, "Dave Brown",        "Sales & Marketing", "Sales Engineer",            95_000, None, "2021-10-05", "dave@acmecorp.com"),
        (15, "Sophie Martin",     "Sales & Marketing", "Account Executive",         82_000, 14,  "2022-06-01", "sophie.m@acmecorp.com"),
        (16, "Kevin Zhang",       "Sales & Marketing", "Marketing Manager",         98_000, None, "2020-03-15", "kevin.z@acmecorp.com"),
        (17, "Frank Miller",      "Sales & Marketing", "Sales Representative",      72_000, 14,  "2023-01-16", "frank@acmecorp.com"),
        (18, "Eve Davis",         "Legal & Compliance","Chief Compliance Officer",  145_000, None, "2018-11-01", "eve@acmecorp.com"),
        (19, "Omar Hassan",       "Legal & Compliance","Legal Counsel",            135_000, 18,  "2020-08-24", "omar.h@acmecorp.com"),
        (20, "Nina Petrov",       "Legal & Compliance","Compliance Analyst",        89_000, 18,  "2022-09-05", "nina.p@acmecorp.com"),
    ]
    cur.executemany(
        "INSERT INTO employees(id,name,department,position,salary,manager_id,hire_date,email) VALUES (?,?,?,?,?,?,?,?)",
        employees
    )

    projects = [
        (1,  "Platform v4 Migration",    1, 4_200_000, 3_100_000, "in_progress", "2024-01-01", "2024-12-31", 1),
        (2,  "AcmeInsight Launch",       1, 2_800_000, 1_900_000, "in_progress", "2024-03-01", "2024-11-30", 6),
        (3,  "Security Hardening Q4",    1,   750_000,   620_000, "completed",   "2024-07-01", "2024-09-30", 7),
        (4,  "HR Portal Redesign",       2,   320_000,   180_000, "in_progress", "2024-05-01", "2024-12-31", 8),
        (5,  "Global Compliance Audit",  5,   480_000,   310_000, "in_progress", "2024-01-15", "2024-12-15", 18),
        (6,  "ERP System Upgrade",       3,   950_000,   720_000, "in_progress", "2024-02-01", "2025-01-31", 10),
        (7,  "APAC Market Expansion",    4, 3_500_000, 1_800_000, "in_progress", "2024-04-01", "2025-03-31", 14),
        (8,  "DevOps Modernisation",     1,   620_000,   590_000, "completed",   "2024-01-01", "2024-06-30", 5),
        (9,  "GDPR Re-certification",    5,   200_000,   140_000, "in_progress", "2024-09-01", "2024-12-31", 18),
        (10, "Sales Automation CRM",     4, 1_100_000,   450_000, "in_progress", "2024-06-01", "2025-02-28", 16),
    ]
    cur.executemany(
        "INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?)", projects
    )

    random.seed(42)
    transactions = []
    base = date(2024, 1, 1)
    categories = ["payroll", "software", "cloud_infra", "travel", "marketing", "legal", "equipment", "consulting"]
    for i in range(1, 101):
        d = base + timedelta(days=random.randint(0, 364))
        cat = random.choice(categories)
        dept = random.randint(1, 5)
        amount = round(random.uniform(500, 85_000), 2)
        approver = random.choice(["Carol Williams", "Michael Torres", "Alice Smith"])
        transactions.append((i, d.isoformat(), cat, amount, dept, approver, f"{cat.title()} expense Q{(d.month-1)//3+1}"))
    cur.executemany(
        "INSERT INTO financial_transactions VALUES (?,?,?,?,?,?,?)", transactions
    )

    budgets = []
    for dept_id in range(1, 6):
        allocated = [28_000_000, 5_500_000, 4_200_000, 22_000_000, 3_800_000][dept_id - 1]
        spent = allocated * random.uniform(0.6, 0.85)
        budgets.append((dept_id, 2024, dept_id, allocated, round(spent, 2), "annual"))
    cur.executemany(
        "INSERT INTO budget_allocations VALUES (?,?,?,?,?,?)", budgets
    )

    conn.commit()
    conn.close()
    print(f"  ✓ SQLite database created: {DB_PATH}")


# ══════════════════════════════════════════════════════════════════════════════
# 3. JSON LOGS
# ══════════════════════════════════════════════════════════════════════════════

def create_json_logs() -> None:
    random.seed(99)
    users = ["alice", "bob", "carol", "dave", "eve", "frank"]
    actions = [
        "LOGIN", "LOGOUT", "VIEW_DOCUMENT", "EXPORT_REPORT",
        "UPDATE_PROFILE", "ACCESS_DENIED", "QUERY_SUBMITTED", "DOWNLOAD_FILE"
    ]
    base = date(2024, 9, 1)

    audit_log = []
    for i in range(1, 51):
        d = base + timedelta(days=random.randint(0, 90))
        audit_log.append({
            "event_id":   f"AUD-{i:04d}",
            "timestamp":  f"{d.isoformat()}T{random.randint(8,18):02d}:{random.randint(0,59):02d}:00Z",
            "user_id":    random.choice(users),
            "action":     random.choice(actions),
            "resource":   random.choice(["hr_policy.txt", "financial_report_q4_2024.txt",
                                          "employee_db", "audit_logs", "compliance_gdpr.txt"]),
            "ip_address": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "status":     random.choice(["SUCCESS", "SUCCESS", "SUCCESS", "FAILURE"]),
            "session_id": f"sess_{random.randint(100000,999999)}",
        })

    with open(os.path.join(LOGS_DIR, "audit_log.json"), "w") as f:
        json.dump(audit_log, f, indent=2)

    severities = ["LOW", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    alert_messages = [
        "Multiple failed login attempts detected for user {user}",
        "Unusual data export volume from {user} account",
        "Access attempt to restricted resource from unknown IP",
        "Credential stuffing attack detected on /portal/v1/login",
        "Privileged account {user} logged in outside business hours",
        "DLP policy triggered: sensitive data in outbound email",
        "Configuration change to firewall rules by {user}",
        "New admin account created: {user}",
        "SSL certificate expiring in 7 days for api.acmecorp.com",
        "Vulnerability scan completed: 3 HIGH severity findings",
    ]
    system_alerts = []
    for i in range(1, 21):
        d = base + timedelta(days=random.randint(0, 90))
        sev = random.choice(severities)
        msg_template = random.choice(alert_messages)
        msg = msg_template.format(user=random.choice(users))
        system_alerts.append({
            "alert_id":   f"ALERT-{i:04d}",
            "timestamp":  f"{d.isoformat()}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00Z",
            "severity":   sev,
            "category":   random.choice(["authentication", "data_access", "configuration", "vulnerability"]),
            "message":    msg,
            "source":     random.choice(["SIEM", "WAF", "IDS", "DLP"]),
            "resolved":   random.choice([True, True, False]),
            "assigned_to": random.choice(["Security Team", "IT Ops", "Compliance"]),
        })

    with open(os.path.join(LOGS_DIR, "system_alerts.json"), "w") as f:
        json.dump(system_alerts, f, indent=2)

    access_log = []
    for i in range(1, 101):
        d = base + timedelta(days=random.randint(0, 90))
        user = random.choice(users)
        success = random.choices([True, False], weights=[9, 1])[0]
        access_log.append({
            "log_id":       f"ACC-{i:04d}",
            "timestamp":    f"{d.isoformat()}T{random.randint(7,22):02d}:{random.randint(0,59):02d}:00Z",
            "user_id":      user,
            "event":        "LOGIN_SUCCESS" if success else "LOGIN_FAILURE",
            "ip_address":   f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "user_agent":   random.choice(["Chrome/120", "Firefox/121", "Safari/17", "Edge/120"]),
            "mfa_used":     success and random.choice([True, False]),
            "country":      random.choice(["US", "US", "US", "GB", "SG", "AU"]),
        })

    with open(os.path.join(LOGS_DIR, "access_log.json"), "w") as f:
        json.dump(access_log, f, indent=2)

    print(f"  ✓ JSON logs created in {LOGS_DIR}")


# ══════════════════════════════════════════════════════════════════════════════
# 4. INDEX INTO CHROMADB
# ══════════════════════════════════════════════════════════════════════════════

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return [c for c in chunks if len(c.strip()) > 50]


def index_documents() -> None:
    import chromadb
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

    client = chromadb.PersistentClient(path=STORE_DIR)

    # Delete existing collection to rebuild cleanly
    try:
        client.delete_collection("enterprise_docs")
    except Exception:
        pass

    collection = client.create_collection(
        name="enterprise_docs",
        embedding_function=DefaultEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )

    all_chunks: list[dict] = []

    # ── Text documents ────────────────────────────────────────────────────────
    for filename, (category, content) in DOCUMENTS.items():
        # Save the file
        fpath = os.path.join(DOCS_DIR, filename)
        with open(fpath, "w") as f:
            f.write(content)

        chunks = chunk_text(content)
        for ci, chunk in enumerate(chunks):
            all_chunks.append({
                "id":   f"{filename}_chunk_{ci}",
                "text": chunk,
                "metadata": {
                    "source_file":     filename,
                    "source_category": category,
                    "chunk_id":        f"{filename}_chunk_{ci}",
                    "doc_type":        "document",
                },
            })

    # ── JSON logs → index as text ─────────────────────────────────────────────
    log_configs = [
        ("audit_log.json",    "audit_logs"),
        ("system_alerts.json","system_alerts"),
        ("access_log.json",   "access_logs"),
    ]
    for fname, category in log_configs:
        fpath = os.path.join(LOGS_DIR, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath) as f:
            entries = json.load(f)
        # Group entries into chunks of 5
        for gi in range(0, len(entries), 5):
            group = entries[gi: gi + 5]
            text = json.dumps(group, indent=2)
            all_chunks.append({
                "id":   f"{fname}_group_{gi}",
                "text": text,
                "metadata": {
                    "source_file":     fname,
                    "source_category": category,
                    "chunk_id":        f"{fname}_group_{gi}",
                    "doc_type":        "log",
                },
            })

    # ── Batch upsert ──────────────────────────────────────────────────────────
    BATCH = 100
    for i in range(0, len(all_chunks), BATCH):
        batch = all_chunks[i: i + BATCH]
        collection.upsert(
            documents=[c["text"] for c in batch],
            metadatas=[c["metadata"] for c in batch],
            ids=[c["id"] for c in batch],
        )

    print(f"  ✓ Indexed {len(all_chunks)} chunks into ChromaDB ({STORE_DIR})")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n=== Enterprise RAG — Data Setup ===\n")
    print("Step 1/3: Creating SQLite database...")
    create_database()
    print("Step 2/3: Generating JSON log files...")
    create_json_logs()
    print("Step 3/3: Indexing documents into ChromaDB (first run downloads embeddings model ~22MB)...")
    index_documents()
    print("\n✅ Setup complete. Run: uvicorn app:app --reload --port 8000")
