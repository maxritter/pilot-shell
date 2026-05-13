## Step 1: Special Cases (conditional — skip both sub-sections if neither applies)

This step handles the two situational planning paths. Most new plans skip both — when the request is a brand-new feature and no existing code is being replaced, proceed directly to Step 2 (Create Header).

### 1a. Extending an Existing Plan

When adding tasks to an existing plan: load it, parse structure, verify compatibility, mark new tasks with `[NEW]`, update totals. If original + new > 12 tasks, suggest splitting.

### 1b. Migration/Refactoring — Feature Inventory

**When replacing existing code, complete a Feature Inventory BEFORE creating tasks:**

1. List ALL files being replaced with their functions/classes
2. Map EVERY function to a task — no row may be "Not mapped"
3. Every row needs a Task # or explicit "Out of Scope" with user confirmation

"Out of Scope: Changes to X" = X migrates AS-IS (still needs migration task). "Out of Scope: Feature X" = X intentionally REMOVED (needs user confirmation, no task needed).
