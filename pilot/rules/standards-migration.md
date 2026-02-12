---
paths:
  - "**/migrations/**"
  - "**/migrate/**"
  - "**/alembic/**"
  - "**/db/migrate/**"
---

# Migration Standards

Apply these rules when creating or modifying database migrations. Migrations are permanent records of schema evolution and must be treated with extreme care.

## Core Principles

**Reversibility is Mandatory**: Every migration MUST have a working rollback method. If a change cannot be reversed safely, document why and consider a multi-step approach.

**One Logical Change Per Migration**: Each migration should do exactly one thing - add a table, add a column, create an index. This makes debugging easier, rollbacks safer, and code review clearer.

**Never Modify Deployed Migrations**: Once a migration runs in any shared environment, it becomes immutable. Create a new migration to fix issues.

## Migration Structure

**Naming Convention**: Use timestamps and descriptive names:
- `20241118120000_add_email_to_users.py`
- `20241118120100_create_orders_table.rb`

The name should answer "what does this migration do?" without reading the code.

## Schema Changes

**Adding Columns**: Always specify default values for NOT NULL columns on existing tables:

```python
# BAD - locks table during backfill
op.add_column('users', sa.Column('status', sa.String(), nullable=False))

# GOOD - uses default, no lock
op.add_column('users', sa.Column('status', sa.String(), nullable=False, server_default='active'))
```

**Removing Columns**: Use multi-step approach for zero-downtime:
1. Deploy code that stops using the column
2. Deploy migration that removes the column

**Renaming Columns**: Treat as add + remove for zero-downtime:
1. Add new column → 2. Code writes to both → 3. Backfill → 4. Code reads from new → 5. Remove old

## Index Management

**Use concurrent index creation on large tables:**

```python
# PostgreSQL
op.create_index('idx_users_email', 'users', ['email'], postgresql_concurrently=True)
```

**Index Naming**: `idx_<table>_<column(s)>` (e.g., `idx_users_email`, `idx_orders_user_id_created_at`)

## Data Migrations

**Separate from Schema**: Never mix schema and data changes in one migration.

**Batch Processing**: Process large datasets in batches to avoid memory issues and long-running transactions.

**Idempotency**: Data migrations should be safe to run multiple times:
```python
# GOOD - idempotent
op.execute("INSERT INTO settings (key, value) VALUES ('flag', 'true') ON CONFLICT (key) DO NOTHING")
```

## Zero-Downtime Deployments

**Backwards Compatibility**: New migrations must work with the currently deployed code version. Deploy order:
1. Deploy migration (schema change)
2. Deploy new code (uses new schema)

## Red Flags - Stop and Reconsider

If you're about to:
- Modify an existing migration file that's been deployed
- Drop a column without a multi-step plan
- Create a migration without a down method
- Mix schema and data changes in one migration
- Add a NOT NULL column without a default to a large table
- Create an index without CONCURRENT on a production table

**STOP. Plan a safer approach.**

## Checklist Before Committing

- [ ] Migration has descriptive timestamp-based name
- [ ] Down/rollback method implemented and tested
- [ ] Ran migration up and down successfully
- [ ] No schema and data changes mixed
- [ ] Large table indexes use concurrent creation
- [ ] NOT NULL columns on existing tables have defaults
- [ ] Changes are backwards compatible with deployed code
