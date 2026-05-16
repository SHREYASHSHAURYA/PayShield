# PayShield

## Domain

Cybersecurity - Fraud Detection

## Overview

PayShield is a pre-transaction scam risk assistant for UPI-style digital payment scenarios. It analyzes user-visible interaction context before payment execution and estimates scam risk using a hybrid approach that combines:

- rule-based signal detection
- stage-based scam progression tracking
- lightweight machine learning
- explainable risk scoring
- session-aware context handling

The system works on user-provided visible interaction and payment context. It does not require direct access to encrypted communication content.

## Problem Statement

UPI-based digital payments have increased convenience, but social-engineering scams have also grown rapidly. Many fraud systems act only after payment intent is created, which limits preventive action. Traditional systems also often lack clear explanation for why an interaction is risky.

PayShield addresses this by estimating scam risk before transaction completion and presenting explainable risk insights.

## Objectives

- Detect scam progression before transaction execution
- Shift fraud detection from reactive to proactive
- Provide explainable, user-friendly risk insights
- Preserve privacy by avoiding direct access to encrypted communication content
- Reduce false positives through context-aware logic
- Improve detection using lightweight ML
- Support cloud-ready deployment

## Core Idea

PayShield combines these layers:

1. Signal Detection  
   Detects scam indicators such as urgency, impersonation, QR payment prompts, payment requests, account block claims, collect requests, payment links, refund patterns, remote-access patterns, and related fraud signals.

2. Stage Classification  
   Maps detected signals into scam progression stages:
   - Trust
   - Urgency
   - Payment
   - Extraction

3. State Machine  
   Tracks monotonic stage progression and preserves completed stages across sessions.

4. Risk Engine  
   Produces:
   - risk score
   - risk level
   - recommended action
   - explainable reasoning

5. Lightweight ML Layer  
   Generates `scam_probability` from interaction text and structured context.

6. Session Context Layer  
   Adjusts risk using repeat-contact and trusted-beneficiary context for benign known-contact flows.

## Tech Stack

### Backend

- Python 3.10.11
- FastAPI
- Pydantic
- Uvicorn
- scikit-learn
- pandas
- joblib
- pytest
- httpx
- python-dotenv

### Frontend

- React
- TypeScript
- Vite

### ML

- TF-IDF Vectorizer
- Logistic Regression

## Project Structure

```text
payshield/
|- backend/
|  |- app/
|  |  |- api/
|  |  |  |- v1/
|  |  |  |  |- endpoints/
|  |  |- core/
|  |  |- models/
|  |  |- schemas/
|  |  |- services/
|  |  |  |- signal_engine/
|  |  |  |- stage_engine/
|  |  |  |- state_machine/
|  |  |  |- risk_engine/
|  |  |  |- ml_engine/
|  |  |- utils/
|  |  |- main.py
|  |- data/
|  |  |- raw/
|  |  |  |- uci_sms/
|  |  |- processed/
|  |- docs/
|  |  |- test_cases/
|  |- logs/
|  |- models_store/
|  |- scripts/
|  |  |- prepare_dataset.py
|  |  |- train_text_model.py
|  |  |- benchmark_scenarios.py
|  |- tests/
|  |- requirements.txt
|  |- Procfile
|  |- runtime.txt
|  |- pytest.ini
|  |- Dockerfile
|  |- .dockerignore
|  |- .env.example
|  |- .env.production.example
|- frontend/
|  |- public/
|  |- src/
|  |  |- components/
|  |  |- pages/
|  |  |- services/
|  |  |  |- assessment.ts
|  |  |  |- admin.ts
|  |  |- types/
|  |  |  |- assessment.ts
|  |  |  |- admin.ts
|  |  |- App.tsx
|  |  |- main.tsx
|  |  |- vite-env.d.ts
|  |- package.json
|  |- tsconfig.json
|  |- vite.config.ts
|  |- index.html
|  |- vercel.json
|  |- Dockerfile
|  |- .dockerignore
|  |- .env.example
|  |- .env.local.example
|  |- .env.production.example
|- docs/
|  |- deployment_runbook.md
|- render.yaml
|- README.md
|- .gitignore
```

## Features

- Pre-transaction scam risk assessment
- Rule-based scam signal detection
- Sequence-aware stage classification
- State-machine progression tracking
- Explainable risk output
- Real dataset-backed ML scam probability
- Session persistence for repeated interactions
- Trusted-beneficiary and repeat-contact context adjustment
- Multilingual normalization foundation for romanized Hindi / mixed phrasing
- QR payload parsing foundation
- OCR-ready visible-text ingestion foundation
- FastAPI API for backend integration
- React frontend for interactive testing
- Admin dashboard for recent audit-log review
- API key protection
- Rate limiting
- Audit logging
- Runtime status/monitoring endpoint
- Automated backend test coverage
- Containerization and deployment prep

## Signal Detection

The rule engine currently detects signals such as:

- urgency
- impersonation
- authority claim
- reward bait
- fear pressure
- secrecy request
- QR payment prompt
- UPI ID shared
- collect request detected
- payment link shared
- remote app request
- refund claim
- job offer
- KYC claim
- account block claim
- payment request
- transaction confirmation request

## Scam Progression Stages

- Trust
- Urgency
- Payment
- Extraction

The stage classifier maps signal combinations to the highest active stage.  
The state machine preserves progression and prevents backward rollback.

## Risk Output

Each assessment returns:

- `risk_score`
- `risk_level`
- `current_stage`
- `recommended_action`
- `triggered_signals`
- `stage_state`
- `explanation`

Possible risk levels:

- Low
- Medium
- High
- Critical

Possible recommended actions:

- safe_to_continue
- warn_only
- require_extra_confirmation
- recommend_abort

## Machine Learning Layer

The ML layer uses a real SMS dataset to generate a binary scam likelihood score.

### Dataset Used

Primary dataset used:

- UCI SMS Spam Collection

Official dataset link:

- https://archive-beta.ics.uci.edu/dataset/228/sms%2Bspam%2Bcollection/

### ML Pipeline

- TF-IDF vectorizer
- Logistic Regression classifier
- output probability used as `scam_probability`

### Important Note

The ML model does not predict scam stage directly.  
It predicts text-level scam likelihood. Rule-based logic handles signals and stage reasoning.

## Session and Context Handling

PayShield now uses session-aware context:

- repeated interactions with the same `session_id` reuse prior stage state
- repeat-contact context can reduce risk for benign repeated flows
- trusted-beneficiary context can reduce risk for known safe transfers
- strong scam signals still override benign context

## Multilingual and Rich Input Foundations

The current implementation includes:

- text normalization for romanized Hindi / mixed scam phrasing
- QR payload parsing for UPI QR links
- OCR-ready visible text ingestion from interaction metadata

This foundation improves detection without changing the public API contract.

## Local Backend Setup

From `backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend health check:

```text
http://127.0.0.1:8000/health
```

Backend runtime status:

```text
http://127.0.0.1:8000/status
```

Backend Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Local Frontend Setup

From `frontend`:

```powershell
npm install
npm run dev
```

Frontend URL:

```text
http://127.0.0.1:5173
```

## Environment Files

Backend examples:

```text
backend/.env.example
backend/.env.production.example
```

Frontend examples:

```text
frontend/.env.example
frontend/.env.local.example
frontend/.env.production.example
```

## API

### Health Endpoint

`GET /health`

Example response:

```json
{
  "status": "ok",
  "service": "PayShield"
}
```

### Status Endpoint

`GET /status`

Returns runtime metadata such as:

- service name
- API prefix
- model path
- model name
- model version
- training dataset
- rate-limit config
- audit log file

### Risk Assessment Endpoint

`POST /api/v1/risk/assess`

Headers required:

- `x-api-key`
- `x-client-id` is supported for rate limiting and audit logging

The endpoint accepts:

- session metadata
- interaction events
- payment context
- user flags

The endpoint returns:

- risk level
- risk score
- current stage
- recommended action
- triggered signals
- stage state
- explanation

### Admin Audit Log Endpoint

`GET /api/v1/admin/audit-logs?limit=10`

Headers required:

- `x-api-key`

Returns recent backend audit log entries.

## ML Dataset Preparation

### Raw dataset location

```text
backend/data/raw/uci_sms/SMSSpamCollection
```

### Prepare normalized dataset

From `backend`:

```powershell
python .\scripts\prepare_dataset.py
```

This creates:

```text
backend/data/processed/sms_training.csv
```

### Train the model

From `backend`:

```powershell
python .\scripts\train_text_model.py
```

This creates:

```text
backend/models_store/scam_text_pipeline.joblib
```

### Benchmark scenarios

From `backend`:

```powershell
python .\scripts\benchmark_scenarios.py
```

## Testing

From `backend`:

```powershell
pytest -q
```

Current automated tests cover:

- signal detection
- stage classification
- state machine progression
- risk engine behavior
- API endpoint validation
- multilingual normalization
- QR parsing
- repeated-safe session behavior

## Frontend Build

From `frontend`:

```powershell
npm run build
```

Build output:

```text
frontend/dist/
```

## Validation Scenarios

Validation scenarios are documented in:

```text
backend/docs/test_cases/validation_scenarios.md
```

## Security and Monitoring

Implemented:

- API key verification
- in-memory rate limiting
- audit logging
- runtime status endpoint
- model metadata file

Key monitoring/support files:

```text
backend/logs/audit.log
backend/models_store/model_metadata.json
```

## Deployment Files

### Backend

- `backend/Procfile`
- `backend/runtime.txt`
- `backend/Dockerfile`
- `backend/.dockerignore`
- `backend/.env.example`
- `backend/.env.production.example`

### Frontend

- `frontend/Dockerfile`
- `frontend/.dockerignore`
- `frontend/vercel.json`
- `frontend/.env.example`
- `frontend/.env.local.example`
- `frontend/.env.production.example`

### Root Deployment Files

- `render.yaml`
- `docs/deployment_runbook.md`

## Cloud Deployment Preparation

The project includes deployment-related files and a separate deployment runbook for backend and frontend deployment preparation.

Runbook location:

```text
docs/deployment_runbook.md
```

## Current Limitations

- The ML model is trained on a real SMS spam dataset, not a dedicated UPI scam progression dataset
- Stage detection is rule-based, not ML-trained
- Benign payment calibration is improved but can still be further refined with a stronger domain-specific dataset
- Multilingual support is a normalization foundation, not full multilingual model training
- Rate limiting and session storage are currently in-memory, not persistent/shared across distributed instances

## Status

Completed:

- backend architecture
- schemas and enums
- signal engine
- stage engine
- state machine
- risk engine
- ML integration
- session persistence
- trusted-beneficiary and repeat-contact risk adjustment
- multilingual normalization foundation
- QR parsing and OCR-ready ingestion foundation
- FastAPI API
- React frontend
- admin dashboard
- backend automated tests
- deployment configuration files
- deployment runbook
- API security
- rate limiting
- audit logging
- monitoring and model metadata
- containerization
