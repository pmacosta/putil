# exh.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Exception handling classes, methods, functions and constants
"""

class ExHandle(object):
	""" Exception handling class """
	def __init__(self, ex_list):
		tlist = list()
		for obj in ex_list:
			obj['checked'] = False
			tlist.append(obj)
		self._ex_list = tlist

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
		tlist = list()
		for obj in self._ex_list:
			obj['checked'] = True if obj['name'] == name else obj['checked']
			tlist.append(obj)
		self._ex_list = tlist

	def start_trace(self, func_name):
		""" Traces which exceptions are being checked and in which routine """
		pass

