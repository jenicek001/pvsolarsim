# Python 3.9+ Multi-Version Testing Guide

## Problem

The CI pipeline tests on Python 3.9, 3.10, 3.11, and 3.12. Code that works on Python 3.10+ may fail on Python 3.9 due to type hint syntax differences.

**Common failure:** Using `list[str]` instead of `List[str]` works on Python 3.10+ but fails on Python 3.9.

## Quick Solution: Pre-Commit Checks

**Before every commit, run:**

```bash
.github/scripts/pre-commit-checks.sh
```

This automatically checks for Python 3.9 compatibility issues.

---

## Docker-Based Multi-Version Testing

For comprehensive testing across all Python versions **before pushing to GitHub**:

```bash
.github/scripts/test-python-versions.sh
```

### What it does:

1. **Creates isolated Docker containers** for Python 3.9, 3.10, 3.11, and 3.12
2. **Installs dependencies** in each environment
3. **Runs full test suite** (ruff, mypy, pytest) in each version
4. **Reports results** for all versions

### Requirements:

- **Docker** (recommended): Fully isolated environments
- **OR local Python versions**: Falls back to local if Docker unavailable

### Fallback to local Python:

If Docker is not available, the script will use locally installed Python versions:

```bash
# Install multiple Python versions with pyenv (recommended)
pyenv install 3.9.18
pyenv install 3.10.13
pyenv install 3.11.7
pyenv install 3.12.1

# Or use your system's package manager
sudo apt install python3.9 python3.10 python3.11 python3.12
```

---

## Manual Testing for Specific Python Version

### Option 1: Docker (Recommended)

```bash
# Test with Python 3.9
docker run --rm -v $PWD:/app -w /app python:3.9-slim bash -c "
    pip install -e '.[dev]' && 
    ruff check src/ tests/ && 
    mypy src/ && 
    pytest --cov
"

# Test with Python 3.10
docker run --rm -v $PWD:/app -w /app python:3.10-slim bash -c "
    pip install -e '.[dev]' && 
    ruff check src/ tests/ && 
    mypy src/ && 
    pytest --cov
"
```

### Option 2: Local Virtual Environments

```bash
# Create Python 3.9 environment
python3.9 -m venv .venv39
source .venv39/bin/activate
pip install -e ".[dev]"

# Run tests
ruff check src/ tests/
mypy src/
pytest --cov

# Deactivate when done
deactivate
```

---

## Python 3.9 Type Hints - Quick Reference

### ❌ **WRONG** (Fails on Python 3.9)

```python
def process_items(items: list[str]) -> dict[str, int]:
    pass

def get_config() -> dict[str, list[int]]:
    pass
```

### ✅ **CORRECT** (Works on Python 3.9+)

```python
from typing import Dict, List

def process_items(items: List[str]) -> Dict[str, int]:
    pass

def get_config() -> Dict[str, List[int]]:
    pass
```

### Common Replacements

| Python 3.10+ (fails 3.9) | Python 3.9+ (works all) |
|-------------------------|------------------------|
| `list[T]`               | `List[T]`              |
| `dict[K, V]`            | `Dict[K, V]`           |
| `tuple[T, ...]`         | `Tuple[T, ...]`        |
| `set[T]`                | `Set[T]`               |
| `str \| None`           | `Optional[str]`        |

---

## Integration with Pre-Commit Hooks

### Install pre-commit (optional but recommended)

```bash
pip install pre-commit
```

### Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pvsolarsim-checks
        name: PVSolarSim Pre-Commit Checks
        entry: .github/scripts/pre-commit-checks.sh
        language: script
        pass_filenames: false
        always_run: true
```

### Install hooks:

```bash
pre-commit install
```

Now checks run automatically on every `git commit`.

---

## CI/CD Workflow

The GitHub Actions workflow (`.github/workflows/test.yml`) automatically:

1. Tests on **Python 3.9, 3.10, 3.11, 3.12**
2. Runs **ruff**, **mypy**, **pytest**
3. **Blocks merge** if any version fails

**To prevent CI failures:**
- Run `.github/scripts/pre-commit-checks.sh` before committing
- Optionally run `.github/scripts/test-python-versions.sh` before pushing

---

## Troubleshooting

### Error: "list is not subscriptable" (Python 3.9)

**Cause:** Using `list[str]` syntax without `from __future__ import annotations`

**Fix:**
```python
# Option 1: Import types (recommended)
from typing import List
def func(items: List[str]):
    pass

# Option 2: Use future annotations (Python 3.7+)
from __future__ import annotations
def func(items: list[str]):
    pass
```

### Error: "unsupported operand type(s) for |" (Python 3.9)

**Cause:** Using `str | None` union syntax (Python 3.10+ only)

**Fix:**
```python
from typing import Optional
def func(name: Optional[str]):
    pass
```

### Docker not found

**Solution:** Install Docker or use local Python versions:

```bash
# Ubuntu/Debian
sudo apt install docker.io

# macOS
brew install docker

# Or use local Python
sudo apt install python3.9 python3.10 python3.11 python3.12
```

---

## Best Practices

1. **Always run pre-commit checks** before committing
2. **Test locally** with `.github/scripts/test-python-versions.sh` before pushing
3. **Use proper imports** from `typing` module
4. **Check PR logs** immediately if CI fails
5. **Fix Python 3.9 issues** as top priority

---

## Examples

### Good Workflow

```bash
# 1. Make changes
vim src/pvsolarsim/weather/quality.py

# 2. Run pre-commit checks
.github/scripts/pre-commit-checks.sh

# 3. (Optional) Run multi-version tests
.github/scripts/test-python-versions.sh

# 4. Commit and push
git add .
git commit -m "Add quality checks"
git push
```

### Fixing CI Failures

```bash
# 1. Check GitHub Actions logs for specific error
# 2. Reproduce locally with failing Python version
docker run --rm -v $PWD:/app -w /app python:3.9-slim bash -c "
    pip install -e '.[dev]' && mypy src/
"

# 3. Fix the issue (e.g., import List from typing)
# 4. Re-run checks
.github/scripts/pre-commit-checks.sh

# 5. Push fix
git commit -am "Fix Python 3.9 type hints"
git push
```

---

## Additional Resources

- [Python typing module docs](https://docs.python.org/3/library/typing.html)
- [PEP 585 - Type Hinting Generics In Standard Collections](https://peps.python.org/pep-0585/)
- [PEP 604 - Allow writing union types as X | Y](https://peps.python.org/pep-0604/)

---

**Last Updated:** 2025-12-29  
**Maintainer:** Development Team
