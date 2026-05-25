---
name: review-implementation-plan
description: Review an implementation plan for completeness, ambiguity, sequencing, risks, dependencies, validation, and handoff readiness before coding.
---

# Review Implementation Plan

Use this skill before implementation begins when the user provides or requests a
plan for a non-trivial change. The goal is to catch ambiguity, missing work,
unsafe sequencing, and validation gaps before code or content changes begin.

## When to use this skill

Use this skill when:

- a plan spans multiple files, modules, systems, or teams
- implementation order affects safety or reviewability
- dependencies, migrations, data changes, or compatibility risks exist
- testing and validation strategy need to be explicit
- the user asks for deep planning, audit, or review before coding

For simple one-file edits, use only the relevant parts and keep the review brief.

## Steps

### 1. Confirm the goal and scope

Restate the requested outcome in concrete terms. Identify:

- what will change
- what will not change
- who or what is affected
- assumptions that need confirmation
- constraints from architecture, compatibility, policy, or tooling

Ask clarifying questions before implementation when scope or constraints are
unclear.

### 2. Check file and ownership specificity

A good plan should identify the likely files, modules, components, or documents
that need work. For each important target, check whether the plan explains:

- why it is in scope
- what kind of change is expected
- whether it is source, generated, synced, or derived content
- whether there are ownership or portability constraints
- whether another source of truth should be edited instead

### 3. Check interface and dependency impact

Review whether the plan accounts for affected public surfaces, contracts, and
callers.

Look for:

- API, command, schema, event, configuration, or data format changes
- dependency additions, removals, or version constraints
- migration, compatibility, or rollback implications
- generated files, documentation, or examples that must stay aligned
- security, privacy, or operational implications

### 4. Check sequencing and reviewability

Ensure the implementation order reduces risk and keeps review manageable.

Prefer sequences that:

1. establish or confirm source-of-truth decisions
2. add tests or validation coverage where useful
3. make the smallest coherent implementation changes
4. update docs, generated files, and metadata
5. run focused validation before broader validation
6. summarize deferred work explicitly

Flag plans that mix unrelated refactors with behavior changes or attempt too much
in one pass.

### 5. Check test and validation strategy

Verify that the plan names the checks that prove the work is complete. Consider:

- unit, integration, end-to-end, contract, snapshot, or manual checks
- linting, formatting, type checking, static analysis, build, or docs checks
- migration or compatibility validation
- failure cases and regression coverage
- what to do if an expected check is unavailable

A plan should distinguish focused iteration checks from final handoff checks.

### 6. Check risks and fallback options

Identify material risks and how the implementation should respond.

Common risks include:

- unclear ownership or source of truth
- accidental breaking changes
- large review surface
- flaky or expensive validation
- hidden generated artifacts
- data loss, security, privacy, or operational exposure

For each significant risk, note a mitigation, fallback, or question.

### 7. Produce a plan review summary

Return a concise review that includes:

- readiness assessment
- required clarifying questions, if any
- missing or weak plan sections
- recommended implementation order changes
- required validation commands or checks
- deferred backlog items that should not block the first pass

Do not begin implementation until required questions are answered and the user has
approved moving from planning to execution.

## Output checklist

- goal, scope, and non-goals are clear
- target files or modules are specific enough to act on
- dependencies and public interfaces are accounted for
- implementation sequence is reviewable
- validation strategy is explicit
- risks, fallback options, and deferred work are documented
