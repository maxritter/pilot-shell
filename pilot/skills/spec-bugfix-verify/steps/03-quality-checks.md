## Step 3: Quality Checks

1. **Type checker** — zero new errors
2. **Linter** — errors are blockers, fix immediately
3. **Build** (if applicable) — must succeed
4. **Performance audit** — For changed files on hot paths: expensive uncached work? Heavy dependency imports with lighter alternatives? Repeated invocations redoing work when input hasn't changed? Structural issues — visible in source, no running program needed.
