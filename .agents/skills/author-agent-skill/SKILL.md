---
name: author-agent-skill
description: Create, update, or review Agent Skill directories and SKILL.md files for valid frontmatter, structure, portability, progressive disclosure, and validation readiness.
---

# Author Agent Skill

Use this skill when creating, updating, or reviewing an Agent Skill. The goal is
to keep each skill valid, easy for agents to discover, portable across projects,
and concise enough to load only the guidance needed for the task.

## When to use this skill

Use this skill when:

- creating a new skill directory
- editing an existing `SKILL.md`
- reviewing skill metadata, naming, or structure
- deciding what belongs in `scripts/`, `references/`, or `assets/`
- checking whether a skill remains reusable outside its current repository

## Steps

### 1. Confirm the skill purpose

Define the task the skill helps an agent perform. Prefer a focused workflow over
a broad collection of unrelated guidance.

Confirm:

- the user-facing task or decision the skill supports
- when an agent should use the skill
- whether the skill is generic, language-specific, framework-specific, or
  repository-specific
- whether examples and commands can stay portable

### 2. Choose a valid skill name

Use a short, descriptive, kebab-case directory name. The frontmatter `name` must
match the parent directory exactly.

The name must:

- be 1 to 64 characters
- use only lowercase letters, numbers, and hyphens
- not start or end with a hyphen
- not contain consecutive hyphens

Prefer action-oriented names such as `write-adr`, `run-local-quality-gate`, or
`author-agent-skill`.

### 3. Add required frontmatter

`SKILL.md` must start on the first line with YAML frontmatter. Include `name`
and `description`.

Use this minimal shape:

```md
---
name: skill-name
description: Brief description of what the skill does and when to use it.
---
```

The description should explain both:

- what the skill helps with
- when an agent should use it

Keep the description non-empty, specific, and no longer than 1024 characters.

### 4. Use only supported optional frontmatter fields

Add optional fields only when they are useful and supported by the skill format.

Supported optional fields are:

- `license`
- `compatibility`
- `metadata`
- `allowed-tools`

Do not add custom frontmatter fields unless the target skill system or repository
tooling explicitly requires them.

### 5. Structure the skill body

After frontmatter, include one top-level heading that names the skill in a
human-readable form.

A practical structure is:

```md
---
name: skill-name
description: Brief description of what the skill does and when to use it.
---

# Skill Name

Short explanation of when and why to use the skill.

## Steps

1. First action
2. Second action
3. Validation or handoff action
```

Use section headings only when they improve navigation. Use `## Steps` for a
repeatable workflow.

### 6. Apply progressive disclosure

Keep the main `SKILL.md` concise and self-contained. Move detailed or rarely used
material into optional directories when needed:

- `scripts/` for executable helper code
- `references/` for focused supporting documentation
- `assets/` for templates, static files, schemas, or examples

When referencing supporting files, use relative paths from the skill root. Prefer
simple one-level references where practical.

### 7. Keep reusable skills portable

For reusable skills, avoid local repository paths, private project names, local
usernames, or commands that only make sense in one repository.

Prefer placeholders such as:

- `<package_name>`
- `<app_name>`
- `<repo_name>`
- `<python_version>`

If a section must be repository-specific, label it clearly so readers can tell it
is not part of the portable guidance.

### 8. Keep formatting plain

Use plain Markdown that improves navigation and correctness. Avoid emojis,
decorative separators, banners, ornamental callouts, and visual-only formatting.

Prefer:

- concise headings
- short paragraphs
- simple bullet lists
- minimal examples in fenced code blocks

### 9. Validate before handoff

Run the repository's skill or documentation validation command when available. If
the target environment provides an Agent Skills validator, use it for the changed
skill directory.

When no validator is available, manually check the review checklist below.

## Review checklist

- `SKILL.md` exists in the skill directory
- frontmatter starts at the first line
- frontmatter includes `name` and `description`
- `name` matches the parent directory exactly
- `name` is valid kebab-case
- unsupported frontmatter fields are absent
- a single top-level heading follows the frontmatter
- instructions explain when and how to use the skill
- examples are generic and portable unless clearly marked otherwise
- optional `scripts/`, `references/`, and `assets/` content is necessary and
  referenced clearly
- formatting is plain and free of decorative noise
- validation was run or any skipped validation is documented
