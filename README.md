# claims_processor
Generative AI-powered Intelligent Claims Processing system for automating insurance claim document ingestion, extraction, validation, and human-in-the-loop review.

---

## Overview

`claims_processor` is a lightweight prototype and starter kit for building an end-to-end claims automation pipeline. It demonstrates:

- Document ingestion (PDFs, images, text)
- OCR and structured parsing (pdfplumber, pytesseract)
- Entity extraction and normalization (spaCy + normalization helpers)
- Generative AI assisted summarization & normalization (OpenAI prompts)
- Rule-based validation and human-in-the-loop (HITL) flagging
- Local storage to JSON/SQLite for traceability
- Tests and example data for CI/smoke checks

This repository is intentionally modular so you can replace or extend individual components (for example, swap OpenAI for another LLM, or replace SQLite with S3/Postgres).

---

## Features

- Ingest PDFs and images, convert to text.
- Extract structured claim fields based on a configurable JSON schema.
- Normalize amounts, dates, and redact PII.
- Use prompt templates in `configs/prompts.yaml` to instruct a GenAI model to normalize and summarize.
- Validate extracted data against `configs/rules.yaml` and flag low-confidence fields for manual review.
- Store processed outputs under `data/processed/` and optionally in `db/claims.db` for HITL workflows.

---

## Use Case (Beautifully explained)

Imagine an insurance company that receives hundreds of diverse claim documents daily — PDFs that are scanned forms, emailed images of bills, and free-text incident reports. Manually processing each file for data entry is slow, costly, and error-prone.

claims_processor automates this workflow:

1. Ingest: Drop a claim PDF or image into the `data/raw/` folder (or upload via whatever front-end you wire in).
2. Extract: The OCR pipeline extracts text, and parsers match fields like `claim_id`, `date_of_loss`, `policy_number`, `claim_amount`, and `insured_name`.
3. Normalize: A small normalization module standardizes dates, monetary formats, and redacts PII where required.
4. GenAI Assist: A configurable prompt guides a GenAI model to summarize the claim details into the `CLAIM_SCHEMA` fields, improving recall for messy or handwritten inputs.
5. Validate: Business rules (e.g., `claim_amount` not exceeding policy limits) are applied; fields below a confidence threshold are marked for HITL.
6. Store & Review: Cleaned JSON outputs are saved to `data/processed/` and flagged items are stored in `db/claims.db` for a human reviewer to resolve.

Business impact:

- Dramatically reduce manual data-entry time.
- Improve data consistency across claims and carriers.
- Provide audit trails (original file → processed JSON → reviewer actions).

---

## Quickstart (Local)

Requirements:

- Python 3.11+ (the development environment here uses 3.13)
- Tesseract installed on your system for OCR (if you plan to process images)
- pip packages from `requirements.txt`

Install dependencies:

```powershell
cd C:\Users\DELL\claims_processor
python -m pip install -r requirements.txt
```

Run an example (process a local file):

```powershell
python -m src.main --input data/raw/mock_claim_20251008_070054.txt
```

Run tests:

```powershell
pytest -q
```

---

## Configuration

- `configs/schema.json` — Defines the structured claim fields the system extracts and stores.
- `configs/prompts.yaml` — Prompt templates used by the GenAI step.
- `configs/rules.yaml` — Business validation rules (amount thresholds, required fields, etc.).
- `.env.example` — Template environment variables (copy to `.env` and set `OPENAI_API_KEY`).

---

## Project Structure

A brief view of important folders:

- `src/` — Primary application code (ingestion, extraction, processing, validation, storage, utils)
- `configs/` — JSON/YAML config artifacts
- `data/` — `raw/`, `processed/`, and `test/` datasets
- `tests/` — PyTest test suite
- `db/` — Local SQLite DB for HITL prototype

---

## Development & Contribution

- Follow the repo style (PEP8-ish). Use small, modular changes.
- Add unit tests for new behavior under `tests/`.
- If you change public behavior (schema, prompts), update `configs/` and `README` accordingly.

Suggested development flow:

```powershell
git checkout -b feat/my-feature
# make changes
pytest -q
git add . && git commit -m "feat: add ..."
git push origin feat/my-feature
```

---

## Extending to Production

- Replace local file ingestion with an S3/Queue-based pipeline.
- Swap SQLite for Postgres and configure connection via `DATABASE_URL` in `.env`.
- Add authentication + an admin UI for HITL reviewers.
- Add batching and worker processes (Celery/RQ) for scale.

---

## Troubleshooting

- If OCR produces bad text: confirm Tesseract and its language packs are installed. For scanned PDFs, ensure good DPI during `pdf2image` conversion.
- If OpenAI calls fail: set `OPENAI_API_KEY` in `.env` and ensure network access.
- If tests fail: run `pytest -q -k <test_name>` to isolate.

---

## License

This project is MIT licensed — see the `LICENSE` file.

---

## Contact

Open issues or PRs on the repository. For quick help, open a discussion describing your environment and a minimal reproducer.
