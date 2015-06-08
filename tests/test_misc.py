# test_misc.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,E1101,F0401,R0915,W0621

from __future__ import print_function
import ast
import datetime
import inspect
import mock
import os
import pytest
import re
import struct
import sys
import tempfile
from fractions import Fraction
from numpy import array

import putil.misc
import putil.test
if sys.version_info.major == 2:
	from putil.compat2 import _write
else:
	from putil.compat3 import _write


###
# Tests
###
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
	with pytest.raises(OSError) as excinfo:
		with putil.misc.ignored(RuntimeError):
			os.remove('_some_file_')
	assert excinfo.value.strerror == "No such file or directory"
	assert excinfo.value.filename == '_some_file_'
	assert excinfo.value.errno == 2


def test_timer(capsys):
	""" Test Timer context manager """
	# Test argument validation
	with pytest.raises(RuntimeError) as excinfo:
		with putil.misc.Timer(5):
			pass
	assert putil.test.get_exmsg(excinfo) == 'Argument `verbose` is not valid'
	# Test that exceptions within the with statement are re-raised
	with pytest.raises(RuntimeError) as excinfo:
		with putil.misc.Timer():
			raise RuntimeError('Error in code')
	assert putil.test.get_exmsg(excinfo) == 'Error in code'
	# Test normal operation
	with putil.misc.Timer() as tobj:
		sum(range(100))
	assert isinstance(tobj.elapsed_time, float) and (tobj.elapsed_time > 0)
	tregexp = re.compile(r'Elapsed time: [\d|\.]+\[msec\]')
	with putil.misc.Timer(verbose=True) as tobj:
		sum(range(100))
	out, _ = capsys.readouterr()
	assert tregexp.match(out)


def test_pcolor():
	""" Test pcolor() function """
	putil.test.assert_exception(
		putil.misc.pcolor,
		{'text':5, 'color':'red', 'tab':0},
		RuntimeError,
		'Argument `text` is not valid'
	)
	putil.test.assert_exception(
		putil.misc.pcolor,
		{'text':'hello', 'color':5, 'tab':0},
		RuntimeError,
		'Argument `color` is not valid'
	)
	putil.test.assert_exception(
		putil.misc.pcolor,
		{'text':'hello', 'color':'red', 'tab':5.1},
		RuntimeError,
		'Argument `tab` is not valid'
	)
	putil.test.assert_exception(
		putil.misc.pcolor,
		{'text':'hello', 'color':'hello', 'tab':5},
		ValueError,
		'Unknown color hello'
	)
	assert putil.misc.pcolor('Text', 'none', 5) == '     Text'
	assert putil.misc.pcolor('Text', 'blue', 2) == '\033[34m  Text\033[0m'
	# These statements should not raise any exception
	putil.misc.pcolor('Text', 'RED')
	putil.misc.pcolor('Text', 'NoNe')


def test_binary_string_to_octal_string():
	""" Test binary_string_to_octal_string() function """
	obj = putil.misc.binary_string_to_octal_string
	if sys.version_info.major == 2:
		ref = (
			'\\1\\0\\2\\0\\3\\0\\4\\0\\5\\0\\6\\0\\a\\0'
			'\\b\\0\\t\\0\\n\\0\\v\\0\\f\\0\\r\\0\\16\\0'
		)
		assert obj(
			''.join([struct.pack('h', num) for num in range(1, 15)])
		) == ref
	else:
		ref = (
			r'\o1\0\o2\0\o3\0\o4\0\o5\0\o6\0\a\0'
			r'\b\0\t\0\n\0\v\0\f\0\r\0\o16\0'
		)
		assert obj(
			''.join([struct.pack('h', num).decode('ascii') for num in range(1, 15)])
		) == ref


def test_char_string_to_decimal_string():
	""" Test char_string_to_decimal_string() function """
	ref = '72 101 108 108 111 32 119 111 114 108 100 33'
	assert putil.misc.char_to_decimal('Hello world!') == ref


def test_isnumber():
	""" Test isnumber() function """
	assert putil.misc.isnumber(5)
	assert putil.misc.isnumber(1.5)
	assert putil.misc.isnumber(complex(3.2, 9.5))
	assert not putil.misc.isnumber(True)


def test_isreal():
	""" Test isreal() function """
	assert putil.misc.isreal(5)
	assert putil.misc.isreal(1.5)
	assert not putil.misc.isreal(complex(3.2, 9.5))
	assert not putil.misc.isreal(True)


def test_per():
	""" Test prec() function """
	obj = putil.misc.per
	putil.test.assert_exception(
		obj,
		{'arga':5, 'argb':7, 'prec':'Hello'},
		RuntimeError,
		'Argument `prec` is not valid'
	)
	putil.test.assert_exception(
		obj,
		{'arga':'Hello', 'argb':7, 'prec':1},
		RuntimeError,
		'Argument `arga` is not valid'
	)
	putil.test.assert_exception(
		obj,
		{'arga':5, 'argb':'Hello', 'prec':1},
		RuntimeError,
		'Argument `argb` is not valid'
	)
	putil.test.assert_exception(
		obj,
		{'arga':5, 'argb':[5, 7], 'prec':1},
		TypeError,
		'Arguments are not of the same type'
	)
	assert obj(3, 2, 1) == 0.5
	assert obj(3.1, 3.1, 1) == 0
	ttuple = zip(obj([3, 1.1, 5], [2, 1.1, 2], 1), [0.5, 0, 1.5])
	assert all([test == ref for test, ref in ttuple])
	ttuple = zip(obj(array([3, 1.1, 5]), array([2, 1.1, 2]), 1), [0.5, 0, 1.5])
	assert all([test == ref for test, ref in ttuple])
	assert obj(4, 3, 3) == 0.333
	assert obj(4, 0, 3) == 1e20
	ttuple = zip(obj(array([3, 1.1, 5]), array([2, 0, 2]), 1), [0.5, 1e20, 1.5])
	assert all([test == ref for test, ref in ttuple])


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
		print(obj.var1)
	assert (
		putil.test.get_exmsg(excinfo) ==
		"'Bundle' object has no attribute 'var1'"
	)
	assert obj.var2 == 20
	assert len(obj) == 1
	obj = putil.misc.Bundle(var3=30, var4=40, var5=50)
	assert obj.var3 == 30
	assert obj.var4 == 40
	assert obj.var5 == 50
	assert len(obj) == 3
	assert str(obj) == 'var3 = 30\nvar4 = 40\nvar5 = 50'
	assert repr(obj) == 'Bundle(var3=30, var4=40, var5=50)'


def test_make_dir(capsys):
	""" Test make_dir() function """
	def mock_os_makedir(file_path):
		print(file_path)
	home_dir = os.environ['HOME']
	with mock.patch('os.makedirs', side_effect=mock_os_makedir):
		fname = os.path.join(home_dir, 'some_dir', 'some_file.ext')
		putil.misc.make_dir(fname)
		stdout, _ = capsys.readouterr()
		assert stdout == os.path.dirname(fname)+'\n'
		putil.misc.make_dir(os.path.join(os.path.abspath(os.sep), 'some_file.ext'))
		stdout, _ = capsys.readouterr()
		assert stdout == ''


def test_normalize():
	""" Test normalize() function """
	putil.test.assert_exception(
		putil.misc.normalize,
		{'value':'a', 'series':[2, 5], 'offset':10},
		RuntimeError,
		'Argument `value` is not valid'
	)
	putil.test.assert_exception(
		putil.misc.normalize,
		{'value':5, 'series':[2, 5], 'offset':'a'},
		RuntimeError,
		'Argument `offset` is not valid'
	)
	putil.test.assert_exception(
		putil.misc.normalize,
		{'value':5, 'series':['a', 'b']},
		RuntimeError,
		'Argument `series` is not valid'
	)
	putil.test.assert_exception(
		putil.misc.normalize,
		{'value':5, 'series':[2, 5], 'offset':10},
		ValueError,
		'Argument `offset` has to be in the [0.0, 1.0] range'
	)
	putil.test.assert_exception(
		putil.misc.normalize,
		{'value':0, 'series':[2, 5], 'offset':0},
		ValueError,
		'Argument `value` has to be within the bounds of argument `series`'
	)
	assert putil.misc.normalize(15, [10, 20]) == 0.5
	assert putil.misc.normalize(15, [10, 20], 0.5) == 0.75


def test_gcd():
	""" Test gcd() function """
	assert putil.misc.gcd([]) is None
	assert putil.misc.gcd([7]) == 7
	assert putil.misc.gcd([48, 18]) == 6
	assert putil.misc.gcd([20, 12, 16]) == 4
	assert putil.misc.gcd([0.05, 0.02, 0.1]) == 0.01
	ref = [Fraction(5, 3), Fraction(2, 3), Fraction(10, 3)]
	assert putil.misc.gcd(ref) == Fraction(1, 3)


def test_pgcd():
	""" Test pgcd() function """
	assert putil.misc.pgcd(48, 18) == 6
	assert putil.misc.pgcd(2.7, 107.3) == 0.1
	assert putil.misc.pgcd(3, 4) == 1
	assert putil.misc.pgcd(0.05, 0.02) == 0.01
	assert putil.misc.pgcd(5, 2) == 1
	assert putil.misc.pgcd(Fraction(5, 3), Fraction(2, 3)) == Fraction(1, 3)


def test_isalpha():
	""" Test isalpha() function """
	assert putil.misc.isalpha('1.5')
	assert putil.misc.isalpha('1E-20')
	assert not putil.misc.isalpha('1EA-20')


def test_ishex():
	""" Test ishex() function """
	assert not putil.misc.ishex(5)
	assert not putil.misc.ishex('45')
	assert putil.misc.ishex('F')


def test_isiterable():
	""" Test isiterable() function """
	assert putil.misc.isiterable([1, 2, 3])
	assert putil.misc.isiterable({'a':5})
	assert putil.misc.isiterable(set([1, 2, 3]))
	assert not putil.misc.isiterable(3)


def test_ellapsed_time_string():
	""" Test elapsed_time_string() function """
	obj = putil.misc.elapsed_time_string
	assert obj(
		datetime.datetime(2015, 1, 1),
		datetime.datetime(2015, 1, 1)) == 'None'
	putil.test.assert_exception(
		obj,
		{
			'start_time':datetime.datetime(2015, 2, 1),
			'stop_time':datetime.datetime(2015, 1, 1)
		},
		RuntimeError,
		'Invalid time delta specification'
	)
	assert obj(
		datetime.datetime(2014, 1, 1),
		datetime.datetime(2015, 1, 1)
	) == '1 year'
	assert obj(
		datetime.datetime(2014, 1, 1),
		datetime.datetime(2016, 1, 1)
	) == '2 years'
	assert obj(
		datetime.datetime(2014, 1, 1),
		datetime.datetime(2014, 1, 31)
	) == '1 month'
	assert obj(
		datetime.datetime(2014, 1, 1),
		datetime.datetime(2014, 3, 2)
	) == '2 months'
	assert obj(
		datetime.datetime(2014, 1, 1, 10),
		datetime.datetime(2014, 1, 1, 11)
	) == '1 hour'
	assert obj(
		datetime.datetime(2014, 1, 1, 10),
		datetime.datetime(2014, 1, 1, 12)
	) == '2 hours'
	assert obj(
		datetime.datetime(2014, 1, 1, 1, 10),
		datetime.datetime(2014, 1, 1, 1, 11)
	) == '1 minute'
	assert obj(
		datetime.datetime(2014, 1, 1, 1, 10),
		datetime.datetime(2014, 1, 1, 1, 12)
	) == '2 minutes'
	assert obj(
		datetime.datetime(2014, 1, 1, 1, 10, 1),
		datetime.datetime(2014, 1, 1, 1, 10, 2)
	) == '1 second'
	assert obj(
		datetime.datetime(2014, 1, 1, 1, 10, 1),
		datetime.datetime(2014, 1, 1, 1, 10, 3)
	) == '2 seconds'
	assert obj(
		datetime.datetime(2014, 1, 1, 1, 10, 1),
		datetime.datetime(2015, 1, 1, 1, 10, 2)
	) == '1 year and 1 second'
	assert obj(
		datetime.datetime(2014, 1, 1, 1, 10, 1),
		datetime.datetime(2015, 1, 1, 1, 10, 3)
	) == '1 year and 2 seconds'
	assert obj(
		datetime.datetime(2014, 1, 1, 1, 10, 1),
		datetime.datetime(2015, 1, 2, 1, 10, 3)
	) == '1 year, 1 day and 2 seconds'
	assert obj(
		datetime.datetime(2014, 1, 1, 1, 10, 1),
		datetime.datetime(2015, 1, 3, 1, 10, 3)
	) == '1 year, 2 days and 2 seconds'


def test_tmp_file():
	""" Test TmpFile context manager """
	def write_data(file_handle):
		_write(file_handle, 'Hello world!')
	# Test argument validation
	with pytest.raises(RuntimeError) as excinfo:
		with putil.misc.TmpFile(5) as fname:
			pass
	assert putil.test.get_exmsg(excinfo) == 'Argument `fpointer` is not valid'
	# Test behavior when no function pointer is given
	with putil.misc.TmpFile() as fname:
		assert isinstance(fname, str) and (len(fname) > 0)
		assert os.path.exists(fname)
	assert not os.path.exists(fname)
	# Test that exceptions within the with statement are re-raised
	with pytest.raises(OSError) as excinfo:
		with putil.misc.TmpFile(write_data) as fname:
			raise OSError('No data')
	assert putil.test.get_exmsg(excinfo) == 'No data'
	assert not os.path.exists(fname)
	# Test behaviour under "normal" circumstances
	with putil.misc.TmpFile(write_data) as fname:
		with open(fname, 'r') as fobj:
			line = fobj.readlines()
		assert line == ['Hello world!']
		assert os.path.exists(fname)
	assert not os.path.exists(fname)


def test_strframe():
	""" Test strframe() function """
	def check_basic_frame(lines):
		assert lines[0].startswith('\x1b[33mFrame object ID: 0x')
		assert lines[1] == 'File name......: {0}'.format(os.path.realpath(__file__))
		assert lines[2].startswith('Line number....: ')
		assert lines[3] == 'Function name..: test_strframe'
		assert lines[4] == r"Context........: ['\tfobj = inspect.stack()[0]\n']"
		assert lines[5] == 'Index..........: 0'
	fobj = inspect.stack()[0]
	lines = putil.misc.strframe(fobj).split('\n')
	check_basic_frame(lines)
	assert len(lines) == 6
	lines = [
		line for num, line in
			enumerate(putil.misc.strframe(fobj, extended=True).split('\n'))
			if (num < 6) or line.startswith('f_')
	]
	check_basic_frame(lines)
	assert lines[6].startswith('f_back ID......: 0x')
	assert lines[7].startswith('f_builtins.....: {')
	assert lines[8].startswith(
		'f_code.........: '
		'<code object test_strframe at 0x'
	)
	assert lines[9].startswith('f_globals......: {')
	assert lines[10].startswith('f_lasti........: ')
	assert lines[11].startswith('f_lineno.......: ')
	assert lines[12].startswith('f_locals.......: {')
	if sys.version_info.major == 2:
		assert lines[13] == 'f_restricted...: False'
		assert lines[14].startswith('f_trace........: ')
		assert len(lines) == 15
	else:
		assert lines[13].startswith('f_trace........: ')
		assert len(lines) == 14


def test_quote_str():
	""" Test quote_str() function """
	assert putil.misc.quote_str(5) == 5
	assert putil.misc.quote_str('Hello!') == '"Hello!"'
	assert putil.misc.quote_str('He said "hello!"') == "'He said \"hello!\"'"


def test_flatten_list():
	""" Test flatten_list() function """
	obj = putil.misc.flatten_list
	assert obj([1, 2, 3]) == [1, 2, 3]
	assert obj([1, [2, 3, 4], 5]) == [1, 2, 3, 4, 5]
	assert obj([1, [2, 3, [4, 5, 6]], 7]) == [1, 2, 3, 4, 5, 6, 7]
	ref = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
	assert obj([1, [2, 3, [4, [5, 6, 7], 8, 9]], [10, 11], 12]) == ref


def test_cidict():
	""" Test CiDict class """
	assert putil.misc.CiDict() == {}
	obj = putil.misc.CiDict(one=1, TwO=2, tHrEe=3, FOUR=4)
	assert obj == {'one':1, 'two':2, 'three':3, 'four':4}
	assert obj['four'] == 4
	obj['FIve'] = 5
	assert obj == {'one':1, 'two':2, 'three':3, 'four':4, 'five':5}
	assert obj['five'] == 5
	assert len(obj) == 5
	del obj['five']
	assert obj == {'one':1, 'two':2, 'three':3, 'four':4}
	obj = putil.misc.CiDict(zip(['aa', 'bb', 'cc'], [10, 20, 30]))
	assert obj == {'aa':10, 'bb':20, 'cc':30}
	with pytest.raises(TypeError) as excinfo:
		putil.misc.CiDict(zip(['aa', 'bb', [1, 2]], [10, 20, 30]))
	assert putil.test.get_exmsg(excinfo) == "unhashable type: 'list'"
	with pytest.raises(ValueError) as excinfo:
		putil.misc.CiDict(['Prop1', 'Prop2', 'Prop3', 'Prop4'])
	assert putil.test.get_exmsg(excinfo) == (
		"dictionary update sequence "
		"element #0 has length 5; 2 is required"
	)

def test_pprint_ast_node():
	""" Test pprint_ast_node() function """
	putil.test.assert_exception(
		putil.misc.pprint_ast_node,
		{'node':5},
		RuntimeError,
		'Argument `node` is not valid'
	)
	ret = []
	ret.append('class MyClass(object):')
	ret.append('	def __init__(self, a, b):')
	ret.append('		self._value = a+b')
	ref2 = []
	ref2.append("Module(body=[")
	ref2.append("    ClassDef(name='MyClass', bases=[")
	ref2.append("        Name(id='object', ctx=Load(), lineno=1, col_offset=14),")
	ref2.append("      ], body=[")
	ref2.append("        FunctionDef(name='__init__', args=arguments(args=[")
	ref2.append("            Name(id='self', ctx=Param(), lineno=2, "
			   "col_offset=14),")
	ref2.append("            Name(id='a', ctx=Param(), lineno=2, col_offset=20),")
	ref2.append("            Name(id='b', ctx=Param(), lineno=2, col_offset=23),")
	ref2.append("          ], vararg=None, kwarg=None, defaults=[]), body=[")
	ref2.append("            Assign(targets=[")
	ref2.append("                Attribute(value=Name(id='self', ctx=Load(), "
			   "lineno=3, col_offset=2), attr='_value', ctx=Store(), lineno=3, "
			   "col_offset=2),")
	ref2.append("              ], value=BinOp(left=Name(id='a', ctx=Load(), "
			   "lineno=3, col_offset=16), op=Add(), right=Name(id='b', "
			   "ctx=Load(), lineno=3, col_offset=18), lineno=3, col_offset=16),"
			   " lineno=3, col_offset=2),")
	ref2.append("          ], decorator_list=[], lineno=2, col_offset=1),")
	ref2.append("      ], decorator_list=[], lineno=1, col_offset=0),")
	ref2.append("  ])")

	ref3 = []
	ref3.append("Module(body=[")
	ref3.append("    ClassDef(name='MyClass', bases=[")
	ref3.append("        Name(id='object', ctx=Load(), lineno=1, col_offset=14),")
	ref3.append("      ], keywords=[], starargs=None, kwargs=None, body=[")
	ref3.append("        FunctionDef(name='__init__', args=arguments(args=[")
	ref3.append("            arg(arg='self', annotation=None, lineno=2, "
			    "col_offset=14),")
	ref3.append("            arg(arg='a', annotation=None, lineno=2, "
			    "col_offset=20),")
	ref3.append("            arg(arg='b', annotation=None, lineno=2, "
			    "col_offset=23),")
	ref3.append("          ], vararg=None, kwonlyargs=[], kw_defaults=[], "
			    "kwarg=None, defaults=[]), body=[")
	ref3.append("            Assign(targets=[")
	ref3.append("                Attribute(value=Name(id='self', ctx=Load(), "
			    "lineno=3, col_offset=2), attr='_value', ctx=Store(), "
			    "lineno=3, col_offset=7),")
	ref3.append("              ], value=BinOp(left=Name(id='a', ctx=Load(), "
			    "lineno=3, col_offset=16), op=Add(), right=Name(id='b', "
			    "ctx=Load(), lineno=3, col_offset=18), lineno=3, "
			    "col_offset=16), lineno=3, col_offset=2),")
	ref3.append("          ], decorator_list=[], returns=None, lineno=2, "
			    "col_offset=1),")
	ref3.append("      ], decorator_list=[], lineno=1, col_offset=0),")
	ref3.append("  ])")

	assert putil.misc.pprint_ast_node(
		ast.parse('\n'.join(ret)),
		include_attributes=True,
		annotate_fields=True
	) == '\n'.join(ref2 if sys.version_info.major == 2 else ref3)
	ref2 = []
	ref2.append("Module([")
	ref2.append("    ClassDef('MyClass', [")
	ref2.append("        Name('object', Load(), 1, 14),")
	ref2.append("      ], [")
	ref2.append("        FunctionDef('__init__', arguments([")
	ref2.append("            Name('self', Param(), 2, 14),")
	ref2.append("            Name('a', Param(), 2, 20),")
	ref2.append("            Name('b', Param(), 2, 23),")
	ref2.append("          ], None, None, []), [")
	ref2.append("            Assign([")
	ref2.append("                Attribute(Name('self', Load(), 3, 2), "
			   "'_value', Store(), 3, 2),")
	ref2.append("              ], BinOp(Name('a', Load(), 3, 16), Add(), "
			   "Name('b', Load(), 3, 18), 3, 16), 3, 2),")
	ref2.append("          ], [], 2, 1),")
	ref2.append("      ], [], 1, 0),")
	ref2.append("  ])")
	ref3 = []
	ref3.append("Module([")
	ref3.append("    ClassDef('MyClass', [")
	ref3.append("        Name('object', Load(), 1, 14),")
	ref3.append("      ], [], None, None, [")
	ref3.append("        FunctionDef('__init__', arguments([")
	ref3.append("            arg('self', None, 2, 14),")
	ref3.append("            arg('a', None, 2, 20),")
	ref3.append("            arg('b', None, 2, 23),")
	ref3.append("          ], None, [], [], None, []), [")
	ref3.append("            Assign([")
	ref3.append("                Attribute(Name('self', Load(), 3, 2), "
			    "'_value', Store(), 3, 7),")
	ref3.append("              ], BinOp(Name('a', Load(), 3, 16), Add(), "
			    "Name('b', Load(), 3, 18), 3, 16), 3, 2),")
	ref3.append("          ], [], None, 2, 1),")
	ref3.append("      ], [], 1, 0),")
	ref3.append("  ])")
	assert putil.misc.pprint_ast_node(
		ast.parse('\n'.join(ret)),
		include_attributes=True,
		annotate_fields=False
	) == '\n'.join(ref2 if sys.version_info.major == 2 else ref3)


def test_private_props():
	""" Test private_props() function """
	obj = putil.pinspect.Callables()
	assert sorted(list(putil.misc.private_props(obj))) == [
		'_callables_db',
		'_class_names',
		'_fnames',
		'_module_names',
		'_modules_dict',
		'_reverse_callables_db'
	]
