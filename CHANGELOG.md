# CHANGELOG

<!-- version list -->

## v2.5.1 (2026-04-08)

### Bug Fixes

- **ci**: Pin setup-uv action to v7 for workflow stability
  ([`93b0b52`](https://github.com/Nexus-Thread/py-llmframe/commit/93b0b529cc79b058a0be19c5124e8da78f9bc958))

### Chores

- **ci**: Bump GitHub Actions in workflow configs
  ([`5b05a55`](https://github.com/Nexus-Thread/py-llmframe/commit/5b05a55f97ac29d2ddbe1f144138e4ec96ebb6e1))

### Continuous Integration

- Add manual workflow for OpenAI live integration tests
  ([`970fa13`](https://github.com/Nexus-Thread/py-llmframe/commit/970fa133bf51543e11c99ceeed9d35e1d6ecd278))


## v2.5.0 (2026-04-08)

### Features

- **batch**: Persist submitted batch metadata to disk
  ([`0d23c9b`](https://github.com/Nexus-Thread/py-llmframe/commit/0d23c9b66e8a5b98134f16f5e83997542d3c3609))

### Testing

- Add opt-in live OpenAI integration coverage
  ([`d781f32`](https://github.com/Nexus-Thread/py-llmframe/commit/d781f323e677affd42cab506b20a49cd13299af2))


## v2.4.0 (2026-04-08)

### Features

- Add OpenAI Responses batch support to adapter
  ([`3f76219`](https://github.com/Nexus-Thread/py-llmframe/commit/3f76219a2c0b5b1b00a293e6748de89f6bd0607b))


## v2.3.0 (2026-04-07)

### Features

- Expand public package exports for core API
  ([`664836e`](https://github.com/Nexus-Thread/py-llmframe/commit/664836ead5a5cd59ab7499421ea2cdc390e94f06))


## v2.2.0 (2026-04-07)

### Chores

- Bump llmframe version to 2.1.0
  ([`422ba72`](https://github.com/Nexus-Thread/py-llmframe/commit/422ba72eef02023dc651b1f43326d8951a90a66c))

- **release**: Remove changelog generation from semantic release
  ([`09bf6e1`](https://github.com/Nexus-Thread/py-llmframe/commit/09bf6e1f69f302c77ff1a36993e5285f0247ffaa))

### Documentation

- Move maintainer guidance from README to docs
  ([`9834912`](https://github.com/Nexus-Thread/py-llmframe/commit/983491232c9694b6c82167f732d17c39f3e140d6))

### Features

- Add JSON debug writer and developer Makefile
  ([`0ce9e41`](https://github.com/Nexus-Thread/py-llmframe/commit/0ce9e419612dedb49bb9e5c7454d83fc09c37204))

### Refactoring

- **llm**: Make usage tracker provider-agnostic
  ([`432f7d4`](https://github.com/Nexus-Thread/py-llmframe/commit/432f7d459b67eae62e5ce5e478279f8dfe193f27))

- **llm-adapter**: Centralize structured output config
  ([`e2fb5c6`](https://github.com/Nexus-Thread/py-llmframe/commit/e2fb5c6e8efd5372c82a8ccfd2d6266402fc61a4))

- **openai**: Encapsulate transport casts and tighten typing
  ([`7a7e16a`](https://github.com/Nexus-Thread/py-llmframe/commit/7a7e16aa499835a1bd437466559ed513f6c6b4a0))


## v2.1.0 (2026-04-07)

### Documentation

- **shared**: Clarify shared type module docstrings
  ([`a855476`](https://github.com/Nexus-Thread/py-llmframe/commit/a85547659c5ce60aceef28e0c1f8dcf2f67db608))

### Features

- **application**: Export LLM port type aliases
  ([`a5b0a0b`](https://github.com/Nexus-Thread/py-llmframe/commit/a5b0a0b5eef89af19b38b0eeaa4046c5d2faf77e))


## v2.0.1 (2026-04-06)

### Bug Fixes

- Bump version
  ([`d843451`](https://github.com/Nexus-Thread/py-llmframe/commit/d8434513199cf0e62db6c812f43777351f10c6bc))

### Chores

- **release**: Sync semantic-release with pyproject version
  ([`78d353f`](https://github.com/Nexus-Thread/py-llmframe/commit/78d353f514ace8f25725bf4bb2720d858dfed1ef))

- **scripts**: Add clinerules sync helper
  ([`952d001`](https://github.com/Nexus-Thread/py-llmframe/commit/952d001277551777efa23103a9fa71658fdeaba9))

### Refactoring

- **llm**: Make provider boundary explicit and document OpenAI-first support
  ([`89a986a`](https://github.com/Nexus-Thread/py-llmframe/commit/89a986a6bbcf436e79d4be56c4cb5aa67d4e54ac))


## v2.0.0 (2026-04-02)

### Continuous Integration

- Add Python version matrix tests to CI workflow
  ([`6e9d38e`](https://github.com/Nexus-Thread/py-llmframe/commit/6e9d38edcb1f2572fb9d92a96a82c223cbe31ab2))

### Refactoring

- Remove legacy OpenAI adapter compatibility shim
  ([`81273ef`](https://github.com/Nexus-Thread/py-llmframe/commit/81273ef03ad3630b37d83202895aa07ef026f21a))

- **llm**: Reorganize OpenAI adapter into provider module
  ([`b65ad3b`](https://github.com/Nexus-Thread/py-llmframe/commit/b65ad3b0d00fee96dde657292dbf7e21bdd26d09))


## v1.0.0 (2026-04-02)

- Initial Release
