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

Contributing
============

1. The `repository <https://bitbucket.org/pacosta/putil>`_ may be forked from Bitbucket; clone the forked repository recursively since the `Read the Docs theme <https://github.com/snide/sphinx_rtd_theme>`_ is a repository submodule [#f1]_:

	.. code-block:: bash

		$ git clone --recursive https://github.com/[github-user-name]/putil.git
		$ cd putil
		$ export PUTIL_DIR=${PWD}

2. Install the project's Git hooks. The pre-commit hooks do some minor consistency checks, namely trailing whitespace and `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ compliance via Pylint. Assuming the directory to which
   the repository was cloned is in the :code:`$PUTIL_DIR` shell environment variable:

	.. code-block:: bash

		$ ${PUTIL_DIR}/sbin/setup-git-hooks.sh

3. Ensure that Python can find the package modules (update the :code:`PYTHONPATH` environment variable, or use `sys.paths() <https://docs.python.org/2/library/sys.html#sys.path>`_, etc.)

   .. code-block:: bash

		$ export PYTHONPATH=${PYTHONPATH}:${PUTIL_DIR}

   This is relevant only if it is desired to run unit tests, measure test coverage and/or (re)build the documentation using the cloned repository (and not a virtual environment). This option is attractive as it allows for faster
   iterations, but final pre-commit validation should be done using the `Tox`_ flow (:code:`pkg-validate.sh` script, see below)

4. Install the dependencies (if needed):

    * `Cog`_ (helps generate automatic exceptions documentation)
 
    * `Coverage <http://coverage.readthedocs.org/en/coverage-4.0a5/>`_ (measures unit test coverage)

    * `Funcsigs <https://pypi.python.org/pypi/funcsigs>`_

    * `Matplotlib <http://matplotlib.org/>`_

    * `Mock <http://www.voidspace.org.uk/python/mock/>`_

    * `Numpy <http://www.numpy.org/>`_

    * `Pillow <https://python-pillow.github.io/>`_ (fork of the Python Image Library)

    * `PyContracts <https://andreacensi.github.io/contracts/>`_

    * `Py.test`_ (unit test runner)

    * `Pytest-coverage <https://pypi.python.org/pypi/pytest-cov>`_

    * `Scipy <http://www.scipy.org/>`_

    * `Sphinx <http://sphinx-doc.org/>`_ (documentation)

    * `Tox <https://tox.readthedocs.org/>`_


5. Write a unit test which shows that a bug was fixed or that a new feature or API works as expected. Run the package tests to ensure that the bug fix or new feature does not have adverse side effects. If possible
   achieve 100% test coverage of the contributed code. For a thorough code validation use the :code:`pkg-validate.sh` script (see below)

6. Continuous integration is available via `Shippable <http://www.shippable.com/>`_. The Docker image used is `shippableimages/ubuntu1404_python <https://registry.hub.docker.com/u/shippableimages/ubuntu1404_python/>`_; it may
   be necessary to update the build image in the "Settings" tab of the Shippable putil repository page for the tests to pass (this image is already specified in the Shippable YML configuration file). In "Build image" select
   "Custom image", in "Custom image name", type ``shippableimages/ubuntu1404_python`` and finally click on the "Save" button

7. The :code:`${PUTIL_DIR}/sbin` directory contains all relevant development scripts:

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

   * coverage.sh: measures test coverage of a module

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

   * pkg-validate.sh: uses `tox <https://tox.readthedocs.org/>`_ to run the package unit tests, measure test coverage and build the documentation in virtual environments

	.. code-block:: bash

		$ ${PUTIL_DIR}/sbin/pkg-validate.sh -h
		pkg-validate.sh
		
		Usage:
		  pkg-validate.sh [-h]
		
		Options:
		  -h  Show this screen

.. rubric:: Footnotes

.. [#f1] All shell examples are for the `bash <https://www.gnu.org/software/bash/>`_ shell

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

