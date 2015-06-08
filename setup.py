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
import io, sys


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
LONG_DESCRIPTION = read('README.rst', 'CHANGELOG.rst')


###
# Classes
###
class PyTest(TestCommand):
	user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

	def initialize_options(self):
		TestCommand.initialize_options(self)
		self.pytest_args = []

	def finalize_options(self):
		TestCommand.finalize_options(self)
		self.test_args = []
		self.test_suite = True

	def run_tests(self):
		import pytest
		#import os, pytest
		#pkg_dir = os.path.dirname(__file__)
		#sys.path += [
		#	os.path.join(pkg_dir, 'sbin'),
		#	os.path.join(pkg_dir, 'tests/support')
		#]
		errno = pytest.main(self.test_args)
		sys.exit(errno)


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
		import shlex, tox
		errno = tox.cmdline(args=shlex.split(self.tox_args))
		sys.exit(errno)


###
# Processing
###
INSTALL_REQUIRES = [
	'decorator>=3.4.2',
	'matplotlib>=1.4.3',
	'numpy>=1.9.2',
	'Pillow>=2.7.0',
	'PyContracts>=1.7.6',
	'scipy>=0.15.1',
]
if sys.version_info.major == 2:
	INSTALL_REQUIRES.append(
		[
			'funcsigs>=0.4',
		]
	)
setup(
	name='putil',
	version='0.9.0.5',
	url='http://bitbucket.org/pacosta/putil/',
	license='MIT',
	author='Pablo Acosta-Serafini',
	tests_require=['cogapp>=2.4',
	               'coverage>=3.7.1',
	               'mock>=1.0.1',
	               'pytest>=2.6.3',
	               'pytest-cov>=1.8.0',
	               'pytest-xdist>=1.8',
	               'tox>=1.9.0',
	              ],
	install_requires=INSTALL_REQUIRES,
	cmdclass={'tests': PyTest},
	author_email='pmacosta@yahoo.com',
	description=('This library provides a collection of utility modules to '
				 'supplement the Python standard library'),
	include_package_data=True,
	long_description=LONG_DESCRIPTION,
	packages=['putil', 'putil.plot', 'tests', 'docs'],
	package_data={'':[
		'tests/support/*.py',
		'tests/support/plot/*.py',
		'tests/support/ref_images/*.png',
		'tests/support/ref_images_ci/*.png',
		'docs/support/*.py'
	]},
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
	             'Topic :: Software Development :: Libraries :: Python Modules',
	            ],
)
