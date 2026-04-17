## Step 9: Discover New Rules

1. List undocumented areas (comparing Step 2 + Step 5)
2. For each candidate area, find the actual patterns before drafting:
   ```bash
   # With Probe (preferred)
   probe search "how is [pattern] implemented across the codebase" ./ --max-results 5 --max-tokens 2000
   probe extract src/example.ts#patternFunction

   # Without Probe (fallback)
   # Grep(pattern="[pattern]", head_limit=10)
   # Read representative files directly
   ```
3. Prioritize by: frequency, uniqueness, mistake likelihood
4. AskUserQuestion (multiSelect): which areas to document
5. For each: ask clarifying questions, draft rule using search results and code examples, confirm before creating
6. **Place in correct directory** based on scope:
   - Repo-wide → `.claude/rules/{slug}-{pattern-name}.md`
   - Product-specific → `.claude/rules/{product}/{slug}-{product}-{pattern-name}.md` (add `paths` frontmatter)
   - Team-specific → `.claude/rules/{product}/{team}/{slug}-{team}-{pattern-name}.md` (**must** have `paths` frontmatter)
   - If nested directories exist (from Step 2), always ask which scope level the rule belongs to
   - Create product/team directories as needed (`mkdir -p`)

**Rule format:** Standard Name → When to Apply → The Pattern (code examples) → Why (if not obvious) → Common Mistakes → Good/Bad examples.
