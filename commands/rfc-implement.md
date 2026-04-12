Read the RFC at: `rfcs/$ARGUMENTS.md`

**Pre-flight checks (do NOT skip):**
1. Verify RFC status is `approved` or `implementing`. If it's `draft` or `in-review`, STOP and tell the user.
2. Check that zero open questions have status `open`. If any exist, STOP and list them.
3. Read the Implementation Plan section.

**Implementation rules:**
- Follow the implementation plan step by step, in order
- After completing each step, check off the corresponding item in the RFC
- Update RFC status to `implementing` if it's `approved`
- Each step = one logical unit. If the next step depends on reviewing the result of the current one, stop and ask the user to confirm before proceeding (use AskUserQuestion).
- If you discover something the RFC didn't account for, do NOT silently work around it. Add it as a new open question in the RFC with status `open`, flag it to the user, and STOP.

**After all steps are complete:**
- Update RFC status to `done`
- Run the hard-critic agent against all changed files
- Fix critical/high issues before reporting completion
