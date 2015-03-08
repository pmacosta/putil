# exh.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
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
	"""
	Sets global exception handler

	:param	value: Exception handler
	:type	value: :py:class:`putil.exh.ExHandle()` object

	:raises: TypeError (Argument `value` is not valid)
	"""
	if not isinstance(value, ExHandle):
		raise TypeError('Argument `value` is not valid')
	mod_obj = sys.modules['__main__']
	setattr(mod_obj, '_EXH', value)


def get_exh_obj():
	"""
	Returns global exception handler

	:rtype: :py:class:`putil.exh.ExHandle()` object if global exception handler is set, *None* otherwise
	"""
	mod_obj = sys.modules['__main__']
	return getattr(mod_obj, '_EXH') if hasattr(mod_obj, '_EXH') else None


def get_or_create_exh_obj(full_fname=False):
	"""
	Returns global exception handler if it is set, otherwise creates a new global exception handler and returns it

	:param	full_fname: Flag that indicates whether fully qualified function/method names should be obtained for functions/methods that use the exception manager. There is performance penalty if **full_name** is `True` as \
	the call stack needs to be traced. This argument is only relevant if the global exception handler is not set and a new one is created
	:type	full_fname: boolean
	:rtype: :py:class:`putil.exh.ExHandle()` object if handler is set
	:raises: TypeError (Argument `full_name` is not valid)
	"""
	mod_obj = sys.modules['__main__']
	if not hasattr(mod_obj, '_EXH'):
		set_exh_obj(ExHandle(full_fname))
	return getattr(mod_obj, '_EXH')


def del_exh_obj():
	"""
	Deletes global exception handler (if any)
	"""
	mod_obj = sys.modules['__main__']
	try:
		delattr(mod_obj, '_EXH')
	except:	#pylint: disable=W0702
		pass


def _ex_type_str(extype):	#pylint: disable-msg=R0201
	""" Returns a string corresponding to the exception type """
	return str(extype)[str(extype).rfind('.')+1:str(extype).rfind("'")]


def _get_code_id(frame_obj):
	""" Get callable ID from frame object, separated so that it can be mocked in testing """
	return (frame_obj.f_code.co_filename, frame_obj.f_code.co_firstlineno)


def _valid_frame(fobj):
	""" Selects valid stack frame to process """
	fin = fobj.f_code.co_filename
	fna = fobj.f_code.co_name
	return not (fin.endswith('/putil/exh.py') or fin.endswith('/putil/exdoc.py') or fin.endswith('/putil/check.py')  or fin.endswith('/putil/pcontracts.py') or\
			 (fna in ['<module>', '<lambda>', 'contracts_checker']))


###
# Classes
###
class ExHandle(object):	#pylint: disable=R0902
	"""
	Exception manager

	:param	full_fname: Flag that indicates whether fully qualified function/method names should be obtained for functions/methods that use the exception manager. There is performance penalty if **full_name** is `True` as \
	the call stack needs to be traced
	:type	full_fname: boolean
	:rtype: :py:class:`putil.exh.ExHandle()` object
	:raises: TypeError (Argument `full_name` is not valid)
	"""
	def __init__(self, full_fname=False):
		if not isinstance(full_fname, bool):
			raise TypeError('Argument `full_fname` is not valid')
		self._cache = {}
		self._ex_dict = {}
		self._callables_obj = putil.pinspect.Callables()
		self._callables_separator = '/'
		self._full_fname = full_fname

	def __copy__(self):
		cobj = ExHandle(full_fname=self._full_fname)
		cobj._ex_dict = copy.deepcopy(self._ex_dict)	#pylint: disable=W0212
		cobj._callables_obj = copy.copy(self._callables_obj)	#pylint: disable=W0212
		return cobj

	def __str__(self):
		ret = ['Name....: {0}\nFunction: {1}\nType....: {2}\nMessage.: {3}\nChecked.: {4}'.format(key, self._ex_dict[key]['function'], _ex_type_str(self._ex_dict[key]['type']), \
																							self._ex_dict[key]['msg'], self._ex_dict[key]['checked']) for key in sorted(self._ex_dict.keys())]
		return '\n\n'.join(ret)

	def _exceptions_db(self):	#pylint: disable-msg=R0201
		""" Returns a list of dictionaries suitable to be used with putil.tree module """
		return [{'name':self._ex_dict[key]['function'] if self._full_fname else key, 'data':'{0} ({1})'.format(_ex_type_str(self._ex_dict[key]['type']), self._ex_dict[key]['msg'])} for key in self._ex_dict.keys()]

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
		# Calling inspect.stack() is slow, try to see if there is a cache hit calling sys._getframe which is faster and only use inspect.stack() if there is a cache miss
		fnum = 0
		cache_frame = sys._getframe(fnum)	#pylint: disable=W0212
		while not _valid_frame(cache_frame):
			fnum += 1
			cache_frame = sys._getframe(fnum)	#pylint: disable=W0212
		cache_key = id(cache_frame)	#pylint: disable=W0631
		if cache_key in self._cache:
			return cache_key, self._cache[cache_key]
		if not self._full_fname:
			return cache_key, None

		# Filter stack to omit frames that are part of the exception handling module, argument validation, or top level (tracing) module
		# Stack frame -> (frame object [0], filename [1], line number of current line [2], function name [3], list of lines of context from source code [4], index of current line within list [5])
		# Class initializations appear as: filename = '<string>', function name = '__init__', list of lines of context from source code = None, index of current line within list = None
		ret = list()
		decorator_flag, skip_flag = False, False
		prev_name = name = ''

		#fstack = tuple([obj for obj in inspect.stack()][::-1])
		#for num, (fob, fin, lin, fun, fuc, fui) in enumerate(fstack):
		stack = inspect.stack()
		for fob, fin, lin, fun, fuc, fui in reversed(stack[fnum:]):	#pylint: disable=W0631
			# print putil.misc.pcolor('{0:3d}/{1:3d}'.format(num, len(fstack)), 'yellow')+' '+putil.misc.strframe((fob, fin, lin, fun, fuc, fui))
			if skip_flag:
				# print putil.misc.pcolor('Skipped', 'green')
				skip_flag = False
				continue
			# Gobble up two frames if it is a decorator
			if (fin == '<string>') and (lin == 2) and (fuc == None) and (fui == None):	# frame corresponds to a decorator
				skip_flag = True
				if not decorator_flag:
					#name = prev_name = self._get_callable_full_name(fob, fun)
					name = prev_name = self._get_callable_full_name(fob, fin, lin, fun, fuc, fui)
					# print putil.misc.pcolor('Decorator (frame used) -> {0}'.format(name), 'green')
					ret.append(name)
					decorator_flag = True
			elif _valid_frame(fob):
				#name = self._get_callable_full_name(fob, fun)
				name = self._get_callable_full_name(fob, fin, lin, fun, fuc, fui)
				if (decorator_flag and (name != prev_name)) or (not decorator_flag):
					# print putil.misc.pcolor('Regular frame (frame used) -> {0}'.format(name), 'green')
					ret.append(name)
				# else:
					# print putil.misc.pcolor('Chained decorator (extra frame)', 'green')
				prev_name = name
				decorator_flag = False
		# print self._callables_separator.join(ret)
		ret = self._callables_separator.join(ret)
		if len(self._cache) > 10:
			self._cache.clear()
		self._cache[cache_key] = ret
		return cache_key, ret

	def _get_callable_full_name(self, fob, fin, lin, fun, fuc, fui):	#pylint: disable=R0913,W0613
		""" Get full path [module, class (if applicable) and function name] of callable """
		func_obj = None
		if fin != '<string>':
			code_id = _get_code_id(fob)
		else:
			#func_obj = self._get_func_obj(fob, fun)
			func_obj = fob.f_globals[fun]
			while getattr(func_obj, '__wrapped__', None):
				func_obj = getattr(func_obj, '__wrapped__')
			code_id = putil.pinspect._get_code_id(func_obj)	# pylint: disable=W0212
		self._get_module_name(fob, func_obj)
		try:
			return self._callables_obj.reverse_callables_db[code_id]
		except:
			# print '\nCallables database'
			# print '------------------'
			# print '\n'.join(sorted(self._get_callables_db().keys()))
			# print 'Reverse callables database'
			# print '--------------------------'
			# print '\n'.join(sorted(self._callables_obj.reverse_callables_db.values()))
			raise RuntimeError('Callable with call ID {0} not found in reverse callables database'.format(code_id))

	def _get_callables_separator(self):
		""" Get callable separator character """
		return self._callables_separator

	def _get_exception_by_name(self, name):
		""" Find exception object """
		exname = self._get_ex_data(name)['ex_name']
		if exname not in self._ex_dict:
			raise ValueError('Exception name {0} not found'.format(name))
		return self._ex_dict[exname]

	def _get_ex_data(self, name=None):	#pylint: disable=R0201
		""" Returns hierarchical function name """
		func_id, func_name = self._get_callable_path()
		ex_name = ''.join([str(func_id), self._callables_separator if name is not None else '', name if name is not None else ''])
		return {'func_name':func_name, 'ex_name':ex_name}

	def _get_module_name(self, frame_obj, func_obj):
		""" Get module name and optionally trace it """
		code = frame_obj.f_code
		scontext = frame_obj.f_locals.get('self', None)
		# Module name
		module = inspect.getmodule(code)
		module_name = module.__name__ if module else (scontext.__module__ if scontext else sys.modules[func_obj.__module__].__name__)
		self._callables_obj.trace(sys.modules[module_name])
		return module_name

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
	Callables database of the modules using the exception handler, as reported by :py:meth:`putil.pinspect.Callables.callables_db`
	"""

	callables_separator = property(_get_callables_separator, None, None, doc='Callable separator character')
	"""
	Character ('/') used to separate the sub-parts of fully qualified function names in :py:meth:`putil.exh.ExHandle.callables_db` and **name** key of :py:meth:`putil.exh.ExHandle.exceptions_db`
	"""

	exceptions_db = property(_exceptions_db, None, None, doc='Formatted exceptions')
	"""
	Exceptions database. A list of dictionaries that contain the following keys:

	 * **name** *(string)* -- Exception name of the form '*function_identifier* / *exception_name*'. The contents of *function_identifier* depend on the value of **full_fname** used to
	   create the exception handler. If **full_name** is `True`, *function_identifier* is the fully qualified function name as it appears in the callables database (:py:meth:`putil.exh.ExHandle.callables_db`).
	   If **full_name** is `False`, then *function_identifier* is a decimal string representation of the function's identifier as reported by the `id() <https://docs.python.org/2/library/functions.html#id>`_
	   function. *exception_name* is the name of the exception provided when it was defined in :py:meth:`putil.exh.ExHandle.add_exception` (**exname** argument)

	 * **data** *(string)* -- Text of the form '*exception_type* (*exception_message*)' where *exception_type* and *exception_message* are the exception type and exception message, respectively, given when the exception was
	   defined by :py:meth:`putil.exh.ExHandle.add_exception` (**extype** and **exmsg** arguments)
	"""
