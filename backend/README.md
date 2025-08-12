# Biz Analysis API (FastAPI)

Minimal MVP backend exposing endpoints for BCG, SWOT, and Porter analyses.

## Quick Start
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open: http://localhost:8000/docs

## Test Endpoints

**Health:**
```bash
curl http://localhost:8000/health
```

**BCG (example):**
```bash
curl -X POST http://localhost:8000/bcg \
  -H "Content-Type: application/json" \
  -d '[{"name":"Alpha","market_share":0.3,"largest_rival_share":0.25,"market_growth_rate":14}]'
```

## CORS

Development origin allowed: http://localhost:5173 (frontend).

## Deploy (Railway)

Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Set env var `CORS_ORIGINS` if you need to add production domain later.
