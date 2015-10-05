# test_test.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import pytest

import putil.test


###
# Test functions
###
def test_exception_type_str():
    """ Test exception_type_str function behavior """
    class MyException(Exception):
        pass
    assert putil.test.exception_type_str(RuntimeError) == 'RuntimeError'
    assert putil.test.exception_type_str(Exception) == 'Exception'
    assert putil.test.exception_type_str(MyException) == 'MyException'


def test_assert_exception():
    """ Test assert_exception function behavior """
    def func1(par1):
        if par1 == 1:
            raise RuntimeError('Exception 1')
        elif par1 == 2:
            raise ValueError('The number 1234 is invalid')
    putil.test.assert_exception(
        func1, {'par1':1}, RuntimeError, 'Exception 1'
    )
    with pytest.raises(AssertionError):
        putil.test.assert_exception(
            func1, {'par1':0}, RuntimeError, 'Exception 1'
        )
    putil.test.assert_exception(
        func1,
        {'par1':2},
        ValueError,
        r'The number \d+ is invalid'
    )
    with pytest.raises(AssertionError):
        putil.test.assert_exception(func1, {'par1':1}, OSError, 'Exception 5')
    with pytest.raises(AssertionError):
        putil.test.assert_exception(
            func1,
            {'par1':2},
            ValueError,
            'Exception message is wrong'
        )

