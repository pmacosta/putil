# pylint: disable=W0212
"""
my_module2 module
"""

def setter_enclosing_func(offset):
	""" Test function to see if property enclosures are detected """
	def setter_closure_func(self, value):
		""" Actual closure function, should be reported as: putil.tests.my_module.TraceClass.line.setter_enclosing_func.setter_closure_func """
		self._value = offset+value
	return setter_closure_func
