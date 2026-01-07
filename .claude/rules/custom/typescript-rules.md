## TypeScript Development Standards

**Standards:** Detect package manager | Explicit types on exports | Self-documenting code

### Package Manager - DETECT FIRST, THEN USE CONSISTENTLY

**MANDATORY: Detect and use the project's existing package manager. NEVER mix package managers.**

Check the project root for lock files:
- `bun.lockb` → use **bun**
- `pnpm-lock.yaml` → use **pnpm**
- `yarn.lock` → use **yarn**
- `package-lock.json` → use **npm**

If no lock file exists, check `packageManager` field in `package.json`, or default to npm.

**If you're about to run `npm` but see `yarn.lock`:** STOP. Use yarn instead.

**Why this matters:** Mixing package managers corrupts lock files and breaks reproducible builds.

### Type Annotations

**Explicit return types on all exported functions:**
```typescript
export function processOrder(orderId: string, userId: number): Order { ... }
export async function fetchUser(id: string): Promise<User> { ... }
```

**Interfaces for objects, types for unions:**
```typescript
interface User { id: string; email: string; }
type Status = 'pending' | 'active' | 'suspended';
```

### Code Style

**Self-documenting code. Minimize comments.**
```typescript
// BAD: if (u.r === 'admin')
// GOOD: if (user.isAdmin())
```

**One-line JSDoc for exports:**
```typescript
/** Calculate discounted price by applying rate. */
export function calculateDiscount(price: number, rate: number): number { ... }
```

**Import order:** Node built-ins → External packages → Internal modules → Relative imports

### Verification Checklist

Before completing TypeScript work, **always run** (using detected package manager):

1. **Format:** Use project's `format` script, or `prettier --write .` / `biome format --write .`
2. **Lint:** Use project's `lint` script, or `eslint . --fix` / `biome check --fix .`
3. **Type check:** Use project's `typecheck` script, or `tsc --noEmit`
4. **Tests:** Use project's `test` script

Verify:
- [ ] All commands pass
- [ ] Explicit return types on exports
- [ ] Correct lock file committed

### Quick Reference

| Task         | npm                  | yarn              | pnpm              | bun              |
| ------------ | -------------------- | ----------------- | ----------------- | ---------------- |
| Install all  | `npm install`        | `yarn`            | `pnpm install`    | `bun install`    |
| Add package  | `npm install pkg`    | `yarn add pkg`    | `pnpm add pkg`    | `bun add pkg`    |
| Add dev dep  | `npm install -D pkg` | `yarn add -D pkg` | `pnpm add -D pkg` | `bun add -D pkg` |
| Run script   | `npm run script`     | `yarn script`     | `pnpm script`     | `bun script`     |
| Exec binary  | `npx cmd`            | `yarn dlx cmd`    | `pnpm dlx cmd`    | `bunx cmd`       |
