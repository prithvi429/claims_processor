# 🧾 Claims Processor — Generative AI–Powered Intelligent Claims Processing

A lightweight, end-to-end claims automation pipeline for insurance companies — powered by OCR, NLP, and Generative AI.
This system ingests raw claim documents (PDFs, images, text), extracts key information, validates it, and enables human-in-the-loop review for low-confidence data points.

---

## ✨ Overview

Modern insurance operations handle hundreds of claim documents daily — often scanned, handwritten, or poorly structured. Manual data entry is slow, error-prone, and expensive. Claims Processor automates this process through:

- 📥 Document ingestion (PDF, image, text)
- 🧠 OCR + Entity Extraction (form fields, amounts, names, dates)
- ✍️ Generative AI summarization & normalization
- ✅ Rule-based validation & HITL flagging
- 🧾 Structured output with audit trail

The project is modular so you can extend or replace components (OCR engine, LLM provider, DB, cloud provider).

---

## 🚀 Features

- Ingest PDFs, images, and text documents
- OCR text extraction (pytesseract + pdfplumber)
- Entity extraction with spaCy and regex helpers
- GenAI-based summarization & normalization using OpenAI APIs
- Rule-based validation via `configs/rules.yaml`
- Human-in-the-loop (HITL) workflow for low-confidence fields
- Full traceability: raw file → processed JSON → reviewer actions

---

## 🏗️ Architecture

```
┌──────────────┐
│  Raw Claim   │
│ (PDF/Image)  │
└──────┬───────┘
       │ Ingest
       ▼
┌──────────────┐
│ OCR & Parser │───► Structured Fields
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  GenAI Layer │───► Summarized & Normalized Data
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Validation & │───► Flag low-confidence
│   Rules      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ HITL Review  │───► Final Approved Output
└──────────────┘
```

---

## 🏗️ Proposed AWS Deployment (conceptual)

| Component | AWS Service | Purpose |
|---|---|---|
| File Storage | Amazon S3 | Store raw and processed claim documents |
| Processing Backend | AWS Lambda / Amazon ECS | Stateless OCR & AI processing |
| Queue & Event Triggers | Amazon SQS | Decouple ingestion from processing |
| OCR & NLP | Amazon Textract + OpenAI API | AI-powered text extraction & summarization |
| Database | Amazon RDS / DynamoDB | Store metadata and reviewer actions |
| HITL Interface | Streamlit / Amplify | Reviewer UI for flagged claims |
| Secrets & Encryption | Secrets Manager / KMS | Secure API keys and data |
| Monitoring | CloudWatch | Pipeline observability |

---

## 🛡️ Security & Compliance

- 🔐 Sensitive data encrypted at rest (KMS in cloud setups)
- 🔑 Secrets and API keys stored in Secrets Manager or environment variables
- 👤 Fine-grained IAM roles for services and reviewers
- 🧾 Reviewer actions are logged for auditability
- 🪪 PII redaction performed in processing pipeline

---

## 🧰 Tech Stack

- Language: Python 3.13 (works on 3.11+)
- OCR: Tesseract, pdfplumber
- NLP: spaCy, regex helpers
- GenAI: OpenAI GPT APIs
- Validation: YAML-based rules
- UI: Streamlit (optional)
- Containerization: Docker

---

## 🧪 Local Quickstart

### Requirements

- Python 3.11+
- Tesseract OCR installed locally (for image/PDF OCR)
- Set `OPENAI_API_KEY` in `.env` if using GenAI features
- Install pip packages from `requirements.txt`

### Clone & install

```powershell
git clone https://github.com/yourname/claims_processor.git
cd claims_processor
python -m pip install -r requirements.txt
```

### Run a processing example

```powershell
python -m src.main --input data/raw/mock_claim_20251008_070054.txt
```

### Run tests

```powershell
pytest -q
```

---

## 🧭 Configuration

| File | Purpose |
|---|---|
| `configs/schema.json` | Defines structured claim fields |
| `configs/prompts.yaml` | Prompt templates for LLM normalization |
| `configs/rules.yaml` | Business validation rules |
| `.env` | Environment variables (API keys, DB URLs) |
| `data/` | Raw and processed claim files |
| `db/` | Local SQLite DB for HITL prototype |

---

## 🧑‍💻 Human-in-the-Loop (HITL) Workflow

1. Low-confidence fields are flagged by `validation`.
2. Flagged claims are stored in the local DB for review.
3. Reviewers use the Streamlit UI to confirm or correct fields.
4. Final approved JSON is stored in `data/processed/` along with reviewer metadata.

---

## 📈 Business Impact

- ⏳ Reduce manual data entry and turnaround time
- 🧮 Increase data accuracy via automated validation
- 🧾 Provide full traceability for audits and compliance
- 🧑‍⚖️ Empower auditors & reviewers with HITL dashboard

---

## 🛠️ Extending to Production

- Replace local ingestion with S3 or API-based upload
- Swap SQLite for RDS/Postgres and configure via `DATABASE_URL`
- Run processing as stateless workers (Lambda / ECS) behind SQS
- Add RBAC and authentication for reviewer UI
- Integrate with insurance core systems via webhooks/APIs

---

## 🐞 Troubleshooting

- OCR errors: Ensure Tesseract and language packs installed; increase PDF DPI for scanned documents.
- OpenAI/API errors: Verify `OPENAI_API_KEY` in `.env` and network connectivity.
- Validation failures: Inspect `configs/rules.yaml` and thresholds.
- Tests failing: Run `pytest -q -k <test_name>` to isolate.

---

## 📸 Demo (Optional)

Upload claim document → Auto process → HITL Review → Final Output JSON.

Add screenshots or a Loom recording link here for a quick demo.

---

## 📜 License

MIT License — see the `LICENSE` file.

---

## 📬 Contact

Open issues or PRs on GitHub. For quick help, open a discussion with your environment and a minimal reproducer.
