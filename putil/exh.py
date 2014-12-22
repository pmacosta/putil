# exh.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Exception handling classes, methods, functions and constants
"""

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


###
# Classes
###
class ExHandle(object):	#pylint: disable=R0902
	"""
	Manages exceptions and optionally automatically generates exception documentation in with `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ mark-up

	:param	obj: Object to document exceptions for
	:type	obj: Class object or module-level object
	:rtype: :py:class:`putil.exh.ExHandle()` object

	:raises:
	 * TypeError (Argument `obj` is of the wrong type)

	 * ValueError (Hidden objects cannot be traced)
	"""
	def __init__(self):
		self._callable_db = dict()
		self._module_db = list()
		self._ex_list = list()
		self._callable_obj = putil.pinspect.Callables()

	def __copy__(self):
		cobj = ExHandle()
		cobj._callable_db = copy.copy(self._callable_db)	#pylint: disable=W0212
		cobj._module_db = copy.copy(self._module_db)	#pylint: disable=W0212
		cobj._ex_list = copy.copy(self._ex_list)	#pylint: disable=W0212
		return cobj

	def __deepcopy__(self, memodict=None):
		memodict = dict() if memodict is None else memodict
		cobj = ExHandle()
		cobj._callable_db = copy.deepcopy(self._callable_db)	#pylint: disable=W0212
		cobj._module_db = copy.deepcopy(self._module_db)	#pylint: disable=W0212
		cobj._ex_list = copy.deepcopy(self._ex_list, memodict)	#pylint: disable=W0212
		return cobj

	def __str__(self):
		ret = ['Name....: {0}\nFunction: {1}\nType....: {2}\nMessage.: {3}\nChecked.: {4}'.format(ex['name'], ex['function'], self._ex_type_str(ex['type']), ex['msg'], ex['checked']) for ex in self._ex_list]
		return '\n\n'.join(ret)

	def _ex_type_str(self, extype):	#pylint: disable-msg=R0201
		""" Returns a string corresponding to the exception type """
		return str(extype)[str(extype).rfind('.')+1:str(extype).rfind("'")]

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

	def _get_callable_db(self):
		""" Returns database of callables """
		return self._callable_obj.callables_db

	def _get_callable_name(self):	#pylint: disable=R0201,R0914
		""" Get fully qualified calling function name """
		ret = list()
		# Filter stack to omit frames that are part of the exception handling module, argument validation, or top level (tracing) module
		# Stack frame -> (frame object [0], filename [1], line number of current line [2], function name [3], list of lines of context from source code [4], index of current line within list [5])
		# Class initializations appear as: filename = '<string>', function name = '__init__', list of lines of context from source code = None, index of current line within list = None
		fstack = [(fo, fn, (fin, fc, fi) == ('<string>', None, None)) for fo, fin, _, fn, fc, fi in inspect.stack() if self._valid_frame(fin, fn)]
		for frame_obj, func in [(fo, fn) for num, (fo, fn, flag) in reversed(list(enumerate(fstack))) if not (flag and num)]:
			func_obj = frame_obj.f_locals.get(func, frame_obj.f_globals.get(func, getattr(frame_obj.f_locals.get('self'), func, None) if 'self' in frame_obj.f_locals else None))
			ret.append(self._get_callable_path(frame_obj, func_obj))
		return '.'.join(ret)

	def _get_callable_path(self, frame_obj, func_obj):
		""" Get full path of callable """
		# Most of this code re-factored from pycallgraph/tracer.py of the Python Call Graph project (https://github.com/gak/pycallgraph/#python-call-graph)
		code = frame_obj.f_code
		scontext = frame_obj.f_locals.get('self', None)
		# Module name
		module = inspect.getmodule(code)
		module_name = module.__name__ if module else (scontext.__module__ if scontext else sys.modules[func_obj.__module__].__name__)
		self._callable_obj.trace(sys.modules[module_name])
		ret = module_name
		# Class name
		ret += ('.'+scontext.__class__.__name__) if scontext else ''
		# Function/method/attribute name
		func_name = code.co_name
		ret += '.'+('__main__' if func_name == '?' else (func_obj.__name__ if func_name == '' else func_name))
		return ret

	def _get_exception_by_name(self, name):
		""" Find exception object """
		exname = self._get_ex_data(name)['ex_name']
		for obj in self._ex_list:
			if obj['name'] == exname:
				return obj
		raise ValueError('Exception name {0} not found'.format(name))

	def _get_ex_data(self, name=None):	#pylint: disable=R0201
		""" Returns hierarchical function name """
		func_name = self._get_callable_name()
		ex_name = '{0}{1}{2}'.format(func_name, '.' if func_name is not None else '', name if name is not None else '')
		return {'func_name':func_name, 'ex_name':ex_name}

	def _tree_data(self):	#pylint: disable-msg=R0201
		""" Returns a list of dictionaries suitable to be used with putil.tree module """
		return [{'name':ex['function'], 'data':'{0} ({1})'.format(self._ex_type_str(ex['type']), ex['msg'])} for ex in self._ex_list]

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
		for edict in edata:
			if (not isinstance(edict, dict)) or (isinstance(edict, dict) and (('field' not in edict) or ('value' not in edict))):
				return False

	def _valid_frame(self, fin, fna):	#pylint: disable-msg=R0201
		""" Selects valid stack frame to process """
		return not (fin.endswith('/putil/exh.py') or fin.endswith('/putil/exhdoc.py') or fin.endswith('/putil/check.py')  or fin.endswith('/putil/pcontracts.py') or (fna in ['<module>', '<lambda>', 'contracts_checker']))

	def add_exception(self, exname, extype, exmsg):	#pylint: disable=R0913,R0914
		"""
		Adds exception to handler

		:param	exname: Exception name. Has to be unique within the namespace, duplicates are eliminated
		:type	exname: string
		:param	extype: Exception type. *Must* be derived from `Exception <https://docs.python.org/2/library/exceptions.html#exceptions.Exception>`_ class
		:type	extype: Exception type object, i.e. RuntimeError, TypeError, etc.
		:param	exmsg: Exception message
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
		self._ex_list.append({'name':ex_data['ex_name'], 'function':ex_data['func_name'], 'type':extype, 'msg':exmsg, 'checked':False})
		self._ex_list = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in self._ex_list)] # Remove duplicates

	def raise_exception_if(self, exname, condition, edata=None):
		"""
		Conditionally raises exception

		:param	exname: Exception name
		:type	exname: string
		:param condition: Value that determines whether the exception is raised *(True)* or not *(False)*.
		:type  condition: boolean
		:param edata: Replacement values for token fields in exception message (see :py:meth:`putil.exh.add_exception`)
		:type  edata: Dictionary or iterable of dictionaries
		:raises:
		 * TypeError (Argument `condition` is of the wrong type)

		 * TypeError (Argument `exmsg` is of the wrong type)

		 * TypeError (Argument `exname` is of the wrong type)
		"""
		if not isinstance(exname, str):
			raise TypeError('Argument `exname` is not valid')
		if not isinstance(condition, bool):
			raise TypeError('Argument `condition` is not valid')
		if not self._validate_edata(edata):
			raise TypeError('Argument `exdata` is not valid')
		eobj = self._get_exception_by_name(exname)
		if condition:
			self._raise_exception(eobj, edata)
		eobj['checked'] = True

	# Managed attributes
	callable_db = property(_get_callable_db, None, None, doc='Dictionary of callables')
