# Trippy - Product Specification

## Overview

Trippy is a collaborative trip planning application that helps groups plan travel together and manage shared expenses with built-in reimbursement tracking.

## Problem Statement

Planning group trips is challenging:

- Coordinating schedules, destinations, and activities across multiple people
- Tracking who paid for what during the trip
- Settling up expenses fairly after the trip ends

## Target Users

- Friend groups planning vacations together
- Families coordinating travel

## Group Size

- Optimized for 6-12 members per trip
- Maximum supported: 20-25 members

## Core Features

### 1. Trip Planning

- [ ] Create and manage trips with dates, destinations
- [ ] Invite collaborators via email/link
- [ ] Add unscheduled ideas (destinations, activities, events, dining)
- [ ] "Like" ideas to signal interest
- [ ] Schedule ideas (date-flexible or specific time)
- [ ] Add logistical itinerary items (flights, lodging)
- [ ] Shared calendar view of trip schedule
- [ ] Discussion/comments on ideas and itinerary items

### 2. Expense Tracking

- [ ] Log expenses with amount, category, payer
- [ ] Attach receipts (photo upload)
- [ ] Split expenses equally or custom amounts
- [ ] Expenses can be posted in multiple currencies
- [ ] Display currency based on user preference
- [ ] Real-time expense dashboard

### 3. Reimbursement

- [ ] Calculate who owes whom
- [ ] Minimize transactions (debt simplification)
- [ ] Mark payments as settled
- [ ] Payment reminders

### 4. Notifications

- [ ] Email notifications for trip activity
- [ ] In-app notifications

## Roles & Permissions

### Organizer

- Can modify any trip details
- Can modify any idea, itinerary item, expense, or reimbursement
- Can invite/remove members

### Contributor

- Can modify their own profile details
- Can only modify ideas, itinerary items, expenses, or reimbursements they created
- Can view all trip content

### Guest (no account)

- Can view ideas and itinerary (read-only)
- Cannot add or modify any content
- Cannot view expenses or reimbursements

## User Stories

### Trip Organizer

- As an organizer, I want to create a trip and invite friends so we can plan together
- As an organizer, I want to set the trip dates and destination so everyone knows the basics
- As an organizer, I want to see all expenses in one place so I can track the budget
- As an organizer, I want to edit any item if corrections are needed

### Trip Contributor

- As a contributor, I want to accept an invite and create an account
- As a contributor, I want to add ideas to the idea collection / backlog
- As a contributor, I want to "like" ideas I'm interested in
- As a contributor, I want to add ideas to the schedule (date-flexible or specific time)
- As a contributor, I want to log expenses I paid for so I can get reimbursed
- As a contributor, I want to see what I owe others so I can settle up

## Trip Lifecycle

- **Active**: Upcoming or in-progress trips
- **Archived**: Past trips (displayed separately in UI)
- Trip data remains available indefinitely for users with active accounts

## Success Metrics

- Planning engagement (items added per trip)
- Itinerary usage (items added to itinerary)
- User retention (return trips planned)
- Expense settlement rate

## Out of Scope (v1)

- Payment processing (Venmo/PayPal integration)
- Flight/hotel booking within app
- AI-powered idea suggestions
- AI-powered flight lookups & suggestions
- Photo uploads / gallery
- Offline mode
- Push notifications
- SMS notifications

---

## Revision History

| Date       | Author | Changes                                      |
| ---------- | ------ | -------------------------------------------- |
| 2026-01-14 | -      | Initial draft                                |
| 2026-01-14 | -      | Added roles/permissions, notifications, decisions |
