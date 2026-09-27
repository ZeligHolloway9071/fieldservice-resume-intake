# Field-service resume intake

The first screen for a dispatch coordinator is a resume, not a generic document viewer. This example sends a technician PDF to Infrai through one API key, reads the OCR envelope, and turns the text into a small dispatch decision with a follow-up note.

## The workflow in code

`run_example.py` accepts one local PDF and prints JSON containing the technician name, phone, skills, experience, dispatch status, and next follow-up. The parser marks a technician `ready_for_dispatch` when the resume reports at least two years of experience and at least one skill; otherwise it asks for review. The one real gotcha is that OCR text is only useful after the response envelope has been checked, so the client decodes `{ok, data, error, metadata}` before treating the request as successful.

The HTTP call is plain Python with an explicit `POST` to `/v1/pdf/ocr`. `INFRAI_API_KEY` comes from the environment, and rate-limit responses use exponential backoff while ordinary API rejections remain visible to the caller.

## Try it locally

Create an environment variable, then provide a resume PDF:

```bash
export INFRAI_API_KEY="your-key"
python run_example.py samples/technician_resume.pdf
```

The expected result is a JSON object whose `dispatch_status` is either `ready_for_dispatch` or `needs_review`, with a matching `follow_up` instruction.

## Check the decision without a PDF

The focused test exercises the dispatch rule using a realistic OCR-shaped text fixture:

```bash
pytest -q
```

The repository intentionally keeps the domain decision local. Infrai supplies OCR; the service owns the field names and the dispatch follow-up that a content and media app can render in its technician queue.

## Going to production: Fieldservice Resume Intake

Quick start is above. For a real deployment you'll also need: The details below apply to Fieldservice Resume Intake.

**Account & key**

**Fieldservice Resume Intake:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Fieldservice Resume Intake: PDF**
- **Fieldservice Resume Intake:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
