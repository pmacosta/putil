Putil Library
=============



.. highlight:: bash

This library provides a collection of utility modules to supplement the excellent Python standard library. The modules provided are:

* **eng**: this module provides engineering-related functions, mainly handling numbers represented in engineering notation, obtaining their constituent components and converting to and from regular floats

* **exdoc**: this module can be used to automatically generate exceptions documentation marked up in `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ with the help of the :ref:`exh-module` and
  `cog <http://nedbatchelder.com/code/cog/>`_

* **exh**: this module can be used to register exceptions and then conditionally raising them if a given condition is true

* **misc**: this module contains miscellaneous utility functions that can be applied in a variety of circumstances: there are context managers, membership functions (a certain argument is of a given type), numerical functions
  and string functions

* **pcontracts**: This module is a thin wrapper around the `PyContracts <https://andreacensi.github.io/contracts/>`_ library that enables customization of the exception type raised and limited customization of the exception message

* **pcsv**: this module can be used to handle comma-separated values (CSV) files and do lightweight processing on their data. For example

* **plot**: this module can be used to create high-quality, presentation-ready X-Y graphs quickly and easily

* **test**: this module contains functions to aid in the unit testing of modules in the package (`py.test <http://www.pytest.org>`_-based)

* **tree**: this module can be used to build, handle, process and search `tries <http://wikipedia.org/wiki/Trie>`_

Installing
==========

.. code-block:: bash

	$ pip install putil

Documentation
=============

Available at `<http://my-docs.org/>`_

Dependencies
============

* `cog`_

* `funcsigs <https://pypi.python.org/pypi/funcsigs>`_

* `PyContracts <https://andreacensi.github.io/contracts/>`_

* `py.test`_

* `Sphinx <http://sphinx-doc.org/>`_

Contributing
============

1. Fork the `repository <https://github.com/pmacosta/putil>`_ from GitHub. Clone the forked repository recursively since the `Read the Docs theme <https://github.com/snide/sphinx_rtd_theme>`_ is a repository submodule

2. Install the project's Git hooks. The pre-commit hooks do some minor consistency checks, namely trailing whitespace and `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ compliance via Pylint. Assuming the directory to which
   the repository was cloned is in the :code:`$PUTIL_DIR` shell environment variable:

.. code-block:: bash

	$ ${PUTIL_DIR}/bin/setup-git-hooks.sh

3. The :code:`${PUTIL_DIR}/bin` directory contains all relevant scripts:

   * coverage.sh: measures test coverage in a module

   * generate-docs.sh: (re) builds the package documentation

   * gen_ref_images.py: generates the plot module reference images needed for unit testing

   * run-package-coverage.sh: measures test coverage for all modules in package

   * run-package-tests.sh: runs unit tests for all modules in packages

   * test.sh: runs a module's unit tests

4. Write a test which shows that the bug was fixed or that the feature works as expected
