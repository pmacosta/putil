﻿# setup.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0904,W0201

# Taken in large part from http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
# With additional hint from http://oddbird.net/set-your-code-free-preso/
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
		errno = pytest.main(self.test_args)
		sys.exit(errno)


###
# Processing
###
#	install_requires=['cogapp>=2.4',
#	                  'funcsigs>=0.4',
#	                  'matplotlib>=1.4.2',
#	                  'numpy>=1.8.2',
#	                  'PyContracts>=1.7.1',
#	                  'pytest>=2.6.3',
#	                  'scipy>=0.14.0'
#	                 ],
setup(
	name='putil',
	version='0.9',
	url='http://github.com/pmacosta/putil/',
	license='MIT',
	author='Pablo Acosta-Serafini',
	test_requires=[
		           'cogapp',
	               'funcsigs',
	               'mock',
	               'numpy',
	               'PyContracts',
	               'pytest>',
	              ],
	install_requires=['cogapp>=2.4',
	                  'funcsigs>=0.4',
	                  'numpy>=1.8.2',
	                  'mock>=1.0.1',
	                  'PyContracts>=1.7.1',
	                  'pytest>=2.6.3',
	                 ],
	cmdclass={'test': PyTest},
	author_email='pmacosta@yahoo.com',
	description='This library provides a collection of utility modules to supplement the excellent Python standard library',
	long_description=LONG_DESCRIPTION,
	packages=['putil'],
	include_package_data=True,
	platforms='any',
	classifiers=[
		         'Programming Language :: Python',
		         'Programming Language :: Python :: 2.7',
	             'Development Status :: 4 - Beta',
	             'Natural Language :: English',
	             'Environment :: Web Environment',
	             'Intended Audience :: Developers',
	             'License :: OSI Approved :: MIT License',
	             'Operating System :: OS Independent',
	             'Topic :: Software Development :: Libraries :: Python Modules',
	            ],
	extras_require={
		'testing':[
			       'mock',
				   'PyContracts',
			       'pytest'
		          ],
	}
)