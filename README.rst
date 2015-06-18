.. README.rst
.. Copyright (c) 2013-2015 Pablo Acosta-Serafini
.. See LICENSE for details

Putil Library
=============

.. role:: bash(code)
	:language: bash

.. [[[cog
.. import os, sys
.. from docs.support.term_echo import ste
.. file_name = sys.modules['docs.support.term_echo'].__file__
.. mdir = os.path.realpath(
..     os.path.dirname(os.path.dirname(os.path.dirname(file_name)))
.. )
.. ]]]
.. [[[end]]]

This library provides a collection of utility modules to supplement the
Python standard library. The modules provided are:

* **eng**: engineering-related functions including a) handling numbers
  represented in engineering notation, obtaining their constituent
  components and converting to and from regular floats; b) pretty printing
  Numpy vectors; and c) formatting numbers represented in scientific
  notation with a greater degree of control and options than standard
  Python string formatting

* **exdoc**: automatically generate exceptions documentation marked up in
  `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ with help from
  `cog <http://nedbatchelder.com/code/cog/>`_ and the exh module

* **exh**: register exceptions and then raise them if a given condition is true

* **misc**: miscellaneous utility functions that can be applied in a variety
  of circumstances; there are context managers, membership functions (test if
  an argument is of a given type), numerical functions and string functions

* **pcontracts**: thin wrapper around the
  `PyContracts <https://andreacensi.github.io/contracts/>`_ library that
  enables customization of the exception type raised and limited
  customization of the exception message

* **pcsv**: handle comma-separated values (CSV) files and do lightweight
  processing of their data

* **pinspect**: supplements Python's introspection capabilities

* **plot**: create high-quality, presentation-ready X-Y graphs quickly and
  easily

* **ptypes**: several pseudo-type definitions which can be enforced
  and/or validated with custom contracts defined using the pcontracts module

* **test**: functions to aid in the unit testing of modules in the package
  (`py.test <http://www.pytest.org>`_-based)

* **tree**: build, handle, process and search
  `tries <http://wikipedia.org/wiki/Trie>`_

Interpreter
===========

The package has been developed and tested with Python 2.7 and Python 3.4

Installing
==========

.. code-block:: bash

	$ pip install putil

Documentation
=============

Available at `Read the Docs <https://readthedocs.org/projects/putil/>`_

Contributing
============

1. The `repository <https://bitbucket.org/pacosta/putil>`_ may be forked from
   Bitbucket; clone the forked repository recursively since the `Read the Docs
   documentation theme <https://github.com/snide/sphinx_rtd_theme>`_ is a
   repository sub-module [#f1]_:

		.. code-block:: bash

			$ git clone --recursive \
			      https://bitbucket.org/[bitbucket-user-name]/putil.git
			$ cd putil
			$ export PUTIL_DIR=${PWD}

2. Install the project's Git hooks. The pre-commit hook does some minor
   consistency checks, namely trailing whitespace and
   `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ compliance via
   Pylint. Assuming the directory to which the repository was cloned is
   in the :bash:`$PUTIL_DIR` shell environment variable:

		.. code-block:: bash

			$ ${PUTIL_DIR}/sbin/setup-git-hooks.sh

3. Ensure that the Python interpreter can find the package modules
   (update the :bash:`$PYTHONPATH` environment variable, or use
   `sys.paths() <https://docs.python.org/2/library/sys.html#sys.path>`_,
   etc.)

		.. code-block:: bash

			$ export PYTHONPATH=${PYTHONPATH}:${PUTIL_DIR}

   This is relevant only if it is desired to run unit tests, measure
   test coverage and/or (re)build the documentation using the cloned
   repository (and not a virtual environment). This option is attractive
   as it allows for faster iterations, but final pre-commit validation
   should be done using the `tox`_ flow (:bash:`pkg-validate.sh` script,
   see below)

4. Install the dependencies (if needed):

    * `Cog`_

    * `Coverage <http://coverage.readthedocs.org/en/coverage-4.0a5/>`_

    * `Funcsigs <https://pypi.python.org/pypi/funcsigs>`_

    * `Matplotlib <http://matplotlib.org/>`_

    * `Mock <http://www.voidspace.org.uk/python/mock/>`_

    * `Numpy <http://www.numpy.org/>`_

    * `Pillow <https://python-pillow.github.io/>`_

    * `PyContracts <https://andreacensi.github.io/contracts/>`_

    * `Py.test`_

    * `Pytest-coverage <https://pypi.python.org/pypi/pytest-cov>`_

    * `Pytest-xdist <https://pypi.python.org/pypi/pytest-xdist>`_ (optional)

    * `Scipy <http://www.scipy.org/>`_

    * `Sphinx <http://sphinx-doc.org/>`_

    * `Tox <https://tox.readthedocs.org/>`_

5. Write a unit test which shows that a bug was fixed or that a new feature
   or API works as expected. Run the package tests to ensure that the bug fix
   or new feature does not have adverse side effects. If possible achieve 100%
   code and branch coverage of the contribution. For a thorough code validation
   use the :bash:`pkg-validate.sh` script (see below)

.. 6. Continuous integration is available via `Shippable
..    <http://www.shippable.com/>`_. The Docker image used is
..    `shippableimages/ubuntu1404_python
..    <https://registry.hub.docker.com/u/shippableimages/ubuntu1404_python/>`_; it
..    may be necessary to update the build image in the "Settings" tab of the
..    Shippable putil repository page for the tests to pass (this image is already
..    specified in the Shippable YML configuration file). In "Build image" select
..    "Custom image", in "Custom image name", type
..    ``shippableimages/ubuntu1404_python`` and finally click on the "Save" button

7. The :bash:`${PUTIL_DIR}/sbin` directory contains all relevant development
   scripts:

   * **build-docs.sh:** (re)builds the package documentation

		.. [[[cog ste('build-docs.sh -h', 0, mdir, cog.out) ]]]

		.. code-block:: bash

		    $ ${PUTIL_DIR}/sbin/build-docs.sh -h
		    build-docs.sh

		    Usage:
		      build-docs.sh -h
		      build-docs.sh -r [-n num-cpus] [module-name]
		      build-docs.sh [module-name]

		    Options:
		      -h  Show this screen
		      -r  Rebuild exceptions documentation. If no module name
		          is given all modules with auto-generated exceptions
		          documentation are rebuilt
		      -n  Number of CPUs to use [default: 1]


		.. [[[end]]]

   * **build-tags.sh:** builds the project's
     `exuberant ctags <http://ctags.sourceforge.net/>`_ file
     :bash:`${PUTIL_DIR}/tags`

		.. [[[cog ste('build-tags.sh -h', 0, mdir, cog.out) ]]]

		.. code-block:: bash

		    $ ${PUTIL_DIR}/sbin/build-tags.sh -h
		    build-tags.sh

		    Usage:
		      build-tags.sh -h
		      build-tags.sh

		    Options:
		      -h  Show this screen


		.. [[[end]]]

   * **gen_ref_images.py:** (re)generates the plot module reference images
     needed for unit testing

	.. code-block:: bash

		$ ${PUTIL_DIR}/sbin/gen_ref_images.py
		Generating image [PUTIL_DIR]/tests/support/...
		...

   * **test.sh:** runs a module's unit tests, doctests or coverage

		.. [[[cog ste('test.sh -h', 6, mdir, cog.out) ]]]

		.. code-block:: bash

		    $ ${PUTIL_DIR}/sbin/test.sh -h
		    test.sh

		    Usage:
		      test.sh -h
		      test.sh -d [-e env] [-n num-cpus]
		      test.sh -c [-e env] [-n num-cpus] [module-name]
		      test.sh [-e env] [-n num-cpus] [module-name] [test-name]

		    Options:
		      -h  Show this screen
		      -c  Measure test coverage
		      -d  Verify doctests
		      -e  Interpreter version [default: PY27|py34]
		      -n  Number of CPUs to use [default: 1]

		    If no module name is given all package modules are processed


		.. [[[end]]]

   * **pkg-validate.sh:** uses `tox <https://tox.readthedocs.org/>`_ to run
     the package unit tests, verify doctests, measure test coverage and build
     the documentation in virtual environments

		.. [[[cog ste('pkg-validate.sh -h', 6, mdir, cog.out) ]]]

		.. code-block:: bash

		    $ ${PUTIL_DIR}/sbin/pkg-validate.sh -h
		    pkg-validate.sh

		    Usage:
		      pkg-validate.sh -h
		      pkg-validate.sh [-n num-cpus] [-e env]

		    Options:
		      -h  Show this screen
		      -e  Interpreter version [default: PY27|py34]
		      -n  Number of CPUs to use [default: 1]


		.. [[[end]]]


.. rubric:: Footnotes

.. [#f1] All examples are for the `bash <https://www.gnu.org/software/bash/>`_
   shell

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
