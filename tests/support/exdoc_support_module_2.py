# pylint: disable=W0212
"""
exdoc_support_module_2 module
"""

def module_enclosing_func(offset):
	""" Test function to see if module-level enclosures are detected """
	def module_closure_func(self):
		""" Actual closure function, should be reported as: putil.tests.my_module.module_enclosing_func.module_closure_func """
		self._exobj.add_exception(exname='illegal_value', extype=TypeError, exmsg='Argument `value` is not valid')
		return self._value1+offset
	return module_closure_func
