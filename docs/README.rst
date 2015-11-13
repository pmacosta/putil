.. README.rst
.. Copyright (c) 2013-2015 Pablo Acosta-Serafini
.. See LICENSE for details

.. image::
   https://travis-ci.org/pmacosta/putil.svg?branch=develop

.. image::
   https://ci.appveyor.com/api/projects/status/
   7dpk342kxs8kcg5t/branch/develop?svg=true

.. image::
   https://readthedocs.org/projects/pip/badge/?version=stable
   :target: http://pip.readthedocs.org/en/stable/?badge=stable
   :alt: Documentation Status

.. image::
   https://codecov.io/github/pmacosta/putil/coverage.svg?branch=develop
   :target: https://codecov.io/github/pmacosta/putil?branch=develop

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
.. import docs.support.requirements_to_rst
.. docs.support.requirements_to_rst.def_links(cog)
.. ]]]
.. _Astroid: https://bitbucket.org/logilab/astroid
.. _Cog: http://nedbatchelder.com/code/cog
.. _Coverage: http://coverage.readthedocs.org/en/coverage-4.0a5
.. _Decorator: https://pythonhosted.org/decorator
.. _Funcsigs: https://pypi.python.org/pypi/funcsigs
.. _Matplotlib: http://matplotlib.org
.. _Mock: http://www.voidspace.org.uk/python/mock
.. _Numpy: http://www.numpy.org
.. _Pillow: https://python-pillow.github.io
.. _PyContracts: https://andreacensi.github.io/contracts
.. _Pylint: http://www.pylint.org
.. _Py.test: http://pytest.org
.. _Pytest-coverage: https://pypi.python.org/pypi/pytest-cov
.. _Pytest-xdist: https://pypi.python.org/pypi/pytest-xdist
.. _Scipy: http://www.scipy.org
.. _Six: https://pythonhosted.org/six
.. _Sphinx: http://sphinx-doc.org
.. _ReadTheDocs Sphinx theme: https://github.com/snide/sphinx_rtd_theme
.. _Inline Syntax Highlight Sphinx Extension:
   https://bitbucket.org/klorenz/sphinxcontrib-inlinesyntaxhighlight
.. _Tox: https://testrun.org/tox
.. _Virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs
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
  `Cog`_ and the :py:mod:`exh <putil.exh>` module

* **exh**: register exceptions and then raise them if a given condition is true

* **misc**: miscellaneous utility functions that can be applied in a variety
  of circumstances; there are context managers, membership functions (test if
  an argument is of a given type), numerical functions and string functions

* **pcontracts**: thin wrapper around the
  `PyContracts`_ library that
  enables customization of the exception type raised and limited
  customization of the exception message

* **pcsv**: handle comma-separated values (CSV) files and do lightweight
  processing of their data

* **pinspect**: supplement Python's introspection capabilities

* **plot**: create high-quality, presentation-ready X-Y graphs quickly and
  easily

* **ptypes**: several pseudo-type definitions which can be enforced
  and/or validated with custom contracts defined using the
  :py:mod:`pcontracts <putil.pcontracts>` module

* **test**: functions to aid in the unit testing of modules in the package
  (`Py.test`_-based)

* **tree**: build, handle, process and search
  `tries <http://wikipedia.org/wiki/Trie>`_

Interpreter
===========

The package has been developed and tested with Python 2.6, 2.7, 3.3, 3.4
and 3.5 under Linux (Debian, Ubuntu) and Microsoft Windows

Installing
==========

.. code-block:: bash

	$ pip install putil

Documentation
=============

Available at `Read the Docs <https://putil.readthedocs.org>`_

Contributing
============

1. Abide by the adopted `code of conduct
   <http://contributor-covenant.org/version/1/3/0>`_

2. Fork the `repository <https://github.com/pmacosta/putil>`_ from
   GitHub and then clone personal copy [#f1]_:

	.. code-block:: bash

		$ git clone \
		      https://github.com/[github-user-name]/putil.git
                Cloning into 'putil'...
                ...
		$ cd putil
		$ export PUTIL_DIR=${PWD}

3. Install the project's Git hooks and build the documentation. The pre-commit
   hook does some minor consistency checks, namely trailing whitespace and
   `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ compliance via
   Pylint. Assuming the directory to which the repository was cloned is
   in the :bash:`$PUTIL_DIR` shell environment variable:

	.. code-block:: bash

		$ ${PUTIL_DIR}/sbin/complete-cloning.sh
                Installing Git hooks
                Building putil package documentation
                ...

4. Ensure that the Python interpreter can find the package modules
   (update the :bash:`$PYTHONPATH` environment variable, or use
   `sys.paths() <https://docs.python.org/2/library/sys.html#sys.path>`_,
   etc.)

	.. code-block:: bash

		$ export PYTHONPATH=${PYTHONPATH}:${PUTIL_DIR}

5. Install the dependencies (if needed, done automatically by pip):

    .. [[[cog
    .. import docs.support.requirements_to_rst
    .. docs.support.requirements_to_rst.proc_requirements(cog)
    .. ]]]


    * `Astroid`_ (older than 1.4)

    * `Cog`_ (2.4 or newer)

    * `Coverage`_ (3.7.1 or newer)

    * `Decorator`_ (3.4.2 or newer)

    * `Funcsigs`_ (Python 2.x only, 0.4 or newer)

    * `Inline Syntax Highlight Sphinx Extension`_ (0.2 or newer)

    * `Matplotlib`_ (1.3.1 or newer)

    * `Mock`_ (Python 2.x only, 1.0.1 or newer)

    * `Numpy`_ (1.8.2 or newer)

    * `Pillow`_ (2.6.1 or newer)

    * `Py.test`_ (2.7.0 or newer)

    * `PyContracts`_ (1.7.2 or newer except 1.7.7)

    * `Pylint`_ (Python 2.6: 1.3 or newer and older than 1.4, Python 2.7
      or newer: 1.3.1 or newer and older than 1.5)

    * `Pytest-coverage`_ (1.8.0 or newer)

    * `Pytest-xdist`_ (optional, 1.8.0 or newer)

    * `ReadTheDocs Sphinx theme`_ (0.1.9 or newer)

    * `Scipy`_ (0.13.3 or newer)

    * `Six`_ (1.4.0 or newer)

    * `Sphinx`_ (1.2.3 or newer)

    * `Tox`_ (1.9.0 or newer)

    * `Virtualenv`_ (13.1.2 or newer)

    .. [[[end]]]

6. Implement a new feature or fix a bug

7. Write a unit test which shows that the contributed code works as expected.
   Run the package tests to ensure that the bug fix or new feature does not
   have adverse side effects. If possible achieve 100% code and branch
   coverage of the contribution. Thorough package validation
   can be done via Tox and Py.test:

	.. code-block:: bash

            $ tox
            GLOB sdist-make: .../putil/setup.py
            py26-pkg inst-nodeps: .../putil/.tox/dist/putil-...zip

   `Setuptools <https://bitbucket.org/pypa/setuptools>`_ can also be used
   (Tox is configured as its virtual environment manager) [#f2]_:

	.. code-block:: bash

	    $ python setup.py tests
            running tests
            running egg_info
            writing requirements to putil.egg-info/requires.txt
            writing putil.egg-info/PKG-INFO
            ...

   Tox (or Setuptools via Tox) runs with the following default environments:
   ``py26-pkg``, ``py27-pkg``, ``py33-pkg``, ``py34-pkg`` and ``py35-pkg``
   [#f3]_. These use the Python 2.6, 2.7, 3.3, 3.4 and 3.5 interpreters,
   respectively, to test all code in the documentation (both in Sphinx
   ``*.rst`` source files and in docstrings), run all unit tests, measure test
   coverage and re-build the exceptions documentation. To pass arguments to
   Py.test (the test runner) use a double dash (``--``) after all the Tox
   arguments, for example:

	.. code-block:: bash

	    $ tox -e py27-pkg -- -n 4
            GLOB sdist-make: .../putil/setup.py
            py27-pkg inst-nodeps: .../putil/.tox/dist/putil-...zip
            ...

   Or use the :code:`-a` Setuptools optional argument followed by a quoted
   string with the arguments for Py.test. For example:

	.. code-block:: bash

	    $ python setup.py tests -a "-e py27-pkg -- -n 4"
            running tests
            ...

   There are other convenience environments defined for Tox [#f4]_:

    * ``py26-repl``, ``py27-repl``, ``py33-repl``, ``py34-repl`` and
      ``py35-repl`` run the Python 2.6, 2.7, 3.3, 3.4 or 3.5 REPL,
      respectively, in the appropriate virtual environment. The ``putil``
      package is pip-installed by Tox when the environments are created.
      Arguments to the interpreter can be passed in the command line
      after a double dash (``--``)

    * ``py26-test``, ``py27-test``, ``py33-test``, ``py34-test`` and
      ``py35-test`` run py.test using the Python 2.6, 2.7, 3.3, 3.4
      or Python 3.5 interpreter, respectively, in the appropriate virtual
      environment. Arguments to py.test can be passed in the command line
      after a double dash (``--``) , for example:

	.. code-block:: bash

	    $ tox -e py34-test -- -x test_eng.py
            GLOB sdist-make: [...]/putil/setup.py
            py34-test inst-nodeps: [...]/putil/.tox/dist/putil-[...].zip
            py34-test runtests: PYTHONHASHSEED='680528711'
            py34-test runtests: commands[0] | [...]py.test -x test_eng.py
            ==================== test session starts ====================
            platform linux -- Python 3.4.2 -- py-1.4.30 -- [...]
            ...

    * ``py26-cov``, ``py27-cov``, ``py33-cov``, ``py34-cov`` and
      ``py35-cov`` test code and branch coverage using the Python 2.6,
      2.7, 3.3, 3.4 or 3.5 interpreter, respectively, in the appropriate
      virtual environment. Arguments to py.test can be passed in the command
      line after a double dash (``--``). The report can be found in
      :bash:`${PUTIL_DIR}/.tox/py[PV]/usr/share/putil/tests/htmlcov/index.html`
      where ``[PV]`` stands for ``26``, ``27``, ``33``, ``34`` or ``35``
      depending on the interpreter used

8. Verify that continuous integration tests pass. The package has continuous
   integration configured for Linux (via `Travis <http://www.travis-ci.org>`_)
   and for Microsoft Windows (via `Appveyor <http://www.appveyor.com>`_).
   Aggregation/cloud code coverage is configured via
   `Codecov <https://codecov.io>`_

9. Document the new feature or bug fix (if needed). The script
   :bash:`${PUTIL_DIR}/sbin/build_docs.py` re-builds the whole package
   documentation (re-generates images, cogs source files, etc.):

	.. [[[cog ste('build_docs.py -h', 0, mdir, cog.out) ]]]

	.. code-block:: bash

	    $ ${PUTIL_DIR}/sbin/build_docs.py -h
	    usage: build_docs.py [-h] [-d DIRECTORY] [-r]
	                         [-n NUM_CPUS] [-t]
	                         [module_name [module_name ...]]

	    Build putil package documentation

	    positional arguments:
	      module_name           Module name for which to build
	                            documentation for

	    optional arguments:
	      -h, --help            show this help message and exit
	      -d DIRECTORY, --directory DIRECTORY
	                            specify source file directory
	                            (default ../putil)
	      -r, --rebuild         rebuild exceptions documentation.
	                            If no module name is given all
	                            modules with auto-generated
	                            exceptions documentation are
	                            rebuilt
	      -n NUM_CPUS, --num-cpus NUM_CPUS
	                            number of CPUs to use (default: 1)
	      -t, --test            diff original and rebuilt file(s)
	                            (exit code 0 indicates file(s) are
	                            identical, exit code 1 indicates
	                            file(s) are different)


	.. [[[end]]]

    Output of shell commands can be automatically included in reStructuredText
    source files with the help of Cog_ and the :code:`docs.support.term_echo` module.

    .. autofunction:: docs.support.term_echo.ste
        :noindex:

    .. autofunction:: docs.support.term_echo.term_echo
        :noindex:

    Similarly Python files can be included in docstrings with the help of Cog_
    and the :code:`docs.support.incfile` module

    .. autofunction:: docs.support.incfile.incfile
        :noindex:

.. rubric:: Footnotes

.. [#f1] All examples are for the `bash <https://www.gnu.org/software/bash/>`_
   shell

.. [#f2] It appears that Scipy dependencies do not include Numpy (as they
   should) so running the tests via Setuptools will typically result in an
   error. The putil requirement file specifies Numpy before Scipy and this
   installation order is honored by Tox so running the tests via Tox sidesteps
   Scipy's broken dependency problem but requires Tox to be installed before
   running the tests (Setuptools installs Tox if needed)

.. [#f3] It is assumed that all the Python interpreters are in the executables
   path. Source code for the interpreters can be downloaded from Python's main
   `site <http://www.python.org/downloads>`_

.. [#f4] Tox configuration largely inspired by
   `Ionel's codelog <http://blog.ionelmc.ro/2015/04/14/
   tox-tricks-and-patterns/>`_

.. include:: ../CHANGELOG.rst

License
=======

.. include:: ../LICENSE
