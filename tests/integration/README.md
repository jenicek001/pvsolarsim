# Integration Tests

This directory contains integration tests that validate complete workflows and real-world scenarios.

## Test Files

- **test_pr*.py** - Integration tests for pull request validation
  - Each file tests a complete feature set from a specific PR
  - Uses real-world system configurations
  - Validates end-to-end workflows

### Current Integration Tests

- **test_pr1.py** - Solar position and clear-sky irradiance (Week 2-3)
- **test_pr2.py** - POA irradiance calculations (Week 4)
- **test_pr3.py** - Temperature modeling (Week 5)
- **test_pr4.py** - Power calculation with cloud cover (Week 6)
- **test_pr5.py** - Annual simulation (Week 7)
- **test_pr6.py** - Weather data integration (Week 8)
- **test_pr7.py** - Weather quality validation & interpolation (Week 9)
  - **Real-world demonstration:** Prague 14.04 kWp system
  - **Features:** Quality checks, gap filling, NaN interpolation
  - **Benchmarking:** Czech Republic performance expectations
  - **Results:** See `docs/implementation/PR7_TEST_RESULTS.md`

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
