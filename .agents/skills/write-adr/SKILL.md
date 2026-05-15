---
name: write-adr
description: Create an Architecture Decision Record with the next sequential number, a clear title, and documented consequences.
---

# Write an Architecture Decision Record (ADR)

Use this skill when the user asks to document an architectural decision, record
a design choice, or create an ADR. ADRs are for durable decisions, not routine
implementation notes.

## Goal

Create a new ADR in the ADR directory with the next sequential number, a clear
title, and a concise record of the decision and its consequences.

## Steps

### 1. Locate the ADR directory

Use the repository's existing ADR directory when one is present. Common names
include `adr/` and `docs/adr/`.

If no ADR directory exists, ask for the preferred location when that choice is
unclear. If the user has asked you to proceed without asking, use
`<adr_directory>` as a placeholder and create it.

### 2. Determine the next ADR number

Inspect Markdown files in the ADR directory, find the highest four-digit file
prefix, then increment it by one.

- If no ADRs exist yet, start with `0001`.
- Example: if `0003-...` is the latest ADR, use `0004`.

### 3. Create the ADR file

Use this file name format:

`<adr_directory>/<NNNN>-<short-title-kebab-case>.md`

Example:

`<adr_directory>/0004-standardize-api-error-format.md`

Derive the slug from the ADR title by converting it to kebab-case. Remove filler
words only when doing so keeps the title recognizable.

### 4. Fill in the ADR template

Use today's date for the Date field unless the user requests a different date.

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

- Focus on why and what was decided, not step-by-step implementation details.
- Keep the context factual and specific.
- Record one decision per ADR.
- Keep the decision statement short and explicit.
- Link related ADRs, issues, or PRs when helpful.
- Preserve existing ADR style when the repository already has a clear template.
- Do not delete old ADRs; deprecate or supersede them.
