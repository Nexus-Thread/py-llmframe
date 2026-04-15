---
name: python-add-adapter
description: Add an input or output adapter to a Python hexagonal project while keeping business logic in the application layer.
---

# Add an Adapter

Add an input or output adapter to a Python hexagonal project while keeping business logic in the application layer.

This skill owns adapter implementation. If the required application boundary
does not exist yet, define the port first with `python-add-port`.

## Prerequisites

- The relevant port interface exists in `src/<app_name>/application/ports/`.
- The adapter technology has been chosen and any required library is installed (for example with `uv add <library>`).

If the port does not exist yet, use `python-add-port` before implementing the
adapter.

## Input adapter

An input adapter receives external input and calls the application through an input port or service entry point.

### 1. Create the module

```
src/<app_name>/adapters/input/<adapter_name>/
    __init__.py
    adapter.py
```

Keep `__init__.py` lightweight. Re-export the public symbol only when you want a stable package-level API, and declare `__all__` when it adds clarity:

```python
from .adapter import router

__all__ = ["router"]
```

### 2. Implement

- Accept external input and map it to an application command or query DTO.
- Call the application through its input port or service entry point.
- Map the result or exception back to the external format.
- Map domain or application exceptions to adapter-level error responses when
  they are part of the caller-visible boundary.
- Import domain types directly only when the port contract or exception mapping
  requires them; otherwise prefer application DTOs.
- Do not call domain services, repositories, or output adapters directly from
  the adapter.
- Keep all business logic in the application service.
- Update routing, framework registration, or other entry-point wiring so the
  adapter is reachable in the running system.

### 3. Test

Place transport-level tests under `tests/integration/adapters/input/<adapter_name>/`.
Test through the framework test client or transport boundary, injecting a fake
or stubbed application service to keep tests focused on adapter behavior.

Add unit tests under `tests/unit/adapters/input/<adapter_name>/` only when the
adapter contains meaningful mapping or serialization helpers that warrant
direct, framework-free verification.

## Output adapter

An output adapter implements a port interface and talks to external infrastructure.

### 1. Create the module

```
src/<app_name>/adapters/output/<adapter_name>/
    __init__.py
    adapter.py
```

Keep `__init__.py` lightweight. Re-export the public symbol only when you want a stable package-level API, and declare `__all__` when it adds clarity:

```python
from .adapter import <AdapterName>

__all__ = ["<AdapterName>"]
```

### 2. Implement

- Implement all port interface methods.
- Map infrastructure types to the domain or application types required by the
  port. Do not expose infrastructure types beyond the adapter boundary.
- Raise domain exceptions, not infrastructure exceptions.
- Keep framework clients, ORM models, serializers, and transport-specific configuration inside the adapter package.
- Update dependency injection, bootstrap, or composition-root wiring when the
  new adapter becomes part of the runtime path.

### 3. Test

Write unit tests under `tests/unit/adapters/output/<adapter_name>/` using fakes,
stubs, or mocks around the infrastructure boundary. Follow with integration
tests under `tests/integration/adapters/output/<adapter_name>/` when adapter
behavior depends on actual driver, network, or persistence integration.
