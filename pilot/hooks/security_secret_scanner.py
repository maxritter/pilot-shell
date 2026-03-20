"""PostToolUse hook — scans files written by Write/Edit for secrets.

Triggered after: Write, Edit, MultiEdit

Behaviour:
  - If HIGH severity secrets found → block (prevent the write result from
    being accepted; Claude sees a block reason and must fix the file)
  - If MEDIUM secrets found → warn via additionalContext
  - No findings → silent pass

Exit codes:
  0  → pass (optionally with additionalContext)
  2  → block (drops tool result, surfaces reason to Claude)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from security.secrets.detector import Severity, scan_file
from security.audit.logger import log_secret_found
from _lib.util import post_tool_use_block, post_tool_use_context

RED = "\033[0;31m"
YELLOW = "\033[0;33m"
NC = "\033[0m"


def run() -> int:
    try:
        hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    tool_name = hook_data.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        return 0

    tool_input = hook_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return 0

    # Skip binary / non-text files and known safe paths
    p = Path(file_path)
    if p.suffix in (".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".eot"):
        return 0

    findings = scan_file(file_path)
    if not findings:
        return 0

    # Audit
    log_secret_found(file_path, [f.to_dict() for f in findings])

    high_findings = [f for f in findings if f.severity == Severity.HIGH]
    med_findings = [f for f in findings if f.severity == Severity.MEDIUM]

    if high_findings:
        sys.stderr.write(
            f"{RED}[PilotSec] SECRET DETECTED in {p.name} — {len(high_findings)} HIGH severity finding(s){NC}\n"
        )
        lines = [f"[PilotSec] Secrets detected in {file_path}:"]
        for f in high_findings:
            lines.append(
                f"  Line {f.line_number}: {f.description} ({f.pattern_name}) — {f.redacted}"
            )
        lines.append("")
        lines.append(
            "Remove or replace the secret before this file can be accepted. "
            "Use environment variables or a secrets manager instead of hardcoded values."
        )
        print(post_tool_use_block("\n".join(lines)))
        return 2

    if med_findings:
        sys.stderr.write(
            f"{YELLOW}[PilotSec] Potential secrets in {p.name} — {len(med_findings)} MEDIUM finding(s){NC}\n"
        )
        lines = [f"[PilotSec] Possible secrets detected in {file_path}:"]
        for f in med_findings:
            lines.append(
                f"  Line {f.line_number}: {f.description} ({f.pattern_name}) — {f.redacted}"
            )
        lines.append("Review and confirm these are not real credentials.")
        print(post_tool_use_context("\n".join(lines)))

    return 0


if __name__ == "__main__":
    sys.exit(run())
