---
paths:
  - "**/*.go"
---

## Go Development Standards

**Standards:** Use go modules | go test for tests | gofmt + go vet + golangci-lint for quality | Self-documenting code

### Module Management

**Use Go modules for dependency management:**

```bash
# Initialize a new module
go mod init module-name

# Add dependencies (automatically via imports)
go mod tidy

# Update dependencies
go get -u ./...

# Verify dependencies
go mod verify
```

**Why modules:** Standard Go dependency management, reproducible builds, version control.

### Testing & Quality

**⚠️ CRITICAL: Always use minimal output flags to avoid context bloat.**

```bash
# Tests - USE MINIMAL OUTPUT
go test ./...                           # All tests
go test ./... -v                        # Verbose (only when debugging)
go test ./... -short                    # Skip long-running tests
go test ./... -race                     # With race detector
go test ./... -cover                    # With coverage
go test -coverprofile=coverage.out ./...  # Coverage report

# Code quality
gofmt -w .                              # Format code
goimports -w .                          # Format + organize imports
go vet ./...                            # Static analysis
golangci-lint run                       # Comprehensive linting
```

**Why minimal output?** Verbose test output consumes context tokens rapidly. Only add `-v` when debugging specific failing tests.

**Table-driven tests:** Preferred for testing multiple cases:
```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name    string
        email   string
        wantErr bool
    }{
        {"valid email", "user@example.com", false},
        {"missing @", "userexample.com", true},
        {"empty", "", true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := ValidateEmail(tt.email)
            if (err != nil) != tt.wantErr {
                t.Errorf("ValidateEmail(%q) error = %v, wantErr %v", tt.email, err, tt.wantErr)
            }
        })
    }
}
```

### Code Style Essentials

**Formatting:** `gofmt` handles all formatting. Run `gofmt -w .` before committing.

**Naming Conventions:**
- **Packages:** lowercase, single word (e.g., `http`, `json`, `user`)
- **Exported:** PascalCase (e.g., `ProcessOrder`, `UserService`)
- **Unexported:** camelCase (e.g., `processOrder`, `userService`)
- **Acronyms:** ALL CAPS (e.g., `HTTPServer`, `XMLParser`, `userID`)
- **Interfaces:** Often use -er suffix (e.g., `Reader`, `Writer`, `Handler`)

**Comments:** Write self-documenting code. Comments for exported functions should start with the function name:
```go
// ProcessOrder handles order processing for the given user.
func ProcessOrder(userID string, order Order) error {
    // implementation
}
```

### Error Handling

**Always handle errors explicitly. Never ignore them.**

```go
// GOOD - handle error
result, err := doSomething()
if err != nil {
    return fmt.Errorf("failed to do something: %w", err)
}

// BAD - ignoring error
result, _ := doSomething()
```

**Error wrapping:** Use `fmt.Errorf` with `%w` for context:
```go
if err != nil {
    return fmt.Errorf("processing user %s: %w", userID, err)
}
```

**Custom errors:** Use sentinel errors for domain-specific error types:
```go
var ErrNotFound = errors.New("not found")
var ErrInvalidInput = errors.New("invalid input")

if errors.Is(err, ErrNotFound) {
    // handle not found
}
```

### Common Patterns

**Context propagation:** Always pass context as first parameter:
```go
func ProcessRequest(ctx context.Context, req Request) (Response, error) {
    result, err := db.QueryContext(ctx, query)
    if err != nil {
        return Response{}, err
    }
    return Response{Data: result}, nil
}
```

**Defer for cleanup:**
```go
f, err := os.Open(path)
if err != nil {
    return nil, err
}
defer f.Close()
```

**Struct initialization with named fields:**
```go
user := User{
    ID:    "123",
    Name:  "Alice",
    Email: "alice@example.com",
}
```

### Project Structure

**Standard Go project layout:**
```
project/
├── cmd/              # Main applications
│   └── myapp/
│       └── main.go
├── internal/         # Private packages
│   └── service/
├── pkg/              # Public packages
│   └── api/
├── go.mod
└── go.sum
```

**Package organization:**
- Keep packages focused and cohesive
- Avoid circular dependencies
- Use `internal/` for private packages

### Verification Checklist

Before completing Go work:
- [ ] Code formatted: `gofmt -w .`
- [ ] Tests pass: `go test ./...`
- [ ] Static analysis clean: `go vet ./...`
- [ ] Linting clean: `golangci-lint run`
- [ ] No ignored errors
- [ ] Dependencies tidy: `go mod tidy`
- [ ] No production file exceeds 300 lines (500 = hard limit, refactor immediately)

### Quick Reference

| Task              | Command                    |
| ----------------- | -------------------------- |
| Init module       | `go mod init module-name`  |
| Run tests         | `go test ./...`            |
| Coverage          | `go test -cover ./...`     |
| Format            | `gofmt -w .`               |
| Static analysis   | `go vet ./...`             |
| Lint              | `golangci-lint run`        |
| Tidy deps         | `go mod tidy`              |
| Build             | `go build ./...`           |
| Run               | `go run cmd/myapp/main.go` |
