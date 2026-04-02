# CHANGELOG

<!-- version list -->

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
