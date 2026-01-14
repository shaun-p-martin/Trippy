# Trippy - Technical Specification

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Next.js        │────▶│  FastAPI        │────▶│  PostgreSQL     │
│  Frontend       │     │  Backend        │     │  Database       │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
     :3000                   :8000
```

## Technology Stack

### Frontend

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TBD (React Context / Zustand / Redux)
- **API Client**: TBD (fetch / axios / react-query)

### Backend

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL
- **Authentication**: JWT with refresh tokens
- **Email**: AWS SES

### Infrastructure

- **Hosting**: TBD
- **File Storage**: Amazon S3 (for receipt uploads)
- **CI/CD**: GitHub Actions

## Data Models

### User

```
User
├── id: UUID (PK)
├── email: string (unique)
├── name: string
├── password_hash: string
├── preferred_currency: string (ISO 4217, default: USD)
├── created_at: timestamp
└── updated_at: timestamp
```

### Trip

```
Trip
├── id: UUID (PK)
├── name: string
├── description: text
├── destination: string
├── start_date: date
├── end_date: date
├── created_by: UUID (FK → User)
├── created_at: timestamp
└── updated_at: timestamp
```

### TripMember

```
TripMember
├── id: UUID (PK)
├── trip_id: UUID (FK → Trip)
├── user_id: UUID (FK → User, nullable for guests)
├── role: enum (organizer, contributor, guest)
├── invite_token: string (for pending invites)
├── invite_email: string (for pending invites)
└── joined_at: timestamp
```

### Idea

```
Idea
├── id: UUID (PK)
├── trip_id: UUID (FK → Trip)
├── title: string
├── description: text
├── category: enum (destination, activity, event, dining, other)
├── location: string (nullable)
├── url: string (nullable, for links/references)
├── estimated_cost: decimal (nullable)
├── created_by: UUID (FK → User)
├── created_at: timestamp
└── updated_at: timestamp
```

### IdeaLike

```
IdeaLike
├── id: UUID (PK)
├── idea_id: UUID (FK → Idea)
├── user_id: UUID (FK → User)
└── created_at: timestamp
```

### ItineraryItem

```
ItineraryItem
├── id: UUID (PK)
├── trip_id: UUID (FK → Trip)
├── idea_id: UUID (FK → Idea, nullable - if created from idea)
├── title: string
├── description: text
├── category: enum (flight, lodging, activity, event, dining, transport, other)
├── location: string
├── scheduled_date: date
├── start_time: time (nullable - for time-flexible items)
├── end_time: time (nullable)
├── is_flexible: boolean (default: false)
├── created_by: UUID (FK → User)
├── created_at: timestamp
└── updated_at: timestamp
```

### Expense

```
Expense
├── id: UUID (PK)
├── trip_id: UUID (FK → Trip)
├── paid_by: UUID (FK → User)
├── amount: decimal
├── currency: string (ISO 4217)
├── description: string
├── category: enum (food, transport, accommodation, activity, other)
├── receipt_url: string (nullable)
├── created_by: UUID (FK → User)
├── created_at: timestamp
└── updated_at: timestamp
```

### ExpenseSplit

```
ExpenseSplit
├── id: UUID (PK)
├── expense_id: UUID (FK → Expense)
├── user_id: UUID (FK → User)
├── amount: decimal
├── currency: string (ISO 4217, same as expense)
└── is_settled: boolean (default: false)
```

### Comment

```
Comment
├── id: UUID (PK)
├── trip_id: UUID (FK → Trip)
├── idea_id: UUID (FK → Idea, nullable)
├── itinerary_item_id: UUID (FK → ItineraryItem, nullable)
├── content: text
├── created_by: UUID (FK → User)
├── created_at: timestamp
└── updated_at: timestamp
```

### Notification

```
Notification
├── id: UUID (PK)
├── user_id: UUID (FK → User)
├── trip_id: UUID (FK → Trip)
├── type: enum (invite, comment, expense_added, settlement_reminder, etc.)
├── title: string
├── message: text
├── is_read: boolean (default: false)
├── email_sent: boolean (default: false)
├── created_at: timestamp
```

## API Endpoints

### Authentication

- `POST /auth/register` - Create account
- `POST /auth/login` - Get access token
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Invalidate token
- `GET /auth/me` - Get current user
- `PUT /auth/me` - Update profile (including preferred_currency)

### Trips

- `GET /trips` - List user's trips (with archived filter)
- `POST /trips` - Create trip
- `GET /trips/{id}` - Get trip details
- `PUT /trips/{id}` - Update trip
- `DELETE /trips/{id}` - Delete trip (organizer only)
- `POST /trips/{id}/invite` - Invite member
- `GET /trips/{id}/members` - List members
- `DELETE /trips/{id}/members/{member_id}` - Remove member (organizer only)
- `POST /trips/join/{invite_token}` - Accept invite

### Ideas

- `GET /trips/{id}/ideas` - List ideas
- `POST /trips/{id}/ideas` - Add idea
- `PUT /trips/{id}/ideas/{idea_id}` - Update idea (creator or organizer)
- `DELETE /trips/{id}/ideas/{idea_id}` - Delete idea (creator or organizer)
- `POST /trips/{id}/ideas/{idea_id}/like` - Like idea
- `DELETE /trips/{id}/ideas/{idea_id}/like` - Unlike idea
- `POST /trips/{id}/ideas/{idea_id}/schedule` - Add idea to itinerary

### Itinerary

- `GET /trips/{id}/itinerary` - List items (with date filter)
- `POST /trips/{id}/itinerary` - Add item
- `PUT /trips/{id}/itinerary/{item_id}` - Update item (creator or organizer)
- `DELETE /trips/{id}/itinerary/{item_id}` - Delete item (creator or organizer)

### Comments

- `GET /trips/{id}/ideas/{idea_id}/comments` - List idea comments
- `POST /trips/{id}/ideas/{idea_id}/comments` - Add comment
- `GET /trips/{id}/itinerary/{item_id}/comments` - List itinerary item comments
- `POST /trips/{id}/itinerary/{item_id}/comments` - Add comment
- `DELETE /trips/{id}/comments/{comment_id}` - Delete comment (creator or organizer)

### Expenses

- `GET /trips/{id}/expenses` - List expenses
- `POST /trips/{id}/expenses` - Add expense
- `PUT /trips/{id}/expenses/{expense_id}` - Update expense (creator or organizer)
- `DELETE /trips/{id}/expenses/{expense_id}` - Delete expense (creator or organizer)
- `GET /trips/{id}/expenses/summary` - Get balances (in user's preferred currency)
- `POST /trips/{id}/expenses/settle` - Mark settlement between two users

### Notifications

- `GET /notifications` - List user's notifications
- `PUT /notifications/{id}/read` - Mark as read
- `PUT /notifications/read-all` - Mark all as read

## Authorization Rules

| Action                     | Organizer | Contributor | Guest |
| -------------------------- | --------- | ----------- | ----- |
| View trip details          | Yes       | Yes         | Yes   |
| View ideas                 | Yes       | Yes         | Yes   |
| View itinerary             | Yes       | Yes         | Yes   |
| View expenses              | Yes       | Yes         | No    |
| Add/edit own content       | Yes       | Yes         | No    |
| Edit others' content       | Yes       | No          | No    |
| Delete others' content     | Yes       | No          | No    |
| Invite/remove members      | Yes       | No          | No    |
| Modify trip settings       | Yes       | No          | No    |

## Currency Handling

- Expenses stored in original currency
- Display converted to user's preferred currency
- Use exchange rate API for conversion (TBD: Open Exchange Rates / Fixer.io)
- Cache exchange rates daily

## Security Considerations

- Password hashing with bcrypt
- JWT access tokens (15 min expiry) + refresh tokens (7 day expiry)
- Rate limiting on auth endpoints
- Input validation on all endpoints
- CORS restricted to frontend origin
- Authorization checks on all mutations

## Performance Considerations

- Database indexes on foreign keys and frequently queried fields
- Pagination on list endpoints (default: 50 items)
- Caching strategy TBD
- Group size limit: 25 members per trip

---

## Real-time Updates

- **Technology**: WebSockets
- **Use cases**: New ideas/comments, expense updates, member joins, itinerary changes
- **Implementation**: FastAPI WebSocket endpoints, client reconnection handling

## Open Technical Questions

1. Debt simplification algorithm implementation

## Revision History

| Date       | Author | Changes                                         |
| ---------- | ------ | ----------------------------------------------- |
| 2026-01-14 | -      | Initial draft                                   |
| 2026-01-14 | -      | Added Ideas, Likes, Comments, Notifications, auth rules |
| 2026-01-14 | -      | Confirmed S3 for storage, SES for email                  |
| 2026-01-14 | -      | WebSockets for real-time updates                         |
