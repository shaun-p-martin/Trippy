# Trippy - Technical Specification

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Next.js        │────▶│  FastAPI        │────▶│  PostgreSQL     │
│  Frontend :3000 │     │  Backend :8000  │     │  Database       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
     /api/* rewrite  →  /v1/* + /health
```

## Technology Stack

### Frontend

- **Framework:** Next.js 16 (App Router), React 19, TypeScript
- **Styling:** Tailwind CSS 4
- **Data fetching:** TanStack Query (planned; fetch wrappers in Phase 0)
- **API access:** Browser → `/api/*` rewrite → FastAPI

### Backend

- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Database:** PostgreSQL (driver: `psycopg` v3; SQLAlchemy URL `postgresql+psycopg://...`)
- **Auth:** JWT access + refresh tokens (email/password v1)
- **Email (later):** AWS SES
- **Files (later):** Amazon S3

### Infrastructure

- **Local DB:** Docker Compose Postgres
- **CI/CD:** GitHub Actions (later)
- **Hosting:** TBD

## Domain Models

### Traveler

```
Traveler
├── id: UUID (PK)
├── email: string (unique, not null)
├── password_hash: string (not null)
├── first_name: string
├── last_name: string
├── display_name: string (nullable)
├── mobile: string (nullable)
├── venmo_username: string (nullable)
├── cashapp_username: string (nullable)
├── zelle_email: string (nullable)
├── zelle_phone: string (nullable)
├── lightning_address: string (nullable)
├── crypto_wallet_address: string (nullable)
├── crypto_chain: string (nullable)
├── preferred_currency: string (ISO 4217, default USD)
├── is_active: boolean (default true)
├── created_at: timestamp
└── updated_at: timestamp
```

### Trip

```
Trip
├── id: UUID (PK)
├── name: string
├── description: text (nullable)
├── start_date: date (nullable)
├── end_date: date (nullable)
├── created_by_id: UUID (FK → Traveler)
├── is_archived: boolean (default false)
├── created_at: timestamp
└── updated_at: timestamp
```

Invariant: at least one Tripmate with role `administrator`.

### TripStop

```
TripStop
├── id: UUID (PK)
├── trip_id: UUID (FK → Trip)
├── location_name: string  # city/region, not street address
├── sort_order: int (default 0)
├── created_at: timestamp
└── updated_at: timestamp
```

### TripStopMateDate

```
TripStopMateDate
├── id: UUID (PK)
├── trip_stop_id: UUID (FK → TripStop)
├── tripmate_id: UUID (FK → Tripmate)
├── arrival_date: date (nullable)
└── departure_date: date (nullable)
```

Derived (API computed, not stored): earliest arrival / latest departure across mate dates.

### Tripmate

```
Tripmate
├── id: UUID (PK)
├── trip_id: UUID (FK → Trip)
├── traveler_id: UUID (FK → Traveler, nullable until invite accepted)
├── role: enum (viewer | commenter | contributor | administrator)
├── invite_email: string (nullable)
├── invite_token: string (nullable, unique)
├── invite_status: enum (pending | accepted | revoked)
├── joined_at: timestamp (nullable)
├── created_at: timestamp
└── updated_at: timestamp
```

Unique: `(trip_id, traveler_id)` when traveler_id is set.

### Idea (Phase 2 — implemented)

```
Idea
├── id: UUID (PK)
├── trip_id: UUID (FK → Trip)
├── name: string
├── description: text (nullable)
├── location_text: string (nullable)
├── apple_maps_url: string (nullable)
├── google_maps_url: string (nullable)
├── idea_types: JSON array of IdeaType
├── official_website: string (nullable)
├── contact_phone: string (nullable)
├── contact_email: string (nullable)
├── created_by_id: UUID (FK → Traveler)
├── created_at: timestamp
└── updated_at: timestamp

IdeaComment
├── id: UUID (PK)
├── idea_id: UUID (FK → Idea)
├── parent_id: UUID (FK → IdeaComment, nullable — replies)
├── content: text
├── created_by_id: UUID (FK → Traveler)
├── created_at / updated_at

IdeaReaction
├── id: UUID (PK)
├── idea_id: UUID (FK → Idea)
├── traveler_id: UUID (FK → Traveler)
├── reaction_type: like (extensible)
├── unique (idea_id, traveler_id, reaction_type)
```

Schedule-from-idea link: Phase 3.

### Schedule / Travel (Phase 3+)

- **Travel:** trip-scoped legs (from/to, times, carrier notes)
- **ScheduleItem:** optional link to Idea; start/end datetime or date-flexible

### Expense + Contribution (Phase 4+)

```
Expense
├── id: UUID (PK)
├── trip_id: UUID (FK → Trip)
├── description: string
├── total_amount: decimal
├── currency: string (ISO 4217)
├── status: enum (not_yet_paid | paid_awaiting_reimbursement | paid_fully_settled)
├── payer_tripmate_id: UUID (FK → Tripmate)
├── preferred_repayment: string (nullable)
├── created_by_id: UUID (FK → Traveler)
├── created_at / updated_at

Contribution
├── id: UUID (PK)
├── expense_id: UUID (FK → Expense)
├── tripmate_id: UUID (FK → Tripmate)
├── amount: decimal
├── status: enum (requested | unpaid | partly_paid | fully_paid)
```

M2M: Expense ↔ Idea (optional).

## Authorization

Role hierarchy for checks: `viewer < commenter < contributor < administrator`.

| Action | Min role |
| --- | --- |
| View trip-scoped resources | viewer |
| Comment / react | commenter |
| Create/edit own content | contributor |
| Edit others’ content, invite, trip settings | administrator |

Trip-scoped routes resolve the current Traveler’s Tripmate membership (or 403/404).

## API Endpoints

Base path on backend: `/v1` (frontend calls `/api/v1/...` via Next rewrite).

### Phase 0–1 (implemented foundation)

#### Auth / Traveler

- `POST /v1/auth/register` — create Traveler + tokens
- `POST /v1/auth/login` — tokens
- `POST /v1/auth/refresh` — new access token
- `GET /v1/travelers/me` — current profile
- `PATCH /v1/travelers/me` — update profile

#### Trips

- `GET /v1/trips` — list trips for current traveler
- `POST /v1/trips` — create trip (creator becomes administrator)
- `GET /v1/trips/{id}` — detail + membership role
- `PATCH /v1/trips/{id}` — update (admin)
- `DELETE /v1/trips/{id}` — soft-archive or delete (admin)

#### Stops

- `GET /v1/trips/{id}/stops`
- `POST /v1/trips/{id}/stops` — admin
- `PATCH /v1/trips/{id}/stops/{stop_id}` — admin
- `DELETE /v1/trips/{id}/stops/{stop_id}` — admin

#### Tripmates

- `GET /v1/trips/{id}/tripmates`
- `POST /v1/trips/{id}/tripmates/invite` — admin; body: email, role
- `PATCH /v1/trips/{id}/tripmates/{mate_id}` — change role (admin)
- `DELETE /v1/trips/{id}/tripmates/{mate_id}` — remove (admin; cannot remove last admin)
- `POST /v1/invites/{token}/accept` — authenticated traveler accepts

#### Health

- `GET /health`

### Phase 2 (Ideas — implemented)

#### Ideas

- `GET /v1/trips/{id}/ideas` — list (optional `?idea_type=`)
- `POST /v1/trips/{id}/ideas` — create (contributor+)
- `GET /v1/trips/{id}/ideas/{idea_id}` — detail
- `PATCH /v1/trips/{id}/ideas/{idea_id}` — update (creator or admin)
- `DELETE /v1/trips/{id}/ideas/{idea_id}` — delete (creator or admin)

#### Comments

- `GET /v1/trips/{id}/ideas/{idea_id}/comments`
- `POST /v1/trips/{id}/ideas/{idea_id}/comments` — commenter+
- `DELETE /v1/trips/{id}/ideas/{idea_id}/comments/{comment_id}` — author or admin

#### Reactions

- `POST /v1/trips/{id}/ideas/{idea_id}/reactions` — toggle like (commenter+)

### Later phases (planned)

- Schedule idea / travel legs (Phase 3)
- Expenses, contributions, settlement summary (Phase 4)
- Notifications
- WebSockets for live updates

## Auth Token Design

- Access JWT: short-lived (~15 min), subject = traveler id
- Refresh JWT: longer-lived (~7 days), type claim `refresh`
- Password hashing: bcrypt via passlib
- Rate limiting: later

## Security

- CORS limited to frontend origin(s)
- Input validation via Pydantic
- RBAC on all trip mutations
- No secrets in repo; `.env` local only

## Performance

- Indexes on FKs and `email`, `invite_token`
- Pagination default 50 on list endpoints
- Group size soft cap 25 tripmates (enforce later)

## Real-time (later)

WebSockets for ideas/comments/expenses/member joins.

## Open Technical Questions

1. Debt simplification algorithm for multi-party settlement
2. Exchange-rate provider if multi-currency display is prioritized
3. Whether Viewers can see expenses by default

## Revision History

| Date | Changes |
| --- | --- |
| 2026-01-14 | Initial draft (User/TripMember/ItineraryItem) |
| 2026-07-11 | Notion-aligned domain, RBAC, Phase 0–1 API, stack unchanged |
| 2026-07-11 | Phase 2 Ideas API: CRUD, comments, reactions |
