# test_my_module.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0903,W0104,W0105

import docs.support.my_module, pytest, putil.test

def test_func():
	""" Test func() function """
	putil.test.assert_exception(
		docs.support.my_module.func,
		{'name':5},
		TypeError,
		'Argument `name` is not valid'
	)
	assert docs.support.my_module.func('John') == 'My name is John'

def test_my_class():
	""" Test MyClass() class """
	obj = docs.support.my_module.MyClass()
	with pytest.raises(RuntimeError) as excinfo:
		obj.value
	assert excinfo.value.message == 'Attribute `value` not set'
	with pytest.raises(RuntimeError) as excinfo:
		obj.value = 'a'
	assert excinfo.value.message == 'Argument `value` is not valid'
