---
description: Package Boundaries
paths:
  - "installer/**"
  - "launcher/**"
---

# Package Boundaries: launcher vs installer

`launcher/` is **Cython-compiled into a standalone binary** shipped as `~/.pilot/bin/pilot`. `installer/` is a separate Python package running in its own process — often where the launcher source tree isn't on `sys.path` (pipx, `curl | sh`, fresh upgrade before the binary exists).

## ⛔ NEVER `import` across the boundary

```python
# ❌ inside installer/
from launcher.skill_builder import write_skill_md   # ImportError in shipped installs

# ❌ inside launcher/
from installer.steps.settings_merge import merge_settings   # installer not present at runtime
```

Both directions. Each package must work standalone.

## When the installer needs launcher logic

Pick one — never `import`:

1. **Subprocess the binary** — `subprocess.run([pilot_bin, "<subcommand>", ...])`. Use when behavior must match the shipped binary exactly (canonicalization, hashing, drift-sensitive logic). For per-item overhead, add a batched subcommand (`pilot <verb>-batch <root>`).
2. **Vendor (copy)** the code into `installer/<module>.py`. Only for small, stable, pure-stdlib utilities with no shared state. Add a one-line comment pointing back to the launcher source so the duplication is discoverable.

## Quick check before any cross-package import

> "Will this still work after the user installs Pilot Shell via `pipx install pilot-shell` or `curl | sh`?"

If unsure, the answer is no. Use subprocess or vendor.
