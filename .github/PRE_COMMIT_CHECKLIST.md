# Pre-Commit Checklist

**Run BEFORE every commit to prevent CI failures:**

```bash
.github/scripts/pre-commit-checks.sh
```

This script automatically runs:

1. ✅ **Ruff linting** - Code style checks
2. ✅ **Mypy type checking** - Static type analysis (Python 3.9+ compatible)
3. ✅ **Pytest** - All unit tests with coverage

---

## Python 3.9 Type Hints - Quick Reference

**ALWAYS use capitalized types from `typing` module:**

```python
# Import these at the top of your file
from typing import Dict, List, Optional, Set, Tuple

# ❌ WRONG - Fails on Python 3.9
def func(items: list[str]) -> dict[str, int]:
    pass

# ✅ CORRECT - Works on Python 3.9+
def func(items: List[str]) -> Dict[str, int]:
    pass
```

**Common replacements:**
- `list[T]` → `List[T]`
- `dict[K, V]` → `Dict[K, V]`
- `tuple[T, ...]` → `Tuple[T, ...]`
- `set[T]` → `Set[T]`

---

## Manual Checks (if script fails)

```bash
# Fix linting issues
ruff check src/ tests/ --fix

# Check types
mypy src/

# Run tests
pytest --cov
```

---

## When CI Fails

1. **Check GitHub Actions logs** for the specific error
2. **Reproduce locally** using the commands above
3. **Fix the issue**
4. **Re-run pre-commit script** before pushing again

---

**See DEVELOPMENT.md for full details**
