Context: we just finished implementing (and fixing issues in) the RFC at: `rfcs/$ARGUMENTS.md`

Analyze what went wrong or was suboptimal during this RFC cycle:

1. **Read the RFC** — look at resolved questions, risks that materialized, steps that changed during implementation
2. **Read the git diff** — use the "Affected Modules / Files" list from the RFC to scope the diff. If the RFC was implemented on a feature branch, diff against the branch point. If on main, ask the user which commits belong to this RFC.
3. **Identify root causes** — for each bug fix or design change made during implementation:
   - What in the project docs, code comments, naming, or structure made this mistake possible?
   - Was it a missing invariant? Misleading name? Undocumented assumption? Absent test?

4. **Propose concrete fixes** (not vague "improve documentation"):
   - Specific doc updates (which file, what to add/change)
   - Code-level changes: rename, add assertion, add type constraint, add comment at the trap
   - Test additions that would catch this class of issue
   - CLAUDE.md or project CLAUDE.md updates if the pattern is general

5. **Apply the fixes** that are safe and obvious — changes to comments, doc files, CLAUDE.md, adding assertions/types, renaming for clarity. For architectural changes, new dependencies, or test strategy changes — list them and ask first.

The goal: the next RFC for a similar feature should not hit the same issues.
