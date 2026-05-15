---
name: add-hexagonal-feature
description: Implement a new feature or use case in a Python hexagonal project, including domain modeling, ports, application service, and tests.
---

# Add a Hexagonal Feature

Use this skill to implement a new feature, use case, or business capability in
a Python hexagonal project.

This skill focuses on the application and domain changes needed to add a use
case cleanly. It owns feature-level orchestration across domain,
application, and tests. When the change requires a new port or adapter, use the
specialized skill for that procedure instead of duplicating it here.

## Prerequisites

- The project already has the standard hexagonal `src/` layout.
- The feature is clear enough that you understand its inputs, outputs, and core
  business rules.
- The relevant input port already exists, or creating it is part of the same
  change through `python-add-port`.

## Steps

### 1. Name the use case

Choose a clear verb-noun name for the use case, for example `PlaceOrder`,
`RegisterUser`, or `SendNotification`. Use that name consistently for the
related files and classes.

### 2. Model the domain if needed

Create or update files under `src/<app_name>/domain/`:

- **Entity** — an object with identity that changes over time.
- **Value object** — an immutable descriptor (e.g. `EmailAddress`, `Money`).
- **Domain event** — something that happened (e.g. `OrderPlaced`).

Rules:

- Domain objects must be pure Python with no framework imports or I/O.
- Use `@dataclass(frozen=True)` for value objects.
- Raise domain-specific exceptions, not HTTP or database errors.

```python
# src/<app_name>/domain/<entity>.py
from dataclasses import dataclass

@dataclass
class <Entity>:
    id: str
```

### 3. Define or confirm the required ports

Identify the application boundaries the feature needs:

- an input port when an external caller invokes a new use case
- one or more output ports when the application needs infrastructure
  dependencies such as repositories, publishers, or gateways

If a required port does not exist yet, use `python-add-port` for the detailed
procedure. In this skill, keep the focus on deciding which boundaries the
feature needs. Input adapters should depend on input port contracts;
application services should satisfy those contracts and depend on output port
contracts for infrastructure.

If the use case needs command, query, or result objects, create or update them
under `src/<app_name>/application/dtos/`.

### 4. Implement the application service

Create the use case implementation under `src/<app_name>/application/use_cases/`:

```python
class <UseCaseName>:
    def __init__(self, repository: <EntityRepositoryPort>) -> None:
        self._repository = repository

    def execute(self, command: <Command>) -> <Result>:
        ...
```

Rules:

- The application service depends only on domain objects and port interfaces.
- If an input port exists for the use case, the application service must satisfy
  that contract.
- Keep command, query, and result DTOs under `application/dtos/` and use them at
  the application boundary when dedicated boundary types help clarify the use case.
- It must not import from `adapters/`.
- It must not perform I/O directly, including `open()`, HTTP calls, or database
  access.
- If the feature needs a new adapter implementation for an existing or new
  port, use `python-add-adapter` for that procedure.

### 5. Write unit tests

Create application-service tests under `tests/unit/application/`. If the change
adds or changes domain invariants, add or update domain tests under
`tests/unit/domain/` as well.

```python
class FakeRepository:
    def __init__(self) -> None:
        self.saved: list[object] = []

    def save(self, entity: object) -> None:
        self.saved.append(entity)

def test_<use_case_name>_happy_path() -> None:
    repo = FakeRepository()
    use_case = <UseCaseName>(repository=repo)
    use_case.execute(<Command>(...))
    assert len(repo.saved) == 1
```

TDD is encouraged when it fits the change. Writing tests before the
implementation is fine and often preferable.

- Prefer a hand-written fake for outbound ports. Use `MagicMock` only when a
  narrow interaction assertion is clearer than asserting on fake state.
- Cover the happy path and at least one failure or edge case.

## Dependency direction reminder

The canonical dependency rules are in `003-architecture-guardrails.md`. This
diagram is a quick reference only.

```
adapters/input   →  application  →  domain
adapters/output  →  (implements application/ports)
```

Never let an arrow point in the opposite direction.
