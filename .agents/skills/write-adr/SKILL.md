---
name: write-adr
description: Create an Architecture Decision Record with the next sequential number, a clear title, and documented consequences.
---

# Write an Architecture Decision Record (ADR)

Use this skill when the user asks to document an architectural decision,
record a design choice, or create an ADR.

## Goal

Create a new ADR in the ADR directory with the next sequential number, a clear
title, and a concise record of the decision and its consequences.

## Steps

### 1. Locate the ADR directory

Use an existing ADR directory if the repository already has one. Common names
include `adr/` and `docs/adr/`.

If no ADR directory exists, use `<adr_directory>` as a placeholder and create
it.

### 2. Determine the next ADR number

Inspect the files in the ADR directory, find the highest four-digit prefix, then
increment it by one.

- If no ADRs exist yet, start with `0001`.
- Example: if `0003-...` is the latest ADR, use `0004`.

### 3. Create the ADR file

Use this file name format:

`<adr_directory>/<NNNN>-<short-title-kebab-case>.md`

Example:

`<adr_directory>/0004-standardize-api-error-format.md`

Derive the slug from the ADR title by converting it to kebab-case and removing
unnecessary filler words when helpful.

### 4. Fill in the ADR template

Use today's date for the Date field.

```markdown
# <NNNN>. <Short Title in Title Case>

Date: <YYYY-MM-DD>
Status: Proposed | Accepted | Deprecated | Superseded by [NNNN](./<NNNN>-<slug>.md)

## Context

Describe the situation, constraints, and trade-offs that make this decision
necessary.

## Decision

State the decision clearly in one or two sentences. Prefer active voice, for
example: "We will use X because Y."

## Consequences

List the consequences. Use subsections such as Positive, Negative, and Neutral
when helpful. For simple decisions, a flat list is fine.

- ...

## Alternatives considered

Include this section when meaningful alternatives were evaluated. Omit it when
the decision follows an obvious convention or has no real alternatives.

| Option | Reason rejected |
| ------ | --------------- |
| ...    | ...             |
```

### 5. Set the status

Choose the status that matches the user's intent:

| Status                                     | Use when                                                  |
| ------------------------------------------ | --------------------------------------------------------- |
| `Proposed`                                 | The decision is still under discussion.                   |
| `Accepted`                                 | The decision has been agreed and is in effect.            |
| `Deprecated`                               | The decision was once accepted but is no longer followed. |
| `Superseded by [NNNN](./<NNNN>-<slug>.md)` | A newer ADR replaces it.                                  |

If the user does not specify a status, default to `Proposed`. Use `Accepted`
only when the user clearly indicates that the decision is already in effect.

### 6. Update or create the ADR index

If the ADR directory already contains an index file such as `README.md` or
`index.md`, update it.

- If it already contains an ADR table, append an entry such as:

```markdown
| [<NNNN>](./<NNNN>-<slug>.md) | <Short Title> | <Date> | <Status> |
```

- If an index file exists but does not yet contain an ADR table, add one.
- If no ADR index file exists, create one such as `README.md` with a header
  like:

```markdown
# Architecture Decision Records

| ADR                          | Title         | Date   | Status   |
| ---------------------------- | ------------- | ------ | -------- |
| [<NNNN>](./<NNNN>-<slug>.md) | <Short Title> | <Date> | <Status> |
```

## Good ADR practices

- Focus on why, not implementation details.
- Keep the context factual and specific.
- Record one decision per ADR.
- Keep the decision statement short and explicit.
- Link related ADRs, issues, or PRs when helpful.
- Do not delete old ADRs; deprecate or supersede them.
