# Deployment Runbook

## Backend Deployment on Render

1. Push the project to GitHub.
2. Create a new Render web service.
3. Connect the repository.
4. Render will use:
   - `render.yaml`
   - root service directory: `backend`
5. Set the secret environment variable manually:
   - `API_KEY`
6. Confirm these backend environment values are set:
   - `APP_NAME`
   - `API_PREFIX`
   - `FRONTEND_ORIGIN`
   - `MODEL_PATH`
   - `LOW_RISK_MAX`
   - `MEDIUM_RISK_MAX`
   - `HIGH_RISK_MAX`
   - `CRITICAL_RISK_MAX`
   - `MAX_INTERACTION_EVENTS`
   - `RATE_LIMIT_REQUESTS`
   - `RATE_LIMIT_WINDOW_SECONDS`
   - `AUDIT_LOG_FILE`
7. Deploy the backend.
8. After deploy, verify:
   - `/health`
   - `/status`
   - `/docs`

## Frontend Deployment on Vercel

1. Import the `frontend` directory into Vercel.
2. Confirm Vercel uses:
   - `vercel.json`
   - build command: `npm run build`
   - output directory: `dist`
3. Set:
   - `VITE_API_BASE_URL=https://your-backend-domain.com/api/v1`
4. Deploy the frontend.
5. Open the deployed frontend URL.

## Post-Deploy Validation

Backend checks:

- `GET /health` returns `status = ok`
- `GET /status` returns model metadata and runtime settings
- `POST /api/v1/risk/assess` requires valid `x-api-key`

Frontend checks:

- frontend loads successfully
- form submits to deployed backend
- risk result renders properly
- low-risk known-contact case stays low
- obvious scam case becomes high or critical

## Recommended First Production Test

Use this scam-like input:

- message: `I am from bank customer care. Your account will be blocked. Scan this QR and pay now urgently.`

Expected:

- high or critical risk
- payment stage
- warning or abort recommendation

Use this benign input:

- message: `Dinner bill split is 500 INR. Send when free.`

Expected:

- low risk
- no scam-like explanation language
