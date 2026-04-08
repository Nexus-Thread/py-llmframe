# Releasing

This document contains maintainer-oriented release workflow notes.

## Publishing workflow

GitHub Actions publishes this package to PyPI using the workflow at `.github/workflows/ci_cd.yaml`.

- Publishing is triggered by pushes to the `master` branch or by manual workflow dispatch.
- The workflow uses Python Semantic Release to determine the next version from conventional commits and create the release commit and tag.
- `pyproject.toml` version updates are release-managed: do not bump `project.version` in regular feature or fix commits; Semantic Release writes the new version during the release commit.
- Package artifacts are built in CI and published to PyPI only.
- If no releasable commits are detected, the publish job is skipped.
- Publishing targets the `llmframe` project on `pypi.org`.

Before the workflow can publish successfully, configure a trusted publisher in the PyPI project settings for this GitHub repository and workflow file.

Also ensure the workflow has permission to use the repository `GITHUB_TOKEN` to create release commits and tags.

## Example release flow

```bash
git commit -m "feat: add new llm transport option"
git push origin master
```
