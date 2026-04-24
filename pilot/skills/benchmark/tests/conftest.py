"""Shared pytest configuration for the benchmark skill tests.

Inserts the skill root onto sys.path so `from scripts.X import ...` resolves
the same way it does at runtime (the runner does the same insert via
`sys.path.insert` when invoked as a module).
"""

from __future__ import annotations

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))
