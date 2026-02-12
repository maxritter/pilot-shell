# Enforcing Test-Driven Development with Claude Code

AI-generated code is only as reliable as the tests that verify it. Claude writes syntactically correct code fast — but it doesn't know your business logic quirks or undocumented edge cases. TDD makes the test the specification: Claude implements exactly what the tests require, nothing more.

## The Red-Green-Refactor Cycle

TDD with Claude follows three phases:

### 1. Red — Write a Failing Test

You define what "correct" means. The test fails because the feature doesn't exist yet.

```typescript
describe('validateToken', () => {
  it('should return true for valid JWT tokens', () => {
    expect(validateToken(validToken)).toBe(true);
  });
  it('should return false for expired tokens', () => {
    expect(validateToken(expiredToken)).toBe(false);
  });
});
```

Run the test. It **must fail**. A test that passes immediately proves nothing.

### 2. Green — Implement Minimal Code

Claude writes the simplest code that makes the test pass. No extra features, no premature optimization.

```typescript
export function validateToken(token: string): boolean {
  try {
    jwt.verify(token, process.env.JWT_SECRET!);
    return true;
  } catch {
    return false;
  }
}
```

Run the test. It passes.

### 3. Refactor — Improve While Green

Improve the code — extract functions, add error handling, simplify logic. Tests stay green throughout. If they break, the refactor introduced a bug.

## Enforcing TDD with Hooks

The cycle works when you follow it. Hooks make it **automatic, not optional**. Pilot includes a TDD enforcer hook that runs on every file edit:

```json
{
  "PostToolUse:Write": [
    { "shell": "python ${CLAUDE_PLUGIN_ROOT}/hooks/tdd_enforcer.py" }
  ],
  "PostToolUse:Edit": [
    { "shell": "python ${CLAUDE_PLUGIN_ROOT}/hooks/tdd_enforcer.py" }
  ]
}
```

If Claude tries to create production code without a corresponding test file, the hook blocks it. Writing tests first becomes the path of least resistance.

## How Pilot Automates TDD

### Spec-Driven TDD

The `/spec` command mandates TDD for every task:

1. **Plan** — Define what to build, get approval
2. **Implement** — For each task: write failing test → implement → verify green
3. **Verify** — Review agents audit test quality and coverage

You can't skip tests in `/spec`. The workflow blocks progression until tests exist and pass.

### Verification Catches Weak Tests

Even with TDD, tests can be trivial (`expect(true).toBe(true)`). Pilot's verification phase audits:

- **Coverage** — Do tests exercise the actual code paths?
- **Assertions** — Are they meaningful and specific?
- **Edge cases** — Are error paths and boundary conditions tested?

Insufficient tests fail verification. You fix the tests, not the code.

## Bug Fixes Follow TDD Too

**Bug:** `calculateDiscount` returns negative prices for invalid coupons.

```typescript
// Step 1: Regression test (red)
it('should return original price for invalid coupons', () => {
  expect(calculateDiscount(100, 'INVALID')).toBe(100);
});

// Step 2: Fix (green)
const discount = validCoupons[coupon] ?? 0; // Default to 0 for invalid
return price * (1 - discount);
```

Test fails first (proving the bug exists), then passes after the fix (proving it's resolved). The regression test stays forever.

## Key Takeaway

TDD transforms Claude from a code generator into a code implementer. Pilot enforces it with hooks and workflow rules so it's never skipped — even on "quick fixes."
