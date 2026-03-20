"""Security control plane for pilot-shell.

Layered architecture:
  Execution Plane  → runs user commands / AI-generated actions
  Security Plane   → evaluates risk, enforces policy, blocks or annotates
  Intelligence Plane → aggregates findings, correlates context
  Audit Plane      → logs everything: commands, decisions, diffs, artifacts

Flow:
  User/AI → Command
          ↓
  Risk Classifier → Policy Engine → (Allow / Warn / Block)
          ↓
  Execution
          ↓
  Scan + Correlate
          ↓
  Audit Log + Report
"""

from __future__ import annotations

__version__ = "1.0.0"
