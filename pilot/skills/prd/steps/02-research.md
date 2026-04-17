---

## Step 2: Research (Optional)

**After understanding the idea, ask the user which research tier they want.** Use `AskUserQuestion` with these options:

- **Quick (Recommended for simple ideas)** — "Skip research, go straight to brainstorming"
- **Standard** — "Quick web research: competitors, prior art, best practices (5-10 searches)"
- **Deep** — "Thorough parallel research: multiple angles, comprehensive findings (uses sub-agents, higher token cost)"

### Quick Tier

Skip this phase entirely. Proceed to Step 3.

### Standard Tier

1. **Generate 5-8 search queries** based on the topic:
   - Competitor/alternative analysis ("alternatives to X", "X vs Y")
   - Prior art and existing solutions ("how companies solve X")
   - Technical approaches ("best practices for X")
   - User experience patterns ("UX patterns for X")
2. **Discover web-search tool:** `ToolSearch(query="+web-search search")`
3. **Execute searches sequentially**, gathering key findings from each
4. **Optionally fetch full pages** for promising results: `ToolSearch(query="+web-fetch fetch")` then `fetch_url(url="...")`
5. **Compile research summary:**
   - Key findings (3-5 bullet points)
   - Sources with links
   - Trade-offs and patterns discovered
   - Gaps or areas needing more exploration
6. **Present summary to user** before proceeding to brainstorming

### Deep Tier

1. **Generate a research outline** with 3-5 research angles based on the topic. Examples:
   - "Competitor landscape" — what exists, market positioning, pricing
   - "Technical approaches" — architectures, frameworks, implementation patterns
   - "User experience" — UX patterns, onboarding flows, common pain points
   - "Prior art" — academic papers, blog posts, case studies
2. **Launch 2-4 web-search-agent sub-agents in parallel:**

   For each research angle:
   ```
   Agent(
     subagent_type="web-search-agent",
     run_in_background=true,
     prompt="Research angle: <angle_name>\n\nTopic: <user_topic>\n\nFocus on: <specific questions for this angle>\n\nReturn findings in this format:\n## <Angle Name>\n### Key Findings\n- ...\n### Sources\n- [Link](url)\n### Trade-offs & Considerations\n- ...\n\nWrite your findings to: <output_path>"
   )
   ```

   Output path: `/tmp/prd-research-<angle-slug>.md`

3. **Wait for all agents to complete** (bash polling):
   ```bash
   for i in $(seq 1 120); do
     COUNT=$(ls /tmp/prd-research-*.md 2>/dev/null | wc -l)
     [ "$COUNT" -ge <expected_count> ] && echo "ALL_DONE" && break
     sleep 2
   done
   ```
4. **Read all output files** and synthesize into a comprehensive research summary
5. **Present synthesized findings to user** — organized by angle, with key insights highlighted
6. **Clean up temp files:** `rm -f /tmp/prd-research-*.md`

**Cap:** Maximum 4 parallel agents, each limited to 5 search queries.

### Research Output

When research was performed (Standard or Deep), the findings are embedded in the PRD under a `## Research Findings` section after Key Decisions.
