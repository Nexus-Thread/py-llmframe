# Repository navigation guidelines for hexagonal Python projects

Use these guidelines to organize and navigate code in hexagonal Python projects.

## Standard directory structure

### Source layout pattern
Prefer a `src/<package_name>/` layout for libraries and reusable services. Smaller applications may use `<package_name>/` at the project root if packaging and test imports stay clear.

In monorepos, apply this mental model to each package or service, and keep entry points, tests, and docs discoverable near each package root.

```
src/<package_name>/
├── domain/                  # Core business logic
│   ├── entities/           # Domain entities
│   ├── value_objects/      # Immutable value objects
│   ├── services/           # Domain services
│   └── exceptions.py       # Domain-specific errors
├── application/            # Use cases and orchestration
│   ├── use_cases/          # Application use cases
│   ├── ports/              # Input/output ports (interfaces)
│   └── dtos/               # Command/query/result DTOs and other application boundary types
└── adapters/               # External system interfaces
    ├── input/              # Driving adapters (CLI, HTTP, GraphQL)
    └── output/             # Driven adapters (DB, APIs, messaging)
```

### Test layout pattern
```
tests/
├── unit/                   # Fast, isolated unit tests
│   ├── domain/            # Domain logic tests
│   ├── application/       # Use case tests
│   └── adapters/
│       ├── input/         # Driving adapter unit tests
│       └── output/        # Driven adapter unit tests
├── integration/           # Integration tests with I/O
│   └── adapters/
│       ├── input/         # Driving adapter integration tests
│       └── output/        # Driven adapter integration tests
└── e2e/                   # Optional end-to-end scenarios
```

Test directories should mirror the source structure where practical. `e2e/` may be organized by user flow instead of strict source mirroring.

## Documentation and configuration
- `README.md`: Project onboarding, setup, and usage
- `docs/`: Architecture decision records (ADRs), design docs
- `examples/`: Runnable code examples and integration snippets
- `pyproject.toml`: Primary package, build, dependency, and tool configuration
- `uv.lock`: Locked dependency state for the project

## Search workflow

Prefer cross-platform tools such as IDE search, `rg`, and `rg --files` for
local exploration.

For reusable command recipes and the step-by-step process for generating a
project-specific navigation guide, use `workflows/update-repo-navigation.md`.

## Navigation principles
- **Layer isolation**: Code in `domain/` should not import from `adapters/` or `application/`
- **Port discovery**: Look in `application/ports/` to understand system boundaries
- **DTO discovery**: Look in `application/dtos/` for command, query, and result types that define the application boundary
- **Entry points**: Find wiring and configuration in entry point files (`__main__.py`, `cli.py`, or framework-specific bootstrap modules)
- **Packaging clues**: Start with `pyproject.toml` and `uv.lock` to identify package roots, toolchain, and supported Python versions
- **Test mirroring**: Navigate tests using the same path as the source module under test
