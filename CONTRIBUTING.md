# Contributing to PVSolarSim

Thank you for your interest in contributing to PVSolarSim!

## Quick Links

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Development Setup

1. Fork the repository on GitHub

2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pvsolarsim.git
   cd pvsolarsim
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Code Style

PVSolarSim follows PEP 8 and uses these tools:

- **Black**: Code formatter (line length: 100)
- **isort**: Import sorter
- **Ruff**: Fast Python linter
- **mypy**: Static type checker

Run formatters and linters:
```bash
black src/ tests/
isort src/ tests/
ruff check src/ tests/
mypy src/
```

### Type Hints

All functions must have type hints:

```python
def calculate_power(
    location: Location,
    system: PVSystem,
    timestamp: datetime
) -> PowerResult:
    """Calculate instantaneous power output."""
    ...
```

### Docstrings

Use NumPy-style docstrings for all public APIs. See documentation for examples.

## Testing

### Writing Tests

- Use pytest for all tests
- Aim for >90% code coverage
- Test edge cases and error conditions
- Use descriptive test names

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pvsolarsim

# Run specific test file
pytest tests/test_solar.py
```

## Pull Request Process

1. Create a new branch: `git checkout -b feature/your-feature-name`

2. Make your changes:
   - Follow code style guidelines
   - Add tests for new features
   - Update documentation

3. Run tests and linters:
   ```bash
   pytest
   black src/ tests/
   ruff check src/ tests/
   mypy src/
   ```

4. Commit with descriptive messages:
   ```bash
   git commit -m "Add feature: description of change"
   ```

5. Push to your fork:
   ```bash
   git push origin your-branch
   ```

6. Open a Pull Request on GitHub

## Types of Contributions

### Bug Reports

Open an issue with:
- Python version
- PVSolarSim version
- Minimal code to reproduce
- Expected vs. actual behavior
- Error message and traceback

### Feature Requests

Open an issue describing:
- The problem it solves
- Proposed solution
- Example usage

### Documentation

Documentation improvements are always welcome:
- Fix typos and grammar
- Add examples
- Improve clarity

## Code of Conduct

Be respectful and inclusive:
- Use welcoming language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue on GitHub
- Email: jenicek001@users.noreply.github.com

For more detailed guidelines, see the [full documentation](https://pvsolarsim.readthedocs.io/en/latest/contributing.html).
