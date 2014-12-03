# exh.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Exception handling classes, methods, functions and constants
"""

import sys
import copy
import inspect
import operator

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
		if edata is not None:
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
		return self._callable_db

	def _get_callable_name(self):	#pylint: disable=R0201,R0914
		""" Get fully qualified calling function name """
		ret = list()
		# Filter stack to omit frames that are part of the exception handling module, argument validation, or top level (tracing) module
		# Stack frame -> (frame object [0], filename [1], line number of current line [2], function name [3], list of lines of context from source code [4], index of current line within list [5])
		# Class initializations appear as: filename = '<string>', function name = '__init__', list of lines of context from source code = None, index of current line within list = None
		fstack = [(fo, fn, (fin, fc, fi) == ('<string>', None, None)) for fo, fin, _, fn, fc, fi in inspect.stack() if self._valid_frame(fin, fn)]
		for fobj, func in [(fo, fn) for num, (fo, fn, flag) in reversed(list(enumerate(fstack))) if not (flag and num)]:
			func_obj = fobj.f_locals.get(func, fobj.f_globals.get(func, getattr(fobj.f_locals.get('self'), func, None) if 'self' in fobj.f_locals else None))
			fname, fdict = putil.pinspect.get_callable_path(fobj, func_obj)
			ftype = 'attr' if any([hasattr(func_obj, attr) for attr in ['fset', 'fget', 'fdel']]) else 'meth'
			# Methods that return a function have an empty function object. Strategy in this case is to find out which enclosing module-level function or class method returns the function
			# by looking at the line numbers at which each enclosing callable starts, and comparing it with the callable line number
			if fname and (not func_obj):
				try:
					mod_obj = sys.modules[fdict['module']]
					container_obj = getattr(mod_obj, fdict['class'] if fdict['class'] else fdict['module'])
				except:
					raise
				#	raise RuntimeError('Could not get container object')
				lines_dict = dict()
				for element_name in dir(container_obj):
					func_obj = getattr(container_obj, element_name)
					if func_obj and getattr(func_obj, 'func_code', None):
						lines_dict[element_name] = func_obj.func_code.co_firstlineno
				sorted_lines_dict = sorted(lines_dict.items(), key=operator.itemgetter(1))
				func_name = [member for member, line_no in sorted_lines_dict if line_no < fobj.f_lineno][-1]
				fname = '.'.join(filter(None, [fdict['module'], fdict['class'], func_name, fdict['function']]))	#pylint: disable=W0141
			# If callable is an attribute, "trace" module(s) where attributes are to find
			if (fname not in self._callable_db) and (ftype == 'attr'):
				self._make_module_callables_list(sys.modules[func_obj.__module__])
			# Method in class
			elif (fname not in self._callable_db) and hasattr(func_obj, 'im_class'):
				cls_obj = func_obj.im_class
				self._make_module_callables_list(cls_obj, cls_obj.__name__)
			# Module-level function
			elif fname not in self._callable_db:
				self._callable_db[fname] = {'type':ftype, 'code':None if not hasattr(func_obj, 'func_code') else func_obj.func_code}
			ret.append(fname)
		return '.'.join(ret)

	def _make_module_callables_list(self, obj, cls_name=''):	#pylint: disable=R0914
		""" Creates a list of callable functions at and below an object hierarchy """
		for call_name, call_obj, base_obj in putil.pinspect.public_callables(obj):
			call_full_name = '{0}.{1}.{2}'.format((obj if call_name == '__init__' else base_obj).__module__, cls_name, call_name) if cls_name else '{0}.{1}'.format(base_obj.__module__, call_name)
			call_type = 'attr' if any([hasattr(call_obj, attr) for attr in ['fset', 'fget', 'fdel']]) else 'meth'
			self._callable_db[call_full_name] = {'type':call_type, 'code':None if not hasattr(call_obj, 'func_code') else call_obj.func_code}
			# Setter/getter/deleter object have no introspective way of finding out what class (if any) they belong to
			# Need to compare code objects with class or module members to find out cross-link
			if call_type == 'attr':
				attr_dict = dict()
				# Object may have property but be None if it does not have a getter, setter or deleter assigned to it
				attr_tuple = [(attrn, getattr(call_obj, attrn)) for attrn in ['fset', 'fget', 'fdel'] if hasattr(call_obj, attrn) and getattr(call_obj, attrn)]
				# Scan module objects if not done before
				for modname in [attr_obj.__module__ for _, attr_obj in attr_tuple if attr_obj.__module__ not in self._module_db]:
					self._module_db.append(modname)
					self._make_module_callables_list(sys.modules[modname])
				for attr, attr_obj in attr_tuple:
					attr_module = attr_obj.__module__
					# Compare code objects, only reliable way of finding out if function object is the same as class/module object
					for mkey, mvalue in [(mcall, mvalue) for mcall, mvalue in self._callable_db.items() if mcall.startswith(attr_module+'.') and self._callable_db[mcall].get('code', None)]:
						if mvalue['code'] == attr_obj.func_code:
							attr_dict[attr] = mkey
							break
				self._callable_db[call_full_name]['attr'] = attr_dict

	def _tree_data(self):	#pylint: disable-msg=R0201
		""" Returns a list of dictionaries suitable to be used with putil.tree module """
		return [{'name':ex['function'], 'data':'{0} ({1})'.format(self._ex_type_str(ex['type']), ex['msg'])} for ex in self._ex_list]

	def _valid_frame(self, fin, fna):	#pylint: disable-msg=R0201
		""" Selects valid stack frame to process """
		return not (fin.endswith('/putil/exh.py') or fin.endswith('/putil/exhdoc.py') or fin.endswith('/putil/check.py')  or fin.endswith('/putil/pcontracts.py') or (fna in ['<module>', '<lambda>', 'contracts_checker']))

	def add_exception(self, name, extype, exmsg):	#pylint: disable=R0913,R0914
		""" Add exception to handler

		:param	name: Exception name. Has to be unique within the namespace, duplicates are eliminated
		:type	name: string
		:param	extype: Exception type. *Must* be derived from `Exception <https://docs.python.org/2/library/exceptions.html#exceptions.Exception>`_ class
		:type	name: Exception type object (i.e. RuntimeError, TypeError, etc.)
		:param	exmsg: Exception message
		:type	exmsg: string

		:raises:
		 * TypeError (Argument `exmsg` is of the wrong type)

		 * TypeError (Argument `extype` is of the wrong type)

		 * TypeError (Argument `name` is of the wrong type)
		"""
		if not isinstance(name, str):
			raise TypeError('Argument `name` is of the wrong type')
		if not str(extype).startswith("<type 'exceptions."):
			raise TypeError('Argument `extype` is of the wrong type')
		if not isinstance(exmsg, str):
			raise TypeError('Argument `exmsg` is of the wrong type')
		ex_data = self.get_ex_data(name)
		self._ex_list.append({'name':ex_data['ex_name'], 'function':ex_data['func_name'], 'type':extype, 'msg':exmsg, 'checked':False})
		self._ex_list = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in self._ex_list)] # Remove duplicates

	def get_exception_by_name(self, name):
		""" Find exception object """
		exname = self.get_ex_data(name)['ex_name']
		for obj in self._ex_list:
			if obj['name'] == exname:
				return obj
		raise ValueError('Exception name {0} not found'.format(name))

	def get_ex_data(self, name=None):	#pylint: disable=R0201
		""" Returns hierarchical function name """
		func_name = self._get_callable_name()
		ex_name = '{0}{1}{2}'.format(func_name, '.' if func_name is not None else '', name if name is not None else '')
		return {'func_name':func_name, 'ex_name':ex_name}

	def raise_exception(self, name, **kargs):
		""" Raise exception by name """
		if (len(kargs) == 1) and ('edata' not in kargs):
			raise RuntimeError('Illegal keyword argument passed to raise_exception')
		if len(kargs) > 1:
			raise RuntimeError('Illegal keyword argument{0} passed to raise_exception'.format('s' if len(kargs)-(1 if 'edata' in kargs else 0) > 1 else ''))
		obj = self.get_exception_by_name(name)
		_, _, tbobj = sys.exc_info()
		if len(kargs):
			raise obj['type'], obj['type'](self._format_msg(obj['msg'], kargs['edata'])), tbobj
		else:
			raise obj['type'], obj['type'](obj['msg']), tbobj

	def raise_exception_if(self, name, condition, **kargs):
		""" Raise exception by name if condition is true """
		if (len(kargs) == 1) and ('edata' not in kargs):
			raise RuntimeError('Illegal keyword argument passed to raise_exception')
		if len(kargs) > 1:
			raise RuntimeError('Illegal keyword argument{0} passed to raise_exception'.format('s' if len(kargs)-(1 if 'edata' in kargs else 0) > 1 else ''))
		if condition:
			self.raise_exception(name, **kargs)
		self.get_exception_by_name(name)['checked'] = True

	# Managed attributes
	callable_db = property(_get_callable_db, None, None, doc='Dictionary of callables')
