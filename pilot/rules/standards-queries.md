---
paths:
  - "**/*.sql"
  - "**/queries/**"
  - "**/repository/**"
  - "**/repositories/**"
  - "**/dao/**"
---

# Queries Standards

**Core Rule:** Write secure, performant queries using parameterized statements, eager loading, and strategic indexing.

## SQL Injection Prevention - Mandatory

**NEVER concatenate user input into SQL strings.** Always use parameterized queries.

```python
# BAD - Vulnerable to SQL injection
query = f"SELECT * FROM users WHERE email = '{user_email}'"

# GOOD - Parameterized
cursor.execute("SELECT * FROM users WHERE email = %s", (user_email,))

# GOOD - ORM
User.query.filter_by(email=user_email).first()
```

**This applies to ALL user input:** query parameters, form data, URL paths, headers, cookies.

## N+1 Query Problem

**Bad - N+1 queries:**
```python
users = User.query.all()
for user in users:
    posts = user.posts  # Separate query per user
```

**Good - Eager loading:**
```python
users = User.query.options(joinedload(User.posts)).all()
```

**When to use each:**
- `joinedload` / `include`: One-to-one or small one-to-many
- `selectinload` / separate query: Large one-to-many or many-to-many

## Select Only Required Columns

```python
# BAD
users = User.query.all()  # Fetches all columns

# GOOD
users = db.session.query(User.id, User.email, User.name).all()
```

## Transactions for Data Consistency

**Use transactions when:**
- Multiple related writes must succeed or fail together
- Reading then writing based on that read (prevent race conditions)

```python
with Session(engine) as session:
    try:
        user = session.query(User).filter_by(id=user_id).with_for_update().first()
        user.balance -= amount
        transaction = Transaction(user_id=user_id, amount=amount)
        session.add(transaction)
        session.commit()
    except Exception:
        session.rollback()
        raise
```

## Query Timeouts

Set timeouts to prevent runaway queries from blocking resources.

**Typical values:** Simple queries: 1-2s, Complex reports: 10-30s, Background jobs: 60s+

## Common Anti-Patterns

**Loading all records then filtering in application code:**
```python
# BAD - loads entire table into memory
all_users = User.query.all()
active_users = [u for u in all_users if u.status == 'active']

# GOOD - filter in database
active_users = User.query.filter_by(status='active').all()
```

**Using LIKE with leading wildcard:**
```sql
-- BAD - can't use index
SELECT * FROM users WHERE email LIKE '%@example.com'

-- GOOD - can use index
SELECT * FROM users WHERE email LIKE 'user@%'
```

## Query Optimization Checklist

- [ ] All user input uses parameterized queries
- [ ] No N+1 queries (verified with query logging)
- [ ] Only required columns selected
- [ ] Indexes exist for WHERE/JOIN/ORDER BY columns
- [ ] Related writes wrapped in transactions
- [ ] Query timeout set appropriately
- [ ] Tested with realistic data volumes
