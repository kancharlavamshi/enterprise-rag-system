"""
Quick CLI demo — shows RBAC enforcement, multi-source retrieval, and citations.
Usage: python demo.py
"""
from __future__ import annotations
import httpx
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

BASE = "http://localhost:8000"
console = Console()

DEMO_QUERIES = [
    # (user_id, query)
    ("frank",  "What is the vacation and parental leave policy?"),
    ("carol",  "What was ACME's net income in Q4 2024 and what are the 2025 department budgets?"),
    ("frank",  "What are the financial transactions? Show me salary information."),  # RBAC denied
    ("bob",    "How many employees are in each department and what are their salaries?"),
    ("dave",   "What microservices does ACME use and what is the CI/CD pipeline?"),
    ("eve",    "What happened during the September 2024 security incident?"),
    ("alice",  "Show me recent system security alerts and any failed login attempts."),
]


def run_query(user_id: str, query: str) -> None:
    console.rule(f"[bold cyan]{user_id}[/] asks: [italic]{query}[/]")
    try:
        resp = httpx.post(
            f"{BASE}/query",
            json={"user_id": user_id, "query": query, "max_results": 5},
            timeout=60.0,
        )
        data = resp.json()
    except Exception as e:
        console.print(f"[red]Request failed: {e}[/]")
        return

    # Header info
    t = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    t.add_row("[bold]User[/]",    f"{data['user']['name']} ({data['user']['role']})")
    t.add_row("[bold]Intent[/]",  f"{', '.join(data['intents'])} (conf={data['intent_confidence']:.0%})")
    t.add_row("[bold]Sources[/]", ", ".join(data['sources_queried']) or "none")
    if data["denied_categories"]:
        t.add_row("[bold red]Denied[/]", "[red]" + ", ".join(data["denied_categories"]) + "[/]")
    t.add_row("[bold]Chunks[/]",  str(data["chunks_used"]))
    t.add_row("[bold]Latency[/]", f"{data['latency_ms']} ms")
    console.print(t)

    console.print(Panel(data["answer"], title="Answer", border_style="green"))

    if data["citations"]:
        console.print(Panel(data["citations"], title="Citations", border_style="blue"))

    console.print(Panel(data["confidence"], title="Confidence", border_style="yellow"))

    if data["retrieval_trace"]:
        console.print("[dim]Retrieval Trace:[/]")
        for item in data["retrieval_trace"][:3]:
            console.print(
                f"  [{item['rank']}] score={item['relevance_score']:.3f} "
                f"| {item['source_category']} | {item['source']}\n"
                f"      {item['content_preview'][:100]}..."
            )
    console.print()


def main() -> None:
    console.print(Panel.fit(
        "[bold]Enterprise RAG Intelligence System — Demo[/]\n"
        "Demonstrating RBAC, multi-source retrieval, citations & explainability",
        border_style="bold blue",
    ))

    # Check server
    try:
        httpx.get(f"{BASE}/health", timeout=5)
    except Exception:
        console.print("[red]Server not running. Start with: uvicorn app:app --reload[/]")
        return

    for user_id, query in DEMO_QUERIES:
        run_query(user_id, query)


if __name__ == "__main__":
    main()
