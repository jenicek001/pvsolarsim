#!/bin/bash
# Multi-version Python testing using Docker
# This script creates isolated environments for Python 3.9-3.12 and runs all tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================="
echo "Multi-Version Python Testing"
echo "=================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Warning: Docker not found. Falling back to local Python versions.${NC}"
    USE_DOCKER=false
else
    USE_DOCKER=true
fi

# Python versions to test
PYTHON_VERSIONS=("3.9" "3.10" "3.11" "3.12")

# Test results tracking
declare -A RESULTS
ALL_PASSED=true

# Function to run tests in Docker
run_tests_docker() {
    local py_version=$1
    local container_name="pvsolarsim-test-py${py_version}"
    
    echo -e "${YELLOW}Testing with Python ${py_version} (Docker)...${NC}"
    
    # Create Dockerfile for this Python version
    cat > "${PROJECT_ROOT}/.docker/Dockerfile.test-py${py_version}" << EOF
FROM python:${py_version}-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Install dependencies
RUN pip install --upgrade pip && \\
    pip install -e ".[dev]"

# Run tests
CMD ["bash", "-c", "ruff check src/ tests/ && mypy src/ && pytest --cov --cov-report=term-missing -q"]
EOF
    
    # Build and run
    if docker build -f "${PROJECT_ROOT}/.docker/Dockerfile.test-py${py_version}" -t "${container_name}" "${PROJECT_ROOT}" 2>&1 | grep -q "ERROR"; then
        echo -e "${RED}✗ Build failed for Python ${py_version}${NC}"
        RESULTS[$py_version]="FAILED"
        ALL_PASSED=false
        return 1
    fi
    
    if docker run --rm "${container_name}" 2>&1 | tee "/tmp/test-py${py_version}.log"; then
        echo -e "${GREEN}✓ All tests passed for Python ${py_version}${NC}"
        RESULTS[$py_version]="PASSED"
    else
        echo -e "${RED}✗ Tests failed for Python ${py_version}${NC}"
        RESULTS[$py_version]="FAILED"
        ALL_PASSED=false
        
        # Show error log
        echo -e "${YELLOW}Last 20 lines of error log:${NC}"
        tail -20 "/tmp/test-py${py_version}.log"
    fi
    
    echo ""
}

# Function to run tests locally with pyenv/conda
run_tests_local() {
    local py_version=$1
    local python_cmd="python${py_version}"
    
    echo -e "${YELLOW}Testing with Python ${py_version} (local)...${NC}"
    
    # Check if this Python version is available
    if ! command -v "$python_cmd" &> /dev/null; then
        echo -e "${YELLOW}Python ${py_version} not found locally. Skipping.${NC}"
        RESULTS[$py_version]="SKIPPED"
        echo ""
        return 0
    fi
    
    # Create temporary virtual environment
    local venv_dir="/tmp/pvsolarsim-test-py${py_version}"
    rm -rf "$venv_dir"
    
    if ! "$python_cmd" -m venv "$venv_dir"; then
        echo -e "${RED}✗ Failed to create venv for Python ${py_version}${NC}"
        RESULTS[$py_version]="FAILED"
        ALL_PASSED=false
        echo ""
        return 1
    fi
    
    # Activate and install
    source "$venv_dir/bin/activate"
    
    cd "$PROJECT_ROOT"
    
    if ! pip install --upgrade pip &> /dev/null || ! pip install -e ".[dev]" &> /dev/null; then
        echo -e "${RED}✗ Failed to install dependencies for Python ${py_version}${NC}"
        RESULTS[$py_version]="FAILED"
        ALL_PASSED=false
        deactivate
        echo ""
        return 1
    fi
    
    # Run checks
    echo "  Running ruff..."
    if ! ruff check src/ tests/ &> /dev/null; then
        echo -e "${RED}✗ Ruff failed for Python ${py_version}${NC}"
        RESULTS[$py_version]="FAILED"
        ALL_PASSED=false
        deactivate
        echo ""
        return 1
    fi
    
    echo "  Running mypy..."
    if ! mypy src/ &> /dev/null; then
        echo -e "${RED}✗ Mypy failed for Python ${py_version}${NC}"
        echo "Re-running mypy with output:"
        mypy src/
        RESULTS[$py_version]="FAILED"
        ALL_PASSED=false
        deactivate
        echo ""
        return 1
    fi
    
    echo "  Running pytest..."
    if ! pytest --cov --cov-report=term-missing -q; then
        echo -e "${RED}✗ Pytest failed for Python ${py_version}${NC}"
        RESULTS[$py_version]="FAILED"
        ALL_PASSED=false
        deactivate
        echo ""
        return 1
    fi
    
    echo -e "${GREEN}✓ All tests passed for Python ${py_version}${NC}"
    RESULTS[$py_version]="PASSED"
    
    deactivate
    rm -rf "$venv_dir"
    echo ""
}

# Create Docker directory if using Docker
if [ "$USE_DOCKER" = true ]; then
    mkdir -p "${PROJECT_ROOT}/.docker"
fi

# Run tests for each Python version
for version in "${PYTHON_VERSIONS[@]}"; do
    if [ "$USE_DOCKER" = true ]; then
        run_tests_docker "$version"
    else
        run_tests_local "$version"
    fi
done

# Summary
echo "=================================="
echo "Test Summary"
echo "=================================="
for version in "${PYTHON_VERSIONS[@]}"; do
    result=${RESULTS[$version]}
    if [ "$result" = "PASSED" ]; then
        echo -e "Python ${version}: ${GREEN}✓ PASSED${NC}"
    elif [ "$result" = "FAILED" ]; then
        echo -e "Python ${version}: ${RED}✗ FAILED${NC}"
    else
        echo -e "Python ${version}: ${YELLOW}⊘ SKIPPED${NC}"
    fi
done
echo "=================================="

# Cleanup Docker files
if [ "$USE_DOCKER" = true ]; then
    rm -rf "${PROJECT_ROOT}/.docker"
fi

# Exit with error if any tests failed
if [ "$ALL_PASSED" = false ]; then
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
