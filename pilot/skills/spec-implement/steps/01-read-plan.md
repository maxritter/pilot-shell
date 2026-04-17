---

## Step 1: Read Plan & Gather Context

1. **Read the COMPLETE plan** — understand architecture and design
2. **Summarize understanding** — demonstrate comprehension
3. **Check current state:** `git status --short`, `git diff --name-only`, plan progress (`[x]` vs `[ ]`)

**Research tools during implementation:** CodeGraph (`codegraph_context` to orient on each task, `codegraph_explore` for deep code understanding in one call, `codegraph_callers`/`codegraph_callees` before modifying any function, `codegraph_impact` for blast radius), Context7 (library docs), Probe CLI `probe search` (find patterns by intent), `probe extract` (extract code blocks), grep-mcp (production examples).

**⛔ Before modifying any function:** Run `codegraph_callers` + `codegraph_callees` to understand the call graph. This is not optional — it catches callers you'd otherwise miss.
