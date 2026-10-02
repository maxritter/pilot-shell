---
title: Simplify
description: An optional pass after the build that makes the whole change simpler, with the same behaviour.
---

![The Feature route with the quality pass highlighted](pathname:///img/diagrams/track-quality-light.svg)
![The Feature route with the quality pass highlighted](pathname:///img/diagrams/track-quality-dark.svg)

Coding agents tend to leave near-copies, extra wrappers and code for cases that cannot happen, and that makes a codebase harder to change over time. Simplify is the first step of the [quality pass](../check/verify.md#the-quality-pass) that opens Verify. It is on by default.

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

[Verification](../check/verify.md) then checks that nothing broke. A simplification that broke something is undone.

## Good to know

- There is no extra command; it runs by itself in a feature build. A bug has nothing to simplify, so its route has no Simplify step.
- Switch it off in [Settings](../../reference/settings.md#optional-steps), when a task starts, or at the handoff, and your task skips it.
- It runs on the model you chose for [subagents](../../reference/settings.md#subagents). If that is **This session**, your agent does it.
- Planning helps too: research names the code to reuse, and the design says where each new piece lives.
