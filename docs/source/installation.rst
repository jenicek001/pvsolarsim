Installation
============

Requirements
------------

PVSolarSim requires Python 3.9 or later.

Installing from PyPI
--------------------

The easiest way to install PVSolarSim is via pip:

.. code-block:: bash

   pip install pvsolarsim

This will install PVSolarSim and all required dependencies.

Installing from Source
----------------------

To install from source (for development or to get the latest unreleased features):

.. code-block:: bash

   git clone https://github.com/jenicek001/pvsolarsim.git
   cd pvsolarsim
   pip install -e ".[dev]"

The ``[dev]`` option installs additional development dependencies including:

* pytest and pytest-cov (for testing)
* black, ruff, isort (for code formatting and linting)
* mypy (for type checking)
* pvlib (for validation)

Dependencies
------------

PVSolarSim depends on the following packages:

Required Dependencies
~~~~~~~~~~~~~~~~~~~~~

* **numpy** (>=1.24.0): Numerical computing
* **pandas** (>=2.0.0): Data manipulation and time series
* **scipy** (>=1.10.0): Scientific computing
* **requests** (>=2.31.0): HTTP client for weather APIs
* **pydantic** (>=2.5.0): Data validation
* **python-dateutil** (>=2.8.0): Date utilities
* **pytz** (>=2023.3): Timezone support

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

* **pvlib** (>=0.10.0): For validation and comparison (included in dev install)
* **matplotlib** (>=3.5.0): For plotting (future feature)
* **jupyter** (>=1.0.0): For running tutorial notebooks

Verifying Installation
----------------------

After installation, verify that PVSolarSim is installed correctly:

.. code-block:: python

   import pvsolarsim
   print(pvsolarsim.__version__)

You should see the version number (e.g., ``0.1.0``).

To run the test suite:

.. code-block:: bash

   pytest

Or with coverage:

.. code-block:: bash

   pytest --cov=pvsolarsim

Troubleshooting
---------------

NumPy/SciPy Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you encounter issues installing NumPy or SciPy, you may need to install system dependencies first:

**Ubuntu/Debian:**

.. code-block:: bash

   sudo apt-get install python3-dev build-essential

**macOS:**

.. code-block:: bash

   xcode-select --install

**Windows:**

Install the latest Visual C++ redistributable from Microsoft.

Import Errors
~~~~~~~~~~~~~

If you get import errors, ensure you're using Python 3.9 or later:

.. code-block:: bash

   python --version

Virtual Environment
~~~~~~~~~~~~~~~~~~~

It's recommended to use a virtual environment to avoid dependency conflicts:

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install pvsolarsim

Upgrading
---------

To upgrade to the latest version:

.. code-block:: bash

   pip install --upgrade pvsolarsim

To upgrade a development installation:

.. code-block:: bash

   cd pvsolarsim
   git pull
   pip install -e ".[dev]"
