---
name: update-project-docs
description: Update README, changelog-style notes, and related project-facing documentation after a Python change.
---

# Update Project Docs

Use this skill when a change affects user-visible behavior, configuration,
operations, or developer workflows and the project-facing documentation must be
kept in sync.

## When to use this skill

Use this skill when you need to update:

- `README.md`
- release-facing notes such as `CHANGELOG.md`
- operator or contributor docs under `docs/`
- usage examples for new commands, flags, or configuration

Use `write-adr` instead when the main task is recording an architectural
decision rather than updating usage or operational documentation.

## Steps

### 1. Identify the caller-visible change

List what changed from a reader's perspective, for example:

- a new command, flag, or workflow
- a new environment variable or configuration default
- a changed setup step or dependency workflow
- a new operational concern such as alerts, troubleshooting, or dashboards
- a breaking change, migration, or rollback concern

If the change is not caller-visible, keep documentation updates minimal.

### 2. Update the README when required

Check whether the change affects:

- installation or setup
- local development workflow
- runtime configuration
- how to use the application or interface
- troubleshooting or operational expectations

Update only the affected sections. Prefer short, concrete edits over broad
rewrites.

### 3. Add or adjust examples

Add a short example when it improves comprehension, such as:

- a CLI invocation
- a config snippet
- a short workflow command sequence

Keep examples minimal, directly relevant, and consistent with the real system.

### 4. Handle changelog-style notes

If the project maintains `CHANGELOG.md`, add or update the relevant entry.

If no changelog file exists, prepare a concise changelog-style summary for PR or
handoff notes that covers:

- what changed
- whether it is breaking
- what a user or operator needs to do

### 5. Cover configuration changes explicitly

If the change introduces or modifies configuration, document:

- variable or setting name
- expected type or format
- default value or absence semantics
- where it is used
- whether existing users need to change anything

### 6. Add operational notes when relevant

When the change affects operations, document the practical details, such as:

- new alerts or dashboards
- new failure modes
- troubleshooting steps
- rollout, migration, or rollback guidance

### 7. Keep architectural rationale in the right place

If the documentation update starts to explain a durable architectural decision,
use `write-adr` to record that rationale and keep the README or ops docs focused
on usage and consequences.

## Output checklist

- README updated where behavior or usage changed
- configuration documented clearly
- examples kept short and accurate
- changelog-style note captured when release-facing
- ADR used when the change is architectural rather than purely operational
