# PayShield

PayShield is a pre-transaction scam risk assistant for UPI-style digital payment scenarios. It combines rule-based signal detection, stage-based scam progression tracking, lightweight machine learning, and explainable risk scoring.

## Project Structure

```
payshield/
|- backend/
|- frontend/
|- docs/
|- scripts/
```

## Local Backend Setup

`cd backend`
`python -m venv .venv`
`.\.venv\Scripts\Activate.ps1`
`pip install -r requirements.txt`
`uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`

Health check:
`http://127.0.0.1:8000/health`

API docs:
`http://127.0.0.1:8000/docs`

## Local Frontend Setup

`cd frontend`
`npm install`
`npm run dev`

Frontend URL:
`http://127.0.0.1:5173`

## Test Commands

Backend tests:
`cd backend`
`pytest -q`

Frontend production build:
`cd frontend`
`npm run build`

## ML Model Preparation

Raw dataset location:
`backend/data/raw/uci_sms/SMSSpamCollection`

Prepare dataset:
`cd backend`
`python .\scripts\prepare_dataset.py`

Train model:
`python .\scripts\train_text_model.py`

Trained model output:
`backend/models_store/scam_text_pipeline.joblib`

## Environment Files

Backend example:
`backend/.env.example`

Frontend example:
`frontend/.env.example`

## Cloud Deployment Checklist

### Backend

- Python version: `3.10.11`
- Install dependencies from `backend/requirements.txt`
- Expose service using `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Ensure `models_store/scam_text_pipeline.joblib` is present in deployment
- Allow frontend origin in CORS settings

### Frontend

- Set `VITE_API_BASE_URL` to deployed backend URL ending in `/api/v1`
- Build using `npm run build`
- Deploy the generated `frontend/dist` folder

## Sample Validation Scenario

Use this message in the UI:
`I am from bank customer care. Your account will be blocked. Scan this QR and pay now urgently.`

Expected direction:

- Risk level: `Critical`
- Current stage: `Payment`
- Recommended action: `recommend_abort`
