---
name: python-add-env-settings-adapter
description: Add an environment-backed runtime settings adapter for a Python hexagonal app or library, including application DTOs, validation, and tests.
---

# Add an Environment Settings Adapter

Use this skill when a Python hexagonal application or library needs runtime
configuration loaded from environment variables or a `.env` file.

This skill captures a strong default pattern for an `env_settings_adapter`:

- the **application layer** owns the runtime settings DTO and any
  application-level configuration exception,
- the **input adapter** owns environment parsing, normalization, and
  validation,
- the adapter entry point is intentionally **thin** and only converts the
  validated adapter model into the application DTO,
- tests cover DTO defaults and adapter validation and normalization behavior.

Use this skill when the work spans both the application DTO and the input
adapter. If you only need to add an adapter to an existing configuration
boundary, `python-add-adapter` may be enough. If the configuration change
introduces a meaningful architectural decision, also use `write-adr`.

## Prerequisites

- The project follows a Python hexagonal layout with `src/<app_name>/`.
- The runtime configuration requirements are known well enough to identify:
  - required settings,
  - optional settings and defaults,
  - grouped or feature-flagged settings,
  - validation and normalization rules.
- The project either already uses `pydantic-settings` or the user has approved
  adding it as a dependency.

## Target structure

A typical result looks like this:

```text
src/<app_name>/
├── application/
│   ├── dtos/
│   │   ├── __init__.py
│   │   └── app_settings.py
│   └── exceptions.py
└── adapters/
    └── input/
        └── env_settings_adapter/
            ├── __init__.py
            ├── adapter.py
            └── settings.py

tests/unit/<app_name>/
├── application/dtos/test_app_settings.py
└── adapters/input/env_settings_adapter/test_env_settings.py
```

Adjust names if the project already has a better local convention, but keep the
same responsibilities and dependency direction.

Related skills:

- Use `python-add-adapter` when the configuration boundary already exists and
  you only need to implement or extend the adapter.
- Use `update-project-docs` when runtime configuration changes require README or
  operator-facing documentation updates.
- Use `write-adr` when the configuration approach or boundary is a durable
  architectural decision.

## Steps

### 1. Define the application-facing settings DTO

Create or update `src/<app_name>/application/dtos/app_settings.py`.

The DTO should:

- represent the runtime settings consumed by application services,
- use application/domain-friendly types such as `Path`, `Literal`, `Enum`,
  `int`, `float`, and `bool`,
- define defaults in the application layer so callers can rely on one canonical
  source of defaults,
- stay independent of `pydantic`, framework types, and environment libraries.

A good default pattern is an immutable dataclass:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_OUTPUT_DIR = Path("out")


@dataclass(frozen=True, slots=True)
class AppSettings:
    api_key: str
    log_level: str = "INFO"
    output_dir: Path = field(default_factory=lambda: DEFAULT_OUTPUT_DIR)
    debug_enabled: bool = False
```

Rules:

- Put defaults here, not in the adapter-facing environment model, unless the
  project has a strong reason to centralize them elsewhere.
- Use `field(default_factory=...)` for `Path` or other non-scalar defaults.
- Keep the DTO focused on runtime configuration, not transport-specific
  concerns.

### 2. Define an application-level configuration exception

If the project does not already have one, add a configuration-focused
application exception such as `ConfigurationError` in
`src/<app_name>/application/exceptions.py`.

The adapter should translate `pydantic` or environment-loading failures into
this application-level exception so the rest of the system does not depend on
adapter library exception types.

Example:

```python
class ApplicationError(Exception):
    """Base application-layer error."""


class ConfigurationError(ApplicationError):
    """Raised when runtime configuration is missing or invalid."""
```

### 3. Create the input adapter package

Create:

```text
src/<app_name>/adapters/input/env_settings_adapter/
    __init__.py
    adapter.py
    settings.py
```

Keep `__init__.py` lightweight:

```python
from .adapter import EnvSettingsAdapter

__all__ = ["EnvSettingsAdapter"]
```

Use a different exported adapter name only if the project already has a more
specific naming convention.

### 4. Implement the adapter-facing environment model in `settings.py`

Use `pydantic-settings` to define the external configuration surface.

Responsibilities of this module:

- declare environment variable names and descriptions,
- parse raw environment values,
- normalize strings, paths, enums, and similar inputs,
- validate allowed values and numeric constraints,
- validate grouped settings for optional features,
- convert `ValidationError` into a caller-friendly application exception.

A representative shape:

```python
from __future__ import annotations

from pathlib import Path

from pydantic import Field, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from <app_name>.application.exceptions import ConfigurationError


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )

    api_key: str = Field(alias="API_KEY")
    log_level: str | None = Field(default=None, alias="LOG_LEVEL")
    output_dir: Path | None = Field(default=None, alias="OUTPUT_DIR")
    debug_enabled: bool | None = Field(default=None, alias="DEBUG_ENABLED")

    @field_validator("api_key", "log_level", mode="before")
    @classmethod
    def validate_non_empty_text(cls, value: object) -> object:
        ...

    @model_validator(mode="after")
    def validate_feature_requirements(self) -> EnvSettings:
        ...
        return self


def load_settings_from_env() -> EnvSettings:
    try:
        return EnvSettings()
    except ValidationError as exc:
        raise ConfigurationError("Invalid configuration: ...") from exc
```

Rules:

- Keep `pydantic` and `pydantic-settings` imports in the adapter package.
- Use field aliases to expose the environment variable contract explicitly.
- Normalize blank strings before later validation so callers get clear errors.
- Prefer small helper functions for repeated normalization and grouped validation.
- Aggregate validation errors into a stable, readable message.
- Validate feature-flag bundles after parsing. Example: if
  `PUBLISH_ENABLED=true`, require `PUBLISH_BASE_URL` and `PUBLISH_TOKEN`.
- Ignore unrelated extra environment variables unless the project requires
  strict rejection.
- Keep environment-specific parsing and validation out of the application layer.

### 5. Keep `adapter.py` intentionally thin

`adapter.py` should convert the validated adapter-facing settings model into the
application DTO and nothing more.

Example:

```python
from <app_name>.application.dtos import AppSettings

from .settings import EnvSettings, load_settings_from_env


def _to_app_settings(settings: EnvSettings) -> AppSettings:
    return AppSettings(**settings.model_dump(exclude_none=True))


class EnvSettingsAdapter:
    """Load AppSettings from environment-backed settings."""

    def load(self) -> AppSettings:
        return _to_app_settings(load_settings_from_env())
```

Rules:

- Do not duplicate validation here.
- Do not put business logic here.
- Prefer `model_dump(exclude_none=True)` so the application DTO still applies
  its own defaults.
- Keep this adapter easy to test and easy to reuse from the composition root.

### 6. Wire the adapter at the composition root

Update the application entry point, CLI bootstrap, or framework startup code to
load `AppSettings` through the new adapter.

Typical flow:

1. instantiate `EnvSettingsAdapter`,
2. call `load()` once at startup,
3. pass the resulting `AppSettings` DTO into logging setup, service factories,
   and adapters that need runtime config.

Keep environment access centralized. Do not scatter `os.getenv()` calls across
the codebase once this adapter exists.

### 7. Test both DTO defaults and adapter behavior

Add or update unit tests.

#### DTO tests

Test the application DTO directly in
`tests/unit/<app_name>/application/dtos/test_app_settings.py`.

Cover at least:

- required fields,
- project defaults,
- preservation of explicit overrides,
- default `Path` or feature-flag behavior.

#### Adapter tests

Test `EnvSettingsAdapter` in
`tests/unit/<app_name>/adapters/input/env_settings_adapter/test_env_settings.py`.

Cover behaviors such as:

- missing required settings raises `ConfigurationError`,
- explicit env values override DTO defaults,
- blank strings are rejected or trimmed as intended,
- choice fields are normalized correctly,
- optional feature groups require complete configuration only when enabled,
- unset optional values allow DTO defaults to apply,
- path-like values are converted to `Path`.

Use `monkeypatch` to control environment variables. Keep tests deterministic and
isolated from the developer's real environment.

### 8. Update package exports and docs

If the project intentionally exposes the adapter or DTO at package level, update
the relevant `__init__.py` exports.

Update `README.md` when the runtime configuration surface changes. Document:

- required environment variables,
- important defaults,
- feature-flagged settings,
- `.env` support if present,
- any new dependency such as `pydantic-settings`.

If the change introduces a durable architectural decision, use `write-adr`.

### 9. Validate locally

Run the narrowest relevant tests first, then the full project quality gate.

Preferred order:

1. focused DTO and adapter tests,
2. `run-local-quality-gate` for full validation.

At minimum, final validation should satisfy the repository’s configured:

- `uv run ruff check .`
- `uv run mypy .`
- `uv run pytest`

## Design checklist

Before finishing, verify these architectural properties:

- Application code depends on `AppSettings`, not on `BaseSettings`.
- The adapter owns `pydantic-settings`, environment aliases, and parsing rules.
- DTO defaults live in the application layer and remain the canonical defaults.
- Validation errors are translated into an application exception.
- Feature-group requirements are enforced in one clear place.
- The composition root loads configuration once and passes the DTO inward.

## When to use a different approach

This pattern is a strong default, but adapt it when needed:

- For very small scripts or one-off tools, a full adapter package may be too
  heavy.
- For libraries, keep runtime configuration optional and avoid forcing `.env`
  loading unless the library truly owns process-level configuration.
- If configuration comes from files, secrets managers, or remote config sources
  instead of environment variables, keep the same application DTO boundary but
  implement a different input adapter.
