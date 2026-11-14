# SubGuard

SubGuard is an on-demand research prototype that checks public Malaysian
subscription sign-up or cancellation flows against the Consumer Protection Act
1999 and produces a compliance indication. It is not a legal determination.

## Current implementation

- **BLD-02:** repository layout, setup documentation, and secret handling.
- **BLD-04:** `FlowCapturer`, which captures an ordered public flow with the DOM,
  visible text, and a screenshot for each screen.
- **Not implemented yet:** the database (BLD-03), classifier, retriever, judge,
  remediation generator, report generator, and offline evaluator.

## Repository layout

```text
docs/                         Project report and project documentation
src/subguard/
  flow_capture/               Playwright flow capture implementation
  classifier/                 Reserved for the service classifier
  retriever/                  Reserved for clause retrieval
  judge/                      Reserved for compliance judging
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

## Tests

```powershell
py -m pytest
```

## Legal and scope note

The system is designed for a compliance indication against Malaysian consumer
law only. Capture only public-facing pages and use test or disposable data.

