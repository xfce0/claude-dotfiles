Read the RFC at: `rfcs/$ARGUMENTS.md`

Do NOT implement anything. Your job is adversarial review.
You MAY edit the RFC file to add new open questions (Step 3) and update status, but you must NOT change any other content.

**Step 0 — Status transition:**
If RFC status is `draft`, update it to `in-review`.

**Step 1 — Scoped codebase check:**
- Read every file listed in "Affected Modules / Files"
- Check their direct imports/dependents (one level deep)
- If the section is empty or missing, flag that as the first issue

**Step 2 — Review checklist:**
For each item, state PASS or FAIL with a one-line reason:
- Problem statement is specific (not "improve X" — what exactly is broken/missing?)
- Non-goals are defined and meaningful
- Constraints are concrete (numbers, not "should be fast")
- Affected modules list is complete — no files that should be listed are missing
- Interfaces/contracts are fully specified (types, error cases, edge cases)
- No conflicts with existing code patterns or conventions
- Implementation steps are concrete and ordered (not "handle edge cases")
- Risks section addresses at least: failure detection, rollback, data migration (if applicable)

**Step 3 — Open questions:**
- List new questions you found (add them to the RFC's Open Questions section with status: open)
- For existing open questions, note if you have enough context to propose solutions

**Step 4 — Exit criteria check:**
State whether this RFC is ready for implementation:
- Zero open questions with status `open`
- All affected interfaces fully specified
- All implementation steps are concrete
If NOT ready, summarize what's blocking.
If ready (all criteria pass), update RFC status to `approved`.
