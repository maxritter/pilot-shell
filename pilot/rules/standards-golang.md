---
paths:
  - "**/*.go"
---

## Go Development Standards

**Standards:** Go modules | go test | gofmt + go vet + golangci-lint | Self-documenting code

### Module Management

```bash
go mod init module-name    # Initialize
go mod tidy                # Add/remove deps
go get -u ./...            # Update deps
```

### Testing & Quality

**Use minimal output flags to avoid context bloat.**

```bash
go test ./...                             # All tests
go test ./... -race                       # With race detector
go test -coverprofile=coverage.out ./...  # Coverage report

gofmt -w .                                # Format
go vet ./...                              # Static analysis
golangci-lint run                         # Comprehensive linting
```

**Table-driven tests** preferred for multiple cases. Use `t.Run()` for subtests.

### Code Style

- **Packages:** lowercase, single word (`http`, `json`, `user`)
- **Exported:** PascalCase (`ProcessOrder`, `UserService`)
- **Unexported:** camelCase (`processOrder`, `userService`)
- **Acronyms:** ALL CAPS (`HTTPServer`, `XMLParser`, `userID`)
- **Interfaces:** Often -er suffix (`Reader`, `Writer`, `Handler`)
- **Comments:** Exported functions start with function name: `// ProcessOrder handles...`

### Error Handling

- Always handle errors explicitly — never `result, _ := doSomething()`
- Wrap with context: `fmt.Errorf("processing user %s: %w", userID, err)`
- Use sentinel errors: `var ErrNotFound = errors.New("not found")`

### Common Patterns

- **Context:** Always first parameter: `func ProcessRequest(ctx context.Context, ...)`
- **Defer:** For cleanup: `defer f.Close()`
- **Struct init:** Named fields: `User{ID: "123", Name: "Alice"}`

### Project Structure

```
cmd/         # Main applications
internal/    # Private packages
pkg/         # Public packages
```

### Verification Checklist

- [ ] `gofmt -w .` — formatted
- [ ] `go test ./...` — tests pass
- [ ] `go vet ./...` — clean
- [ ] `golangci-lint run` — clean
- [ ] `go mod tidy` — deps tidy
- [ ] No ignored errors
- [ ] Production files ideally under 800 lines (1000+ = consider splitting)
