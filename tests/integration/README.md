# Integration Tests

This directory contains integration tests that validate complete workflows and real-world scenarios.

## Test Files

- **test_pr*.py** - Integration tests for pull request validation
  - Each file tests a complete feature set from a specific PR
  - Uses real-world system configurations
  - Validates end-to-end workflows

## Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run specific integration test
pytest tests/integration/test_pr4.py

# Run with verbose output
pytest tests/integration/ -v
```

## Difference from Unit Tests

- **Unit tests** (in `tests/` root): Test individual functions and modules in isolation
- **Integration tests** (in `tests/integration/`): Test complete workflows with realistic data

## Real-World System Configuration

Many tests use a real 14.04 kWp system in Prague, Czech Republic:
- Location: 50.0807494°N, 14.8594164°E, 300m altitude
- Panels: 16×450W München + 18×380W Canadian Solar
- Orientation: 35° tilt, 202° azimuth (SSW)
- Total area: 68.64 m², efficiency: 20.45%
