# test_my_module.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0410,C0411,R0903,W0104,W0105

import pytest, docs.support.my_module, putil.test

def test_func():
    """ Test func() function """
    putil.test.assert_exception(
        docs.support.my_module.func,
        TypeError,
        'Argument `name` is not valid',
        {'name':5}
    )
    assert docs.support.my_module.func('John') == 'My name is John'

def test_my_class():
    """ Test MyClass() class """
    obj = docs.support.my_module.MyClass()
    with pytest.raises(RuntimeError) as excinfo:
        obj.value
    assert putil.test.get_exmsg(excinfo) == 'Attribute `value` not set'
    with pytest.raises(RuntimeError) as excinfo:
        obj.value = 'a'
    assert putil.test.get_exmsg(excinfo) == 'Argument `value` is not valid'
