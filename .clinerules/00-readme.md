# How this ruleset is structured

## Structure and ordering
- Files in `.clinerules/` are **active** rules.
- This ruleset is an **opinionated reusable profile** for Python projects using hexagonal architecture with Cline.
- Rule files use sortable prefixes (for example `00-`, `01-`, `02-`, `03-`) to keep the reading order stable.
- Each file should focus on a single theme (core standards, architecture, testing, etc.).

## Opinionated defaults
- This ruleset is intentionally opinionated.
- Use `uv` for dependency management, environment management, and command execution.
- Use `ruff` for formatting, linting, and import cleanup.
- Use `mypy` for type checking.
- Use `pytest` for automated tests.
- Use `pytest-asyncio` for async tests when async code is present.
- Use Google-style docstrings.
- Use `pyproject.toml` and `uv.lock` as the canonical tooling and dependency configuration surface.
- Prefer dependency groups for development-only tooling and test dependencies.
- Use `application/dtos/` as the default home for command, query, and result DTOs in the application layer.
- Follow hexagonal architecture with inward-pointing dependencies and explicit ports/adapters boundaries.

## Rule precedence and conflict resolution
- Treat rules marked as **hard constraints** or **non-negotiable** as highest priority within `.clinerules/`.
- Explicit overrides beat implicit interpretation. When a later module intentionally sharpens an earlier rule, it should say so directly.
- More specific rules take precedence over broader rules on the same topic.
- **Must** statements take precedence over **Should** statements.
- If two rules with the same strength and scope still conflict, use file order only as a **last-resort tiebreaker**, then update the ruleset to make precedence explicit.
- Any intentional deviation must be documented in ADR/PR notes.

## Reusable-asset portability
- Keep this ruleset copyable into another repository without assuming a specific local folder workflow beyond `.clinerules/` itself.
- Do not require repository-specific maintenance conventions such as sibling "bank," "disabled," or archive folders inside reusable rule content.
- If a host repository wants local enable/disable mechanics, document them in repo-specific maintainer docs rather than in the reusable rules themselves.

## Adding or updating rules
- Prefer **small, focused** rule files rather than large monoliths.
- Use **Must/Should** language for clarity and consistency.
- When adding a new module, update this README and keep the sortable prefix order obvious and stable.

## Rule authoring standards
- Keep each module focused on one primary topic with a clearly implied owner.
- Avoid restating requirements owned by another module unless the later module is adding stricter or more specific constraints.
- Prefer one requirement per bullet so review discussions can reference a single rule precisely.
- Use **Must** only for review-blocking requirements.
- Use **Should** for strong defaults that may allow justified exceptions.
- When step-by-step guidance already exists in a skill, keep the rule focused on policy and reference the skill by name.
- When a later module intentionally overrides or sharpens an earlier rule, make that override explicit.

## Ownership and specialization
- Earlier files should define broad policy and defaults for their topic.
- Later specialized files should define detailed mechanics for narrower subtopics.
- When a specialized file exists, earlier files should point to it instead of repeating detailed guidance.
- Use skills for reusable procedures instead of embedding that guidance in rule files.

### Topic ownership map
- `01-cline-operating-guidance.md`: lightweight Cline operating behavior, scope control, and validation discipline
- `02-core-standards.md`: universal coding behavior, typing defaults, DTO boundary guidance, error handling, and baseline logging policy
- `03-architecture-guardrails.md`: architecture boundaries, dependency direction, and ports/adapters responsibilities
- `04-testing-standards.md`: automated testing expectations; detailed pytest mechanics belong in `write-pytest-tests`
- `05-docs-and-adr.md`: required project documentation outside source code; concrete update workflow belongs in `update-project-docs`
- `06-module-structure.md`: file, package, and export mechanics; restructuring workflow belongs in `split-python-module`
- `07-performance-and-observability.md`: performance expectations and runtime visibility; concrete instrumentation workflow belongs in `add-observability`
- `08-repo-navigation.md`: project discovery, canonical layout, and navigation principles; command recipes belong in `workflows/update-repo-navigation.md`
- `09-pr-and-commit-hygiene.md`: review and change-management discipline
- `10-tooling-and-ci.md`: dependency-group, local quality gate, and CI policy; command sequencing belongs in quality-gate skills
- `11-documentation-standards.md`: in-code documentation policy; drafting mechanics belong in `write-python-docstrings`
- `12-logging-conventions.md`: logging implementation mechanics and privacy-safe logging details
- `13-command-execution-safety.md`: command execution and process safety

## Active modules
- `01-cline-operating-guidance.md` - Read before editing, make minimal changes, validate proportionally, and avoid unrelated churn
- `02-core-standards.md` - Naming, formatting, typing defaults, DTO guidance, error handling, baseline logging policy
- `03-architecture-guardrails.md` - Hexagonal architecture doctrine, ports/adapters boundaries, adapter directory structure
- `04-testing-standards.md` - Testing pyramid, isolation requirements, and review-blocking testing policy
- `05-docs-and-adr.md` - Documentation obligations, ADR triggers, and changelog policy
- `06-module-structure.md` - File organization, splitting rules, and `__init__.py` conventions
- `07-performance-and-observability.md` - Performance, tracing, metrics, and observability policy
- `08-repo-navigation.md` - Generic navigation guidelines for hexagonal architecture, including canonical application and test layout
- `09-pr-and-commit-hygiene.md` - PR size, commit messages, reviews
- `10-tooling-and-ci.md` - `uv` dependency-group, validation policy, and CI expectations
- `11-documentation-standards.md` - Clear, concise docstrings and comments policy
- `12-logging-conventions.md` - Module-level logger standard, structured context, and safe redaction practices
- `13-command-execution-safety.md` - Hard ban on inline interpreter heredocs; require temp scripts and non-interactive git usage

## Workflows
- `workflows/update-repo-navigation.md` - Generate project-specific navigation maps when adapting this reusable ruleset to a concrete project
- `workflows/improve.md` - Focused improvement workflow; mirrors `shared/clinerules/workflows/improve.md` and is included here for drop-in portability

## Related skills

Skills should own focused procedures. When one skill needs a neighboring task, reference the related skill by name and decision context instead of repeating the full procedure. Keep those references portable and optional unless a dependency is truly mandatory.

Prefer short inline references inside the relevant step. Add a dedicated `Related skills` section only when a skill has several common handoffs that would otherwise be hard to discover.

### Skill relationship index
- `bootstrap-python-app` - Initialize a new Python hexagonal project with base tooling and structure
- `add-hexagonal-feature` - Add an end-to-end use case across domain, application, and tests
- `python-add-port` - Define a focused input or output port contract in the application layer
- `python-add-adapter` - Implement an input or output adapter against an existing port
- `update-project-docs` - Update README, changelog-style notes, and related project-facing docs after a change
- `split-python-module` - Safely split a large Python module or package while preserving boundaries and intentional imports
- `add-observability` - Add profiling, metrics, tracing, and operational notes for meaningful workflows
- `write-python-docstrings` - Write concise Google-style docstrings and inline comments where they add value
- `write-adr` - Record significant architectural decisions and consequences
- `format-python-code` - Formats Python code using ruff and applies safe auto-fixes
- `lint-python-code` - Lints Python code using ruff and mypy for type checking
- `write-pytest-tests` - Writes or refactors Python tests in clear, pytest-native style
- `run-python-tests` - Runs automated tests for a Python project using pytest
- `run-local-quality-gate` - Orchestrates the execution of Python code formatting, linting, type checking, and testing

### Typical delegation patterns
- From `bootstrap-python-app`
  - use `add-hexagonal-feature` when the project is ready for the first use case
  - use `python-add-port` when defining a new boundary before feature implementation
  - use `python-add-adapter` when connecting infrastructure or transports
  - use `update-project-docs` when setup changes require README or developer-doc updates
  - use `write-adr` when setup choices need durable documentation
- From `add-hexagonal-feature`
  - use `write-pytest-tests` when the feature needs new or revised pytest coverage
  - use `python-add-port` when the feature needs a new application boundary
  - use `python-add-adapter` when the feature needs an input or output adapter
  - use `update-project-docs` when the feature changes README-visible behavior or configuration
  - use `add-observability` when the feature adds a critical path that needs metrics, tracing, or troubleshooting notes
  - use `write-python-docstrings` when new public APIs or non-obvious contracts need in-code documentation
  - use `write-adr` when the feature introduces a meaningful architectural decision
- From `python-add-port`
  - use `add-hexagonal-feature` when the work is broader than defining the port
  - use `python-add-adapter` when an adapter must implement the new contract
  - use `write-adr` when boundary design needs explicit rationale
- From `python-add-adapter`
  - use `python-add-port` when the required boundary does not exist yet
  - use `add-hexagonal-feature` when adapter work is part of a full use case change
  - use `write-pytest-tests` when the adapter needs focused pytest coverage
  - use `add-observability` when the adapter adds important I/O, retries, or operator-visible failure modes
  - use `update-project-docs` when the adapter changes external configuration or usage
  - use `write-adr` when integration choices should be documented
- From `split-python-module`
  - use `write-python-docstrings` when the split creates new public modules or package surfaces
  - use `update-project-docs` when the split changes public import paths or developer-facing structure docs
- From `update-project-docs`
  - use `write-adr` when the documentation update reflects an architectural decision rather than only usage or operations guidance
- From `add-observability`
  - use `update-project-docs` when new alerts, dashboards, or troubleshooting notes need durable operator-facing documentation
- From `write-pytest-tests`
  - use `run-python-tests` to execute focused tests during iteration and the full suite before handoff
- From `write-adr`
  - use it as a documentation companion to feature, port, adapter, or bootstrap work when decisions have lasting architectural impact
- From `run-local-quality-gate`
  - use `format-python-code` to apply auto-fixes and format the codebase
  - use `lint-python-code` to perform linting and type checking
  - use `run-python-tests` to execute all automated tests

## Enforcement and automation matrix
Use this map to keep "Must" rules enforceable rather than merely advisory.

Interpret enforcement labels as follows:
- **Tool-enforced**: verified directly by automated tooling.
- **Review-enforced**: verified primarily in code review.
- **Process-enforced**: verified through operating discipline when tools cannot reliably enforce the rule.

| Rule area | Primary enforcement | Secondary enforcement |
| --- | --- | --- |
| Naming, formatting, imports | `uv run ruff check . --fix`, `uv run ruff format .`, `uv run ruff check .` | PR review |
| Type contracts and API drift | `uv run mypy .` | PR review |
| Behavior changes and regressions | `uv run pytest` | Targeted regression and contract tests |
| Architecture boundaries (hexagonal) | Review-enforced against `03-architecture-guardrails.md` | Optional import-lint/custom boundary scripts |
| Module/file structure conventions | Review-enforced against `06-module-structure.md` | Optional project audit script |
| Docs/ADR/changelog updates | Review-enforced via PR checklist | Release checklist |
| Logging conventions | Review-enforced against `12-logging-conventions.md` | Runtime log sampling |
| Command execution safety | Process-enforced (no `python - <<'PY'` patterns; git `--no-pager`/non-interactive) | PR review |

## Rules-to-enforcement alignment
- Hard constraints should be backed by tool enforcement where practical; otherwise, mark them as review-enforced or process-enforced.
- If automation cannot fully enforce a rule, write the rule so a reviewer can still evaluate compliance consistently.
- Keep rule text, examples, and tooling configuration aligned. When they differ intentionally, document the reason in the relevant rule file or PR notes.

## Scope
These rules apply to Python projects using hexagonal architecture unless explicitly stated otherwise.

## Project-specific customization
For project-specific navigation and structure details:
1. Use the workflow in `workflows/update-repo-navigation.md` to generate a current map, or follow the same steps manually if the workflow file is not bundled.
2. Store project-specific documentation in `docs/` or the project root.
3. Keep `.clinerules/` generic and portable across projects.
