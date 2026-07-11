# Trippy - Product Specification

## Overview

Trippy is a collaborative group trip planner. Multiple people (TripMates) plan a trip together: compile and discuss ideas for places and activities, share a schedule, and track shared expenses with reimbursement status.

Primary planning source: Notion project *“Trippy” (Group Trip Planner)* and *Stories & Entities*.

## Problem Statement

Planning group trips is hard:

- Coordinating stops, dates, and activities across multiple people
- Compiling and debating ideas in one shared place
- Tracking who paid for what and settling up fairly

## Target Users & Scope

- Friend groups and families planning leisure travel
- **In scope focus:** US-based travelers first
- **Out of focus:** business travel; non-US-first productization

## Group Size

- Optimized for roughly 6–12 members per trip
- Soft max ~20–25 members

## Domain Language

| Term | Meaning |
| --- | --- |
| **Traveler** | User profile / account in Trippy |
| **Trip** | Root collaborative entity (dates, stops, membership) |
| **TripStop** | City/region where one or more TripMates spend time |
| **Tripmate** | Membership of a Traveler on a Trip, with a role |
| **Idea** | Candidate activity/place/dining for the trip |
| **Expense** | Shared cost with payer, total, and per-person contributions |

## Core Features

### 1. Account (Traveler)

- Create account; later: 3rd-party auth
- Edit profile (name, contact, preferred payout handles)
- Disable account

### 2. Trip administration

- Create trip with start/end dates (date-only)
- Manage TripStops (locations with optional per-mate arrival/departure)
- Archive past trips (later UX)

### 3. Tripmate management

- Invite by role: Viewer, Commenter, Contributor, Administrator
- Change role; remove from trip
- Accept invite via token/link

### 4. Ideas

- [x] Add / edit / browse ideas (types, maps links, contact)
- [x] Comment and react (like)
- [ ] Schedule an idea onto the group plan (Phase 3)
- Later: merge similar ideas; AI generate/recommend (not v1)

### 5. Schedule

- Combined schedule and personal schedule views
- Travel legs (add/remove/modify)
- Plan activities from ideas

### 6. Expenses & reimbursement

- Create expenses (optionally link Ideas[])
- Splits/contributions per person with settlement status
- Mark settled; attach payment proof (later)
- Surface preferred payout methods from Traveler profile (no in-app payment rails v1)

### 7. Notifications (later)

- Email + in-app for invites and trip activity

## Roles & Permissions

| Action | Viewer | Commenter | Contributor | Administrator |
| --- | --- | --- | --- | --- |
| View trip, ideas, schedule | Yes | Yes | Yes | Yes |
| View expenses | Yes* | Yes | Yes | Yes |
| Comment / react | No | Yes | Yes | Yes |
| Create/edit own ideas, schedule items, expenses | No | No | Yes | Yes |
| Edit/delete others’ content | No | No | No | Yes |
| Invite / change roles / remove mates | No | No | No | Yes |
| Modify trip details & stops | No | No | No | Yes |
| Merge ideas (later) | No | No | No | Yes |

\*Expense visibility for pure Viewer may be tightened later; v0 treats trip members as able to see balances unless we productize a guest-only invite path.

Every Trip must always have **at least one Administrator**.

## Idea types

Dining, Entertainment & Dining, Tour, Guided Activity, Unguided Activity, Sightseeing/Landmark, Shopping, Supplies & Provisions, Other

## Expense statuses (settlement-oriented)

**Expense**

- Not Yet Paid
- Paid Awaiting Reimbursement
- Paid, Fully Settled

**Contribution / split**

- Requested
- Unpaid
- Partly Paid
- Fully Paid

## Success Metrics

- Planning engagement (ideas per trip)
- Schedule usage (ideas promoted to plan / travel legs)
- Return trips planned
- Expense settlement rate

## Out of Scope (v1)

- Payment processing (Venmo/PayPal/crypto rails)
- Flight/hotel booking inside the app
- AI idea generation / similarity (stories exist; deferred)
- Full Pinterest/map presentation polish
- Offline mode, push/SMS notifications
- Monetization (freemium/ads)

## Front-end note

Product planning to date is backend/domain-heavy. The UI is a **thin functional shell**: auth, trip list, trip hub tabs (Ideas | Schedule | Expenses | Mates). Visual/map experience comes later.

## Trip Lifecycle

- **Active:** upcoming or in progress
- **Archived:** past (still readable for members)

## Revision History

| Date | Changes |
| --- | --- |
| 2026-01-14 | Initial draft (User/Organizer/Guest model) |
| 2026-07-11 | Reconciled with Notion: Traveler/Tripmate/TripStop, 4 roles, settlement statuses, phased UI shell |
| 2026-07-11 | Phase 2 Ideas implemented (CRUD, comments, likes; simple card UI) |
