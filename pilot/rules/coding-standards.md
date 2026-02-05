## Coding Standards

Apply these standards to all code changes.

### Priority Order (When Trade-offs Arise)

**Correctness > Maintainability > Performance > Brevity**

When you must choose between competing concerns:
1. **Correctness** - Code must work correctly. Never sacrifice correctness for anything.
2. **Maintainability** - Code others can understand and modify. Prefer readable over clever.
3. **Performance** - Fast enough for the use case. Don't optimize prematurely.
4. **Brevity** - Concise is nice, but never at the cost of the above.

### Core Principles

**DRY (Don't Repeat Yourself)**: When you see duplicated logic, extract it into a reusable function immediately. If you're about to copy-paste code, stop and create a shared function instead.

**YAGNI (You Aren't Gonna Need It)**: Build only what's explicitly required. Don't add abstractions, features, or complexity for hypothetical future needs. Add them when you have concrete evidence they're needed.

**Single Responsibility**: Each function should do one thing well. If you need "and" to describe what a function does, it's doing too much and should be split.

### Naming Conventions

Use descriptive names that reveal intent without requiring comments:
- Functions: `calculate_discount`, `validate_email`, `fetch_active_users`
- Avoid: `process`, `handle`, `data`, `temp`, `x`, `do_stuff`
- Use domain terminology familiar to the project
- Spell out words unless the abbreviation is universally understood

### Code Organization

**Imports**: Order as standard library → third-party → local application. Remove unused imports immediately.

**Dead Code**: Delete unused functions, commented-out blocks, and unreachable code. Use version control to recover old code if needed.

**Function Size**: Keep functions small and focused. Extract complex logic into well-named helper functions.

### Before Modifying Code

**Dependency Check**: Before modifying any function or feature, identify downstream consumers:
1. Use `Grep` or LSP `findReferences` to find all callers
2. Check if your changes affect return types, parameters, or behavior
3. Plan to update all affected call sites

This catches breaking changes before you make them, not during verification.

### Self-Correction

**Fix obvious mistakes immediately without asking permission:**
- Syntax errors, typos, missing imports
- Off-by-one errors discovered during testing
- Minor formatting issues

For low-level errors discovered during execution, correct and continue. Don't stop to report every minor fix. Reserve user communication for decisions, not status updates on trivial fixes.

### Quality Checks

**Diagnostics**: Check diagnostics before starting work and after making changes. Fix all errors before considering the task complete.

**Formatting**: Let automated formatters handle code style. Don't manually format code.

**Backward Compatibility**: Only add compatibility logic when explicitly required by the user. Don't assume you need to support old versions.

**Use Fast Tools**: Prefer `rg` (ripgrep) over grep/find for searching. It's 5-10x faster and already installed.

### Decision Framework

When writing code, ask:
1. Is this the simplest solution that works?
2. Am I duplicating existing logic?
3. Will the names make sense to someone reading this in 6 months?
4. Does each function have a single, clear purpose?
5. Have I removed all unused code and imports?
6. Have I checked diagnostics?

If any answer is no, refactor before proceeding.
