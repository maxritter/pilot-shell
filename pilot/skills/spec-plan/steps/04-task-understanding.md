## Step 4: Task Understanding, Discuss & Clarify

1. Restate the task in your own words — core problem, assumptions
2. **Scope check:** Does this task describe multiple independent subsystems (e.g., "build chat, file storage, billing, and analytics")? If so, flag immediately — don't spend questions refining details of a task that needs decomposition first. Suggest splitting into separate plans, one per subsystem, each producing working software on its own. Proceed with the first sub-task.
3. Identify gray areas:

   | Domain      | Typical Gray Areas                                 |
   | ----------- | -------------------------------------------------- |
   | UI/frontend | Layout, interaction patterns, empty/loading states |
   | API/backend | Response shape, error codes, auth, pagination      |
   | CLI/scripts | Output format, flags, exit codes                   |
   | Data/config | Schema, migration, validation, defaults            |

4. **⛔ Code-first rule: ground every question in the Step 3 Workspace Scan output.** Before formulating a question, ask "can I answer this from the codebase?" If yes, do that instead — don't ask. For questions you do ask, **option labels must reference real files and symbols when the scan found them** — e.g., `Extend LicenseAuth in launcher/auth.py:42`, not `Extend existing module`. Only ask the user about decisions the code can't make — purpose, priority trade-offs, scope boundaries, behavioral expectations not yet encoded.

   - If `Greenfield?: yes` in the scan output, fall back to generic options and note the fallback under "Autonomous Decisions" in Step 9.
   - If the scan output names symbols/files relevant to a question, generic labels are a regression — use the names. Asking the user about facts already in the codebase, or asking with abstract options when grounded ones are available, is the single biggest source of unnecessary friction in planning.

5. **Ask Batch 1 questions** → notify, then use `AskUserQuestion` with each question as a separate entry with predefined options:

   ```bash
   ~/.pilot/bin/pilot notify plan_approval "Input Needed" "<plan_name> — clarification questions" --plan-path "<plan_path>" 2>/dev/null || true
   ```

   Each question must have 2-4 concrete options. Use `multiSelect: true` when choices aren't mutually exclusive.

   Even when the task seems clear, ask about: scope boundaries (what's explicitly out), priority trade-offs (speed vs completeness), or behavioral expectations (error handling, edge cases). **Only skip if the task is a trivial single-file change.**
