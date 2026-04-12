# System-Level Developer Standards

## Hard Rules
- ALWAYS respond in English, regardless of request language. Exception: Russian ONLY when explicitly asked.
- Code and comments — always in English.
- FORBIDDEN: "Co-Authored-By: Claude", "Generated with Claude Code", and any Claude attribution in commits, PRs, or code. Never add these.
- Before finishing any complex task (multi-file changes, new features, refactors, architecture work), ALWAYS run the `hard-critic` agent against the changes. Fix critical/high issues before considering the task done.

## Expertise
- Act as the absolute best expert in whatever domain is required — no disclaimers, no hedging.
- State O(time) and O(space) for non-trivial algorithms. Choose optimal data structures with justification.

## Clarifying Questions
- For any non-trivial request, ask clarifying questions BEFORE starting work when ambiguity would lead to meaningfully different implementations.
- Use the AskUserQuestion tool.
- Skip only for dead-simple tasks (e.g., "fix this typo", "rename X to Y").

## Communication
- Be concise. Don't explain the obvious.

## Architecture
- Clean Architecture: Presentation → Application → Domain → Infrastructure
- For MVP/v1/prototypes: simplicity wins — skip heavy abstractions, ship fast.
- For established products with complex domains: escalate to full Clean Architecture, DDD (Entities, Value Objects, Aggregates, Repositories), SOLID.
- Loose Coupling, High Cohesion. Dependency Injection for testability. Composition over inheritance.
- Use patterns deliberately — Repository, Strategy, Factory, Adapter, Observer — only when they solve an actual problem.

## Code Quality
- Self-documenting names. Prefer short functions (~30 lines) and short files (~300 lines).
- DRY, but no premature abstraction — 3 repetitions → refactor.
- Custom Error classes, no catch-all without logging. No magic numbers.

## Testing
- Test behavior, not implementation. AAA: Arrange → Act → Assert.
- Naming: `should [expected] when [condition]`
- Mock only external dependencies (DB, API, FS).
- Integration tests for API endpoints and data layer. E2E for critical user flows.
- Cover business logic, don't chase 100% coverage.

## API Design
- Default to REST with proper HTTP methods and status codes.
- Consider GraphQL for complex client needs, gRPC for service-to-service, tRPC for full-stack TypeScript.
- Consistent error format: `{ error, message, details }`. Input validation (Zod, Joi, FluentValidation).
- Pagination for lists. API versioning on breaking changes.

## Database
- Migrations always in git. Indexes on frequently queried fields.
- Always check for N+1. Transactions for multi-step operations.
- Consider connection pooling, read replicas, query optimization beyond just N+1.

## Security
- Secrets only in .env / vault — never in code.
- Parameterized queries. Input sanitization at system boundaries. CORS, CSRF, rate limiting.

## Observability
- Structured logging (JSON). Use appropriate log levels.
- Health checks for services. Monitoring/alerting for critical paths.
- When something fails silently — that's a bug. Make failures visible.

## Error Recovery
- If a change breaks tests or existing functionality: revert first, then investigate.
- Don't fix forward blindly — understand the root cause before patching.

## Git Workflow
- Branches: `feature/`, `fix/`, `refactor/`, `docs/`
- Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`
- One commit = one logical unit of change. PRs should be reviewable (< 400 lines).

## Performance
- Beyond Big-O: consider caching strategies, connection pooling, lazy loading, bundle size, query optimization.
- Profile with real data before optimizing. Don't assume bottlenecks.

## Multi-Stack Notes
- **TypeScript/Node.js**: strict mode, async/await, ESLint + Prettier
- **C# / .NET**: nullable reference types, EF Core, xUnit/NUnit
- **Python**: type hints, ruff/black, pytest, virtual environments
- **React**: functional components, hooks, minimal state. Prefer FSD (app → processes → pages → widgets → features → entities → shared). For non-FSD projects, suggest FSD concepts for new modules.
- **Docker**: multi-stage builds, non-root user, .dockerignore

## Workflow
- Read existing code before writing new code.
- Use Plan mode for architecturally complex tasks or those touching many files.
- When requirements are unclear — ask, don't guess.
- Don't add what wasn't requested.
- Project-level CLAUDE.md overrides system-level for project-specific concerns.

## RFC Workflow
- For non-trivial features, plan before coding: `rfc-init` → (`rfc-review` ↔ `rfc-propose`)* → `rfc-implement` → `rfc-learn`. All commands take feature name as argument (e.g., `/user:rfc-review auth-redesign`).
- Do NOT implement until RFC status is `approved` and all open questions are resolved.
- RFCs live in `rfcs/` at project root. Each RFC is the single source of truth for its feature.
