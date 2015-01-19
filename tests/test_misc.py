# test_misc.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0302

"""
putil.misc unit tests
"""

import os
import tempfile

import putil.misc
import putil.test

def test_ignored():
	""" Test ignored context manager """
	test_list = list()
	with tempfile.NamedTemporaryFile(delete=False) as fobj:
		with open(fobj.name, 'w') as output_obj:
			output_obj.write('This is a test file')
		test_list.append(os.path.exists(fobj.name))
		with putil.misc.ignored(OSError):
			os.remove(fobj.name)
		test_list.append(not os.path.exists(fobj.name))
	with putil.misc.ignored(OSError):
		os.remove('_some_file_')
	assert test_list == [True]*len(test_list)


def test_pcolor():
	""" Test pcolor() function """
	test_list = list()
	test_list.append(putil.test.trigger_exception(putil.misc.pcolor, {'text':5, 'color':'red', 'tab':0}, TypeError, 'Argument `text` is not valid'))
	test_list.append(putil.test.trigger_exception(putil.misc.pcolor, {'text':'hello', 'color':5, 'tab':0}, TypeError, 'Argument `color` is not valid'))
	test_list.append(putil.test.trigger_exception(putil.misc.pcolor, {'text':'hello', 'color':'red', 'tab':5.1}, TypeError, 'Argument `tab` is not valid'))
	test_list.append(putil.misc.pcolor('Text', 'none', 5) == '     Text')
	test_list.append(putil.misc.pcolor('Text', 'blue', 2) == '\033[34m  Text\033[0m')
	# These statements should not raise any exception
	putil.misc.pcolor('Text', 'RED')
	putil.misc.pcolor('Text', 'NoNe')
	assert test_list == [True]*len(test_list)


def test_pgcd():
	""" Test if the custom greatest common divisor function works """
	test_list = list()
	test_list.append(putil.misc.pgcd(48, 18) == 6)
	test_list.append(putil.misc.pgcd(2.7, 107.3) == 0.1)
	test_list.append(putil.misc.pgcd(3, 4) == 1)
	test_list.append(putil.misc.pgcd(0.05, 0.02) == 0.01)
	assert test_list == len(test_list)*[True]


def test_isexception():
	""" Test isexception() function """
	test_list = list()
	test_list.append(putil.misc.isexception(str) == False)
	test_list.append(putil.misc.isexception(3) == False)
	test_list.append(putil.misc.isexception(RuntimeError) == True)
	assert test_list == [True]*len(test_list)


