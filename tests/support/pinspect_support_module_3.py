# pylint: disable=W0212
"""
putil.pinspect testing support module #3
"""

def deleter(self):	#pylint: disable=W0613
	""" Getter function to test if enclosed class detection works with property action functions in different files """
	print 'Deleter action'

def another_class_enclosing_func():
	""" Test function to see if classes within enclosures are detected, in this case with property actions imported via 'from *' """
	from pinspect_support_module_1 import simple_property_generator
	class FromImportClosureClass(object):	#pylint: disable=R0903
		""" Actual class """
		def __init__(self, value):
			self._value = value

		encprop = simple_property_generator()

	return FromImportClosureClass

def another_property_action_enclosing_function():	#pylint: disable=C0103
	""" Generator function to test namespace support for enclosed class properties """
	def fget(self):
		""" Actual getter function """
		return math.sqrt(self._value)	#pylint:disable=E0602
	return property(fget)
