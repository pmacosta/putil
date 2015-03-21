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

* `cog`_ (helps generate automatic exceptions documentation)

* `funcsigs <https://pypi.python.org/pypi/funcsigs>`_

* `PyContracts <https://andreacensi.github.io/contracts/>`_

* `py.test`_ (unit test runner)

* `Sphinx <http://sphinx-doc.org/>`_ (documentation)

Contributing
============

1. The `repository <https://github.com/pmacosta/putil>`_ may be forked from GitHub; clone the forked repository recursively since the `Read the Docs theme <https://github.com/snide/sphinx_rtd_theme>`_ is a repository submodule:

.. code-block:: bash

	$ git clone --recursive https://github.com/[github-user-name]/putil.git
	$ cd putil
	$ export PUTIL_DIR=${PWD}

2. Install the project's Git hooks. The pre-commit hooks do some minor consistency checks, namely trailing whitespace and `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ compliance via Pylint. Assuming the directory to which
   the repository was cloned is in the :code:`$PUTIL_DIR` shell environment variable:

.. code-block:: bash

	$ ${PUTIL_DIR}/sbin/setup-git-hooks.sh

3. The :code:`${PUTIL_DIR}/sbin` directory contains all relevant scripts:

   * build-docs.sh: (re)builds the package documentation

	.. code-block:: bash

		$ ${PUTIL_DIR}/sbin/build-docs.sh -h
			build-docs.sh

			Usage:
			  build-docs.sh [-h] [-r] [module-name]

			Options:
			  -h  Show this screen
			  -r  Rebuild exceptions documentation. If no module name is given all
			      modules with auto-generated exceptions documentation are rebuilt

   * build-tags.sh: builds the project's `exhuberant ctags <http://ctags.sourceforge.net/>`_ file :code:`${PUTIL_DIR}/tags`

	.. code-block:: bash

		$ ${PUTIL_DIR}/sbin/build-tags.sh -h
		build-tags.sh

		Usage:
		  build-tags.sh [-h]

		Options:
		  -h  Show this screen

   * coverage.sh: measures test coverage in a module

	.. code-block:: bash

		$ ${PUTIL_DIR}/sbin/coverage.sh -h
		coverage.sh

		Usage:
		  coverage.sh [-h] [module-name]

		Options:
		  -h  Show this screen

   * gen_ref_images.py: (re)generates the plot module reference images needed for unit testing

	.. code-block:: bash

		$ python ${PUTIL_DIR}/sbin/gen_ref_images.py
		Generating image [PUTIL_DIR]/tests/support/ref_images/series_marker_false_interp_straight_line_style_solid.png
		...

   * run-package-coverage.sh: measures test coverage for all modules in package

	.. code-block:: bash

		$ ${PUTIL_DIR}/sbin/run-package-coverage.sh -h
		run-package-coverage.sh

		Usage:
		  run-package-coverage.sh [-h]

		Options:
		  -h  Show this screen

   * run-package-tests.sh: runs unit tests for all modules in packages. This is the same as executing the shell command :code:`${PUTIL_DIR}/py.test -x -s -vv`

	.. code-block:: bash

		$ ${PUTIL_DIR}/sbin/run-package-tests.sh -h
		run-package-tests.sh

		Usage:
		  run-package-tests.sh [-h]

		Options:
		  -h  Show this screen

   * test.sh: runs a module's unit tests

	.. code-block:: bash

		$ ${PUTIL_DIR}/sbin/test.sh -h
		test.sh

		Usage:
		  test.sh [-h] [module-name] [test-name]

		Options:
		  -h  Show this screen

4. Write a unit test which shows that a bug was fixed or that a new feature or API works as expected. Run the package tests to ensure that the bug fix or new feature does not have adverse side effects. If possible
   achieve 100% test coverage of the contributed code

License
=======

The MIT License (MIT)

Copyright (c) 2013-2015 Pablo Acosta-Serafini

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
