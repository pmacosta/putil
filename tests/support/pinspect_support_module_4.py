# pylint: disable=W0212
"""
putil.pinspect testing support module #4
"""

def another_property_action_enclosing_function():	#pylint: disable=C0103
	""" Generator function to test namespace support for enclosed class properties """
	def fget(self):
		""" Actual getter function """
		return math.sqrt(self._value)	#pylint:disable=E0602
	return property(fget)
