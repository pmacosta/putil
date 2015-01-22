# pinspect_support_module_4.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212


def another_property_action_enclosing_function():	#pylint: disable=C0103
	""" Generator function to test namespace support for enclosed class properties """
	def fget(self):
		""" Actual getter function """
		return math.sqrt(self._value)	#pylint:disable=E0602
	return property(fget)
