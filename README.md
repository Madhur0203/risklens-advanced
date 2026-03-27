# RiskLens Advanced

RiskLens is an end-to-end **Risk Signal Intelligence Platform** for trade/compliance-style datasets.
It combines:

- multi-source ingestion (CSV / Excel)
- feature engineering
- rule-based risk signals
- anomaly detection
- predictive scoring
- lightweight NLP signal extraction from notes
- explainability (global + local reasons)
- recommendations / next best action
- analyst feedback loop
- interactive React frontend with dark / light theme

## Stack

### Backend
- FastAPI
- Pandas / NumPy
- scikit-learn
- SHAP (optional; graceful fallback if unavailable)
- SQLite + SQLAlchemy
- Uvicorn

### Frontend
- React + TypeScript + Vite
- Framer Motion
- Recharts
- React Router
- TanStack Query
- Axios

## Features

- Upload shipment / invoice / vendor / exception files
- Synthetic enterprise dataset generator
- Hybrid risk engine:
  - deterministic business rules
  - anomaly score via Isolation Forest
  - predictive risk via Gradient Boosting
  - text signal score from analyst notes and exception comments
- Interactive dashboard:
  - KPIs
  - risk trend chart
  - risk distribution
  - top vendors / ports / carriers
  - filters for severity, vendor, port, carrier, text keyword
- Cases page:
  - sortable/filterable case list
  - local explanations
  - recommendation engine
  - analyst feedback capture
- Dark / light theme
- Animated cards, drawers, transitions

## Run locally

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend will run at `http://127.0.0.1:8000`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend will run at `http://127.0.0.1:5173`.

## API summary

- `GET /api/health`
- `POST /api/bootstrap` create sample data and train models
- `POST /api/upload` ingest files
- `GET /api/dashboard`
- `GET /api/cases`
- `GET /api/cases/{case_id}`
- `POST /api/feedback`
- `POST /api/retrain`

## Notes

- SHAP is optional. If unavailable, feature-importance fallback is used.
- The app is designed to be strong and complete as source code. Dependency install and local execution still depend on your machine environment.
