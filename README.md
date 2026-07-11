# Trippy

Collaborative group trip planner — ideas, schedule, and shared expenses.

**Stack:** Next.js (frontend) + FastAPI (API) + PostgreSQL

## Repo layout

```
Trippy/
├── App/
│   ├── backend/     # FastAPI
│   └── frontend/    # Next.js
├── docs/
│   ├── PRODUCT_SPEC.md
│   └── TECHNICAL_SPEC.md
└── docker-compose.yml
```

## Local setup

### 1. Database

Postgres 16 is required.

**Option A — Docker**

```bash
docker compose up -d
```

**Option B — Homebrew (this machine)**

```bash
brew services start postgresql@16
createuser -s trippy 2>/dev/null || true
psql -d postgres -c "ALTER USER trippy WITH PASSWORD 'trippy';"
createdb -O trippy trippy 2>/dev/null || true
```

### 2. Backend

```bash
cd App/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # if needed
alembic upgrade head
uvicorn app.main:app --reload
```

- API: http://localhost:8000  
- OpenAPI: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

### 3. Frontend

```bash
cd App/frontend
npm install
npm run dev
```

- App: http://localhost:3000  
- Browser calls `/api/*` which Next rewrites to the FastAPI backend.

## Domain (short)

Travelers join Trips as Tripmates (viewer / commenter / contributor / administrator). Trips have TripStops, Ideas, Schedule, and Expenses — see `docs/` and Notion Stories & Entities.
