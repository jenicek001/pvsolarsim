#!/bin/bash
# Pre-commit checks to run before pushing code
# This script ensures code passes all CI checks locally before committing

set -e  # Exit on first error

echo "🔍 Running pre-commit checks..."
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found at .venv/"
    echo "   Run: python -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'"
    exit 1
fi

# Check we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Must run from repository root (where pyproject.toml is)"
    exit 1
fi

echo "1️⃣  Linting with ruff..."
ruff check src/ tests/
if [ $? -ne 0 ]; then
    echo "❌ Ruff linting failed"
    exit 1
fi
echo "✅ Ruff passed"
echo ""

echo "2️⃣  Type checking with mypy..."
mypy src/
if [ $? -ne 0 ]; then
    echo "❌ Mypy type checking failed"
    exit 1
fi
echo "✅ Mypy passed"
echo ""

echo "3️⃣  Running tests with pytest..."
pytest --cov --cov-report=term-missing -q
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi
echo "✅ All tests passed"
echo ""

echo "✅ All pre-commit checks passed! Safe to commit and push."
