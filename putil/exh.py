# exh.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import sys
import copy
import inspect

import putil.misc
import putil.pinspect

###
# Functions
###
def set_exh_obj(value):
	""" Create exception handler object """
	mod_obj = sys.modules['__main__']
	setattr(mod_obj, '_EXH', value)


def get_exh_obj():
	""" Get exception handler object (if any) """
	mod_obj = sys.modules['__main__']
	return getattr(mod_obj, '_EXH') if hasattr(mod_obj, '_EXH') else None


def del_exh_obj():
	""" Create exception handler object """
	mod_obj = sys.modules['__main__']
	delattr(mod_obj, '_EXH')


def _ex_type_str(extype):	#pylint: disable-msg=R0201
	""" Returns a string corresponding to the exception type """
	return str(extype)[str(extype).rfind('.')+1:str(extype).rfind("'")]


def _get_code_id(frame_obj):
	""" Get callable ID from frame object, separated so that it can be mocked in testing """
	return (frame_obj.f_code.co_filename, frame_obj.f_code.co_firstlineno)


def _is_decorator(fin, lin, fuc, fui):
	""" Determine if frame components refer to a decorator """
	return (fin == '<string>') and (lin == 2) and (fuc == None) and (fui == None)

def _valid_frame(fin, fna):
	""" Selects valid stack frame to process """
	return not (fin.endswith('/putil/exh.py') or fin.endswith('/putil/exdoc.py') or fin.endswith('/putil/check.py')  or fin.endswith('/putil/pcontracts.py') or (fna in ['<module>', '<lambda>', 'contracts_checker']))


###
# Classes
###
class ExHandle(object):	#pylint: disable=R0902
	"""
	Manages exceptions
	"""
	def __init__(self):
		self._ex_dict = dict()
		self._callables_obj = putil.pinspect.Callables()
		self._callables_separator = '/'

	def __copy__(self):
		cobj = ExHandle()
		cobj._ex_dict = copy.deepcopy(self._ex_dict)	#pylint: disable=W0212
		cobj._callables_obj = copy.copy(self._callables_obj)	#pylint: disable=W0212
		return cobj

	def __str__(self):
		ret = ['Name....: {0}\nFunction: {1}\nType....: {2}\nMessage.: {3}\nChecked.: {4}'.format(key, self._ex_dict[key]['function'], _ex_type_str(self._ex_dict[key]['type']), \
																							self._ex_dict[key]['msg'], self._ex_dict[key]['checked']) for key in sorted(self._ex_dict.keys())]
		return '\n\n'.join(ret)

	def _format_msg(self, msg, edata):	#pylint: disable=R0201
		""" Substitute parameters in exception message """
		edata = edata if isinstance(edata, list) else [edata]
		for field in edata:
			if '*[{0}]*'.format(field['field']) not in msg:
				raise RuntimeError('Field {0} not in exception message'.format(field['field']))
			msg = msg.replace('*[{0}]*'.format(field['field']), field['value'])
		return msg

	def _get_callables_db(self):
		""" Returns database of callables """
		return self._callables_obj.callables_db

	def _get_callable_path(self):	#pylint: disable=R0201,R0914
		""" Get fully qualified calling function name """
		# Filter stack to omit frames that are part of the exception handling module, argument validation, or top level (tracing) module
		# Stack frame -> (frame object [0], filename [1], line number of current line [2], function name [3], list of lines of context from source code [4], index of current line within list [5])
		# Class initializations appear as: filename = '<string>', function name = '__init__', list of lines of context from source code = None, index of current line within list = None
		# Debug
		ret = list()
		decorator_flag = False
		skip_num = 0
		prev_name = name = ''
		for fob, fin, lin, fun, fuc, fui in [obj for obj in inspect.stack()][::-1]:
			# print putil.misc.strframe((fob, fin, lin, fun, fuc, fui))
			if skip_num > 0:
				# print putil.misc.pcolor('Skipped', 'green')
				skip_num -= 1
				continue
			# Gobble up two frames if it is a decorator
			if _is_decorator(fin, lin, fuc, fui) and (not decorator_flag):
				name = prev_name = self._get_callable_full_name(fob, fun)
				# print putil.misc.pcolor('Decorator (frame used) -> {0}'.format(name), 'green')
				ret.append(name)
				skip_num = 1
				decorator_flag = True
				continue
			elif _is_decorator(fin, lin, fuc, fui) and decorator_flag:
				# print putil.misc.pcolor('Chained decorator', 'green')
				skip_num = 1
				continue
			if fin.endswith('/putil/exh.py'):
				# print putil.misc.pcolor('End of chain encountered', 'green')
				break
			elif _valid_frame(fin, fun):
				name = self._get_callable_full_name(fob, fun)
				if (decorator_flag and (name != prev_name)) or (not decorator_flag):
					# print putil.misc.pcolor('Regular frame (frame used) -> {0}'.format(name), 'green')
					ret.append(name)
				# else:
				#	print putil.misc.pcolor('Chained decorator (extra frame)', 'green')
				prev_name = name
			# else:
			#	print putil.misc.pcolor('Invalid frame', 'green')
			decorator_flag = False
		return self._callables_separator.join(ret)

	def _get_callable_full_name(self, frame_obj, func):
		""" Get full path [module, class (if applicable) and function name] of callable """
		func_obj = frame_obj.f_locals.get(func, frame_obj.f_globals.get(func, getattr(frame_obj.f_locals.get('self'), func, None) if 'self' in frame_obj.f_locals else None))
		if func_obj:
			# Most of this code re-factored from pycallgraph/tracer.py of the Python Call Graph project (https://github.com/gak/pycallgraph/#python-call-graph)
			# Module name
			ret = self._get_module_name(frame_obj, func_obj)
			# Class name
			scontext = frame_obj.f_locals.get('self', None)
			ret += ('.'+scontext.__class__.__name__) if scontext else ''
			# Function/method/attribute name
			code = frame_obj.f_code
			func_name = code.co_name
			ret += '.'+('__main__' if func_name == '?' else (func_obj.__name__ if func_name == '' else func_name))
		else:
			# Function object could not be found, (possibly because it is an enclosed function), try to find it via code ID in the callables database
			code_id = _get_code_id(frame_obj)
			for name, value in self._callables_obj.callables_db.items():
				if code_id == value['code_id']:
					break
			else:
				print '\nFunction name {0}\nCode ID: {1}'.format(func, code_id)
				raise RuntimeError('Callable full name could not be obtained')
			ret = name	#pylint: disable=W0631
		return ret

	def _get_exception_by_name(self, name):
		""" Find exception object """
		exname = self._get_ex_data(name)['ex_name']
		if exname not in self._ex_dict:
			raise ValueError('Exception name {0} not found'.format(name))
		return self._ex_dict[exname]

	def _get_ex_data(self, name=None):	#pylint: disable=R0201
		""" Returns hierarchical function name """
		func_name = self._get_callable_path()
		ex_name = '{0}{1}{2}'.format(func_name, self._callables_separator if func_name is not None else '', name if name is not None else '')
		return {'func_name':func_name, 'ex_name':ex_name}

	def _get_callables_separator(self):
		""" Get callable separator character """
		return self._callables_separator

	def _get_module_name(self, frame_obj, func_obj):
		""" Get module name and optionally trace it """
		code = frame_obj.f_code
		scontext = frame_obj.f_locals.get('self', None)
		# Module name
		module = inspect.getmodule(code)
		module_name = module.__name__ if module else (scontext.__module__ if scontext else sys.modules[func_obj.__module__].__name__)
		self._callables_obj.trace(sys.modules[module_name])
		return module_name

	def _exceptions_db(self):	#pylint: disable-msg=R0201
		""" Returns a list of dictionaries suitable to be used with putil.tree module """
		return [{'name':self._ex_dict[key]['function'], 'data':'{0} ({1})'.format(_ex_type_str(self._ex_dict[key]['type']), self._ex_dict[key]['msg'])} for key in self._ex_dict.keys()]

	def _raise_exception(self, eobj, edata=None):
		""" Raise exception by name """
		_, _, tbobj = sys.exc_info()
		if edata:
			raise eobj['type'], eobj['type'](self._format_msg(eobj['msg'], edata)), tbobj
		else:
			raise eobj['type'], eobj['type'](eobj['msg']), tbobj

	def _validate_edata(self, edata):	#pylint: disable=R0201
		""" Validate edata argument of raise_exception_if method """
		if edata == None:
			return True
		if not (isinstance(edata, dict) or putil.misc.isiterable(edata)):
			return False
		edata = [edata] if isinstance(edata, dict) else edata
		for edict in edata:
			if (not isinstance(edict, dict)) or (isinstance(edict, dict) and (('field' not in edict) or ('field' in edict and (not isinstance(edict['field'], str))) or ('value' not in edict))):
				return False
		return True

	def add_exception(self, exname, extype, exmsg):	#pylint: disable=R0913,R0914
		r"""
		Adds exception to handler

		:param	exname: Exception name. Has to be unique within the namespace, duplicates are eliminated
		:type	exname: string
		:param	extype: Exception type. *Must* be derived from `Exception <https://docs.python.org/2/library/exceptions.html#exceptions.Exception>`_ class
		:type	extype: Exception type object, i.e. RuntimeError, TypeError, etc.
		:param	exmsg: Exception message that can contain fields to be replaced when the exception is raised via :py:meth:`putil.exh.ExHandle.raise_exception_if`. A field starts with the characters '\*[' and ends with the \
		 characters ']\*', the field name follows the same rules as variable names and is between these two sets of characters. For example, `*[file_name]*` defines the `file_name` field
		:type	exmsg: string
		:raises:
		 * TypeError (Argument `exmsg` is of the wrong type)

		 * TypeError (Argument `extype` is of the wrong type)

		 * TypeError (Argument `exname` is of the wrong type)
		"""
		if not isinstance(exname, str):
			raise TypeError('Argument `exname` is not valid')
		if not str(extype).startswith("<type 'exceptions."):
			raise TypeError('Argument `extype` is not valid')
		if not isinstance(exmsg, str):
			raise TypeError('Argument `exmsg` is not valid')
		ex_data = self._get_ex_data(exname)
		self._ex_dict[ex_data['ex_name']] = {'function':ex_data['func_name'], 'type':extype, 'msg':exmsg, 'checked':False}

	def raise_exception_if(self, exname, condition, edata=None):
		"""
		Conditionally raises exception

		:param	exname: Exception name
		:type	exname: string
		:param condition: Value that determines whether the exception is raised *(True)* or not *(False)*.
		:type  condition: boolean
		:param edata: Replacement values for fields in the exception message (see :py:meth:`putil.exh.ExHandle.add_exception`). Each dictionary can have only these two keys:

		 * **field** *(string)* -- Field name

		 * **value** *(any)* -- Field value, to be converted into a string with the format string method
		:type  edata: Dictionary or iterable of dictionaries
		:raises:
		 * TypeError (Argument `condition` is of the wrong type)

		 * TypeError (Argument `edata` is of the wrong type)

		 * TypeError (Argument `exmsg` is of the wrong type)

		 * TypeError (Argument `exname` is of the wrong type)
		"""
		if not isinstance(exname, str):
			raise TypeError('Argument `exname` is not valid')
		if not isinstance(condition, bool):
			raise TypeError('Argument `condition` is not valid')
		if not self._validate_edata(edata):
			raise TypeError('Argument `edata` is not valid')
		eobj = self._get_exception_by_name(exname)
		if condition:
			self._raise_exception(eobj, edata)
		eobj['checked'] = True

	# Managed attributes
	callables_db = property(_get_callables_db, None, None, doc='Dictionary of callables')
	"""
	Callables database of the modules needed to be traced to uniquely identify the function where exceptions are added, as reported by :py:meth:`putil.pinspect.Callables.callables_db`
	"""

	callables_separator = property(_get_callables_separator, None, None, doc='Callable separator character')
	"""
	Callables separator character ('/')
	"""

	exceptions_db = property(_exceptions_db, None, None, doc='Formatted exceptions')
	"""
	Exceptions database. A list of dictionaries that contain the following keys:

	 * **name** *(string)* -- Exception name of the format *function_name*. *exception_name*, where *function_name* is the full function name as it appears in the callable database (:py:meth:`putil.exh.ExHandle.callables_db`)
	   and *exception_name* is the name of the exception given when defined by :py:meth:`putil.exh.ExHandle.add_exception` (**exname** argument)

	 * **data** *(string)* -- Text of the form '*exception_type* (*exception_message*)' where *exception_type* and *exception_message* are the exception type and exception message, respectively, given when the exception was
	   defined by :py:meth:`putil.exh.ExHandle.add_exception` (**extype** and **exmsg** arguments)
	"""
