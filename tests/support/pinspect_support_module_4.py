# pinspect_support_module_4.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

USAGE1 = """\
	This is a test\
	of a multi-line string """	#pylint: disable=C0103

USAGE2 = r"""
	This is a test
	of a raw multi-line string """	#pylint: disable=C0103

USAGE3 = r""" This is a test of a single-line string """	#pylint: disable=C0103

def another_property_action_enclosing_function():	#pylint: disable=C0103
	""" Generator function to test namespace support for enclosed class properties """
	def fget(self):
		""" Actual getter function """
		return math.sqrt(self._value)	#pylint:disable=E0602
	return property(fget)
