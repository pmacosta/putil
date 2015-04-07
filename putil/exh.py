# exh.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import copy, inspect, os, sys, __builtin__

import putil.misc, putil.pinspect


###
# Functions
###
def _ex_type_str(extype):	#pylint: disable=R0201
	""" Returns a string corresponding to the exception type """
	return str(extype)[str(extype).rfind('.')+1:str(extype).rfind("'")]


def _get_class_obj(frame_obj):
	""" Extract class object from a frame object """
	scontext = frame_obj.f_locals.get('self', None)
	return scontext.__class__ if scontext else None


def _get_class_props_obj(class_obj):
	""" Extract property objects from a class object """
	return [(member_name, member_obj) for member_name, member_obj in inspect.getmembers(class_obj) if isinstance(member_obj, property)]


def _get_code_id_from_obj(obj):
	""" Return unique identity tuple to individualize callable object """
	try:
		return (inspect.getfile(obj).replace('.pyc', 'py'), inspect.getsourcelines(obj)[1])
	except:	#pylint: disable=W0702
		return None


def _valid_frame(fobj):
	""" Selects valid stack frame to process """
	fin = fobj.f_code.co_filename
	return not (fin.endswith(os.path.join('putil', 'exh.py')) or fin.endswith(os.path.join('putil', 'exdoc.py')) or fin.endswith(os.path.join('putil', 'check.py')) or (not os.path.isfile(fin)))


def del_exh_obj():
	"""
	Deletes global exception handler (if set)
	"""
	try:
		delattr(__builtin__, '_EXH')
	except:	#pylint: disable=W0702
		pass

def get_exh_obj():
	"""
	Returns the global exception handler

	:rtype: :py:class:`putil.exh.ExHandle` object if global exception handler is set, None otherwise
	"""
	return __builtin__._EXH if hasattr(__builtin__, '_EXH') else None		#pylint: disable=W0212,E1101


def get_or_create_exh_obj(full_cname=False, exclude=None):
	"""
	Returns the global exception handler if it is set, otherwise creates a new global exception handler and returns it

	:param	full_cname: Flag that indicates whether fully qualified function/method/class property names should be obtained for functions/methods/class properties that use the exception manager (True) or not (False).
	  There is a performance penalty if the flag is True as the call stack needs to be traced. This argument is only relevant if the global exception handler is not set and a new one is created
	:type	full_cname: boolean
	:rtype: :py:class:`putil.exh.ExHandle` object
	:raises: RuntimeError (Argument \\`full_cname\\` is not valid)
	"""
	if not hasattr(__builtin__, '_EXH'):
		set_exh_obj(ExHandle(full_cname=full_cname, exclude=exclude))
	return get_exh_obj()


def set_exh_obj(obj):
	"""
	Sets the global exception handler

	:param	obj: Exception handler
	:type	obj: :py:class:`putil.exh.ExHandle` object

	:raises: RuntimeError (Argument \\`obj\\` is not valid)
	"""
	if not isinstance(obj, ExHandle):
		raise RuntimeError('Argument `obj` is not valid')
	setattr(__builtin__, '_EXH', obj)


###
# Classes
###
class ExHandle(object):	#pylint: disable=R0902
	"""
	Exception handler

	:param	full_cname: Flag that indicates whether fully qualified function/method/class property names should be obtained for functions/methods/class properties that use the exception manager (True) or not (False).
	  There is a performance penalty if the flag is True as the call stack needs to be traced
	:type	full_cname: boolean
	:param	exclude: Module exclusion list (only applicable if **full_cname** is True). A particular callable in an otherwise fully qualified name is omitted if it belongs to a module in this list
	:type	exclude: list
	:rtype: :py:class:`putil.exh.ExHandle` object
	:raises:
	 * RuntimeError (Argument \\`exclude\\` is not valid)

	 * RuntimeError (Argument \\`full_cname\\` is not valid)
	"""
	def __init__(self, full_cname=False, exclude=None, _copy=False):
		if not isinstance(full_cname, bool):
			raise RuntimeError('Argument `full_cname` is not valid')
		if (exclude and (not isinstance(exclude, list))) or (isinstance(exclude, list) and any([not isinstance(item, str) for item in exclude])):
			raise RuntimeError('Argument `exclude` is not valid')
		self._ex_dict = {}
		self._callables_separator = '/'
		self._full_cname = full_cname
		self._exclude = exclude
		self._callables_obj = None
		if not _copy:
			self._callables_obj = putil.pinspect.Callables()

	def __add__(self, other):
		"""
		Merges two objects.

		:raises: RuntimeError (Incompatible exception handlers)

		For example:

			>>> import copy, putil.exh, putil.eng, putil.tree
			>>> exhobj = putil.exh.get_or_create_exh_obj()
			>>> putil.eng.peng(100, 3, True)
			' 100.000 '
			>>> tobj = putil.tree.Tree().add_nodes([{'name':'a', 'data':5}])
			>>> obj1 = copy.copy(putil.exh.get_exh_obj())
			>>> putil.exh.del_exh_obj()
			>>> exhobj = putil.exh.get_or_create_exh_obj()
			>>> putil.eng.peng(100, 3, True) # Trace some exceptions
			' 100.000 '
			>>> obj2 = copy.copy(putil.exh.get_exh_obj())
			>>> putil.exh.del_exh_obj()
			>>> exhobj = putil.exh.get_or_create_exh_obj()
			>>> tobj = putil.tree.Tree().add_nodes([{'name':'a', 'data':5}])
			>>> obj3 = copy.copy(putil.exh.get_exh_obj())
			>>> obj1 == obj2
			False
			>>> obj1 == obj3
			False
			>>> obj1 == obj2+obj3
			True

		"""
		if (self._full_cname != other._full_cname) or (self._exclude != other._exclude):	#pylint: disable=W0212
			raise RuntimeError('Incompatible exception handlers')
		robj = ExHandle(full_cname=self._full_cname, exclude=self._exclude, _copy=True)
		robj._ex_dict = copy.deepcopy(self._ex_dict)	#pylint: disable=W0212
		robj._ex_dict.update(copy.deepcopy(other._ex_dict))	#pylint: disable=W0212
		robj._callables_obj = copy.copy(self._callables_obj)+copy.copy(other._callables_obj)	#pylint: disable=W0212
		return robj

	def __copy__(self):
		"""
		Copies object. For example:

			>>> import copy, putil.exh, putil.eng
			>>> exhobj = putil.exh.get_or_create_exh_obj()
			>>> putil.eng.peng(100, 3, True)
			' 100.000 '
			>>> obj1 = putil.exh.get_exh_obj()
			>>> obj2 = copy.copy(obj1)
			>>> obj1 == obj2
			True

		"""
		cobj = ExHandle(full_cname=self._full_cname, exclude=self._exclude, _copy=True)
		cobj._ex_dict = copy.deepcopy(self._ex_dict)	#pylint: disable=W0212
		cobj._callables_obj = copy.copy(self._callables_obj)	#pylint: disable=W0212
		return cobj

	def __eq__(self, other):
		"""
		Tests object equality. For example:

			>>> import copy, putil.exh, putil.eng
			>>> exhobj = putil.exh.get_or_create_exh_obj()
			>>> putil.eng.peng(100, 3, True)
			' 100.000 '
			>>> obj1 = putil.exh.get_exh_obj()
			>>> obj2 = copy.copy(obj1)
			>>> obj1 == obj2
			True
			>>> 5 == obj1
			False

		"""
		return isinstance(other, ExHandle) and (sorted(self._ex_dict) == sorted(other._ex_dict)) and (self._callables_obj == other._callables_obj)	#pylint: disable=W0212


	def __iadd__(self, other):
		"""
		Merges an object into an existing object.

		:raises: RuntimeError (Conflicting information between objects)

		For example:

			>>> import copy, putil.exh, putil.eng, putil.tree
			>>> exhobj = putil.exh.get_or_create_exh_obj()
			>>> putil.eng.peng(100, 3, True)
			' 100.000 '
			>>> tobj = putil.tree.Tree().add_nodes([{'name':'a', 'data':5}])
			>>> obj1 = copy.copy(putil.exh.get_exh_obj())
			>>> putil.exh.del_exh_obj()
			>>> exhobj = putil.exh.get_or_create_exh_obj()
			>>> putil.eng.peng(100, 3, True) # Trace some exceptions
			' 100.000 '
			>>> obj2 = copy.copy(putil.exh.get_exh_obj())
			>>> putil.exh.del_exh_obj()
			>>> exhobj = putil.exh.get_or_create_exh_obj()
			>>> tobj = putil.tree.Tree().add_nodes([{'name':'a', 'data':5}])
			>>> obj3 = copy.copy(putil.exh.get_exh_obj())
			>>> obj1 == obj2
			False
			>>> obj1 == obj3
			False
			>>> obj2 += obj3
			>>> obj1 == obj2
			True

		"""
		if (self._full_cname != other._full_cname) or (self._exclude != other._exclude):	#pylint: disable=W0212
			raise RuntimeError('Incompatible exception handlers')
		self._ex_dict.update(copy.deepcopy(other._ex_dict))	#pylint: disable=W0212
		self._callables_obj += copy.copy(other._callables_obj)	#pylint: disable=W0212
		return self

	def __str__(self):
		"""
		Returns a string with a detailed description of the object's contents. For example:

			>>> import putil.exh, putil.eng
			>>> exhobj = putil.exh.get_or_create_exh_obj()
			>>> putil.eng.peng(100, 3, True)
			>>> print str(putil.exh.get_exh_obj())
			Name....: 139834899098160/contract_peng_frac_length_0
			Function: None
			Type....: RuntimeError
			Message.: Argument `frac_length` is not valid
			...
			Name....: 139834899098160/contract_peng_number_0
			Function: None
			Type....: RuntimeError
			Message.: Argument `number` is not valid
			...
			Name....: 139834899098160/contract_peng_rjust_0
			Function: None
			Type....: RuntimeError
			Message.: Argument `rjust` is not valid

		"""
		ret = []
		for key in sorted(self._ex_dict.keys()):
			rstr = 'Name....: {0}\n'.format(key)
			for fnum, func_name in enumerate(sorted(self._ex_dict[key]['function'])):
				rstr += '{0}{1}\n'.format('Function: ' if fnum == 0 else ' '*10, func_name)
			ret.append(rstr+'Type....: {0}\nMessage.: {1}'.format(_ex_type_str(self._ex_dict[key]['type']), self._ex_dict[key]['msg']))
		return '\n...\n'.join(ret)

	def _format_msg(self, msg, edata):	#pylint: disable=R0201
		""" Substitute parameters in exception message """
		edata = edata if isinstance(edata, list) else [edata]
		for field in edata:
			if '*[{0}]*'.format(field['field']) not in msg:
				raise RuntimeError('Field {0} not in exception message'.format(field['field']))
			msg = msg.replace('*[{0}]*'.format(field['field']), '{0}').format(field['value'])
		return msg

	def _get_callables_db(self):
		""" Returns database of callables """
		return self._callables_obj.callables_db

	def _get_callable_path(self):	#pylint: disable=R0201,R0914
		""" Get fully qualified calling function name """
		# If full_cname is False, then the only thing that matters is to return the ID of the calling function as fast as possible. If full_cname is True, the full calling path has to be calculated because multiple
		# callables can call the same callable, thus the ID does not uniquely identify the callable path
		fnum = 0
		cache_frame = sys._getframe(fnum)	#pylint: disable=W0212
		while not _valid_frame(cache_frame):
			fnum += 1
			cache_frame = sys._getframe(fnum)	#pylint: disable=W0212
		cache_key = id(cache_frame.f_code)	#pylint: disable=W0631
		if not self._full_cname:
			return cache_key, None

		# Filter stack to omit frames that are part of the exception handling module, argument validation, or top level (tracing) module
		# Stack frame -> (frame object [0], filename [1], line number of current line [2], function name [3], list of lines of context from source code [4], index of current line within list [5])
		# Class initializations appear as: filename = '<string>', function name = '__init__', list of lines of context from source code = None, index of current line within list = None
		ret = list()
		decorator_flag, skip_flag = False, False
		prev_name = name = ''
		stack = inspect.stack()
		for fob, fin, lin, fun, fuc, fui in reversed(stack[fnum:]):	#pylint: disable=W0631
			if skip_flag:
				skip_flag = False
				continue
			# Gobble up two frames if it is a decorator
			if (fin == '<string>') and (lin == 2) and (fuc == None) and (fui == None):	# frame corresponds to a decorator
				skip_flag = True
				if not decorator_flag:
					name = prev_name = self._get_callable_full_name(fob, fin, lin, fun, fuc, fui)
					if (not self._exclude) or (self._exclude and (name not in self._exclude) and (not any([name.startswith('{0}.'.format(item)) for item in self._exclude]))):
						ret.append(name)
					decorator_flag = True
			else:
				name = self._get_callable_full_name(fob, fin, lin, fun, fuc, fui)
				if ((decorator_flag and (name != prev_name)) or (not decorator_flag)) and \
				   ((not self._exclude) or (self._exclude and (name not in self._exclude) and (not any([name.startswith('{0}.'.format(item)) for item in self._exclude])))):
					ret.append(name)
				prev_name = name
				decorator_flag = False
		ret = self._callables_separator.join(ret)
		return cache_key, ret

	def _get_callable_full_name(self, fob, fin, lin, fun, fuc, fui):	#pylint: disable=R0913,W0613
		""" Get full path [module, class (if applicable) and function name] of callable """
		func_obj = None
		# Check if object is a class property
		prop_name = self._property_search(fob)
		if prop_name:
			return prop_name
		if os.path.isfile(fin):
			return self._callables_obj.get_callable_from_line(fin, fob.f_lineno)
		if fun in fob.f_globals:
			func_obj = fob.f_globals[fun]
			while getattr(func_obj, '__wrapped__', None):
				func_obj = getattr(func_obj, '__wrapped__')
			code_id = _get_code_id_from_obj(func_obj)	# pylint: disable=W0212
			if code_id:
				self._get_module_name(fob, func_obj)
				return self._callables_obj.reverse_callables_db[code_id]
		return 'dynamic'

	def _get_callables_separator(self):
		""" Get callable separator character """
		return self._callables_separator

	def _get_exception_by_name(self, name):
		""" Find exception object """
		exname = self._get_ex_data(name)['ex_name']
		if exname not in self._ex_dict:
			raise ValueError('Exception name {0} not found'.format(name))
		return self._ex_dict[exname]

	def _get_exceptions_db(self):	#pylint: disable-msg=R0201
		""" Returns a list of dictionaries suitable to be used with putil.tree module """
		if not self._full_cname:
			return [{'name':self._ex_dict[key]['function'] if self._full_cname else key, 'data':'{0} ({1})'.format(_ex_type_str(self._ex_dict[key]['type']), self._ex_dict[key]['msg'])} for key in self._ex_dict.keys()]
		ret = []
		for key in self._ex_dict.keys():
			for func_name in self._ex_dict[key]['function']:
				ret.append({'name':func_name, 'data':'{0} ({1})'.format(_ex_type_str(self._ex_dict[key]['type']), self._ex_dict[key]['msg'])})
		return ret

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
		self._callables_obj.trace([sys.modules[module_name].__file__])
		return module_name

	def _get_prop_actions(self, prop_obj):	#pylint: disable=R0201
		""" Extract property action objects (deleter, setter, getter) from a class object """
		prop_dict = {'fdel':None, 'fget':None, 'fset':None}
		for action in prop_dict.keys():
			action_obj = getattr(prop_obj, action)
			if action_obj:
				prop_dict[action] = id(action_obj.func_code)
		return prop_dict

	def _property_search(self, fobj):
		""" Check if object is a class property and if so return full name, otherwise return None """
		class_obj = _get_class_obj(fobj)
		if not class_obj:
			return
		class_props = _get_class_props_obj(class_obj)
		if not class_props:
			return
		class_file = inspect.getfile(class_obj).replace('.pyc', '.py')
		class_name = self._callables_obj.get_callable_from_line(class_file, inspect.getsourcelines(class_obj)[1])
		prop_actions_dicts = {}
		for prop_name, prop_obj in class_props:
			prop_actions_dicts[prop_name] = self._get_prop_actions(prop_obj)
		func_id = id(fobj.f_code)
		for prop_name, prop_actions_dict in prop_actions_dicts.items():
			for action_name, action_id in prop_actions_dict.items():
				if action_id == func_id:
					prop_name = '.'.join([class_name, prop_name])
					return '{0}({1})'.format(prop_name, 'setter' if action_name == 'fset' else ('getter' if action_name == 'fget' else 'deleter'))

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
		Adds an exception to the handler

		:param	exname: Exception name; has to be unique within the namespace, duplicates are eliminated
		:type	exname: string
		:param	extype: Exception type; *must* be derived from the `Exception <https://docs.python.org/2/library/exceptions.html#exceptions.Exception>`_ class
		:type	extype: Exception type object, i.e. RuntimeError, TypeError, etc.
		:param	exmsg: Exception message; it can contain fields to be replaced when the exception is raised via :py:meth:`putil.exh.ExHandle.raise_exception_if`. A field starts with the characters :code:`'\*['` and ends with the \
		 characters :code:`']\*'`, the field name follows the same rules as variable names and is between these two sets of characters. For example, :code:`\*[file_name]\*` defines the :code:`file_name` field
		:type	exmsg: string
		:raises:
		 * RuntimeError (Argument \`exmsg\` is not valid)

		 * RuntimeError (Argument \`exname\` is not valid)

		 * RuntimeError (Argument \`extype\` is not valid)
		"""
		if not isinstance(exname, str):
			raise RuntimeError('Argument `exname` is not valid')
		if not str(extype).startswith("<type 'exceptions."):
			raise RuntimeError('Argument `extype` is not valid')
		if not isinstance(exmsg, str):
			raise RuntimeError('Argument `exmsg` is not valid')
		ex_data = self._get_ex_data(exname)
		entry = self._ex_dict.get(ex_data['ex_name'], {'function':[], 'type':extype, 'msg':exmsg})
		entry['function'].append(ex_data['func_name'])
		self._ex_dict[ex_data['ex_name']] = entry

	def raise_exception_if(self, exname, condition, edata=None):
		"""
		Raises exception conditionally

		:param	exname: Exception name
		:type	exname: string
		:param condition: Flag that indicates whether the exception should be raised *(True)* or not *(False)*
		:type  condition: boolean
		:param edata: Replacement values for fields in the exception message (see :py:meth:`putil.exh.ExHandle.add_exception` for how to define fields). Each dictionary can have only these two keys:

		 * **field** *(string)* -- Field name

		 * **value** *(any)* -- Field value, to be converted into a string with the `format <https://docs.python.org/2/library/stdtypes.html#str.format>`_ string method

		:type  edata: dictionary or iterable of dictionaries
		:raises:
		 * RuntimeError (Argument \\`condition\\` is not valid)

		 * RuntimeError (Argument \\`edata\\` is not valid)

		 * RuntimeError (Argument \\`exname\\` is not valid)
		"""
		if not isinstance(exname, str):
			raise RuntimeError('Argument `exname` is not valid')
		if not isinstance(condition, bool):
			raise RuntimeError('Argument `condition` is not valid')
		if not self._validate_edata(edata):
			raise RuntimeError('Argument `edata` is not valid')
		eobj = self._get_exception_by_name(exname)
		if condition:
			self._raise_exception(eobj, edata)

	# Managed attributes
	callables_db = property(_get_callables_db, None, None, doc='Dictionary of callables')
	"""
	Returns the callables database of the modules using the exception handler, as reported by :py:meth:`putil.pinspect.Callables.callables_db`
	"""

	callables_separator = property(_get_callables_separator, None, None, doc='Callable separator character')
	"""
	Returns the character (:code:`'/'`) used to separate the sub-parts of fully qualified function names in :py:meth:`putil.exh.ExHandle.callables_db` and **name** key of :py:meth:`putil.exh.ExHandle.exceptions_db`
	"""

	exceptions_db = property(_get_exceptions_db, None, None, doc='Formatted exceptions')
	"""
	Returns the exceptions database. This database is a list of dictionaries that contain the following keys:

	 * **name** *(string)* -- Exception name of the form :code:`'callable_identifier/exception_name'`. The contents of *callable_identifier* depend on the value of the argument **full_cname** used to
	   create the exception handler. If **full_cname** is True, *callable_identifier* is the fully qualified callable name as it appears in the callables database (:py:meth:`putil.exh.ExHandle.callables_db`).
	   If **full_cname** is False, then *callable_identifier* is a decimal string representation of the callable's code identifier as reported by the `id() <https://docs.python.org/2/library/functions.html#id>`_
	   function. *exception_name* is the name of the exception provided when it was defined in :py:meth:`putil.exh.ExHandle.add_exception` (**exname** argument)

	 * **data** *(string)* -- Text of the form :code:`'exception_type (exception_message)'` where *exception_type* and *exception_message* are the exception type and exception message, respectively, given when the exception was
	   defined by :py:meth:`putil.exh.ExHandle.add_exception` (**extype** and **exmsg** arguments)
	"""
