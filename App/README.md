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
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Edit with your database credentials
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000

## API Proxy

The frontend proxies `/api/*` requests to the backend at `http://localhost:8000/*`.
