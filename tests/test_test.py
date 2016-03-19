# test_test.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0201,R0903,W0212

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


def test_assert_arg_invalid():
    """ Test assert_arg_invalid function behavior """
    def func1(par):
        if par == 1:
            raise RuntimeError('Argument `par` is not valid')
    putil.test.assert_arg_invalid(func1, 'par', 1)
    with pytest.raises(AssertionError) as excinfo:
        putil.test.assert_arg_invalid(func1, 'par', 2)
    assert putil.test.get_exmsg(excinfo) == 'Did not raise'


def test_assert_exception():
    """ Test assert_exception function behavior """
    class MyClass0(object):
        def meth1(self, par):
            if par:
                raise TypeError('meth1 exception')
        def meth2(self, par1, par2=0, par3=1):
            ttuple = (par1, par2, par3)
            if ttuple == (0, 1, 2):
                raise IOError('meth2 exception')
            return ttuple
    def func1(par1):
        if par1 == 1:
            raise RuntimeError('Exception 1')
        elif par1 == 2:
            raise ValueError('The number 1234 is invalid')
    putil.test.assert_exception(
        func1, RuntimeError, 'Exception 1', par1=1,
    )
    with pytest.raises(AssertionError):
        putil.test.assert_exception(
            func1, RuntimeError, 'Exception 1', par1=0,
        )
    putil.test.assert_exception(
        func1, ValueError, r'The number \d+ is invalid', par1=2

    )
    with pytest.raises(AssertionError):
        putil.test.assert_exception(func1, OSError, 'Exception 5', par1=1)
    with pytest.raises(AssertionError):
        putil.test.assert_exception(
            func1, ValueError, 'Exception message is wrong', par1=2,
        )
    # Test passing of positional and/or keyword arguments
    cobj = MyClass0()
    putil.test.assert_exception(
        cobj.meth1, TypeError, 'meth1 exception', True
    )
    with pytest.raises(AssertionError) as excinfo:
        putil.test.assert_exception(
            cobj.meth1, TypeError, 'meth1 exception', False
        )
    assert putil.test.get_exmsg(excinfo) == 'Did not raise'
    putil.test.assert_exception(
        cobj.meth2, IOError, 'meth2 exception', 0, 1, 2
    )
    putil.test.assert_exception(
        cobj.meth2, IOError, 'meth2 exception', 0, par3=2, par2=1
    )
    putil.test.assert_exception(
        cobj.meth2, IOError, 'meth2 exception', par3=2, par2=1, par1=0
    )
    with pytest.raises(AssertionError) as excinfo:
        putil.test.assert_exception(
            cobj.meth2, IOError, 'meth2 exception', 3
        )
    assert putil.test.get_exmsg(excinfo) == 'Did not raise'
    with pytest.raises(RuntimeError) as excinfo:
        putil.test.assert_exception(
            cobj.meth1, TypeError, 'meth1 exception', 0, 1, 2, 3, 4
        )
    assert putil.test.get_exmsg(excinfo) == 'Illegal number of arguments'


def test_assert_ro_prop():
    """ Test assert_ro_prop function behavior """
    class MyClass1(object):
        def __init__(self):
            self._value = 1
        def getter(self):
            return self._value
        value = property(getter)
    class MyClass2(object):
        def __init__(self):
            self._value = 1
        def getter(self):
            return self._value
        def deleter(self):
            del self._value
        value = property(getter, None, deleter)
    # Test case where attribute cannot be deleted
    obj1 = MyClass1()
    putil.test.assert_ro_prop(obj1, 'value')
    # Test case where attribute can be deleted
    obj2 = MyClass2()
    try:
        putil.test.assert_ro_prop(obj2, 'value')
    except AssertionError as eobj:
        actmsg = putil.test.get_exmsg(eobj)
        assert actmsg == 'Property can be deleted'
    # Test case where unexpected exception is raised during evaluation
    try:
        putil.test.assert_ro_prop('a', '')
    except SyntaxError as eobj:
        pass
