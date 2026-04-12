Create an RFC document at `rfcs/$ARGUMENTS.md` in the current project root.

Before creating, check if the `rfcs/` directory exists — create it if not.

Use this exact template:

```markdown
# RFC: [Feature Name]

**Status:** draft
<!-- Valid statuses: draft | in-review | approved | implementing | done -->
**Author:** [name]
**Date:** [today]

## Problem Statement
What problem are we solving and why now?

## Non-Goals / Out of Scope
What this RFC explicitly does NOT address. Be specific — this prevents scope creep.

## Constraints
Performance budgets, compatibility requirements, deployment constraints, timeline, dependencies on other teams/systems.

## Proposed Solution
High-level approach. Why this approach over alternatives?

## Technical Design

### Affected Modules / Files
List specific files, modules, and their direct dependents that will be touched.

### Interfaces / Contracts
New or changed APIs, data structures, event contracts, DB schema changes.

### Data Flow
How data moves through the system for the key operations.

## Alternatives Considered
At least one alternative with reasoning for why it was rejected.

## Open Questions

### Q1: [question]
- **Status:** open
- **Options:**
- **Decision:**

## Risks & Rollback
What can go wrong? How do we detect it? How do we roll back?

## Implementation Plan
Ordered steps. Each step should be a single commit-sized unit of work.

1. [ ] Step description — affected files
```

After creating the file:
- Set Author using `git config user.name`. If unavailable, leave `[name]`
- Fill in what you can infer from the feature name
- Leave placeholders for what requires human input
- List 2-3 initial open questions based on ambiguities you can already see
- Check that `rfcs/` is not in `.gitignore`. If it is, warn the user
