# QFTools

QFTools is a Python library for quantitative finance calculations, currently focusing on date arithmetic and calendar operations. More features will be added in future releases.

## Requirements

- Python ≥ 3.13
- NumPy ≥ 2.2.1

## Installation

```bash
pip install qftools
```

## Current Features

- Calendar Operations
- Day Count Conventions
- Tenor Arithmetic
- Date Sequence Generation
- Roll Conventions

## Development

This project uses:
- [Poetry](https://python-poetry.org/) for dependency management
- [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- [pytest](https://docs.pytest.org/) for testing
- [pre-commit](https://pre-commit.com/) for git hooks

### Setting up development environment

```bash
# Clone the repository
git clone https://github.com/reecemiao/QFTools.git
cd qftools

# Install dependencies with Poetry
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

### Running tests
```bash
poetry run pytest
```

### Code Style

The project uses Ruff for both linting and formatting with the following configurations:
- Line length: 120 characters
- Python target version: 3.13
- NumPy docstring convention
- Selected rule sets: `F`, `E`, `W`, `C90`, `I`, `D`

## License

MIT License - see the [LICENSE](LICENSE) file for details.
