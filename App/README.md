# Trippy Application

Full-stack application with FastAPI backend and Next.js frontend.

## Project Structure

```
App/
├── backend/    # FastAPI (Python)
└── frontend/   # Next.js (TypeScript)
```

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# From repo root: docker compose up -d
alembic upgrade head
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000  
OpenAPI docs: http://localhost:8000/docs

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000

## API Proxy

The frontend proxies `/api/*` requests to the backend at `http://localhost:8000/*`.
Example: browser `GET /api/v1/trips` → FastAPI `GET /v1/trips`.
