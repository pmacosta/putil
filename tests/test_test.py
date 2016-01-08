# test_test.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

# PyPI imports
import pytest
# Putil imports
import putil.test


###
# Test functions
###
def test_comp_list_of_dicts():
    """ Test comp_list_of_dicts function behavior """
    list1 = []
    list2 = [{'a':5, 'b':6}]
    assert not putil.test.comp_list_of_dicts(list1, list2)
    list1 = [{'a':5}]
    list2 = [{'a':5, 'b':6}]
    assert not putil.test.comp_list_of_dicts(list1, list2)
    list1 = [{'a':5, 'b':6}]
    list2 = [{'a':5, 'b':6}]
    assert putil.test.comp_list_of_dicts(list1, list2)


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

