---
paths:
  - "**/models/**"
  - "**/models.py"
  - "**/schema.prisma"
  - "**/schema/**"
  - "**/entities/**"
  - "**/*.sql"
  - "**/queries/**"
  - "**/repository/**"
  - "**/repositories/**"
  - "**/dao/**"
  - "**/migrations/**"
  - "**/migrate/**"
  - "**/alembic/**"
  - "**/db/migrate/**"
  - "**/routes/**"
  - "**/api/**"
  - "**/controllers/**"
  - "**/endpoints/**"
  - "**/handlers/**"
---

# Backend Standards

## API Design

- **RESTful:** Resource-based URLs (`GET /users`, `POST /users`, `PUT /users/{id}`). Plural nouns, limit nesting to 2-3 levels.
- **Query params:** Filtering (`?status=active`), sorting (`?sort=created_at`), pagination (`?page=2&limit=50`)
- **Status codes:** `200` OK, `201` Created, `204` No Content | `400`/`401`/`403`/`404`/`409`/`422` | `500`/`503`
- **Response structure:** `{ "data": {...} }` for success, `{ "error": { "code": "...", "message": "..." } }` for errors
- **Validation:** At API boundary. Never expose internal errors (stack traces, DB errors).

## Models

**Models define data structure and integrity. No business logic, no API calls.**

- **Naming:** Models: singular PascalCase (`User`). Tables: plural snake_case (`users`).
- **Required:** `created_at`/`updated_at` timestamps, explicit primary keys
- **Integrity at DB level:** `unique`, `nullable=False`, `CheckConstraint`, `ForeignKey` with explicit `ondelete`
- **Data types:** Money → DECIMAL not FLOAT. Timestamps → TIMESTAMP not VARCHAR. JSON → JSONB not TEXT. UUIDs → UUID not VARCHAR(36).
- **Indexes:** On foreign keys and WHERE/JOIN/ORDER BY columns. Don't over-index.
- **Scope:** Fields, relationships, properties, validation. NOT business logic, API calls, calculations.

## Queries

- **⛔ SQL injection prevention:** NEVER concatenate user input. Always parameterized queries or ORM methods.
- **N+1 prevention:** `joinedload` for one-to-one, `selectinload` for large collections
- **Performance:** Select only required columns, filter in DB not app, avoid leading wildcards
- **Timeouts:** Simple 1-2s, reports 10-30s, background 60s+
- **Transactions:** For multiple related writes and read-then-write (`FOR UPDATE`)

## Migrations

- **Reversible:** Every migration MUST have a working rollback
- **One change per migration.** Never modify deployed migrations.
- **Naming:** Timestamps + descriptive: `20241118120000_add_email_to_users.py`
- **NOT NULL columns:** Always specify `server_default`
- **Removing columns:** Multi-step — stop using it in code first, then remove
- **Indexes:** Concurrent creation on large tables
- **Data migrations:** Separate from schema changes, batch process, make idempotent
- **Zero-downtime:** Migration must work with currently deployed code

## Checklist

- [ ] REST principles, correct status codes
- [ ] All user input parameterized
- [ ] Models: timestamps, constraints, appropriate types
- [ ] No N+1 queries, only required columns
- [ ] Migrations: reversible, one change each, backwards compatible
- [ ] Tested: success and error cases
