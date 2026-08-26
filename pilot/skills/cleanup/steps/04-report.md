## Step 4: Reconcile and Report

Capture `git status --short --untracked-files=all` again and compare it byte-for-byte with the Step 1 snapshot. If it differs, identify whether a read-only check created ignored state or whether the audit unexpectedly changed a tracked/untracked path. Do not delete or repair anything inside this report-only workflow; report the discrepancy precisely.

Before answering, reconcile every execution claim with the transcript:

- exact command, exit status, scope, and concise result;
- analyzer candidates versus corroboration-only leads;
- CodeGraph index presence/freshness limitations when used;
- candidate truncation and excluded paths;
- commands not run and why;
- initial versus final worktree state.

Use this report shape:

```markdown
<Direct result: counts by production, test-only, false-positive, review, and unresolved status.>

### Likely removable
| Symbol | Declaration | Analyzer signal | Independent corroboration | Boundary check |

### Needs review
| Symbol | Declaration | Status | Blocking boundary or missing evidence |

### Test-only and test-supported
| Symbol | Declaration | Status | Evidence |

### Commands and results
| Command | Exit | Scope | Result |

### Worktree
- Initial: <exact snapshot or clean>
- Final: <exact snapshot or clean>
- Unchanged: <yes/no with precise discrepancy>

### Not verified
<Only material gaps.>
```

Omit empty candidate tables, but never omit **Commands and results**, **Worktree**, or material gaps. Do not phrase “likely removable” as “safe to delete.” Do not include a patch, deletion command, or offer that implies changes already occurred.

**Completion:** the report is traceable to fresh command results, test-only findings are separate, every production classification meets its evidence threshold, and the worktree comparison is explicit.
