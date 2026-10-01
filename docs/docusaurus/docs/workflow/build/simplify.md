---
title: Simplify
description: One pass at the end of every build that makes the whole change simpler, with the same behaviour.
---

![The Feature route with Simplify highlighted](pathname:///img/diagrams/track-simplify-light.svg)
![The Feature route with Simplify highlighted](pathname:///img/diagrams/track-simplify-dark.svg)

Coding agents tend to leave near-copies, extra wrappers and code for cases that cannot happen, and that makes a codebase harder to change over time. Every plan ends with a Simplify slice, the last part of the build.

![Simplify: two near-copies merged, existing code reused, a wrapper removed, one commit each, with the same behaviour](pathname:///img/diagrams/simplify-light.svg)
![Simplify: two near-copies merged, existing code reused, a wrapper removed, one commit each, with the same behaviour](pathname:///img/diagrams/simplify-dark.svg)

## What it does

Once everything is built, a fresh helper reads the whole change once and:

- merges near-copies into one;
- reuses code your project already has;
- removes what isn't needed: pass-through wrappers, handling for impossible cases, comments that only repeat the code.

Behaviour stays the same, and each simplification is its own commit.

## The safety net

After each simplification, the tests run again, and the tests of the code it touched run three times, because a timing fault shows only now and then. A test that fails also runs on the code from before the simplification: if it fails there too, it was already flaky and is reported. If it fails only after, the simplification is undone.

[Verification](../check/verify.md) then checks that nothing broke. A simplification that broke something is undone, not patched.

## Good to know

- There is no extra command; it is part of every plan.
- It has its own model in [Settings](../../reference/settings.md#subagents), or **Off**, in which case your agent does it.
- Planning helps too: research names the code to reuse, and the design says where each new piece lives.
