# pinspect_example_3.py
# pylint: disable=C0111,W0611,R0903,W0612,W0212
import math, sys
VERSION = sys.version_info[0]
if VERSION == 2:
	import python2_module as pm
else:
	import python3_module as pm
def my_func():
	""" Enclosing function """
	import putil.eng
	class MyClass(object):
		""" Enclosed class """
		def __init__(self, value):
			self._value = value
			print 'Value received is {0}'.format(putil.eng.peng(value, 3, False))
		def _get_value(self):
			return self._value
		value = property(_get_value, pm._set_value, None, 'Value property')

def print_name(name):
	print 'My name is {0}, and sqrt(2) = {1}'.format(name, math.sqrt(2))
