# Workflow: update repo navigation

Use this workflow when adapting the reusable hexagonal Python rules to a specific project.

## Goal

Produce a short, project-specific navigation guide outside `.clinerules/` so contributors can quickly find package roots, entry points, adapters, and tests.

When documenting reusable navigation workflows, prefer cross-platform examples based on IDE search or `rg`/`rg --files`.

## Recommended output location

- `docs/repo-navigation.md`
- or another discoverable project-owned path near the main developer docs

## Steps

1. Identify the package root (`src/<package_name>/` or the top-level package directory).
2. Locate entry points and composition-root/bootstrap files (`__main__.py`, `cli.py`, ASGI/WSGI app factories, worker startup modules, etc.).
3. Map the hexagonal layers:
   - `domain/`
   - `application/use_cases/`
   - `application/ports/`
   - `application/dtos/`
   - `adapters/input/`
   - `adapters/output/`
   - shared infrastructure or bootstrap modules, if present
4. Map the test layout (`tests/unit/domain/`, `tests/unit/application/`, `tests/unit/adapters/`, `tests/integration/adapters/`, `tests/e2e/`, shared fixtures, contract tests).
5. Record the most useful project-specific search commands for ports, adapters, entry points, and tests.
6. Save the navigation guide outside `.clinerules/` and update it whenever the structure changes significantly.

## Suggested template

```md
# Project navigation

## Package roots

- `src/<package_name>/`

## Entry points / composition root

- `src/<package_name>/cli.py`
- `src/<package_name>/bootstrap.py`

## Domain

- `src/<package_name>/domain/`

## Application

- `src/<package_name>/application/`
  - `src/<package_name>/application/use_cases/`
  - `src/<package_name>/application/ports/`
  - `src/<package_name>/application/dtos/`

## Adapters

- Input: `src/<package_name>/adapters/input/`
- Output: `src/<package_name>/adapters/output/`

## Tests

- Unit: `tests/unit/domain/`, `tests/unit/application/`, `tests/unit/adapters/`
- Integration: `tests/integration/adapters/`
- E2E: `tests/e2e/`

## Useful search commands

- `rg "Protocol|ABC|abstractmethod" src/<package_name>/application/ports/`
- `rg --files src/<package_name>/application/dtos/`
- `rg --files src/<package_name>/adapters/ | rg "(^|/)(adapter\.py|.*_adapter\.py)$"`
- `rg --files -g "pyproject.toml"`
- `rg --files src/<package_name>/ | rg "(^|/)(__main__|cli)\.py$"`
```
