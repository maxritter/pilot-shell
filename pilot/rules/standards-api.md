---
paths:
  - "**/routes/**"
  - "**/api/**"
  - "**/controllers/**"
  - "**/endpoints/**"
  - "**/handlers/**"
---

# API Standards

Apply these standards when creating or modifying API endpoints, route handlers, and controllers.

## RESTful Design Principles

**Resource-based URLs with HTTP methods:**
- `GET /users` - List users
- `GET /users/{id}` - Get specific user
- `POST /users` - Create user
- `PUT /users/{id}` - Replace user (full update)
- `PATCH /users/{id}` - Update user (partial update)
- `DELETE /users/{id}` - Delete user

**Use plural nouns for collections:** `/users`, `/products`, `/orders`

**Limit nesting to 2-3 levels:** `/users/{id}/orders/{order_id}` is fine, deeper is not.

## URL and Naming Conventions

- Use lowercase with hyphens: `/user-profiles` or underscores: `/user_profiles`
- Never mix: `/userProfiles`, `/User-Profiles`
- Check existing endpoints first and match the project's convention

**Query parameters for operations:**
- Filtering: `GET /users?status=active&role=admin`
- Sorting: `GET /users?sort=created_at&order=desc`
- Pagination: `GET /users?page=2&limit=50`
- Search: `GET /users?q=john`

## HTTP Status Codes

**Success:**
- `200 OK` - Successful GET, PUT, PATCH, DELETE
- `201 Created` - Successful POST (include `Location` header)
- `204 No Content` - Successful DELETE with no response body

**Client Errors:**
- `400 Bad Request` - Invalid input, validation failure
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Duplicate resource, constraint violation
- `422 Unprocessable Entity` - Semantic validation failure

**Server Errors:**
- `500 Internal Server Error` - Unexpected server error
- `503 Service Unavailable` - Temporary unavailability

## Request/Response Patterns

**Consistent response structure:**
```json
{
  "data": { "id": 1, "name": "John" },
  "meta": { "timestamp": "2024-01-01T00:00:00Z" }
}
```

**Error response structure:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  }
}
```

## Validation and Error Handling

**Validate at API boundary:**
- Check required fields before processing
- Validate formats (email, phone, URL)
- Enforce business rules
- Return specific error messages

**Never expose internal errors to clients:** No database error messages, stack traces, or internal file paths.

## Before Completing API Work

- [ ] Endpoints follow REST principles
- [ ] URLs use consistent naming convention
- [ ] HTTP methods match operations (GET for read, POST for create, etc.)
- [ ] Status codes accurately reflect responses
- [ ] Validation happens at API boundary
- [ ] Error responses are structured and specific
- [ ] Tests cover success and error cases
