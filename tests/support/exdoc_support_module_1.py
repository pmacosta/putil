# pylint: disable=W0212
"""
exdoc_support_module_1 module
"""

import putil.exh
import exdoc_support_module_2
import putil.pcontracts


###
# Module functions
###
def _validate_arguments():
	""" Internal argument validation, have exceptions defined after a chain of function calls """
	exobj = putil.exh.get_exh_obj() if putil.exh.get_exh_obj() else putil.exh.ExHandle()
	exobj.add_exception(exname='illegal_argument', extype=TypeError, exmsg='Argument is not valid')

def _write():
	""" Internal pass-through function """
	_validate_arguments()

def write():
	""" Module level function #1 """
	exobj = putil.exh.get_exh_obj() if putil.exh.get_exh_obj() else putil.exh.ExHandle()
	exobj.add_exception(exname='illegal_write_call', extype=TypeError, exmsg='Cannot call write')
	_write()

def read():
	""" Module level function #2 """
	exobj = putil.exh.get_exh_obj() if putil.exh.get_exh_obj() else putil.exh.ExHandle()
	exobj.add_exception(exname='illegal_read_call', extype=TypeError, exmsg='Cannot call read')

def probe():
	""" Module level function #3 """
	exobj = putil.exh.get_exh_obj() if putil.exh.get_exh_obj() else putil.exh.ExHandle()
	exobj.add_exception(exname='illegal_probe_call', extype=TypeError, exmsg='Cannot call probe')

###
# Classes
###
def dummy_decorator(func):
	""" Dummy property decorator """
	return func

class ExceptionAutoDocClass(object):	#pylint: disable=R0902,R0903
	""" Class to automatically generate exception documentation for """
	@putil.pcontracts.contract(value1=int, value2=int, value3=int, value4=int)
	@dummy_decorator
	def __init__(self, value1=0, value2=0, value3=0, value4=0):
		self._exobj = putil.exh.get_exh_obj() if putil.exh.get_exh_obj() else putil.exh.ExHandle()
		self._value1 = value1
		self._value2 = value2
		self._value3 = value3
		self._value4 = value4

	def _del_value3(self):	# pylint: disable=C0111
		""" Deleter method for property defined via function """
		self._exobj.add_exception(exname='illegal_value3', extype=TypeError, exmsg='Cannot delete value3')

	def _get_value3(self):	# pylint: disable=C0111
		""" Getter method for property defined via function """
		self._exobj.add_exception(exname='illegal_value3', extype=TypeError, exmsg='Cannot get value3')
		return self._value3

	def _set_value1(self, value):	# pylint: disable=C0111
		""" Setter method for propety with getter defined via enclosed function """
		self._exobj.add_exception(exname='illegal_value1', extype=TypeError, exmsg='Argument `value1` is not valid')
		self._value1 = value

	def _set_value2(self, value):	# pylint: disable=C0111
		""" Setter method for propety with getter defined via lambda """
		self._exobj.add_exception(exname='illegal_value2', extype=TypeError, exmsg='Argument `value2` is not valid')
		self._value2 = value

	def _set_value3(self, value):	# pylint: disable=C0111
		""" Setter method for property defined via function """
		self._exobj.add_exception(exname='illegal_value3', extype=TypeError, exmsg='Argument `value3` is not valid')
		self._value3 = value

	def add(self, operand):	# pylint: disable=C0111
		""" Method #1 that should not appear in exception tree since it has no exceptions defined """
		self._value1 += operand

	def subtract(self, operand):	# pylint: disable=C0111
		""" Method #2 that should not appear in exception tree since it has no exceptions defined """
		self._value1 -= operand

	def multiply(self, operand):	# pylint: disable=C0111
		""" Sample method with defined exceptions in function body to auto-document """
		self._exobj.add_exception(exname='maximum_value', extype=ValueError, exmsg='Overflow')
		self._value1 *= operand

	@putil.pcontracts.contract(divisor='int|float,>0')
	def divide(self, divisor):	# pylint: disable=C0111
		""" Sample method with defined exceptions in argument contract to auto-document """
		self._value1 = self._value1/float(divisor)

	@property
	def temp(self):
		""" Getter method defined with decorator """
		return self._value4

	@temp.setter
	@putil.pcontracts.contract(value=int)
	def temp(self, value):
		""" Setter method defined with decorator """
		self._value4 = value

	@temp.deleter
	def temp(self):	#pylint: disable=R0201
		""" Deleter method defined with decorator """
		print 'Cannot delete attribute'

	value1 = property(exdoc_support_module_2.module_enclosing_func(10), _set_value1)

	value2 = property(lambda self: self._value2+10, _set_value2)

	value3 = property(_get_value3, _set_value3, _del_value3)

