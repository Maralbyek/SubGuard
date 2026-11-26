# SubGuard

SubGuard is an on-demand research prototype that checks public Malaysian
subscription sign-up or cancellation flows against the Consumer Protection Act
1999 and produces a compliance indication. It is not a legal determination.

## Current implementation

- **BLD-02:** repository layout, setup documentation, and secret handling.
- **BLD-03:** PostgreSQL schema in [`db/schema.sql`](db/schema.sql), including
  the standalone offline-evaluation summary table.
- **BLD-04:** `FlowCapturer`, which captures an ordered public flow with the DOM,
  visible text, and a screenshot for each screen.
- **BLD-05 (in progress):** API-independent judge prompt construction and
  response parsing. The Anthropic API call and database connection are not
  implemented yet.
- **Not implemented yet:** classifier, retriever, remediation generator,
  report generator, and offline evaluator.

## Repository layout

```text
docs/                         Project report and project documentation
db/schema.sql                PostgreSQL schema for BLD-03
src/subguard/
  flow_capture/               Playwright flow capture implementation
  classifier/                 Reserved for the service classifier
  retriever/                  Reserved for clause retrieval
  judge/                      Prompt and finding helpers; no API call yet
  remediation/                Reserved for remediation generation
  reporting/                  Reserved for compliance reports
evaluator/                    Reserved for the offline evaluator
tests/                        Automated tests
```

## Setup

Requires Python 3.10+.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -e ".[dev]"
py -m playwright install chromium
```

Copy `.env.example` to `.env` if local API configuration is needed. The current
FlowCapturer does not call an LLM and does not require an API key.

## Capture one public flow

The capturer does not authenticate, fill forms, or submit personal data. Pass
the public URL and the visible selectors that advance the flow in order:

```powershell
subguard-capture `
  --url https://example.com/signup `
  --flow-type sign-up `
  --next-selector "a[href='/signup/step-2']" `
  --next-selector "button[type='submit']" `
  --output-dir captures/example-signup
```

Each screen is written as `screen-001/`, `screen-002/`, and so on. Every
screen directory contains `dom.html`, `visible-text.txt`, and `screenshot.png`.
The output also includes `manifest.json`, which preserves screen order and
metadata.

Only `http` and `https` URLs are accepted. URLs containing credentials and
obvious local/private hosts are rejected.

## Judge preparation and offline test

The judge helpers combine a saved capture's ordered screens with one manually
selected clause to build a prompt. They also parse Claude's requested JSON
response and save a finding record. No Anthropic API key or API call is needed
for these steps:

```python
from subguard.judge import (
    Clause,
    build_judge_question,
    load_captured_flow,
    parse_judge_answer,
    save_finding,
)

flow = load_captured_flow("captures/example-cancellation/manifest.json")
clause = Clause(
    requirement_code="YOUR-CHECKLIST-CODE",
    source_name="Consumer Protection Act 1999",
    section_reference="YOUR-SECTION",
    clause_text="Paste the verified clause text here.",
    question_text="Paste the checklist question here.",
)
print(build_judge_question(flow, clause))  # supply this prompt to Claude manually

# While the API is unavailable, exercise the parser with a JSON sample answer.
sample_answer = """{
  "verdict": "NOT_MET",
  "confidence_percent": 80,
  "rationale": "Example only; not a legal assessment.",
  "page_element": {
    "screen_order": 1,
    "description": "cancel button",
    "tag_name": "button",
    "selector_xpath": "//button[@id='cancel']",
    "text_content": "Cancel",
    "attributes": {"id": "cancel"}
  },
  "remediation_text": "Example remediation."
}"""
finding = parse_judge_answer(sample_answer, screen_count=len(flow.screens))
save_finding(
    finding,
    "finding.json",
    flow_url=flow.source_url,
    requirement_code=clause.requirement_code,
)
```

The saved JSON groups fields from the `finding` and `interface_element`
tables. It is an intermediate record, not a database insert: the project does
not yet assign database IDs or connect to PostgreSQL. Test clause text must be
clearly marked as synthetic; use only verified legal text for an actual check.

## Database

BLD-03 targets PostgreSQL, hosted on the team's selected provider. Apply the
schema with a PostgreSQL client using the `DATABASE_URL` value in `.env`:

```powershell
psql "$env:DATABASE_URL" -f db/schema.sql
```

The schema does not include credentials. Never commit `.env` or a real
`DATABASE_URL`.

## Tests

```powershell
py -m pytest
```

## Legal and scope note

The system is designed for a compliance indication against Malaysian consumer
law only. Capture only public-facing pages and use test or disposable data.
