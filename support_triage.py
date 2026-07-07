#!/usr/bin/env python3
"""AI-assisted support ticket triage and response QA prototype.

The tool has two modes:
- local: deterministic, auditable rules; no dependencies or API key.
- ai: optional OpenAI Responses API with Pydantic structured output.

This is a portfolio prototype. It does not send replies automatically.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional


CATEGORY_RULES = {
    "Payments & orders": ["charged", "payment", "pending payment", "card", "gateway", "transaction"],
    "Email delivery": ["email", "notification", "mail", "inbox", "spam"],
    "Shipping": ["shipping", "flat rate", "postcode", "delivery", "local pickup", "zone"],
    "Plugin conflict": ["plugin", "update", "checkout spinner", "conflict", "deactivate"],
    "Domain & SSL": ["ssl", "certificate", "domain", "not private", "https", "mixed content"],
    "Performance": ["slow", "performance", "page builder", "speed", "cache"],
    "Refunds": ["refund", "money back", "bank"],
    "Inventory & variations": ["out of stock", "variation", "inventory", "stock", "size"],
}

CRITICAL_WORDS = ["checkout unavailable", "cannot place orders", "site down", "data loss", "security breach"]
HIGH_WORDS = ["charged", "certificate warning", "dispatch today", "payment", "not private"]
FINANCIAL_WORDS = ["payment", "charged", "refund", "transaction", "bank", "card"]
PRIVACY_PATTERN = re.compile(
    r"(?P<email>[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})|(?P<phone>\+?\d[\d\s().-]{7,}\d)"
)


def redact_pii(text: str) -> str:
    """Redact obvious emails and phone-like strings before optional API use."""
    def repl(match: re.Match[str]) -> str:
        return "[REDACTED_EMAIL]" if match.group("email") else "[REDACTED_PHONE]"
    return PRIVACY_PATTERN.sub(repl, text)


def classify_category(text: str) -> str:
    lower = text.lower()
    scores = {
        category: sum(1 for keyword in keywords if keyword in lower)
        for category, keywords in CATEGORY_RULES.items()
    }
    category, score = max(scores.items(), key=lambda item: item[1])
    return category if score else "General troubleshooting"


def classify_priority(text: str) -> str:
    lower = text.lower()
    if any(word in lower for word in CRITICAL_WORDS):
        return "Critical"
    if any(word in lower for word in HIGH_WORDS):
        return "High"
    return "Medium"


def classify_sentiment(text: str) -> str:
    lower = text.lower()
    if any(word in lower for word in ["angry", "unacceptable", "furious", "frustrated"]):
        return "Frustrated"
    if any(word in lower for word in ["urgent", "today", "cannot", "not receiving", "warning"]):
        return "Concerned"
    return "Neutral"


def risk_flags(text: str, category: str, priority: str) -> List[str]:
    lower = text.lower()
    flags: List[str] = []
    if any(word in lower for word in FINANCIAL_WORDS):
        flags.append("financial_action")
    if category == "Domain & SSL":
        flags.append("security_or_trust")
    if priority in {"Critical", "High"}:
        flags.append("high_customer_impact")
    if PRIVACY_PATTERN.search(text):
        flags.append("pii_present")
    return flags


def missing_information(category: str) -> List[str]:
    mapping = {
        "Payments & orders": ["order number", "gateway transaction reference", "order notes or gateway status"],
        "Email delivery": ["affected order number", "test-order result", "mail log or sending method"],
        "Shipping": ["full test address", "shipping-zone order", "product shipping class"],
        "Plugin conflict": ["recent changes", "browser/PHP logs", "backup and staging availability"],
        "Domain & SSL": ["affected hostname", "DNS target", "certificate coverage and mixed-content evidence"],
        "Performance": ["baseline URL and timing", "hosting/server context", "recent plugins or theme changes"],
        "Refunds": ["order number", "gateway refund reference", "automatic versus manual refund"],
        "Inventory & variations": ["product URL or ID", "variation settings", "cache/lookup-table state"],
        "General troubleshooting": ["exact error", "steps to reproduce", "recent changes"],
    }
    return mapping.get(category, mapping["General troubleshooting"])


def recommended_actions(category: str) -> List[str]:
    mapping = {
        "Payments & orders": [
            "Compare WooCommerce order notes with the payment gateway.",
            "Confirm capture versus authorization before changing order status.",
            "Check webhooks and gateway logs."
        ],
        "Email delivery": [
            "Confirm the relevant WooCommerce email is enabled.",
            "Run a controlled test order and inspect mail logs.",
            "Separate email generation from delivery/authentication."
        ],
        "Shipping": [
            "Verify the full customer address and shipping-zone precedence.",
            "Confirm the method is enabled and has a valid cost.",
            "Retest with a clean browser session."
        ],
        "Plugin conflict": [
            "Confirm a backup and use staging where possible.",
            "Capture logs before changing components.",
            "Change one variable at a time and preserve a rollback path."
        ],
        "Domain & SSL": [
            "Verify DNS and certificate coverage.",
            "Check WordPress URLs and redirects.",
            "Run a serialized-data-safe URL replacement only after backup."
        ],
        "Performance": [
            "Collect a consistent baseline.",
            "Inspect server, scheduled-action, script, and database evidence.",
            "Test additions individually on staging."
        ],
        "Refunds": [
            "Verify the refund in both WooCommerce and the gateway.",
            "Capture the provider refund reference.",
            "Prevent duplicate financial action."
        ],
        "Inventory & variations": [
            "Check enabled status, price, stock status, and quantity for every variation.",
            "Review parent-level stock settings and attribute combinations.",
            "Regenerate lookup data and clear transients."
        ],
        "General troubleshooting": [
            "Reproduce the problem safely.",
            "Collect exact evidence and recent changes.",
            "Test the smallest reversible change first."
        ],
    }
    return mapping.get(category, mapping["General troubleshooting"])


def local_draft(ticket_id: str, subject: str, message: str, category: str) -> str:
    missing = missing_information(category)
    ask = ", ".join(missing[:2])
    safety = ""
    if category in {"Payments & orders", "Refunds"}:
        safety = " I will avoid changing or repeating a financial action until the gateway record is verified."
    elif category == "Plugin conflict":
        safety = " Before changing components, I would confirm that a current backup or staging environment is available."
    return (
        "Hi,\n\n"
        f"I understand the issue with “{subject}”. I would first verify the current state rather than assume the visible symptom is the root cause."
        f"{safety}\n\n"
        f"Please share the {ask}. I will use that information to narrow the issue and confirm the safest next step.\n\n"
        "Best,\nEva"
    )


def local_analyze(row: Dict[str, str]) -> Dict[str, Any]:
    full_text = f"{row.get('subject', '')}\n{row.get('message', '')}"
    category = classify_category(full_text)
    priority = classify_priority(full_text)
    flags = risk_flags(full_text, category, priority)
    return {
        "ticket_id": row.get("ticket_id", ""),
        "category": category,
        "priority": priority,
        "sentiment": classify_sentiment(full_text),
        "risk_flags": flags,
        "needs_human_review": bool(flags) or priority in {"Critical", "High"},
        "missing_information": missing_information(category),
        "recommended_actions": recommended_actions(category),
        "draft_reply": local_draft(
            row.get("ticket_id", ""),
            row.get("subject", "your issue"),
            row.get("message", ""),
            category,
        ),
        "mode": "local",
    }


def ai_analyze(row: Dict[str, str], model: str) -> Dict[str, Any]:
    """Use the OpenAI Responses API with structured output.

    Requires:
        pip install openai pydantic
        export OPENAI_API_KEY=...
    """
    try:
        from openai import OpenAI
        from pydantic import BaseModel, Field
    except ImportError as exc:
        raise RuntimeError("AI mode requires the openai and pydantic packages.") from exc

    class TicketAnalysis(BaseModel):
        category: str
        priority: Literal["Low", "Medium", "High", "Critical"]
        sentiment: str
        risk_flags: List[str] = Field(default_factory=list)
        needs_human_review: bool
        missing_information: List[str]
        recommended_actions: List[str]
        draft_reply: str

    client = OpenAI()
    redacted = redact_pii(f"Subject: {row.get('subject', '')}\nMessage: {row.get('message', '')}")
    system = """You are a support-triage assistant for a WooCommerce support team.
Return structured analysis for human review. Never claim that you checked a log, account,
payment gateway, or website. Never promise a refund time or a guaranteed fix. Flag financial,
privacy, security, or outage risk. Ask only for information that is necessary. The draft reply
must be calm, plain-language, and transparent about uncertainty."""
    response = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": redacted},
        ],
        text_format=TicketAnalysis,
    )
    parsed = response.output_parsed
    if parsed is None:
        raise RuntimeError("The model returned no parsed output.")
    result = parsed.model_dump()
    result["ticket_id"] = row.get("ticket_id", "")
    result["mode"] = "ai"
    return result


def read_tickets(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def render_html(results: List[Dict[str, Any]], output: Path) -> None:
    cards = []
    for item in results:
        actions = "".join(f"<li>{html.escape(str(x))}</li>" for x in item["recommended_actions"])
        missing = "".join(f"<li>{html.escape(str(x))}</li>" for x in item["missing_information"])
        flags = ", ".join(item["risk_flags"]) if item["risk_flags"] else "None"
        cards.append(f"""
        <article class="card">
          <div class="meta">
            <strong>{html.escape(item['ticket_id'])}</strong>
            <span>{html.escape(item['category'])}</span>
            <span class="priority">{html.escape(item['priority'])}</span>
            <span>mode: {html.escape(item['mode'])}</span>
          </div>
          <h2>Analysis</h2>
          <p><strong>Sentiment:</strong> {html.escape(item['sentiment'])}</p>
          <p><strong>Risk flags:</strong> {html.escape(flags)}</p>
          <p><strong>Human review:</strong> {"Required" if item["needs_human_review"] else "Recommended"}</p>
          <div class="cols"><div><h3>Missing information</h3><ul>{missing}</ul></div>
          <div><h3>Recommended actions</h3><ul>{actions}</ul></div></div>
          <h3>Draft reply for review</h3>
          <pre>{html.escape(item['draft_reply'])}</pre>
        </article>
        """)
    page = f"""<!doctype html><html><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Support Triage Workflow Report</title>
    <style>
    body{{margin:0;background:#f4f1ea;color:#172326;font-family:system-ui,sans-serif;line-height:1.55}}
    main{{width:min(1050px,calc(100% - 32px));margin:50px auto}}
    h1{{font-size:clamp(2.5rem,6vw,5rem);letter-spacing:-.05em;line-height:1;margin-bottom:12px}}
    .intro{{max-width:760px;color:#59676a;margin-bottom:36px}}
    .card{{background:#fffdf8;border:1px solid #d6d9d4;border-radius:20px;padding:28px;margin:18px 0}}
    .meta{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;color:#59676a}}
    .meta span{{border:1px solid #d6d9d4;border-radius:999px;padding:4px 9px;font-size:.82rem}}
    .priority{{font-weight:800}}
    .cols{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
    pre{{white-space:pre-wrap;background:#eef3f1;padding:18px;border-radius:12px;font-family:inherit}}
    a{{color:#0e6b64;font-weight:800}}
    @media(max-width:700px){{.cols{{grid-template-columns:1fr}}}}
    </style></head><body><main>
    <a href="../index.html">← Back to portfolio</a>
    <h1>Support triage and QA report</h1>
    <p class="intro">Generated from eight synthetic WooCommerce tickets. The workflow assists classification and drafting; it does not send messages or perform account actions. Financial, security, privacy, and outage cases remain under human review.</p>
    {''.join(cards)}
    </main></body></html>"""
    output.write_text(page, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="sample_tickets.csv")
    parser.add_argument("--output", default="triage_results.json")
    parser.add_argument("--html", default="report.html")
    parser.add_argument("--mode", choices=["auto", "local", "ai"], default="auto")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-5.5"))
    args = parser.parse_args()

    input_path = Path(args.input)
    rows = read_tickets(input_path)
    use_ai = args.mode == "ai" or (args.mode == "auto" and bool(os.getenv("OPENAI_API_KEY")))

    results: List[Dict[str, Any]] = []
    for row in rows:
        try:
            result = ai_analyze(row, args.model) if use_ai else local_analyze(row)
        except Exception as exc:
            if args.mode == "ai":
                raise
            print(f"AI mode failed for {row.get('ticket_id')}: {exc}; using local mode.", file=sys.stderr)
            result = local_analyze(row)
        results.append(result)

    Path(args.output).write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    render_html(results, Path(args.html))
    print(f"Processed {len(results)} tickets. JSON: {args.output}; HTML: {args.html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
