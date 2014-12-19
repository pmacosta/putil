""" my_module1 module """

def enclosing_func(offset):
	""" Test function to see if code detects enclosures """
	def closure_func(value):
		"""
		Actual closure function, should be reported as:
		putil.my_module.enclosing_func.closure_func
		"""
		return offset+value
	return closure_func

class MyClass(object):	#pylint: disable=R0903
	""" Test class """
	def __init__(self):
		self._value = None
	def _getter_func(self):
		""" Simple getter method """
		return self._value
	def _setter_func(self, value):
		""" Simple setter method """
		self._value = value
	value = property(_getter_func, _setter_func, None, doc='Value property')

