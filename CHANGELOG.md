# CHANGELOG

<!-- version list -->

## v3.1.0 (2026-05-25)

### Continuous Integration

- Update upload-artifact action pin in test workflow
  ([`85e6bcb`](https://github.com/Nexus-Thread/py-llmframe/commit/85e6bcbf9e369dd70fd266f6fe9306b8e20de510))

### Features

- **agents**: Add reusable agent authoring skill docs
  ([`605b7ac`](https://github.com/Nexus-Thread/py-llmframe/commit/605b7acf4d31704e7f9abd9c54e8c361b054c5c8))


## v3.0.0 (2026-05-16)

### Refactoring

- Move LLM orchestration into application layer
  ([`62e0713`](https://github.com/Nexus-Thread/py-llmframe/commit/62e0713607b2bb5f0b7f14bd24008377d418e40a))

### Breaking Changes

- Provider-neutral LLM orchestration now lives in llmframe.application.llm. The historical
  llm_adapter mixin modules base, batch_adapter, single_request_adapter, and logging_utils were
  removed. Use LlmService for application orchestration or the retained LlmAdapter facade for
  compatibility with high-level adapter entry points.


## v2.9.2 (2026-05-16)

### Bug Fixes

- **persistence**: Avoid overwriting JSON artifacts
  ([`9b67261`](https://github.com/Nexus-Thread/py-llmframe/commit/9b672614cf6531562f93c604ac38141f8f5bc86e))

### Refactoring

- **llm**: Extract request payload builders from adapter
  ([`f86408f`](https://github.com/Nexus-Thread/py-llmframe/commit/f86408f41ea533b479046d7d4bcfed6b6598a947))

### Testing

- Strengthen LLM adapter audit coverage and CI gates
  ([`dbd5b0d`](https://github.com/Nexus-Thread/py-llmframe/commit/dbd5b0d75595e35fb1664e6a181b7f3c73a820b6))


## v2.9.1 (2026-05-15)

### Bug Fixes

- **shared**: Resolve recursive JSON type alias exports
  ([`4ca65df`](https://github.com/Nexus-Thread/py-llmframe/commit/4ca65df6fc15473527bf1f9e02bcc0fa38d39c78))

### Chores

- Pin workflow actions and normalize timestamps
  ([`0c3ed1d`](https://github.com/Nexus-Thread/py-llmframe/commit/0c3ed1d70f3e2078f2ee557409ba8a2a2878a05e))

### Continuous Integration

- Add self-contained HTML to live integration reports
  ([`9a0a5b5`](https://github.com/Nexus-Thread/py-llmframe/commit/9a0a5b5733ec210a015f2f03e6062b2a0a381b78))

- Upload HTML report for live OpenAI integration tests
  ([`364ed0d`](https://github.com/Nexus-Thread/py-llmframe/commit/364ed0d59ce7abcdc250906d44db420b33788b28))

### Documentation

- Refine agent skills for hexagonal workflow guidance
  ([`bafdc7e`](https://github.com/Nexus-Thread/py-llmframe/commit/bafdc7e90ebca887fe318a338e04d2b00be2b195))

- **ports**: Clarify LLM application port documentation
  ([`c7fac4b`](https://github.com/Nexus-Thread/py-llmframe/commit/c7fac4bbcc0b60a34622e1dc100c72f4b1f0f3e9))

### Refactoring

- Encapsulate usage tracker token aggregation
  ([`10c2e94`](https://github.com/Nexus-Thread/py-llmframe/commit/10c2e940c85e2a837bbfd21438358250bd3a558e))

- **openai**: Add explicit OpenAI provider builder
  ([`7163814`](https://github.com/Nexus-Thread/py-llmframe/commit/71638140c96c21d6d91809bf7191a7c4ddf40075))

### Testing

- **ci**: Streamline live OpenAI integration test targeting
  ([`c391d00`](https://github.com/Nexus-Thread/py-llmframe/commit/c391d0032f327b0c494258783e14ee2752fca1ca))


## v2.9.0 (2026-04-16)

### Features

- Add local file inputs and default pytest reports
  ([`d6cd291`](https://github.com/Nexus-Thread/py-llmframe/commit/d6cd291cd085eaf7f7d84717407ae2231f7b9768))


## v2.8.0 (2026-04-15)

### Features

- Add local image file input support to LLM adapter
  ([`9c0e3df`](https://github.com/Nexus-Thread/py-llmframe/commit/9c0e3df1ecc29336309364c6be30177dc9cf204d))

### Testing

- Use hosted image URL in OpenAI live image test
  ([`4a5ad87`](https://github.com/Nexus-Thread/py-llmframe/commit/4a5ad871f893f423c106c668d1803af9a96faf56))

- **openai**: Cover hosted and data URL image inputs
  ([`265e404`](https://github.com/Nexus-Thread/py-llmframe/commit/265e404b6db4c8ca52eedd9f1eacd7fcdf675811))


## v2.7.0 (2026-04-15)

### Build System

- Migrate dev extras to uv dependency groups
  ([`100a271`](https://github.com/Nexus-Thread/py-llmframe/commit/100a271be786833c160cc0966725bcf10e0ea703))

### Documentation

- **agents**: Expand skills for observability and app structure
  ([`8b4a9fc`](https://github.com/Nexus-Thread/py-llmframe/commit/8b4a9fca5f38aac8e9e81fb97af2cf8e652c0089))

### Features

- Add multimodal image URL input to LLM adapter
  ([`ddba256`](https://github.com/Nexus-Thread/py-llmframe/commit/ddba256ea96b881034e90a120b75beeeb281a100))


## v2.6.2 (2026-04-09)

### Bug Fixes

- Delete changelog
  ([`3fbf7e2`](https://github.com/Nexus-Thread/py-llmframe/commit/3fbf7e2c5544939adb5a55c908e2f12529266a0a))


## v2.6.1 (2026-04-09)

### Bug Fixes

- Bump version
  ([`4332190`](https://github.com/Nexus-Thread/py-llmframe/commit/4332190edeac0c4c84f4b44c3ca050138f5b33ec))

### Documentation

- **application**: Clarify public port and provider API docs
  ([`f15839c`](https://github.com/Nexus-Thread/py-llmframe/commit/f15839cf35fee51b450fe1da3de5687a813239bf))

### Refactoring

- **batch-store**: Simplify JSON persistence flow
  ([`3b2832c`](https://github.com/Nexus-Thread/py-llmframe/commit/3b2832ce125fb85038f33e2bea60bea6d4ff5d4e))

- **llm-adapter**: Extract schema normalization helpers
  ([`3f59371`](https://github.com/Nexus-Thread/py-llmframe/commit/3f5937178f55e31eb7596bdd9f4e134da3e0760b))

- **openai**: Centralize batch response mapping helpers
  ([`082c959`](https://github.com/Nexus-Thread/py-llmframe/commit/082c9597069a68d695c235c9734a60906a9ebdf6))

- **usage-tracker**: Centralize token value recording
  ([`6a873ae`](https://github.com/Nexus-Thread/py-llmframe/commit/6a873aec4f4135109059c94165df74d971925534))

### Testing

- **json-writer**: Cover artifact output and dir creation
  ([`8ec7f52`](https://github.com/Nexus-Thread/py-llmframe/commit/8ec7f5239285353bbdaaba9a55fc39320a3731b0))


## v2.6.0 (2026-04-08)

### Documentation

- Clarify README for LLM adapter and batch usage
  ([`c04ad14`](https://github.com/Nexus-Thread/py-llmframe/commit/c04ad14aaefc373b4d6a94af621e87882ea21494))

### Features

- **shared**: Export granular JSON type aliases
  ([`56a67cb`](https://github.com/Nexus-Thread/py-llmframe/commit/56a67cb1583d9150ec43720ab4b4fcd9736c78f1))

### Testing

- Deduplicate OpenAI transport test fixtures
  ([`d06904c`](https://github.com/Nexus-Thread/py-llmframe/commit/d06904c660766698ee7b45fff84afc93cb4b7767))


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
