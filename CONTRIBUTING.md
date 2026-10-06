# Contributing

## Branching workflow

- `main` contains stable, runnable versions.
- `develop` integrates changes before they are released to `main`.
- Create short-lived branches from `develop`:
  - `feature/<description>` for new functionality
  - `fix/<description>` for bug fixes
  - `docs/<description>` for documentation
  - `chore/<description>` for tooling and maintenance
- Open pull requests against `develop`.
- Release changes through a pull request from `develop` to `main`.
- Do not push directly to `main` or `develop`.
- Delete short-lived branches after merging.

## Commits

Write small, focused commits with English messages.

Examples:

- `feat(api): add expense filtering`
- `fix(validation): reject invalid dates`
- `docs: explain local setup`

## Checks before merging

Run these commands from the project root:

```bash
make lint
uv run --locked ruff format --check .
make cov
```

All checks must pass. Python application coverage must remain
at or above 80%. Once CI is configured, its checks must also pass.

## Pull request self-review

Every pull request describes:

- What changed and why.
- How the change was tested.
- Any remaining limitations.

Before merging:

- [ ] Review the complete diff.
- [ ] Run the applicable checks and record their results.
- [ ] Add or update tests where appropriate.
- [ ] Update documentation where needed.
- [ ] Check that no secrets or generated files are included.
