Read the RFC at: `rfcs/$ARGUMENTS.md`

If there are no open questions with status `open`, state that no proposals are needed. Suggest running `/user:rfc-review $ARGUMENTS` if the RFC still feels incomplete.

For each open question (status: open):

1. Gather context from the codebase — read relevant files, check patterns, find precedents
2. Propose 2-3 options with:
   - **Option A/B/C:** one-line description
   - **Tradeoffs:** what you gain and lose
   - **Recommendation:** which option and why

Update the RFC file directly:
- Add options under each open question's `Options:` field
- Add your recommendation
- Do NOT change status to `resolved` — that's the human's call
- Do NOT delete or overwrite existing options — only append new ones
- If an option was already listed, skip it

After updating, print a summary of proposals made and any questions where you lacked sufficient context to propose good options.
