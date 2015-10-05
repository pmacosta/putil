# setup.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E1111,R0904,W0201

# Taken in large part from:
#    http://www.jeffknupp.com/blog/2013/08/16/
#    open-sourcing-a-python-project-the-right-way/
# With additional hints from:
#     http://oddbird.net/set-your-code-free-preso/
# The function to get the version number from __init__.py is from:
#     https://python-packaging-user-guide.readthedocs.org/
#     en/latest/single_source_version/
from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as TestCommand
import glob
import io
import os
import re
import sys


###
# Functions
###
def find_version(*file_paths):
    """ Get version number from package __init__.py file """
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string")


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


def load_requirements(pkg_dir, libs):
    """ Get package names from requirements.txt file """
    with open(os.path.join(pkg_dir, 'requirements.txt'), 'r') as fobj:
        lines = [item.strip() for item in fobj.readlines()]
    regexps = [
        re.compile('^{}[>=]*'.format(item))
        for item in libs
        if not item.startswith('#')
    ]
    return [
        item
        for item in lines
        if any([regexp.match(item) for regexp in regexps])
    ]


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
REPO = 'http://bitbucket.org/pacosta/{pkg_name}/'.format(pkg_name=PKG_NAME)
AUTHOR = 'Pablo Acosta-Serafini'
AUTHOR_EMAIL = 'pmacosta@yahoo.com'
PKG_DIR = os.path.abspath(os.path.dirname(__file__))
LONG_DESCRIPTION = read(
    os.path.join(PKG_DIR, 'README.rst'),
    os.path.join(PKG_DIR, 'CHANGELOG.rst')
)
SHORT_DESC = get_short_desc(LONG_DESCRIPTION)
RST_FILES = glob.glob(os.path.join(PKG_DIR, 'docs', '*.rst'))
SHARE_DIR = os.path.join('usr', 'share', PKG_NAME)
DOCS_DIR = os.path.join(SHARE_DIR, 'docs')
TESTS_DIR = os.path.join(SHARE_DIR, 'tests')
SBIN_DIR = os.path.join(SHARE_DIR, 'sbin')

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
INSTALL_REQUIRES = load_requirements(
    PKG_DIR,
    ['decorator', 'matplotlib', 'numpy', 'Pillow', 'PyContracts', 'scipy']
    +
    (['funcsigs', 'mock'] if sys.version_info.major == 2 else [])
)

# package_data is used only for binary packages, i.e.
# $ python setup.py bdist ...
# but NOT when building source packages, i.e.
# $ python setup.py sdist ...
setup(
    name=PKG_NAME,
    version=find_version(os.path.join(PKG_DIR, PKG_NAME, '__init__.py')),
    url=REPO,
    license='MIT',
    author=AUTHOR,
    tests_require=['tox>=1.9.0'],
    install_requires=INSTALL_REQUIRES,
    cmdclass={'tests':Tox},
    author_email=AUTHOR_EMAIL,
    description=SHORT_DESC,
    include_package_data=True,
    long_description=LONG_DESCRIPTION,
    packages=[
        PKG_NAME,
        '{pkg_name}.plot'.format(pkg_name=PKG_NAME),
        '{pkg_name}.pcsv'.format(pkg_name=PKG_NAME)
    ],
    data_files=[
        (
            SHARE_DIR,
            [os.path.join(PKG_DIR, 'README.rst')],
        ),
        (
            SBIN_DIR,
            glob.glob(os.path.join(PKG_DIR, 'sbin', '*')),
        ),
        (
            DOCS_DIR,
            RST_FILES+[
                os.path.join(PKG_DIR, 'docs', '__init__.py'),
                os.path.join(PKG_DIR, 'docs', 'conf.py'),
                os.path.join(PKG_DIR, 'docs', 'make.bat'),
                os.path.join(PKG_DIR, 'docs', 'Makefile'),
            ],
        ),
        (
            os.path.join(DOCS_DIR, '_static'),
            [os.path.join(PKG_DIR, 'docs', '_static', '.keepdir')],
        ),
        (
            os.path.join(DOCS_DIR, 'support'),
            glob.glob(os.path.join(PKG_DIR, 'docs', 'support', '*.py'))
        ),
        (
            os.path.join(DOCS_DIR, 'support'),
            glob.glob(os.path.join(PKG_DIR, 'docs', 'support', '*.csv'))
        ),
        (
            os.path.join(DOCS_DIR, 'support'),
            glob.glob(os.path.join(PKG_DIR, 'docs', 'support', '*.png'))
        ),
        (
            os.path.join(DOCS_DIR, 'support'),
            glob.glob(os.path.join(PKG_DIR, 'docs', 'support', '*.odg'))
        ),
        (
            os.path.join(DOCS_DIR, 'support'),
            glob.glob(os.path.join(PKG_DIR, 'docs', 'support', '*.sh'))
        ),
        (
            TESTS_DIR,
            glob.glob(os.path.join(PKG_DIR, 'tests', 'pytest.ini'))
        ),
        (
            TESTS_DIR,
            glob.glob(os.path.join(PKG_DIR, 'tests', '*.py'))
        ),
        (
            os.path.join(TESTS_DIR, 'plot'),
            glob.glob(os.path.join(PKG_DIR, 'tests', 'plot', '*.py'))
        ),
        (
            os.path.join(TESTS_DIR, 'pcsv'),
            glob.glob(os.path.join(PKG_DIR, 'tests', 'pcsv', '*.py'))
        ),
        (
            os.path.join(TESTS_DIR, 'support'),
            glob.glob(os.path.join(PKG_DIR, 'tests', 'support', '*.py'))
        ),
        (
            os.path.join(TESTS_DIR, 'support', 'ref_images'),
            glob.glob(
                os.path.join(
                    PKG_DIR, 'tests', 'support', 'ref_images', '*.png'
                )
            )
        ),
        (
            os.path.join(TESTS_DIR, 'support', 'ref_images_ci'),
            glob.glob(
                os.path.join(
                    PKG_DIR, 'tests', 'support', 'ref_images_ci', '*.png'
                )
           )
        ),
    ],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
