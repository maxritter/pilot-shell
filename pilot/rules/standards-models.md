---
paths:
  - "**/models/**"
  - "**/models.py"
  - "**/schema.prisma"
  - "**/schema/**"
  - "**/entities/**"
---

# Models Standards

**Core Rule:** Models define data structure and integrity. Keep them focused on data representation, not business logic.

## Naming Conventions

**Models:** Singular, PascalCase (`User`, `OrderItem`, `PaymentMethod`)

**Tables:** Plural, snake_case (`users`, `order_items`, `payment_methods`)

**Avoid generic names:** `data`, `info`, `record`, `entity`

## Required Fields

**Timestamps on every model:**
```python
created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Primary keys:** Always explicit, prefer UUIDs for distributed systems or auto-incrementing integers for simplicity.

## Data Integrity - Database Level

**Use constraints, not just application validation:**

```python
email = Column(String(255), unique=True, nullable=False)
age = Column(Integer, CheckConstraint('age >= 18'))
user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
```

## Data Types - Choose Appropriately

| Data       | Type               | Avoid       |
| ---------- | ------------------ | ----------- |
| Email, URL | VARCHAR(255)       | TEXT        |
| Money      | DECIMAL(10,2)      | FLOAT       |
| Boolean    | BOOLEAN            | TINYINT     |
| Timestamps | TIMESTAMP/DATETIME | VARCHAR     |
| JSON data  | JSON/JSONB         | TEXT        |
| UUIDs      | UUID               | VARCHAR(36) |

## Indexes

**Always index:** Foreign keys, columns in WHERE/JOIN/ORDER BY clauses.

**Don't over-index:** Each index slows writes. Index only queried columns.

## Relationships - Explicit Configuration

**Define both sides of relationships:**
```python
class User(Base):
    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan')

class Order(Base):
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='orders')
```

**Cascade behaviors:** CASCADE (delete related), SET NULL (nullify FK), RESTRICT (prevent deletion). Choose based on business logic.

## What Belongs in Models

**YES:** Field definitions, relationships, simple properties, data validation, database constraints

**NO:** Business logic, external API calls, complex calculations, email sending

## Common Patterns

**Enums for fixed values:**
```python
class OrderStatus(str, Enum):
    PENDING = 'pending'
    PAID = 'paid'
    SHIPPED = 'shipped'

status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
```

## Checklist for New Models

- [ ] Singular model name, plural table name
- [ ] Primary key defined
- [ ] `created_at` and `updated_at` timestamps
- [ ] NOT NULL on required fields
- [ ] UNIQUE constraints where appropriate
- [ ] Foreign keys with explicit cascade behavior
- [ ] Indexes on foreign keys and queried columns
- [ ] Appropriate data types (not all VARCHAR)
- [ ] Relationships defined on both sides
