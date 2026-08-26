## Step 3: Corroborate and Resolve Boundaries

Evaluate each bounded analyzer candidate. Read the declaration and its owning module metadata before searching.

### Required checks

1. **Exact repository search:** search the exact symbol across production, tests, configuration, scripts, manifests, templates, generated-entry metadata, and documentation that can name runtime hooks. Record declaration, import, call, string, and test-only occurrences separately.
2. **Boundary audit:** determine whether the symbol is exported/public or can be consumed through a framework route, plugin registry, dependency injection, reflection, serialization, configuration string, decorator/annotation, CLI entry point, generated binding, FFI, template, or external package API. An unresolved boundary blocks `likely removable`.
3. **One orthogonal corroboration where available:**
   - CodeGraph callers/impact for structural paths;
   - the bundled read-only CodeGraph helper for a scoped heuristic snapshot;
   - Claude LSP references for semantic references;
   - Semble intent search for registration, dispatch, plugin, and indirect-consumer patterns.

Open the decisive source returned by a search/index. Do not cite an index summary without reading its load-bearing location. Do not repeat identical searches through every tool merely to accumulate votes.

### Classification

Assign exactly one status:

- **Likely removable:** a project-native analyzer plus at least one independent corroborating signal agree, exact search found no consumer, and every plausible public/dynamic boundary was resolved.
- **Needs boundary review:** the analyzer nominated it, but an export, dynamic/framework path, generated surface, external consumer, or signal-independence question remains.
- **Test-supported production code:** the declaration is production code and tests are its only observed consumers. This is not a dead-code finding.
- **Test-only candidate:** the declaration itself is confined to tests, fixtures, examples, or benchmarks and has adequate evidence within that separate scope.
- **Referenced / false positive:** a live consumer or required registration contradicts the analyzer candidate.
- **Unresolved:** a tool failure, stale/incomplete index, excessive candidate set, missing source, or ambiguous identity prevents classification.

CodeGraph's `findDeadCode()` output is heuristic: default callbacks, registrations, and dynamic dispatch can appear unreferenced. LSP scope can omit tests or other workspace roots. Semble can miss literal or generated consumers. Exact search can miss computed names. Apply these limitations to the status, not just a disclaimer after it.

**Completion:** each reported symbol has two genuinely independent signals or a conservative non-removable/unresolved status, with tests kept separate from production.
