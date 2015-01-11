# pylint: disable=W0212
"""
putil.pinspect testing support module #2
"""

def setter_enclosing_func(offset):
	""" Test function to see if property enclosures are detected """
	def setter_closure_func(self, num):
		""" Actual closure function """
		self._clsvar = offset+num
	return setter_closure_func
