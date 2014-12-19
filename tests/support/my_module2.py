""" my_module2 module """
def yet_another_enclosing_func(offset, setter_func):
	""" Test function to see if code detects enclosures """
	def yet_another_closure_func(self):
		"""
		Actual closure function, should be reported as:
		putil.my_module2.yet_another_enclosing_func.yet_another_closure_func
		"""
		return offset+self._value	#pylint: disable=W0212
	return property(yet_another_closure_func, setter_func, None, doc='Value property')


class MyClassThatErrorsWhenTraced(object):	#pylint: disable=R0903
	""" Test class that so far raises exception when 'traced' """
	def __init__(self):
		self._value = 10
	def _setter_func(self, value):
		""" Simple setter method """
		self._value = value
	def _setter_func2(self, value):
		""" Simple setter method """
		self._value = value
	value = yet_another_enclosing_func(5, _setter_func)
	line = property(lambda self: self._value+10, _setter_func2)

