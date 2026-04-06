# CHANGELOG

<!-- version list -->

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


## Unreleased

- Breaking: remove legacy `llmframe.adapters.output.llm.openai_adapter` compatibility package; use `llmframe.adapters.output.llm.providers.openai` instead.

## v1.0.0 (2026-04-02)

- Initial Release
