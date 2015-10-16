# test_misc.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,E1101,F0401,R0915,W0621

from __future__ import print_function
import ast
import datetime
import inspect
import os
import pytest
import re
import struct
import sys
import tempfile
from fractions import Fraction
from numpy import array
if sys.hexversion < 0x03000000:
    import mock
else:
    import unittest.mock as mock

import putil.misc
import putil.test
if sys.hexversion < 0x03000000:
    from putil.compat2 import _write
else:
    from putil.compat3 import _write


###
# Test functions
###
def test_ignored():
    """ Test ignored context manager behavior """
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
    """ Test Timer context manager behavior """
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


def test_tmp_file():
    """ Test TmpFile context manager behavior """
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


def test_binary_string_to_octal_string():
    """ Test binary_string_to_octal_string function behavior """
    obj = putil.misc.binary_string_to_octal_string
    if sys.hexversion < 0x03000000:
        ref = (
            '\\1\\0\\2\\0\\3\\0\\4\\0\\5\\0\\6\\0\\a\\0'
            '\\b\\0\\t\\0\\n\\0\\v\\0\\f\\0\\r\\0\\16\\0'
        )
        assert (
            obj(
                ''.join([struct.pack('h', num) for num in range(1, 15)])
            )
            ==
            ref
        )
    else:
        ref = (
            r'\o1\0\o2\0\o3\0\o4\0\o5\0\o6\0\a\0'
            r'\b\0\t\0\n\0\v\0\f\0\r\0\o16\0'
        )
        assert (
            obj(
                ''.join(
                    [
                        struct.pack('h', num).decode('ascii')
                        for num in range(1, 15)
                    ]
                )
            )
            ==
            ref
        )


def test_char_string_to_decimal():
    """ Test char_string_to_decimal_string function """
    ref = '72 101 108 108 111 32 119 111 114 108 100 33'
    assert putil.misc.char_to_decimal('Hello world!') == ref


def test_elapsed_time_string():
    """ Test elapsed_time_string function behavior """
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
    assert (
        obj(
            datetime.datetime(2014, 1, 1),
            datetime.datetime(2015, 1, 1)
        )
        ==
        '1 year'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1),
            datetime.datetime(2016, 1, 1)
        )
        ==
        '2 years'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1),
            datetime.datetime(2014, 1, 31)
        )
        ==
        '1 month'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1),
            datetime.datetime(2014, 3, 2)
        )
        ==
        '2 months'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1, 10),
            datetime.datetime(2014, 1, 1, 11)
        )
        ==
        '1 hour'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1, 10),
            datetime.datetime(2014, 1, 1, 12)
        )
        ==
        '2 hours'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1, 1, 10),
            datetime.datetime(2014, 1, 1, 1, 11)
        )
        ==
        '1 minute'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1, 1, 10),
            datetime.datetime(2014, 1, 1, 1, 12)
        )
        ==
        '2 minutes'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1, 1, 10, 1),
            datetime.datetime(2014, 1, 1, 1, 10, 2)
        )
        ==
        '1 second'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1, 1, 10, 1),
            datetime.datetime(2014, 1, 1, 1, 10, 3)
        )
        ==
        '2 seconds'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1, 1, 10, 1),
            datetime.datetime(2015, 1, 1, 1, 10, 2)
        )
        ==
        '1 year and 1 second'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1, 1, 10, 1),
            datetime.datetime(2015, 1, 1, 1, 10, 3)
        )
        ==
        '1 year and 2 seconds'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1, 1, 10, 1),
            datetime.datetime(2015, 1, 2, 1, 10, 3)
        )
        ==
        '1 year, 1 day and 2 seconds'
    )
    assert (
        obj(
            datetime.datetime(2014, 1, 1, 1, 10, 1),
            datetime.datetime(2015, 1, 3, 1, 10, 3)
        )
        ==
        '1 year, 2 days and 2 seconds'
    )


def test_flatten_list():
    """ Test flatten_list function behavior """
    obj = putil.misc.flatten_list
    assert obj([1, 2, 3]) == [1, 2, 3]
    assert obj([1, [2, 3, 4], 5]) == [1, 2, 3, 4, 5]
    assert obj([1, [2, 3, [4, 5, 6]], 7]) == [1, 2, 3, 4, 5, 6, 7]
    ref = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    assert obj([1, [2, 3, [4, [5, 6, 7], 8, 9]], [10, 11], 12]) == ref


def test_gcd():
    """ Test gcd function behavior """
    assert putil.misc.gcd([]) is None
    assert putil.misc.gcd([7]) == 7
    assert putil.misc.gcd([48, 18]) == 6
    assert putil.misc.gcd([20, 12, 16]) == 4
    ref = [Fraction(5, 3), Fraction(2, 3), Fraction(10, 3)]
    assert putil.misc.gcd(ref) == Fraction(1, 3)


def test_isalpha():
    """ Test isalpha function behavior """
    assert putil.misc.isalpha('1.5')
    assert putil.misc.isalpha('1E-20')
    assert not putil.misc.isalpha('1EA-20')


def test_ishex():
    """ Test ishex function behavior """
    assert not putil.misc.ishex(5)
    assert not putil.misc.ishex('45')
    assert putil.misc.ishex('F')


def test_isiterable():
    """ Test isiterable function behavior """
    assert putil.misc.isiterable([1, 2, 3])
    assert putil.misc.isiterable({'a':5})
    assert putil.misc.isiterable(set([1, 2, 3]))
    assert not putil.misc.isiterable(3)


def test_isnumber():
    """ Test isnumber function behavior """
    assert putil.misc.isnumber(5)
    assert putil.misc.isnumber(1.5)
    assert putil.misc.isnumber(complex(3.2, 9.5))
    assert not putil.misc.isnumber(True)


def test_isreal():
    """ Test isreal function behavior """
    assert putil.misc.isreal(5)
    assert putil.misc.isreal(1.5)
    assert not putil.misc.isreal(complex(3.2, 9.5))
    assert not putil.misc.isreal(True)


def test_make_dir(capsys):
    """ Test make_dir function behavior """
    def mock_os_makedir(file_path):
        print(file_path)
    home_dir = os.environ['HOME']
    with mock.patch('os.makedirs', side_effect=mock_os_makedir):
        fname = os.path.join(home_dir, 'some_dir', 'some_file.ext')
        putil.misc.make_dir(fname)
        stdout, _ = capsys.readouterr()
        assert stdout == os.path.dirname(fname)+'\n'
        putil.misc.make_dir(
            os.path.join(os.path.abspath(os.sep), 'some_file.ext')
        )
        stdout, _ = capsys.readouterr()
        assert stdout == ''


def test_normalize():
    """ Test normalize function behavior """
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


def test_per():
    """ Test per function behavior """
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
    ttuple = zip(
        obj(array([3, 1.1, 5]), array([2, 0, 2]), 1),
        [0.5, 1e20, 1.5]
    )
    assert all([test == ref for test, ref in ttuple])


def test_pcolor():
    """ Test pcolor function behavior """
    putil.test.assert_exception(
        putil.misc.pcolor,
        {'text':5, 'color':'red', 'indent':0},
        RuntimeError,
        'Argument `text` is not valid'
    )
    putil.test.assert_exception(
        putil.misc.pcolor,
        {'text':'hello', 'color':5, 'indent':0},
        RuntimeError,
        'Argument `color` is not valid'
    )
    putil.test.assert_exception(
        putil.misc.pcolor,
        {'text':'hello', 'color':'red', 'indent':5.1},
        RuntimeError,
        'Argument `indent` is not valid'
    )
    putil.test.assert_exception(
        putil.misc.pcolor,
        {'text':'hello', 'color':'hello', 'indent':5},
        ValueError,
        'Unknown color hello'
    )
    assert putil.misc.pcolor('Text', 'none', 5) == '     Text'
    assert putil.misc.pcolor('Text', 'blue', 2) == '\033[34m  Text\033[0m'
    # These statements should not raise any exception
    putil.misc.pcolor('Text', 'RED')
    putil.misc.pcolor('Text', 'NoNe')


def test_pgcd():
    """ Test pgcd function behavior """
    assert putil.misc.pgcd(48, 18) == 6
    assert putil.misc.pgcd(3, 4) == 1
    assert putil.misc.pgcd(0.05, 0.02) == 0.01
    assert putil.misc.pgcd(5, 2) == 1
    assert putil.misc.pgcd(Fraction(5, 3), Fraction(2, 3)) == Fraction(1, 3)


def test_pprint_ast_node():
    """ Test pprint_ast_node function behavior """
    putil.test.assert_exception(
        putil.misc.pprint_ast_node,
        {'node':5},
        RuntimeError,
        'Argument `node` is not valid'
    )
    # Rudimentary tests, just to make sure a reasonable output is produced
    # Actual AST appears to have some variation from Python version to
    # Python version
    keywords = [
        'Module(',
        'ClassDef(',
        'FunctionDef(',
        'Name(',
        'Load()',
        'Attribute(',
        'BinOp',
    ]
    ret = []
    ret.append('class MyClass(object):')
    ret.append('    def __init__(self, a, b):')
    ret.append('        self._value = a+b')
    act = putil.misc.pprint_ast_node(
        ast.parse('\n'.join(ret)),
        include_attributes=True,
        annotate_fields=True
    )
    assert all([item in act for item in keywords])
    act = putil.misc.pprint_ast_node(
        ast.parse('\n'.join(ret)),
        include_attributes=True,
        annotate_fields=False
    )
    assert all([item in act for item in keywords])


def test_quote_str():
    """ Test quote_str function behavior """
    assert putil.misc.quote_str(5) == 5
    assert putil.misc.quote_str('Hello!') == '"Hello!"'
    assert putil.misc.quote_str('He said "hello!"') == "'He said \"hello!\"'"


def test_strframe():
    """ Test strframe function behavior """
    def check_basic_frame(lines):
        assert lines[0].startswith('\x1b[33mFrame object ID: 0x')
        assert lines[1] == 'File name......: {0}'.format(
            os.path.realpath(__file__)
        )
        assert lines[2].startswith('Line number....: ')
        assert lines[3] == 'Function name..: test_strframe'
        assert (
            lines[4] ==
            r"Context........: ['    fobj = inspect.stack()[0]\n']"
        )
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
    if sys.hexversion < 0x03000000:
        assert lines[13] == 'f_restricted...: False'
        assert lines[14].startswith('f_trace........: ')
        assert len(lines) == 15
    else:
        assert lines[13].startswith('f_trace........: ')
        assert len(lines) == 14


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
    assert (
        putil.test.get_exmsg(excinfo)
        ==
        (
            'dictionary update sequence '
            'element #0 has length 5; 2 is required'
        )
    )
