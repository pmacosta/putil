# exh.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Exception handling classes, methods, functions and constants
"""

import inspect

import putil.check

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

	def get_func_name(self):	#pylint: disable=R0201
		""" Get calling function name """
		# Stack frame is a tuple with the following items:
		# 0: the frame object
		# 1: the filename
		# 2: the line number of the current line
		# 3: the function name
		# 4: a list of lines of context from the source code
		# 5: the index of the current line within that list.
		frame_list = inspect.stack()
		func_name = ''
		for num, (fobj, file_name, _, fname, fcontext, findex) in enumerate(frame_list):
			lcontext = fobj.f_locals
			gcontext = fobj.f_globals
			scontext = lcontext['self'] if 'self' in lcontext else None
			if (('wrapper' in fname) and ('check.py' in file_name)) or ('exh.py' in file_name) or ('check.py' in file_name) or ((fcontext is None) and (findex is None)):
				pass
			elif fname != '<module>':
				pfunc = lcontext[fname] if fname in lcontext else (gcontext[fname] if fname in gcontext else (getattr(scontext, fname) if ((scontext is not None) and (getattr(scontext, fname, -1) != -1)) else None))
				if not pfunc:
					raise RuntimeError('Context of parent function could not be obtained')
				func_name = (putil.check.get_funcname(pfunc) if num != len(frame_list)-1 else '')+('' if not func_name else '.')+func_name
				#if ('putil.exh' not in func_name) and ('putil.check' not in func_name):
				#	break
		#if ('search_for_node' not in func_name) and ('build_tree' not in func_name):
		#	for frame in frame_list:
		#		print frame
		#	print func_name
		#	print
		return func_name

	def ex_add(self, name, extype, exmsg):	#pylint: disable=R0913,R0914
		""" Add exception to database """
		func_name = self.get_func_name()
		self._ex_list.append({'name':self.get_ex_name(name), 'function':func_name, 'type':extype, 'msg':exmsg, 'checked':False})
		self._ex_list = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in self._ex_list)] # Remove duplicates

	def get_ex_name(self, name):
		""" Returns hierarchical function name """
		func_name = self.get_func_name()
		return '{0}{1}{2}'.format(func_name, '.' if func_name is not None else '', name)

	def get_exception_by_name(self, name):
		""" Find exception object """
		exname = self.get_ex_name(name)
		for obj in self._ex_list:
			if obj['name'] == exname:
				return obj
		raise ValueError('Exception name {0} not found'.format(name))

	def raise_exception(self, name, **kargs):
		""" Raise exception by name """
		if (len(kargs) == 1) and ('edata' not in kargs):
			raise RuntimeError('Illegal keyword argument passed to raise_exception')
		if len(kargs) > 1:
			raise RuntimeError('Illegal keyword argument{0} passed to raise_exception'.format('s' if len(kargs)-(1 if 'edata' in kargs else 0) > 1 else ''))
		obj = self.get_exception_by_name(name)
		if len(kargs):
			raise obj['type'](self._format_msg(obj['msg'], kargs['edata']))
		else:
			raise obj['type'](obj['msg'])

	def _format_msg(self, msg, edata):	#pylint: disable=R0201
		""" Substitute parameters in exception message """
		edata = edata if isinstance(edata, list) else [edata]
		for field in edata:
			if 'field' not in field:
				raise ValueError('Key `field` not in field definition')
			if 'value' not in field:
				raise ValueError('Key `value` not in field definition')
			if '*[{0}]*'.format(field['field']) not in msg:
				raise RuntimeError('Field {0} not in exception message'.format(field['field']))
			msg = msg.replace('*[{0}]*'.format(field['field']), field['value'])
		return msg

	def raise_exception_if(self, name, condition, **kargs):
		""" Raise exception by name if condition is true """
		if (len(kargs) == 1) and ('edata' not in kargs):
			raise RuntimeError('Illegal keyword argument passed to raise_exception')
		if len(kargs) > 1:
			raise RuntimeError('Illegal keyword argument{0} passed to raise_exception'.format('s' if len(kargs)-(1 if 'edata' in kargs else 0) > 1 else ''))
		if condition:
			self.raise_exception(name, **kargs)
		self.get_exception_by_name(name)['checked'] = True

	def _ex_type_str(self, extype):	#pylint: disable-msg=R0201
		""" Returns a string corresponding to the exception type """
		return str(extype)[str(extype).rfind('.')+1:str(extype).rfind("'")]

	def tree_data(self):	#pylint: disable-msg=R0201
		""" Returns a list of dictionaries suitable to be used with putil.tree module """
		return [{'node':ex['function'], 'data':'{0} ({1})'.format(self._ex_type_str(ex['type']), ex['msg'])} for ex in self._ex_list]

	def __str__(self):
		ret = ['Name....: {0}\nFunction: {1}\nType....: {2}\nMessage.: {3}\nChecked.: {4}'.format(ex['name'], ex['function'], self._ex_type_str(ex['type']), ex['msg'], ex['checked']) for ex in self._ex_list]
		return '\n\n'.join(ret)
