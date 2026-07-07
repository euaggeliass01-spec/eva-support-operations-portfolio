# AI-Assisted Support Triage and Response QA

**Evidence type:** Self-directed portfolio prototype  
**Status:** Working local mode; optional schema-constrained AI mode  
**Safety model:** Human review before any reply or account action

## Problem

High-volume support creates repeated cognitive work:

- determine urgency;
- identify the likely domain;
- notice privacy, financial, security, or outage risk;
- ask for the missing evidence;
- prepare a useful first reply;
- avoid promising actions that have not happened.

The risk is that speed can produce assumptions. This project treats AI as a constrained assistant, not as an autonomous support agent.

## Workflow

```text
CSV tickets
   ↓
PII redaction before optional API use
   ↓
Category + priority + sentiment
   ↓
Risk flags + human-review decision
   ↓
Missing information + troubleshooting actions
   ↓
Draft response
   ↓
JSON output + HTML review report
```

## Run without an API key

```bash
python support_triage.py --mode local
python -m unittest test_support_triage.py
```

Local mode uses transparent rules and standard-library Python only.

## Optional AI mode

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="..."
python support_triage.py --mode ai
```

The implementation uses the OpenAI Responses API with Pydantic structured output. Set `OPENAI_MODEL` to change the model.

## Guardrails

- No automatic sending.
- No claims that the tool checked a customer account, log, payment gateway, or website.
- No request for full payment-card data.
- Financial, security, privacy, and high-impact cases are flagged for human review.
- Obvious email addresses and phone numbers are redacted before optional API use.
- If AI mode is unavailable in `auto` mode, the workflow falls back to local analysis.
- Outputs are prompts for investigation, not diagnoses.

## Evaluation set

The repository includes eight synthetic WooCommerce cases:

1. charged card / pending order;
2. missing customer email;
3. missing German shipping rate;
4. checkout plugin conflict;
5. SSL/domain migration;
6. performance regression;
7. delayed refund;
8. variation inventory error.

## What worked

- Structured fields made outputs easier to compare.
- Explicit “must not claim” instructions reduced false certainty.
- Human-review flags kept financial and outage scenarios visible.
- A deterministic fallback made the tool inspectable and testable.

## What did not work well initially

An unconstrained draft prompt tended to write as though checks had already been performed. The workflow was revised to separate:

- evidence available now;
- evidence still needed;
- safe next action;
- claims that must not be made.

## Next improvements

- Add a small rubric to score reply clarity, empathy, and unsupported claims.
- Store reviewer corrections to build an evaluation set.
- Add multilingual drafting while preserving a single internal English summary.
- Connect categories to a maintained knowledge base instead of hard-coded actions.
