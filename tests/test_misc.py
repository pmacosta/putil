# test_misc.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0302

"""
putil.misc unit tests
"""

import os
import mock
import numpy
import pytest
import struct
import tempfile

import putil.misc
import putil.test

def test_ignored():
	""" Test ignored context manager """
	with tempfile.NamedTemporaryFile(delete=False) as fobj:
		with open(fobj.name, 'w') as output_obj:
			output_obj.write('This is a test file')
		assert os.path.exists(fobj.name)
		with putil.misc.ignored(OSError):
			os.remove(fobj.name)
		assert not os.path.exists(fobj.name)
	with putil.misc.ignored(OSError):
		os.remove('_some_file_')


def test_pcolor():
	""" Test pcolor() function """
	assert putil.test.trigger_exception(putil.misc.pcolor, {'text':5, 'color':'red', 'tab':0}, TypeError, 'Argument `text` is not valid')
	assert putil.test.trigger_exception(putil.misc.pcolor, {'text':'hello', 'color':5, 'tab':0}, TypeError, 'Argument `color` is not valid')
	assert putil.test.trigger_exception(putil.misc.pcolor, {'text':'hello', 'color':'red', 'tab':5.1}, TypeError, 'Argument `tab` is not valid')
	assert putil.test.trigger_exception(putil.misc.pcolor, {'text':'hello', 'color':'hello', 'tab':5}, ValueError, 'Unknown color hello')
	assert putil.misc.pcolor('Text', 'none', 5) == '     Text'
	assert putil.misc.pcolor('Text', 'blue', 2) == '\033[34m  Text\033[0m'
	# These statements should not raise any exception
	putil.misc.pcolor('Text', 'RED')
	putil.misc.pcolor('Text', 'NoNe')


def test_binary_string_to_octal_string():	#pylint: disable=C0103
	""" Test binary_string_to_octal_string() function """
	assert putil.misc.binary_string_to_octal_string(''.join([struct.pack('h', num) for num in range(1, 15)])) == '\\1\\0\\2\\0\\3\\0\\4\\0\\5\\0\\6\\0\\a\\0\\b\\0\\t\\0\\n\\0\\v\\0\\f\\0\\r\\0\\16\\0'


def test_char_string_to_decimal_string():	#pylint: disable=C0103
	""" Test char_string_to_decimal_string() function """
	assert putil.misc.char_to_decimal('Hello world!') == '72 101 108 108 111 32 119 111 114 108 100 33'


def test_isnumber():	#pylint: disable=C0103
	""" Test isnumber() function """
	assert putil.misc.isnumber(5) == True
	assert putil.misc.isnumber(1.5) == True
	assert putil.misc.isnumber(complex(3.2, 9.5)) == True
	assert putil.misc.isnumber(True) == False


def test_isreal():	#pylint: disable=C0103
	""" Test isreal() function """
	assert putil.misc.isreal(5) == True
	assert putil.misc.isreal(1.5) == True
	assert putil.misc.isreal(complex(3.2, 9.5)) == False
	assert putil.misc.isreal(True) == False


def test_prec():	#pylint: disable=C0103
	""" Test prec() function """
	assert putil.test.trigger_exception(putil.misc.per, {'arga':5, 'argb':7, 'prec':'Hello'}, TypeError, 'Argument `prec` is not valid')
	assert putil.test.trigger_exception(putil.misc.per, {'arga':'Hello', 'argb':7, 'prec':1}, TypeError, 'Argument `arga` is not valid')
	assert putil.test.trigger_exception(putil.misc.per, {'arga':5, 'argb':'Hello', 'prec':1}, TypeError, 'Argument `argb` is not valid')
	assert putil.test.trigger_exception(putil.misc.per, {'arga':5, 'argb':[5, 7], 'prec':1}, TypeError, 'Arguments are not of the same type')
	assert putil.misc.per(3, 2, 1) == 0.5
	assert putil.misc.per(3.1, 3.1, 1) == 0
	assert all([test == ref for test, ref in zip(putil.misc.per([3, 1.1, 5], [2, 1.1, 2], 1), [0.5, 0, 1.5])])
	assert all([test == ref for test, ref in zip(putil.misc.per(numpy.array([3, 1.1, 5]), numpy.array([2, 1.1, 2]), 1), [0.5, 0, 1.5])])
	assert putil.misc.per(4, 3, 3) == 0.333
	assert putil.misc.per(4, 0, 3) == 1e20
	assert all([test == ref for test, ref in zip(putil.misc.per(numpy.array([3, 1.1, 5]), numpy.array([2, 0, 2]), 1), [0.5, 1e20, 1.5])])


def test_pgcd():
	""" Test if the custom greatest common divisor function works """
	assert putil.misc.pgcd(48, 18) == 6
	assert putil.misc.pgcd(2.7, 107.3) == 0.1
	assert putil.misc.pgcd(3, 4) == 1
	assert putil.misc.pgcd(0.05, 0.02) == 0.01


def test_isexception():
	""" Test isexception() function """
	assert putil.misc.isexception(str) == False
	assert putil.misc.isexception(3) == False
	assert putil.misc.isexception(RuntimeError) == True

def test_bundle():
	""" Test Bundle class """
	obj = putil.misc.Bundle()
	obj.var1 = 10
	obj.var2 = 20
	assert obj.var1 == 10
	assert obj.var2 == 20
	assert len(obj) == 2
	del obj.var1
	with pytest.raises(AttributeError) as excinfo:
		print obj.var1
	assert excinfo.value.message == "'Bundle' object has no attribute 'var1'"
	assert obj.var2 == 20
	assert len(obj) == 1
	obj = putil.misc.Bundle(var3=30, var4=40, var5=50)
	assert obj.var3 == 30	#pylint: disable=E1101
	assert obj.var4 == 40	#pylint: disable=E1101
	assert obj.var5 == 50	#pylint: disable=E1101
	assert len(obj) == 3
	assert str(obj) == 'var3 = 30\nvar4 = 40\nvar5 = 50'
	assert repr(obj) == 'Bundle(var3=30, var4=40, var5=50)'

def test_make_dir(capsys):
	""" Test make_dir() function """
	def mock_os_makedir(file_path):	#pylint: disable=C0111
		print file_path
	with mock.patch('os.makedirs', side_effect=mock_os_makedir):
		putil.misc.make_dir('~/some_dir/some_file.ext')
		stdout, _ = capsys.readouterr()
		assert stdout == '~/some_dir\n'
		putil.misc.make_dir('/some_file.ext')
		stdout, _ = capsys.readouterr()
		assert stdout == ''

