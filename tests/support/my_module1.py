# pylint: disable=W0212
"""
my_module1 module
"""

import putil.pcontracts

def module_enclosing_func(offset):
	""" Test function to see if module-level enclosures are detected """
	def module_closure_func(value):
		""" Actual closure function, should be reported as: putil.tests.my_module.module_enclosing_func.module_closure_func """
		return offset+value
	return module_closure_func

def setter_enclosing_func(offset):
	""" Test function to see if property enclosures are detected """
	def setter_closure_func(self, value):
		""" Actual closure function, should be reported as: putil.tests.my_module.TraceClass.line.setter_enclosing_func.setter_closure_func """
		self._value = offset+value
	return setter_closure_func

class TraceClass1(object):	#pylint: disable=R0903
	""" First class to trace """
	def __init__(self):
		self._value = None

	value1 = property(lambda self: self._value+10, setter_enclosing_func(5))

def prop_decorator(func):
	""" Dummy property decorator """
	return func

class TraceClass2(object):	#pylint: disable=R0903
	""" Second class to trace """
	def __init__(self):
		self._value = None

	@putil.pcontracts.contract(value=int)
	@prop_decorator
	def _setter_func2(self, value):
		""" Simple setter method """
		print 'The value is {0}'.format(value)
		self._value = value

	def _getter_func2(self):
		""" Simple setter method """
		return self._value

	def _deleter_func2(self):	#pylint: disable=R0201
		""" Simple setter method """
		print 'Cannot delete attribute'

	value2 = property(_getter_func2, _setter_func2, _deleter_func2, doc='Value attribute')


class TraceClass3(object):	#pylint: disable=R0903
	""" Second class to trace """
	def __init__(self):
		self._value = None

	@property
	def value3(self):
		""" Simple setter method """
		return self._value

	@value3.setter
	@putil.pcontracts.contract(value=int)
	def value3(self, value):
		""" Simple setter method """
		print 'The value is {0}'.format(value)
		self._value = value

	@value3.deleter
	def value3(self):	#pylint: disable=R0201
		""" Simple setter method """
		print 'Cannot delete attribute'
