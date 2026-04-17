## Step 6: Exploration

**⛔ START WITH CODEGRAPH — before reading any files or running any searches.**

#### 6.1: Orient with CodeGraph (MANDATORY FIRST ACTION)

```
codegraph_context(task="<task description from user>")
```

This returns entry points, related symbols, and key code. Works best when the task maps to actual code symbols. If it returns irrelevant results (e.g., only tests or UI components), the task may be conceptual — supplement with Probe `probe search "how does X work"` for intent-based discovery.

#### 6.2: Deep dive with CodeGraph explore

After orienting, use `codegraph_search` to find specific symbol names, then:

```
codegraph_explore(query="SymbolA SymbolB relevant-file.ts")
```

This returns **full source code sections** from all relevant files in ONE call — replacing dozens of Read/Grep calls. Use specific symbol names (from search results), not natural language. Follow the call budget in the tool description.

#### 6.3: Systematic exploration

**Explore one area at a time (sequentially, not parallel).** Use CodeGraph and Probe as primary tools — Grep/Glob only for exact text patterns.

| Need                            | Tool                                                    |
| ------------------------------- | ------------------------------------------------------- |
| **Orient on the task**          | CodeGraph `codegraph_context(task=<description>)` — already done in 6.1 |
| **Deep understanding of code**  | CodeGraph `codegraph_search` → `codegraph_explore(query="<symbol names>")` |
| **Understand a feature by intent** | Probe `probe search "how does X work"`               |
| **Find symbols by name**        | CodeGraph `codegraph_search`                            |
| **Extract code by symbol/line** | Probe `probe extract file.ts#symbol`                    |
| **Project file structure**      | CodeGraph `codegraph_files`                             |
| **Call tracing**                | CodeGraph `codegraph_callers`/`codegraph_callees`       |
| **Library/framework docs**      | Context7                                                |
| **Real-world GitHub examples**  | grep-mcp                                                |
| **Exact text/regex**            | Grep/Glob (last resort)                                 |

**Areas (in order):** Architecture → Similar Features → Dependencies → Tests

#### 6.4: Dependency analysis (MANDATORY for 3+ file changes)

For every function you plan to modify: (1) `codegraph_callers` + `codegraph_callees` for the call graph, (2) `Grep` for the symbol name to catch callers the graph may miss, (3) `codegraph_impact` to assess blast radius. CodeGraph gives structure; Grep gives completeness — use both.

For each area: document hypotheses, note full file paths, track unanswered questions. After exploration: read identified files to verify hypotheses, build complete mental model, identify integration points, note reusable patterns.
