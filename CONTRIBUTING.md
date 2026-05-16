# Contributing

Thanks for contributing to this repository.

## Scope

This project is an educational and portfolio-oriented tennis shot analysis demo. Contributions should keep the repository:

- safe for public sharing
- reproducible without private assets
- easy to understand for readers reviewing the project

## Development setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

Optional video dependencies:

```bash
pip install -e .[video]
```

## Development workflow

1. Create a focused branch.
2. Keep changes small and task-oriented.
3. Add or update tests when behavior changes.
4. Run `pytest` before opening a pull request.
5. Update documentation when commands, structure, or public behavior change.

## Privacy rules

Do not commit:

- private videos
- personal data
- internal project references
- secrets or credentials

Before opening a PR, review [docs/SANITIZATION.md](docs/SANITIZATION.md).

## Style guidelines

- Prefer explicit, readable Python.
- Keep public examples deterministic when possible.
- Avoid adding unnecessary framework complexity.
- Preserve the notebook-to-package teaching value of the repository.

## Pull request checklist

- Tests pass locally.
- Docs are updated if needed.
- No private data or assets were added.
- Changes are scoped and explainable.
