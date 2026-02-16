## Pilot Memory & Learning

### Persistent Memory (MCP)

Search past work, decisions, and context across sessions. **3-layer workflow for token efficiency:**

```
1. search(query) → Index with IDs (~50-100 tokens/result)
2. timeline(anchor=ID) → Chronological context around results
3. get_observations([IDs]) → Full details ONLY for filtered IDs
```

**Never fetch full details without filtering first.**

| Tool | Purpose | Key Params |
|------|---------|------------|
| `search` | Find observations | `query`, `limit`, `type`, `project`, `dateStart`, `dateEnd` |
| `timeline` | Context around result | `anchor` (ID), `depth_before`, `depth_after` |
| `get_observations` | Full details | `ids` (array) |
| `save_memory` | Save manually | `text`, `title`, `project` |

**Types:** `bugfix`, `feature`, `refactor`, `discovery`, `decision`, `change`

Use `<private>` tags to exclude content from storage. Web viewer at `http://localhost:41777`.

---

### Online Learning System

**Evaluate sessions for extractable knowledge. Only act when valuable.**

At 65%+ context (when `/learn check` reminder fires):
1. Does this session have a non-obvious solution OR repeatable workflow?
2. **YES** → Invoke `Skill(learn)` before auto-compaction
3. **NO** → Proceed silently, no mention needed

**Triggers for automatic `Skill(learn)` invocation:**
- Non-obvious debugging (solution wasn't in docs)
- Workarounds for limitations
- Undocumented tool/API integration
- Multi-step workflow that will recur
- External service queries (Jira, GitHub, Confluence)

**Don't extract:** Simple tasks, single-step fixes, knowledge in official docs, unverified solutions.
