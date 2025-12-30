Contributing
============

Thank you for your interest in contributing to PVSolarSim!

This document provides guidelines for contributing to the project.

.. contents:: Table of Contents
   :local:
   :depth: 2

Getting Started
---------------

Development Setup
~~~~~~~~~~~~~~~~~

1. **Fork the repository** on GitHub

2. **Clone your fork**:

   .. code-block:: bash

      git clone https://github.com/YOUR_USERNAME/pvsolarsim.git
      cd pvsolarsim

3. **Create a virtual environment**:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\\Scripts\\activate

4. **Install development dependencies**:

   .. code-block:: bash

      pip install -e ".[dev]"

5. **Install pre-commit hooks**:

   .. code-block:: bash

      pre-commit install

6. **Create a new branch** for your changes:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

Code Style
----------

PVSolarSim follows PEP 8 and uses several tools to maintain code quality.

Formatting
~~~~~~~~~~

* **Black**: Code formatter (line length: 100)
* **isort**: Import sorter

Run formatters:

.. code-block:: bash

   black src/ tests/
   isort src/ tests/

Linting
~~~~~~~

* **Ruff**: Fast Python linter
* **mypy**: Static type checker

Run linters:

.. code-block:: bash

   ruff check src/ tests/
   mypy src/

Type Hints
~~~~~~~~~~

All functions must have type hints:

.. code-block:: python

   def calculate_power(
       location: Location,
       system: PVSystem,
       timestamp: datetime,
       ambient_temp: float,
       wind_speed: float = 1.0,
       cloud_cover: float = 0.0
   ) -> PowerResult:
       """Calculate instantaneous power output."""
       ...

Docstrings
~~~~~~~~~~

Use NumPy-style docstrings for all public APIs:

.. code-block:: python

   def my_function(param1: int, param2: str) -> float:
       """
       Short description.

       Longer description with more details about what the function does.

       Parameters
       ----------
       param1 : int
           Description of param1
       param2 : str
           Description of param2

       Returns
       -------
       float
           Description of return value

       Examples
       --------
       >>> my_function(42, "hello")
       3.14

       See Also
       --------
       other_function : Related function

       References
       ----------
       .. [1] Author. (Year). Title. Journal, Volume(Issue), Pages.
       """
       ...

Testing
-------

Writing Tests
~~~~~~~~~~~~~

* Use pytest for all tests
* Aim for >90% code coverage
* Test edge cases and error conditions
* Use descriptive test names

Test structure:

.. code-block:: python

   def test_my_feature_basic():
       """Test basic functionality of my feature."""
       result = my_function(input_data)
       assert result == expected_output

   def test_my_feature_edge_case():
       """Test edge case with zero input."""
       result = my_function(0)
       assert result == 0

   def test_my_feature_invalid_input():
       """Test error handling for invalid input."""
       with pytest.raises(ValueError, match="must be positive"):
           my_function(-1)

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=pvsolarsim

   # Run specific test file
   pytest tests/test_solar.py

   # Run specific test
   pytest tests/test_solar.py::test_solar_position_basic

   # Run slow tests (skipped by default)
   pytest -m slow

Test Markers
~~~~~~~~~~~~

* ``@pytest.mark.slow``: Long-running tests (>1 second)
* Use for integration tests and full simulations

Pull Request Process
--------------------

1. **Update your branch** with the latest changes:

   .. code-block:: bash

      git checkout master
      git pull upstream master
      git checkout your-branch
      git rebase master

2. **Make your changes**:

   * Follow code style guidelines
   * Add tests for new features
   * Update documentation as needed

3. **Run tests and linters**:

   .. code-block:: bash

      pytest
      black src/ tests/
      ruff check src/ tests/
      mypy src/

4. **Commit your changes** with descriptive messages:

   .. code-block:: bash

      git add .
      git commit -m "Add feature: description of change"

   Commit message format:

   * First line: Short summary (50 chars or less)
   * Blank line
   * Detailed description if needed
   * Reference issue numbers: ``Fixes #123``

5. **Push to your fork**:

   .. code-block:: bash

      git push origin your-branch

6. **Open a Pull Request** on GitHub:

   * Describe your changes clearly
   * Reference related issues
   * Include example usage if applicable

7. **Respond to review feedback**:

   * Make requested changes
   * Push updates to your branch
   * Reply to comments

Types of Contributions
----------------------

Bug Reports
~~~~~~~~~~~

Found a bug? Please open an issue with:

* Python version
* PVSolarSim version (``pvsolarsim.__version__``)
* Minimal code to reproduce the bug
* Expected vs. actual behavior
* Full error message and traceback

Feature Requests
~~~~~~~~~~~~~~~~

Have an idea for a new feature? Open an issue describing:

* The problem it solves
* Proposed solution
* Example usage
* Alternatives considered

Documentation
~~~~~~~~~~~~~

Documentation improvements are always welcome:

* Fix typos and grammar
* Add examples
* Clarify explanations
* Improve API documentation

Code Contributions
~~~~~~~~~~~~~~~~~~

We welcome:

* Bug fixes
* New features (discuss in an issue first)
* Performance improvements
* Additional tests
* Code refactoring

Development Guidelines
----------------------

Adding New Modules
~~~~~~~~~~~~~~~~~~

1. Create module in ``src/pvsolarsim/``
2. Add ``__init__.py`` with public API
3. Write comprehensive tests
4. Add documentation
5. Update examples if applicable

Adding Dependencies
~~~~~~~~~~~~~~~~~~~

* Minimize new dependencies
* Justify each dependency
* Pin version ranges in ``pyproject.toml``
* Update documentation

Performance
~~~~~~~~~~~

* Profile before optimizing
* Use NumPy for numerical operations
* Vectorize when possible
* Avoid premature optimization

Backward Compatibility
~~~~~~~~~~~~~~~~~~~~~~

* Maintain backward compatibility when possible
* Deprecate features before removal
* Document breaking changes in CHANGELOG

Release Process
---------------

Releases are managed by maintainers. The process is:

1. Update version in ``pyproject.toml``
2. Update ``CHANGELOG.md``
3. Create release tag
4. Build and upload to PyPI
5. Create GitHub release

Code of Conduct
---------------

Be respectful and inclusive:

* Use welcoming language
* Be respectful of differing viewpoints
* Accept constructive criticism gracefully
* Focus on what is best for the community

License
-------

By contributing, you agree that your contributions will be licensed under the MIT License.

Questions?
----------

* Open an issue on GitHub
* Email: jenicek001@users.noreply.github.com

Thank you for contributing to PVSolarSim! 🌞
