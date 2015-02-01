# test_misc.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0302,C0111

import os
import sys
import mock
import numpy
import pytest
import struct
import inspect
import datetime
import tempfile
import fractions

import putil.misc
import putil.pcsv
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
	putil.test.assert_exception(putil.misc.pcolor, {'text':5, 'color':'red', 'tab':0}, TypeError, 'Argument `text` is not valid')
	putil.test.assert_exception(putil.misc.pcolor, {'text':'hello', 'color':5, 'tab':0}, TypeError, 'Argument `color` is not valid')
	putil.test.assert_exception(putil.misc.pcolor, {'text':'hello', 'color':'red', 'tab':5.1}, TypeError, 'Argument `tab` is not valid')
	putil.test.assert_exception(putil.misc.pcolor, {'text':'hello', 'color':'hello', 'tab':5}, ValueError, 'Unknown color hello')
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
	putil.test.assert_exception(putil.misc.per, {'arga':5, 'argb':7, 'prec':'Hello'}, TypeError, 'Argument `prec` is not valid')
	putil.test.assert_exception(putil.misc.per, {'arga':'Hello', 'argb':7, 'prec':1}, TypeError, 'Argument `arga` is not valid')
	putil.test.assert_exception(putil.misc.per, {'arga':5, 'argb':'Hello', 'prec':1}, TypeError, 'Argument `argb` is not valid')
	putil.test.assert_exception(putil.misc.per, {'arga':5, 'argb':[5, 7], 'prec':1}, TypeError, 'Arguments are not of the same type')
	assert putil.misc.per(3, 2, 1) == 0.5
	assert putil.misc.per(3.1, 3.1, 1) == 0
	assert all([test == ref for test, ref in zip(putil.misc.per([3, 1.1, 5], [2, 1.1, 2], 1), [0.5, 0, 1.5])])
	assert all([test == ref for test, ref in zip(putil.misc.per(numpy.array([3, 1.1, 5]), numpy.array([2, 1.1, 2]), 1), [0.5, 0, 1.5])])
	assert putil.misc.per(4, 3, 3) == 0.333
	assert putil.misc.per(4, 0, 3) == 1e20
	assert all([test == ref for test, ref in zip(putil.misc.per(numpy.array([3, 1.1, 5]), numpy.array([2, 0, 2]), 1), [0.5, 1e20, 1.5])])


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


def test_normalize():
	""" Test normalize() function """
	putil.test.assert_exception(putil.misc.normalize, {'value':5, 'series':[2, 5], 'offset':10}, ValueError, 'Argument `offset` has to be in the [0.0, 1.0] range')
	putil.test.assert_exception(putil.misc.normalize, {'value':0, 'series':[2, 5], 'offset':0}, ValueError, 'Argument `value` has to be within the bounds of argument `series`')
	assert putil.misc.normalize(15, [10, 20]) == 0.5
	assert putil.misc.normalize(15, [10, 20], 0.5) == 0.75


def test_gcd():
	""" Test gcd() function """
	assert putil.misc.gcd([]) == None
	assert putil.misc.gcd([7]) == 7
	assert putil.misc.gcd([48, 18]) == 6
	assert putil.misc.gcd([20, 12, 16]) == 4
	assert putil.misc.gcd([0.05, 0.02, 0.1]) == 0.01
	assert putil.misc.gcd([fractions.Fraction(5, 3), fractions.Fraction(2, 3), fractions.Fraction(10, 3)]) == fractions.Fraction(1, 3)


def test_pgcd():
	""" Test pgcd() function """
	assert putil.misc.pgcd(48, 18) == 6
	assert putil.misc.pgcd(2.7, 107.3) == 0.1
	assert putil.misc.pgcd(3, 4) == 1
	assert putil.misc.pgcd(0.05, 0.02) == 0.01
	assert putil.misc.pgcd(5, 2) == 1
	assert putil.misc.pgcd(fractions.Fraction(5, 3), fractions.Fraction(2, 3)) == fractions.Fraction(1, 3)


def test_isalpha():
	""" Test isalpha() function """
	assert putil.misc.isalpha('1.5') == True
	assert putil.misc.isalpha('1E-20') == True
	assert putil.misc.isalpha('1EA-20') == False


def test_ishex():
	""" Test ishex() function """
	assert putil.misc.ishex(5) == False
	assert putil.misc.ishex('45') == False
	assert putil.misc.ishex('F') == True


def test_smart_round():
	""" Test smart_round() function """
	assert putil.misc.smart_round(None) == None
	assert putil.misc.smart_round(1.3333, 2) == 1.33
	assert (putil.misc.smart_round(numpy.array([1.3333, 2.666666]), 2) == numpy.array([1.33, 2.67])).all()

def test_isiterable():
	""" Test isiterable() function """
	assert putil.misc.isiterable([1, 2, 3]) == True
	assert putil.misc.isiterable({'a':5}) == True
	assert putil.misc.isiterable(set([1, 2, 3])) == True
	assert putil.misc.isiterable(3) == False


def test_pprint_vector():
	""" Test pprint_vector() function """
	assert putil.misc.pprint_vector(None) == 'None'
	assert putil.misc.pprint_vector([1, 2, 3, 4, 5, 6, 7, 8]) == '[ 1, 2, 3, 4, 5, 6, 7, 8 ]'
	assert putil.misc.pprint_vector([1, 2, 3, 4, 5, 6, 7, 8], indent=20) == '[ 1, 2, 3, 4, 5, 6, 7, 8 ]'
	assert putil.misc.pprint_vector([1, 2, 3, 4, 5, 6, 7, 8], limit=True) == '[ 1, 2, 3, ..., 6, 7, 8 ]'
	assert putil.misc.pprint_vector([1, 2, 3, 4, 5, 6, 7, 8], limit=True, indent=20) == '[ 1, 2, 3, ..., 6, 7, 8 ]'
	assert putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 0.8], eng=True) == '[    1.000m,   20.000u,  300.000M,    4.000p,    5.250k,   -6.000n,  700.000 ,  800.000m ]'
	assert putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 0.8], eng=True, indent=20) == '[    1.000m,   20.000u,  300.000M,    4.000p,    5.250k,   -6.000n,  700.000 ,  800.000m ]'
	assert putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 0.8], limit=True, eng=True) == '[    1.000m,   20.000u,  300.000M, ...,   -6.000n,  700.000 ,  800.000m ]'
	assert putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 0.8], limit=True, eng=True, indent=20) == '[    1.000m,   20.000u,  300.000M, ...,   -6.000n,  700.000 ,  800.000m ]'
	assert putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 0.8], eng=True, mant=1) == '[    1.0m,   20.0u,  300.0M,    4.0p,    5.3k,   -6.0n,  700.0 ,  800.0m ]'
	assert putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 0.8], eng=True, mant=1, indent=20) == '[    1.0m,   20.0u,  300.0M,    4.0p,    5.3k,   -6.0n,  700.0 ,  800.0m ]'
	assert putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 0.8], limit=True, eng=True, mant=1) == '[    1.0m,   20.0u,  300.0M, ...,   -6.0n,  700.0 ,  800.0m ]'
	assert putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 0.8], limit=True, indent=20, eng=True, mant=1) == '[    1.0m,   20.0u,  300.0M, ...,   -6.0n,  700.0 ,  800.0m ]'
	assert putil.misc.pprint_vector([1, 2, 3, 4, 5, 6, 7, 8], width=8) == '[ 1, 2,\n  3, 4,\n  5, 6,\n  7, 8 ]'
	assert putil.misc.pprint_vector([1, 2, 3, 4, 5, 6, 7, 8], width=10) == '[ 1, 2, 3,\n  4, 5, 6,\n  7, 8 ]'
	assert putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 8, 9], width=20, eng=True, mant=0) == '[    1m,   20u,\n   300M,    4p,\n     5k,   -6n,\n   700 ,    8 ,\n     9  ]'
	assert putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 0.8], width=30, eng=True, mant=1) == '[    1.0m,   20.0u,  300.0M,\n     4.0p,    5.3k,   -6.0n,\n   700.0 ,  800.0m ]'
	assert putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 8, 9], width=20, eng=True, mant=0, limit=True) == '[    1m,\n    20u,\n   300M,\n   ...\n   700 ,\n     8 ,\n     9  ]'
	assert putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 8, 9], width=30, eng=True, mant=1, limit=True) == '[    1.0m,   20.0u,  300.0M,\n             ...\n   700.0 ,    8.0 ,    9.0  ]'
	header = 'Vector: '
	assert header+putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 8, 9], width=30, eng=True, mant=1, limit=True, indent=len(header)) == \
		'Vector: [    1.0m,   20.0u,  300.0M,\n                     ...\n           700.0 ,    8.0 ,    9.0  ]'
	assert header+putil.misc.pprint_vector([1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 0.8], width=30, eng=True, mant=1, indent=len(header)) == \
		'Vector: [    1.0m,   20.0u,  300.0M,\n             4.0p,    5.3k,   -6.0n,\n           700.0 ,  800.0m ]'
	putil.test.assert_exception(putil.misc.pprint_vector, {'vector':[1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 8, 9], 'width':5, 'eng':True, 'mant':1, 'limit':True}, ValueError, 'Argument `width` is too small')


def test_split_every():
	""" Test split_every() function """
	assert putil.misc.split_every('a, b, c, d', ',', 1) == ['a', ' b', ' c', ' d']
	assert putil.misc.split_every('a , b , c , d ', ',', 1) == ['a ', ' b ', ' c ', ' d ']
	assert putil.misc.split_every('a , b , c , d ', ',', 1, lstrip=True) == ['a ', 'b ', 'c ', 'd ']
	assert putil.misc.split_every('a , b , c , d ', ',', 1, rstrip=True) == ['a', ' b', ' c', ' d']
	assert putil.misc.split_every('a , b , c , d ', ',', 1, lstrip=True, rstrip=True) == ['a', 'b', 'c', 'd']
	assert putil.misc.split_every('a, b, c, d', ',', 2) == ['a, b', ' c, d']
	assert putil.misc.split_every('a, b, c, d', ',', 3) == ['a, b, c', ' d']
	assert putil.misc.split_every('a, b, c, d', ',', 4) == ['a, b, c, d']
	assert putil.misc.split_every('a, b, c, d', ',', 5) == ['a, b, c, d']


def test_ellapsed_time_string():
	""" Test ellapsed_time_string() function """
	assert putil.misc.elapsed_time_string(datetime.datetime(2015, 1, 1), datetime.datetime(2015, 1, 1)) == 'None'
	putil.test.assert_exception(putil.misc.elapsed_time_string, {'start_time':datetime.datetime(2015, 2, 1), 'stop_time':datetime.datetime(2015, 1, 1)}, RuntimeError, 'Invalid time delta specification')
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1), datetime.datetime(2015, 1, 1)) == '1 year'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1), datetime.datetime(2016, 1, 1)) == '2 years'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1), datetime.datetime(2014, 1, 31)) == '1 month'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1), datetime.datetime(2014, 3, 2)) == '2 months'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1, 10), datetime.datetime(2014, 1, 1, 11)) == '1 hour'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1, 10), datetime.datetime(2014, 1, 1, 12)) == '2 hours'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1, 1, 10), datetime.datetime(2014, 1, 1, 1, 11)) == '1 minute'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1, 1, 10), datetime.datetime(2014, 1, 1, 1, 12)) == '2 minutes'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1, 1, 10, 1), datetime.datetime(2014, 1, 1, 1, 10, 2)) == '1 second'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1, 1, 10, 1), datetime.datetime(2014, 1, 1, 1, 10, 3)) == '2 seconds'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1, 1, 10, 1), datetime.datetime(2015, 1, 1, 1, 10, 2)) == '1 year and 1 second'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1, 1, 10, 1), datetime.datetime(2015, 1, 1, 1, 10, 3)) == '1 year and 2 seconds'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1, 1, 10, 1), datetime.datetime(2015, 1, 2, 1, 10, 3)) == '1 year, 1 day and 2 seconds'
	assert putil.misc.elapsed_time_string(datetime.datetime(2014, 1, 1, 1, 10, 1), datetime.datetime(2015, 1, 3, 1, 10, 3)) == '1 year, 2 days and 2 seconds'

def test_tmp_file():
	""" Test TmpFile context manager """
	def write_data(file_handle):	#pylint: disable=C0111
		file_handle.write('Hello world!')
	# Test argument validation
	with pytest.raises(TypeError) as excinfo:
		with putil.misc.TmpFile(5) as file_name:
			pass
	assert excinfo.value.message == 'Argument `fpointer` is not valid'
	# Test behavior when no function pointer is given
	with putil.misc.TmpFile() as file_name:
		assert isinstance(file_name, str) and (len(file_name) > 0)
		assert os.path.exists(file_name)
	assert not os.path.exists(file_name)
	# Test that exceptions within the with statement are re-raised
	with pytest.raises(OSError) as excinfo:
		with putil.misc.TmpFile(write_data) as file_name:
			raise OSError('No data')
	assert excinfo.value.message == 'No data'
	assert not os.path.exists(file_name)
	# Test behaviour under "normal" circumstances
	with putil.misc.TmpFile(write_data) as file_name:
		with open(file_name, 'r') as fobj:
			line = fobj.readlines()
		assert line == ['Hello world!']
		assert os.path.exists(file_name)
	assert not os.path.exists(file_name)

def test_strframe():
	""" Test strframe() function """
	def check_basic_frame(lines):
		assert lines[0].startswith('\x1b[33mFrame object ID: 0x')
		assert lines[1] == 'File name......: /home/pacosta/python/putil/tests/test_misc.py'
		assert lines[2].startswith('Line number....: ')
		assert lines[3] == 'Function name..: test_strframe'
		assert lines[4] == r"Context........: ['\tfobj = inspect.stack()[0]\n']"
		assert lines[5] == 'Index..........: 0'
	fobj = inspect.stack()[0]
	lines = putil.misc.strframe(fobj).split('\n')
	check_basic_frame(lines)
	assert len(lines) == 6
	lines = [line for num, line in enumerate(putil.misc.strframe(fobj, extended=True).split('\n')) if (num < 6) or line.startswith('f_')]
	check_basic_frame(lines)
	assert lines[6].startswith('f_back ID......: 0x')
	assert lines[7].startswith('f_builtins.....: {')
	assert lines[8].startswith('f_code.........: <code object test_strframe at 0x')
	assert lines[9].startswith('f_globals......: {')
	assert lines[10] == 'f_lasti........: 356'
	assert lines[11].startswith('f_lineno.......: ')
	assert lines[12].startswith('f_locals.......: {')
	assert lines[13] == 'f_restricted...: False'
	assert lines[14] == 'f_trace........: None'
	assert len(lines) == 15


def test_quote_str():
	""" Test quote_str() function """
	assert putil.misc.quote_str(5) == 5
	assert putil.misc.quote_str('Hello!') == '"Hello!"'
	assert putil.misc.quote_str('He said "hello!"') == "'He said \"hello!\"'"


def test_strtype_item():
	""" Test strtype_item() function """
	assert putil.misc.strtype_item(str) == 'str'
	assert putil.misc.strtype_item('hello') == '"hello"'
	assert putil.misc.strtype_item(5) == '5'
	assert putil.misc.strtype_item(putil.pcsv.CsvFile) == 'putil.pcsv.CsvFile'


def test_strtype():
	""" Test strtype() function """
	assert putil.misc.strtype(str) == 'str'
	assert putil.misc.strtype('hello') == '"hello"'
	assert putil.misc.strtype(5) == '5'
	assert putil.misc.strtype(putil.pcsv.CsvFile) == 'putil.pcsv.CsvFile'
	assert putil.misc.strtype([str, 5, putil.pcsv.CsvFile]) == '[str, 5, putil.pcsv.CsvFile]'
	assert putil.misc.strtype(set([str, 5, putil.pcsv.CsvFile])) == 'set(5, str, putil.pcsv.CsvFile)'
	assert putil.misc.strtype((str, 5, putil.pcsv.CsvFile)) == '(str, 5, putil.pcsv.CsvFile)'
	assert putil.misc.strtype({'file':str, 'name':'some_file.txt', 'line':5, 'class':putil.pcsv.CsvFile}) == '{"class":putil.pcsv.CsvFile, "file":str, "line":5, "name":"some_file.txt"}'


def test_flatten_list():
	""" Test flatten_list() function """
	assert putil.misc.flatten_list([1, 2, 3]) == [1, 2, 3]
	assert putil.misc.flatten_list([1, [2, 3, 4], 5]) == [1, 2, 3, 4, 5]
	assert putil.misc.flatten_list([1, [2, 3, [4, 5, 6]], 7]) == [1, 2, 3, 4, 5, 6, 7]
	assert putil.misc.flatten_list([1, [2, 3, [4, [5, 6, 7], 8, 9]], [10, 11], 12]) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


def test_delete_module():
	""" Test delete_module() function """
	putil.test.assert_exception(putil.misc.delete_module, {'modname':'not_a_module'}, ValueError, 'Module not_a_module is not imported')
	putil.misc.delete_module('putil.pcsv')
	assert 'putil.pcsv' not in sys.modules


def test_to_scientific_string():
	""" Test _to_scientific() function """
	# Standard floating point mantissa length appears to be 12 digits
	# Positive
	assert putil.misc.to_scientific_string('5.35E+3') == '5.35E+3'
	assert putil.misc.to_scientific_string(0) == '0E+0'
	assert putil.misc.to_scientific_string(0.1) == '1E-1'
	assert putil.misc.to_scientific_string(0.01) == '1E-2'
	assert putil.misc.to_scientific_string(0.001) == '1E-3'
	assert putil.misc.to_scientific_string(0.00101) == '1.01E-3'
	assert putil.misc.to_scientific_string(0.123456789012) == '1.23456789012E-1'
	assert putil.misc.to_scientific_string(1234567.89012) == '1.23456789012E+6'
	assert putil.misc.to_scientific_string(1) == '1E+0'
	assert putil.misc.to_scientific_string(20) == '2E+1'
	assert putil.misc.to_scientific_string(200) == '2E+2'
	assert putil.misc.to_scientific_string(333) == '3.33E+2'
	assert putil.misc.to_scientific_string(4567) == '4.567E+3'
	assert putil.misc.to_scientific_string(4567.890) == '4.56789E+3'
	# Negative
	assert putil.misc.to_scientific_string(-0.1) == '-1E-1'
	assert putil.misc.to_scientific_string(-0.01) == '-1E-2'
	assert putil.misc.to_scientific_string(-0.001) == '-1E-3'
	assert putil.misc.to_scientific_string(-0.00101) == '-1.01E-3'
	assert putil.misc.to_scientific_string(-0.123456789012) == '-1.23456789012E-1'
	assert putil.misc.to_scientific_string(-1234567.89012) == '-1.23456789012E+6'
	assert putil.misc.to_scientific_string(-1) == '-1E+0'
	assert putil.misc.to_scientific_string(-20) == '-2E+1'
	assert putil.misc.to_scientific_string(-200) == '-2E+2'
	assert putil.misc.to_scientific_string(-333) == '-3.33E+2'
	assert putil.misc.to_scientific_string(-4567) == '-4.567E+3'
	assert putil.misc.to_scientific_string(-4567.890) == '-4.56789E+3'

