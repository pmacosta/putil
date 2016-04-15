# test_misc.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,E1101,E1129,F0401,R0915,W0621

# Standard library imports
from __future__ import print_function
from datetime import datetime
import inspect
import os
import platform
import re
import struct
import sys
import time
from fractions import Fraction
if sys.hexversion >= 0x03000000:
    import unittest.mock as mock
# PyPI imports
from numpy import array
import pytest
if sys.hexversion < 0x03000000:
    import mock
# Putil imports
import putil.misc
from putil.test import AE, AI, GET_EXMSG
if sys.hexversion < 0x03000000:
    from putil.compat2 import _unicode_to_ascii, _write
else:
    from putil.compat3 import _unicode_to_ascii, _write


###
# Test functions
###
def test_ignored():
    """ Test ignored context manager behavior """
    with putil.misc.TmpFile() as fname:
        with open(fname, 'w') as output_obj:
            output_obj.write('This is a test file')
        assert os.path.exists(fname)
        with putil.misc.ignored(OSError):
            os.remove(fname)
        assert not os.path.exists(fname)
    with putil.misc.ignored(OSError):
        os.remove('_some_file_')
    with pytest.raises(OSError) as excinfo:
        with putil.misc.ignored(RuntimeError):
            os.remove('_some_file_')

    assert excinfo.value.strerror == (
        'The system cannot find the file specified'
        if platform.system().lower() == 'windows' else
        'No such file or directory'
    )
    assert excinfo.value.filename == '_some_file_'
    assert excinfo.value.errno == 2


def test_timer(capsys):
    """ Test Timer context manager behavior """
    # Test argument validation
    with pytest.raises(RuntimeError) as excinfo:
        with putil.misc.Timer(5):
            pass
    assert GET_EXMSG(excinfo) == 'Argument `verbose` is not valid'
    # Test that exceptions within the with statement are re-raised
    with pytest.raises(RuntimeError) as excinfo:
        with putil.misc.Timer():
            raise RuntimeError('Error in code')
    assert GET_EXMSG(excinfo) == 'Error in code'
    # Test normal operation
    with putil.misc.Timer() as tobj:
        time.sleep(0.5)
    assert isinstance(tobj.elapsed_time, float) and (tobj.elapsed_time > 0)
    tregexp = re.compile(r'Elapsed time: [\d|\.]+\[msec\]')
    with putil.misc.Timer(verbose=True) as tobj:
        time.sleep(0.5)
    out, _ = capsys.readouterr()
    assert tregexp.match(out.rstrip())


def test_tmp_file():
    """ Test TmpFile context manager behavior """
    def write_data(file_handle):
        _write(file_handle, 'Hello world!')
    # Test argument validation
    with pytest.raises(RuntimeError) as excinfo:
        with putil.misc.TmpFile(5) as fname:
            pass
    assert GET_EXMSG(excinfo) == 'Argument `fpointer` is not valid'
    # Test behavior when no function pointer is given
    with putil.misc.TmpFile() as fname:
        assert isinstance(fname, str) and (len(fname) > 0)
        assert os.path.exists(fname)
    assert not os.path.exists(fname)
    # Test that exceptions within the with statement are re-raised
    with pytest.raises(OSError) as excinfo:
        with putil.misc.TmpFile(write_data) as fname:
            raise OSError('No data')
    assert GET_EXMSG(excinfo) == 'No data'
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
        actual = obj(''.join([struct.pack('h', num) for num in range(1, 15)]))
        assert ref == actual
    else:
        ref = (
            r'\o1\0\o2\0\o3\0\o4\0\o5\0\o6\0\a\0'
            r'\b\0\t\0\n\0\v\0\f\0\r\0\o16\0'
        )
        code = lambda x: struct.pack('h', x).decode('ascii')
        actual = obj(''.join([code(num) for num in range(1, 15)]))
        assert ref == actual


def test_char_string_to_decimal():
    """ Test char_string_to_decimal_string function """
    ref = '72 101 108 108 111 32 119 111 114 108 100 33'
    assert putil.misc.char_to_decimal('Hello world!') == ref


def test_elapsed_time_string():
    """ Test elapsed_time_string function behavior """
    obj = putil.misc.elapsed_time_string
    assert obj(datetime(2015, 1, 1), datetime(2015, 1, 1)) == 'None'
    AE(
        obj, RuntimeError, 'Invalid time delta specification',
        start_time=datetime(2015, 2, 1), stop_time=datetime(2015, 1, 1)
    )
    items = [
        ((2014, 1, 1), (2015, 1, 1), '1 year'),
        ((2014, 1, 1), (2016, 1, 1), '2 years'),
        ((2014, 1, 1), (2014, 1, 31), '1 month'),
        ((2014, 1, 1), (2014, 3, 2), '2 months'),
        ((2014, 1, 1, 10), (2014, 1, 1, 11), '1 hour'),
        ((2014, 1, 1, 10), (2014, 1, 1, 12), '2 hours'),
        ((2014, 1, 1, 1, 10), (2014, 1, 1, 1, 11), '1 minute'),
        ((2014, 1, 1, 1, 10), (2014, 1, 1, 1, 12), '2 minutes'),
        ((2014, 1, 1, 1, 10, 1), (2014, 1, 1, 1, 10, 2), '1 second'),
        ((2014, 1, 1, 1, 10, 1), (2014, 1, 1, 1, 10, 3), '2 seconds'),
        (
            (2014, 1, 1, 1, 10, 1),
            (2015, 1, 1, 1, 10, 2),
            '1 year and 1 second'
        ),
        (
            (2014, 1, 1, 1, 10, 1),
            (2015, 1, 1, 1, 10, 3),
            '1 year and 2 seconds'),
        (
            (2014, 1, 1, 1, 10, 1),
            (2015, 1, 2, 1, 10, 3),
            '1 year, 1 day and 2 seconds'),
        (
            (2014, 1, 1, 1, 10, 1),
            (2015, 1, 3, 1, 10, 3),
            '1 year, 2 days and 2 seconds'
        ),
    ]
    for date1, date2, ref in items:
        assert obj(datetime(*date1), datetime(*date2)) == ref


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
    home_dir = os.path.expanduser('~')
    with mock.patch('os.makedirs', side_effect=mock_os_makedir):
        fname = os.path.join(home_dir, 'some_dir', 'some_file.ext')
        putil.misc.make_dir(fname)
        stdout, _ = capsys.readouterr()
        actual = repr(os.path.dirname(fname).rstrip())[1:-1]
        ref = repr(_unicode_to_ascii(stdout.rstrip()))[1:-1]
        assert actual == ref
        putil.misc.make_dir(
            os.path.join(os.path.abspath(os.sep), 'some_file.ext')
        )
        stdout, _ = capsys.readouterr()
        assert stdout == ''


def test_normalize():
    """ Test normalize function behavior """
    obj = putil.misc.normalize
    AI(obj, 'value', value='a', series=[2, 5], offset=10)
    AI(obj, 'offset', value=5, series=[2, 5], offset='a')
    AI(obj, 'series', value=5, series=['a', 'b'])
    exmsg = 'Argument `offset` has to be in the [0.0, 1.0] range'
    AE(obj, ValueError, exmsg, value=5, series=[2, 5], offset=10)
    exmsg = 'Argument `value` has to be within the bounds of argument `series`'
    AE(obj, ValueError, exmsg, value=0, series=[2, 5], offset=0)
    assert putil.misc.normalize(15, [10, 20]) == 0.5
    assert putil.misc.normalize(15, [10, 20], 0.5) == 0.75


def test_normalize_windows_fname():
    """ Test normalize_windows_fname behavior """
    obj = putil.misc.normalize_windows_fname
    in_windows = platform.system().lower() == 'windows'
    ref = r'a\b\c' if in_windows else 'a/b/c//'
    assert obj('a/b/c//') == ref
    ref = r'a\b\c' if in_windows else 'a/b/c'
    assert obj('a/b/c//', True) == ref
    ref = r'\\a\b\c' if in_windows else r'\\a\\b\\c'
    assert obj(r'\\\\\\\\a\\\\b\\c', True) == ref
    ref = r'C:\a\b\c' if in_windows else r'C:\\a\\b\\c'
    assert obj(r'C:\\\\\\\\a\\\\b\\c', True) == ref
    ref = (
        '\\apps\\temp\\new\\file\\wire'
        if in_windows else
        r'\apps\temp\new\\file\\wire'
    )
    assert obj(r'\apps\temp\new\\\\file\\\\\\\\\\wire', True) == ref


def test_per():
    """ Test per function behavior """
    obj = putil.misc.per
    AI(obj, 'prec', arga=5, argb=7, prec='Hello')
    AI(obj, 'arga', arga='Hello', argb=7, prec=1)
    AI(obj, 'argb', arga=5, argb='Hello', prec=1)
    exmsg = 'Arguments are not of the same type'
    AE(obj, TypeError, exmsg, arga=5, argb=[5, 7], prec=1)
    assert obj(3, 2, 1) == 0.5
    assert obj(3.1, 3.1, 1) == 0
    ttuple = zip(obj([3, 1.1, 5], [2, 1.1, 2], 1), [0.5, 0, 1.5])
    assert all([test == ref for test, ref in ttuple])
    ttuple = zip(obj(array([3, 1.1, 5]), array([2, 1.1, 2]), 1), [0.5, 0, 1.5])
    assert all([test == ref for test, ref in ttuple])
    assert obj(4, 3, 3) == 0.333
    assert obj(4, 0, 3) == 1e20
    ttuple = zip(
        obj(array([3, 1.1, 5]), array([2, 0, 2]), 1), [0.5, 1e20, 1.5]
    )
    assert all([test == ref for test, ref in ttuple])


def test_pcolor():
    """ Test pcolor function behavior """
    obj = putil.misc.pcolor
    AI(obj, 'text', text=5, color='red', indent=0)
    AI(obj, 'color', text='hello', color=5, indent=0)
    AI(obj, 'indent', text='hello', color='red', indent=5.1)
    exmsg = 'Unknown color hello'
    AE(obj, ValueError, exmsg, text='hello', color='hello', indent=5)
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


def test_quote_str():
    """ Test quote_str function behavior """
    assert putil.misc.quote_str(5) == 5
    assert putil.misc.quote_str('Hello!') == '"Hello!"'
    assert putil.misc.quote_str('He said "hello!"') == "'He said \"hello!\"'"


def test_strframe():
    """ Test strframe function behavior """
    obj = putil.misc.strframe
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
    lines = obj(fobj).split('\n')
    check_basic_frame(lines)
    assert len(lines) == 6
    lines = [
        line
        for num, line in enumerate(obj(fobj, extended=True).split('\n'))
        if (num < 6) or line.startswith('f_')
    ]
    check_basic_frame(lines)
    assert lines[6].startswith('f_back ID......: 0x')
    assert lines[7].startswith('f_builtins.....: {')
    assert lines[8].startswith(
        'f_code.........: '
        '<code object test_strframe at '
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
    assert 'four' in obj
    assert 'FOUR' in obj
    assert len(obj) == 5
    assert obj == {'one':1, 'two':2, 'three':3, 'four':4, 'five':5}
    assert obj['five'] == 5
    assert len(obj) == 5
    del obj['five']
    assert obj == {'one':1, 'two':2, 'three':3, 'four':4}
    obj = putil.misc.CiDict(zip(['aa', 'bb', 'cc'], [10, 20, 30]))
    assert obj == {'aa':10, 'bb':20, 'cc':30}
    with pytest.raises(TypeError) as excinfo:
        putil.misc.CiDict(zip(['aa', 'bb', [1, 2]], [10, 20, 30]))
    assert GET_EXMSG(excinfo) == "unhashable type: 'list'"
    with pytest.raises(ValueError) as excinfo:
        putil.misc.CiDict(['Prop1', 'Prop2', 'Prop3', 'Prop4'])
    msg = 'dictionary update sequence element #0 has length 5; 2 is required'
    assert GET_EXMSG(excinfo) == msg
