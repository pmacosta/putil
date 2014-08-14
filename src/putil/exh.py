# exh.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Exception handling classes, methods, functions and constants
"""

class ExHandle(object):
	""" Exception handling class """
	def __init__(self, func_name, ex_list):
		for obj in ex_list:
			obj['func'] = func_name
			obj['checked'] = False
		self._ex_list = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in ex_list)] # Remove duplicates
		self._trace_on = False
		self._trace_list = None

	def get_exception_by_name(self, name):
		""" Find exception object """
		for obj in self._ex_list:
			if obj['name'] == name:
				return name
		raise ValueError('Exception name {0} not found'.format(name))

	def raise_exception(self, name):
		""" Raise exception by name """
		obj = self.get_exception_by_name(name)
		raise obj['type'](obj['msg'])

	def raise_exception_if(self, name, condition):
		""" Raise exception by name if condition is true """
		if condition:
			self.raise_exception(name)
		for obj in self._ex_list:
			if obj['name'] == name:
				obj['checked'] = True
				break

	def start_trace(self, func_name):
		""" Traces which exceptions are being checked and in which routine """
		if self._trace_on:
			raise RuntimeError('Exception tracing already on')
		self._trace_on = True
