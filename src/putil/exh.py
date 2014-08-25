# exh.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Exception handling classes, methods, functions and constants
"""

class ExHandle(object):
	""" Exception handling class """
	def __init__(self, func_name=None, ex_list=None):
		self._trace_on = False
		self._trace_list = None
		self._ex_list = list()
		if ((func_name is None) and (ex_list is not None)) or ((func_name is not None) and (ex_list is None)):
			raise RuntimeError('Arguments `func_name` and `ex_list` have to be either both defined or both undefined')
		if (func_name is not None) and (ex_list is not None):
			for obj in ex_list:
				obj['func'] = func_name
				obj['checked'] = False
			self._ex_list = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in ex_list)] # Remove duplicates

	def ex_add(self, name, funcname, extype, exmsg):	#pylint: disable=R0913
		""" Add exception to database """
		self._ex_list.append({'name':name, 'function':funcname, 'type':extype, 'msg':exmsg, 'checked':False})
		self._ex_list = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in self._ex_list)] # Remove duplicates

	def get_exception_by_name(self, name):
		""" Find exception object """
		for obj in self._ex_list:
			if obj['name'] == name:
				return obj
		raise ValueError('Exception name {0} not found'.format(name))

	def raise_exception(self, name):
		""" Raise exception by name """
		obj = self.get_exception_by_name(name)
		raise obj['type'](obj['msg'])

	def raise_exception_if(self, name, condition):
		""" Raise exception by name if condition is true """
		if condition:
			self.raise_exception(name)
		self.get_exception_by_name(name)['checked'] = True

	def start_trace(self, func_name):
		""" Traces which exceptions are being checked and in which routine """
		if self._trace_on:
			raise RuntimeError('Exception tracing already on')
		self._trace_on = True

	def _ex_type_str(self, extype):	#pylint: disable-msg=R0201
		""" Returns a string corresponding to the exception type """
		return str(extype)[str(extype).rfind('.')+1:str(extype).rfind("'")]

	def __str__(self):
		ret = ['Name....: {0}\nFunction: {1}\nType....: {2}\nMessage.: {3}\nChecked.: {4}'.format(ex['name'], ex['function'], self._ex_type_str(ex['type']), ex['msg'], ex['checked']) for ex in self._ex_list]
		return '\n\n'.join(ret)
