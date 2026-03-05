---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.mjs"
  - "**/*.mts"
---

## TypeScript Development Standards

**Standards:** Detect package manager | Strict types | No `any` | Self-documenting code

### Package Manager - DETECT FIRST

**Detect and use the project's existing package manager. Never mix.**

- `bun.lockb` → **bun** | `pnpm-lock.yaml` → **pnpm** | `yarn.lock` → **yarn** | `package-lock.json` → **npm**

No lock file? Check `packageManager` in `package.json`, or default to npm.

### Type Safety

- **Explicit return types** on all exported functions
- **Interfaces** for objects, **types** for unions
- **Never use `any`** — use `unknown`, a specific type, or a generic instead

### Code Style

- Self-documenting code, minimize comments
- One-line JSDoc for exports: `/** Calculate discounted price. */`
- **Import order:** Node built-ins (`node:`) → External → Internal → Relative
- **File names:** kebab-case (`user-service.ts`)

### Common Patterns

- Prefer `node:` prefix for built-ins: `import { readFile } from 'node:fs/promises'`
- Use `const` assertions for literal types: `const ROLES = ['admin', 'user'] as const`
- Don't swallow errors — log and re-throw

### Testing - Minimal Output

```bash
npm test -- --silent         # Suppress console.log
npm test -- --reporters=dot  # Minimal reporter
npm test -- --bail           # Stop on first failure
```

### Verification Checklist

Check `package.json` scripts first — projects often have custom configurations.

- [ ] `tsc --noEmit` — no type errors
- [ ] Lint clean (eslint/biome)
- [ ] Tests pass
- [ ] Explicit return types on exports
- [ ] No `any` types
- [ ] Correct lock file committed
- [ ] Production files ideally under 800 lines (1000+ = consider splitting)

### Quick Reference

| Task | npm | yarn | pnpm | bun |
|------|-----|------|------|-----|
| Install | `npm install` | `yarn` | `pnpm install` | `bun install` |
| Add pkg | `npm install pkg` | `yarn add pkg` | `pnpm add pkg` | `bun add pkg` |
| Run script | `npm run x` | `yarn x` | `pnpm x` | `bun x` |
