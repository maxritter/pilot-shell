## Step 5: Exploration

**⛔ START FROM THE STEP 3 WORKSPACE SCAN — do NOT re-run `codegraph_context` with the same query.**

#### 5.1: Review Step 3 scan output

The Workspace Scan in Step 3 already ran `codegraph_context(task=<task description>)` and (when applicable) a Semble pattern search. Re-read its structured output before any deeper exploration:

```
Entry points: [...]
Related symbols: [...]
Similar patterns: [...]
Greenfield?: [yes | no]
```

If `Greenfield?: yes` AND the task is conceptual rather than symbol-mapped, **now** is the time to broaden with `mcp__semble__search` using different phrasings — Step 3 only ran the obvious noun query. Otherwise, proceed to 5.2 with the scan results as your starting set of entry points.

#### 5.2: Deep dive with CodeGraph explore

After orienting, use `codegraph_search` to find specific symbol names, then:

```
codegraph_explore(query="SymbolA SymbolB relevant-file.ts")
```

This returns **full source code sections** from all relevant files in ONE call — replacing dozens of Read/Grep calls. Use specific symbol names (from search results), not natural language. Follow the call budget in the tool description.

#### 5.3: Systematic exploration

**Explore one area at a time (sequentially, not parallel).** Use CodeGraph and Semble as primary tools — Grep/Glob only for exact text patterns.

| Need                            | Tool                                                    |
| ------------------------------- | ------------------------------------------------------- |
| **Orient on the task**          | CodeGraph `codegraph_context(task=<description>)` — already done in Step 3 |
| **Deep understanding of code**  | CodeGraph `codegraph_search` → `codegraph_explore(query="<symbol names>")` |
| **Understand a feature by intent** | Semble `semble search "how does X work"` or `mcp__semble__search` |
| **Find symbols by name**        | CodeGraph `codegraph_search`                            |
| **Discover similar code from a hit** | Semble `semble find-related file.ts 42` or `mcp__semble__find_related` |
| **Extract enclosing block at `file:line`** | `Read` with `offset`/`limit`, or `codegraph_node` (by symbol name) |
| **Project file structure**      | CodeGraph `codegraph_files`                             |
| **Call tracing**                | CodeGraph `codegraph_callers`/`codegraph_callees`       |
| **Library/framework docs**      | Context7                                                |
| **Real-world GitHub examples**  | grep-mcp                                                |
| **Exact text/regex**            | Grep/Glob (last resort)                                 |

**Areas (in order):** Architecture → Similar Features → Dependencies → Tests

#### 5.4: Dependency analysis (MANDATORY for 3+ file changes)

For every function you plan to modify: (1) `codegraph_callers` + `codegraph_callees` for the call graph, (2) `Grep` for the symbol name to catch callers the graph may miss, (3) `codegraph_impact` to assess blast radius. CodeGraph gives structure; Grep gives completeness — use both.

For each area: document hypotheses, note full file paths, track unanswered questions. After exploration: read identified files to verify hypotheses, build complete mental model, identify integration points, note reusable patterns.
