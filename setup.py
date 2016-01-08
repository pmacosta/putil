# setup.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E1111,R0904,W0122,W0201,W0621

# Taken in large part from:
#    http://www.jeffknupp.com/blog/2013/08/16/
#    open-sourcing-a-python-project-the-right-way/
# With additional hints from:
#     http://oddbird.net/set-your-code-free-preso/
# The function to get the version number from __init__.py is from:
#     https://python-packaging-user-guide.readthedocs.org/
#     en/latest/single_source_version/
# Standard library imports
from __future__ import print_function
import io
import glob
import os
import sys
# PyPI imports
from setuptools import setup
from setuptools.command.test import test as TestCommand
# Putil imports
from sbin.functions import (
    SUPPORTED_VERS, get_pkg_data_files, load_requirements, python_version
)


###
# Supported interpreter check
###
PYTHON_VER = python_version('{0:0x}'.format(sys.hexversion & 0xFFFF0000)[:-4])
if PYTHON_VER not in SUPPORTED_VERS:
    sys.exit(
        'Supported interpreter versions: {0}'.format(', '.join(SUPPORTED_VERS))
    )


###
# Functions
###
def get_short_desc(long_desc):
    """ Get first sentence of first paragraph of long description """
    found = False
    olines = []
    for line in [item.rstrip() for item in long_desc.split('\n')]:
        if (found and (((not line) and (not olines))
           or (line and olines))):
            olines.append(line)
        elif found and olines and (not line):
            return (' '.join(olines).split('.')[0]).strip()
        found = line == '.. [[[end]]]' if not found else found


def read(*filenames, **kwargs):
    """ Read plain text file(s) """
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as fobj:
            buf.append(fobj.read())
    return sep.join(buf)


###
# Global variables
###
PKG_NAME = 'putil'
REPO = 'http://github.com/pmacosta/{pkg_name}/'.format(pkg_name=PKG_NAME)
AUTHOR = 'Pablo Acosta-Serafini'
AUTHOR_EMAIL = 'pmacosta@yahoo.com'
PKG_DIR = os.path.abspath(os.path.dirname(__file__))
LONG_DESCRIPTION = read(
    os.path.join(PKG_DIR, 'README.rst'),
    os.path.join(PKG_DIR, 'CHANGELOG.rst')
)
SHORT_DESC = get_short_desc(LONG_DESCRIPTION)
# Actual directory is os.join(sys.prefix, 'share', PKG_NAME)
SHARE_DIR = os.path.join('share', PKG_NAME)
INSTALL_REQUIRES = load_requirements(PKG_DIR, PYTHON_VER, 'source')
TESTING_REQUIRES = load_requirements(PKG_DIR, PYTHON_VER, 'testing')
try:
    DATA_FILES = get_pkg_data_files(SHARE_DIR)
except IOError:
    print('PKG_DIR: {0}'.format(PKG_DIR))
    print('Contents:')
    print(glob.glob(os.path.join(PKG_DIR, '*')))
    print('PKG_DIR/data')
    print('Contents:')
    print(glob.glob(os.path.join(PKG_DIR, 'data', '*')))
    raise


###
# Extract version (from coveragepy)
###
VERSION_PY = os.path.join(PKG_DIR, 'putil/version.py')
with open(VERSION_PY) as fobj:
    __version__ = VERSION_INFO = ""
    # Execute the code in version.py.
    exec(compile(fobj.read(), VERSION_PY, 'exec'))
if VERSION_INFO[3] == 'alpha':
    DEVSTAT = "3 - Alpha"
elif VERSION_INFO[3] in ['beta', 'candidate']:
    DEVSTAT = "4 - Beta"
else:
    assert VERSION_INFO[3] == 'final'
    DEVSTAT = "5 - Production/Stable"


###
# Classes
###
class Tox(TestCommand):
    user_options = [('tox-args=', 'a', 'Arguments to pass to tox')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import shlex
        import tox
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


###
# Processing
###
# package_data is used only for binary packages, i.e.
# $ python setup.py bdist ...
# but NOT when building source packages, i.e.
# $ python setup.py sdist ...
setup(
    name=PKG_NAME,
    version=__version__,
    url=REPO,
    license='MIT',
    author=AUTHOR,
    tests_require=TESTING_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    cmdclass={'tests':Tox},
    author_email=AUTHOR_EMAIL,
    description=SHORT_DESC,
    long_description=LONG_DESCRIPTION,
    packages=[
        PKG_NAME,
        '{pkg_name}.plot'.format(pkg_name=PKG_NAME),
        '{pkg_name}.pcsv'.format(pkg_name=PKG_NAME),
    ],
    data_files=DATA_FILES,
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Development Status :: '+DEVSTAT,
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
