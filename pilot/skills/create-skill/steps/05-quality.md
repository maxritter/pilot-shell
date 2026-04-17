---

## Step 5: Quality Gates

### Structure Checklist

- [ ] Folder named in kebab-case
- [ ] `SKILL.md` file exists (exact spelling, case-sensitive)
- [ ] YAML frontmatter has `---` delimiters
- [ ] `name` field: kebab-case, no spaces, no capitals, matches folder name
- [ ] `description` includes WHAT and WHEN (under 1024 chars, no XML tags)
- [ ] No `README.md` inside the skill folder
- [ ] SKILL.md under 5,000 words

### Content Checklist

- [ ] Instructions are clear and actionable (commands > descriptions)
- [ ] Error handling included (Common Issues section)
- [ ] Examples provided (concrete input/output)
- [ ] "When NOT to Use" section with explicit exclusions
- [ ] Verification step (how to confirm it worked)
- [ ] No sensitive information (API keys, passwords → use env vars)
- [ ] No hardcoded paths (use relative paths or environment variables)
- [ ] References clearly linked (to `references/` or external docs)

### Triggering Test

Before finalizing, verify the description will activate correctly:

```
Should trigger:
- "[exact phrases a user would say]"
- "[paraphrased version of the request]"
- "[related but different phrasing]"

Should NOT trigger:
- "[unrelated topic that sounds similar]"
- "[general request the skill shouldn't handle]"
```

**Debug approach:** Ask Claude "When would you use the [skill name] skill?" — Claude will quote the description back. Adjust based on what's missing.
