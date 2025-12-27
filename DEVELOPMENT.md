# Development Workflow & CI/CD Best Practices

## CRITICAL: Always Run Local Checks Before Pushing

To prevent CI/CD failures, **ALWAYS** run these checks locally before committing:

```bash
# 1. Linting
ruff check src/ tests/ --fix

# 2. Type checking
mypy src/

# 3. Fast tests (excludes slow integration tests)
pytest --cov --cov-report=xml

# 4. Optional: Run slow tests locally
pytest -m slow -v
```

## Pre-commit Hooks (RECOMMENDED)

Install pre-commit hooks to automatically run checks before each commit:

```bash
pip install pre-commit
pre-commit install
```

This will automatically run:
- Ruff linting and formatting
- Mypy type checking
- Standard code quality checks

## Test Organization

### Fast Tests (Unit Tests)
- Located in `tests/test_*.py`
- Run automatically in CI/CD
- Should complete in < 10 seconds total
- Use mocks/fixtures for external dependencies

### Slow Tests (Integration Tests)
- Marked with `@pytest.mark.slow`
- Excluded from CI/CD by default
- Run locally with: `pytest -m slow`
- Include: full-year simulations, API calls, heavy computations

### Integration Test Scripts
- Located in `tests/integration/test_pr*.py`
- These are **scripts**, not pytest tests
- Run manually: `python tests/integration/test_pr5.py`
- **NOT** included in pytest discovery (excluded via `--ignore=tests/integration`)

## Common Issues & Solutions

### Issue 1: Tests Timing Out in CI

**Symptom:** Pytest hangs for 13+ minutes  
**Cause:** Slow tests (full-year simulations) running in CI  
**Solution:** Mark with `@pytest.mark.slow`

```python
@pytest.mark.slow
class TestAnnualSimulation:
    def test_full_year(self):
        result = simulate_annual(...)  # Takes 30+ seconds
```

### Issue 2: Mypy Type Errors

**Symptom:** `error: Cannot find implementation or library stub`  
**Cause:** Missing type stubs for third-party libraries  
**Solution:** Configure `mypy.ini` to ignore these

Already configured in `mypy.ini`:
```ini
[mypy]
ignore_missing_imports = True
disable_error_code = import-untyped,override,assignment,attr-defined
```

### Issue 3: Integration Tests Discovered by Pytest

**Symptom:** Pytest tries to import `tests/integration/test_pr*.py` and hangs  
**Cause:** These are scripts, not pytest tests  
**Solution:** Exclude via `pyproject.toml`

Already configured:
```toml
[tool.pytest.ini_options]
addopts = ["--ignore=tests/integration"]
```

### Issue 4: Ruff Linting Errors

**Symptom:** F841, B904, C901, etc.  
**Cause:** Code quality issues  
**Solution:** Run `ruff check --fix` to auto-fix most issues

Common fixes:
- **F841** (unused variable): Remove or use underscore prefix
- **B904** (exception without `from`): Use `raise ... from err`
- **C901** (complexity): Split function into smaller helpers

## Making Changes - Workflow

### 1. Start Development
```bash
cd /path/to/pvsolarsim
source .venv/bin/activate  # If using virtual environment
```

### 2. Make Code Changes
- Write new feature
- Add/update tests
- Update documentation

### 3. Run Local Checks
```bash
# Auto-fix linting
ruff check src/ tests/ --fix

# Type check
mypy src/

# Run fast tests
pytest

# Optional: Run specific test
pytest tests/test_mymodule.py -v
```

### 4. Commit Changes
```bash
git add .
git commit -m "Your message"
# Pre-commit hooks run automatically
```

### 5. Push to GitHub
```bash
git push origin your-branch
# CI/CD runs automatically
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/test.yml`) runs:

1. **Install dependencies** - `pip install -e ".[dev]"`
2. **Lint with ruff** - `ruff check src/ tests/`
3. **Type check with mypy** - `mypy src/`
4. **Test with pytest** - `pytest --cov --cov-report=xml`
5. **Upload coverage** - To Codecov

**Important:** Slow tests are excluded by default via `-m "not slow"` in `pyproject.toml`.

## Test Markers

Available pytest markers:

- `@pytest.mark.slow` - Slow tests (excluded from CI)

Run specific markers:
```bash
pytest -m slow          # Run only slow tests
pytest -m "not slow"    # Run all except slow tests (default)
```

## Coverage Requirements

- **Target**: >75% overall coverage
- **Weather modules**: >85% coverage
- **Integration tests**: Not counted in coverage (excluded)

Check coverage:
```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

## When Tests Fail in CI

1. **Check the logs** - GitHub Actions → Failed job → View logs
2. **Reproduce locally**:
   ```bash
   pytest -v  # Verbose output
   pytest tests/test_failing.py::test_name -vv  # Very verbose
   ```
3. **Fix the issue**
4. **Verify fix**:
   ```bash
   ruff check src/ tests/
   mypy src/
   pytest
   ```
5. **Commit and push**

## Configuration Files Reference

- **`pyproject.toml`** - pytest, black, coverage config
- **`mypy.ini`** - mypy type checking config
- **`.pre-commit-config.yaml`** - pre-commit hooks
- **`.github/workflows/test.yml`** - CI/CD pipeline

## Quick Reference

```bash
# Full pre-push checklist
ruff check src/ tests/ --fix && \
mypy src/ && \
pytest && \
echo "✅ Ready to push!"

# Run slow tests locally (optional)
pytest -m slow -v

# Run integration scripts
python tests/integration/test_pr5.py

# Run with coverage
pytest --cov --cov-report=html

# Run specific test file
pytest tests/test_weather_base.py -v
```

## Troubleshooting

**Q: Tests hang locally**  
A: You're probably running slow tests. Use `pytest -m "not slow"` or check `pyproject.toml` config.

**Q: CI fails but tests pass locally**  
A: Check Python version differences. CI tests on 3.9, 3.10, 3.11, 3.12.

**Q: Mypy errors in CI but not locally**  
A: Check `mypy.ini` is committed and mypy version matches.

**Q: How do I add a new slow test?**  
A: Add `@pytest.mark.slow` decorator:
```python
@pytest.mark.slow
def test_expensive_operation():
    result = simulate_annual(...)  # Takes long time
```

---

**Last Updated:** 2025-12-27  
**Maintainer:** Development Team
