# setup.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0904,W0201,E1111

# Taken in large part from
# http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
# With additional hints from http://oddbird.net/set-your-code-free-preso/
from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as TestCommand
import glob
import io
import os
import sys


###
# Functions
###
def read(*filenames, **kwargs):
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
PKG_DIR = os.path.dirname(__file__)
LONG_DESCRIPTION = read(
    os.path.join(PKG_DIR, 'README.rst'),
    os.path.join(PKG_DIR, 'CHANGELOG.rst')
)
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
INSTALL_REQUIRES = [
    'decorator>=3.4.2',
    'matplotlib>=1.4.2',
    'numpy>=1.8.2',
    'Pillow>=2.6.1',
    'PyContracts>=1.7.6',
    'scipy>=0.14.0',
]

if sys.version_info.major == 2:
    INSTALL_REQUIRES.append(
        [
            'funcsigs>=0.4',
        ]
    )

# package_data is used only for binary packages, i.e.
# $ python setup.py bdist ...
# but NOT when building source pacakges, i.e.
# $ python setup.py sdist ...
setup(
    name=PKG_NAME,
    version='0.9.0.5',
    url='http://bitbucket.org/pacosta/{pkg_name}/'.format(pkg_name=PKG_NAME),
    license='MIT',
    author='Pablo Acosta-Serafini',
    tests_require=['tox>=1.9.0'],
    install_requires=INSTALL_REQUIRES,
    cmdclass={'tests':Tox},
    author_email='pmacosta@yahoo.com',
    description=(
        'This library provides a collection of utility modules to '
        'supplement the Python standard library'
    ),
    include_package_data=True,
    long_description=LONG_DESCRIPTION,
    packages=[PKG_NAME, '{pkg_name}.plot'.format(pkg_name=PKG_NAME)],
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
