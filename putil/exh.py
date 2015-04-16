# exh.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E1101,R0201,R0914,W0212

import copy
import imp
import inspect
import os
import sys
import __builtin__
from itertools import izip

import putil.misc
import putil.pinspect


###
# Global variables
###
_BREAK_LIST = ['_pytest']
_INVALID_MODULES_LIST = [
	os.path.join('putil', 'exh.py'),
	os.path.join('putil', 'exdoc.py')
]

###
# Functions
###
def _ex_type_str(extype):
	""" Returns a string corresponding to the exception type """
	return str(extype)[str(extype).rfind('.')+1:str(extype).rfind("'")]


def _get_class_obj(frame_obj):
	""" Extract class object from a frame object """
	scontext = frame_obj.f_locals.get('self', None)
	return scontext.__class__ if scontext else None


def _get_class_props_obj(class_obj):
	""" Extract property objects from a class object """
	return [(member_name, member_obj)
			for member_name, member_obj in inspect.getmembers(class_obj)
			if isinstance(member_obj, property)]


def _get_code_id_from_obj(obj):
	""" Return unique identity tuple to individualize callable object """
	# pylint: disable=W0702
	try:
		return (inspect.getfile(obj).replace('.pyc', 'py'),
			   inspect.getsourcelines(obj)[1])
	except (TypeError, IOError):
		# TypeError: getfile, object is a built-in module, class or function
		# IOError: getsourcelines, code cannot be retrieved
		return None


def _invalid_frame(fobj):
	""" Selects valid stack frame to process """
	fin = fobj.f_code.co_filename
	return (fin.endswith(_INVALID_MODULES_LIST[0]) or
		   fin.endswith(_INVALID_MODULES_LIST[1]) or
		   (not os.path.isfile(fin)))


def del_exh_obj():
	"""
	Deletes global exception handler (if set)
	"""
	try:
		delattr(__builtin__, '_EXH')
	except AttributeError:
		pass

def get_exh_obj():
	"""
	Returns the global exception handler

	:rtype: :py:class:`putil.exh.ExHandle` object if global exception handler
	 is set, None otherwise
	"""
	return __builtin__._EXH if hasattr(__builtin__, '_EXH') else None


def get_or_create_exh_obj(full_cname=False, exclude=None):
	"""
	Returns the global exception handler if it is set, otherwise creates a new
	global exception handler and returns it

	:param	full_cname: Flag that indicates whether fully qualified
	 function/method/class property names are obtained for
	 functions/methods/class properties that use the exception manager (True)
	 or not (False).

	 There is a performance penalty if the flag is True as the call stack needs
	 to be traced. This argument is only relevant if the global exception
	 handler is not set and a new one is created
	:type	full_cname: boolean
	:rtype: :py:class:`putil.exh.ExHandle` object
	:raises:
	 * RuntimeError (Argument \\`exclude\\` is not valid)

	 * RuntimeError (Argument \\`full_cname\\` is not valid)
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
# In the second line of some examples, note that the function
# putil.exh.get_or_create_exh_obj() is not used because if any other
# module that registers exceptions is executed first in the doctest run,
# the exception handler is going to be non-empty and the some of the
# tests in the examples may fail because there is previous history.
# Setting the global # exception handler to a new object makes the example
# start with a clean global exception handler
class ExHandle(object):
	"""
	Exception handler

	:param	full_cname: Flag that indicates whether fully qualified
	 function/method/class property names are obtained for
	 functions/methods/class properties that use the exception manager (True)
	 or not (False).

	 There is a performance penalty if the flag is True as the call stack needs
	 to be traced
	:type	full_cname: boolean
	:param	exclude: Module exclusion list (only applicable if **full_cname**
	 is True). The exceptions of a particular callable are omitted if it
	 belongs to a module in this argument
	:type	exclude: list
	:rtype: :py:class:`putil.exh.ExHandle` object
	:raises:
	 * RuntimeError (Argument \\`exclude\\` is not valid)

	 * RuntimeError (Argument \\`full_cname\\` is not valid)

	 * ValueError (Source for module *[module_name]* could not be found)
	"""
	# pylint: disable=R0902
	def __init__(self, full_cname=False, exclude=None, _copy=False):
		if not isinstance(full_cname, bool):
			raise RuntimeError('Argument `full_cname` is not valid')
		if ((exclude and (not isinstance(exclude, list))) or
		   (isinstance(exclude, list) and
	       any([not isinstance(item, str) for item in exclude]))):
			raise RuntimeError('Argument `exclude` is not valid')
		self._ex_dict = {}
		self._callables_separator = '/'
		self._full_cname = full_cname
		self._exclude = exclude
		self._exclude_list = []
		self._callables_obj = None
		self._call_path_cache = {}
		if not _copy:
			self._callables_obj = putil.pinspect.Callables()
			if exclude:
				mod_files = []
				for mod in exclude:
					mdir = None
					for token in mod.split('.'):
						try:
							mfile, mdir, _ = imp.find_module(
								token,
								[mdir] if mdir else None
							)
						except ImportError:
							raise ValueError(
								'Source for module {0} could not be found'.format(mod)
							)
					if mfile:
						mod_files.append(mfile.name.replace('.pyc', '.py'))
						mfile.close()
				self._exclude_list = mod_files

	def __add__(self, other):
		"""
		Merges two objects.

		:raises: RuntimeError (Incompatible exception handlers)

		For example:

			>>> import copy, putil.exh, putil.eng, putil.tree
			>>> exhobj = putil.exh.set_exh_obj(putil.exh.ExHandle())
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
		if ((self._full_cname != other._full_cname) or
		   (self._exclude != other._exclude)):
			raise RuntimeError('Incompatible exception handlers')
		robj = ExHandle(
			full_cname=self._full_cname,
			exclude=self._exclude,
			_copy=True
		)
		robj._ex_dict = copy.deepcopy(self._ex_dict)
		robj._ex_dict.update(copy.deepcopy(other._ex_dict))
		robj._callables_obj = (copy.copy(self._callables_obj)+
							  copy.copy(other._callables_obj))
		return robj

	def __copy__(self):
		"""
		Copies object. For example:

			>>> import copy, putil.exh, putil.eng
			>>> exhobj = putil.exh.set_exh_obj(putil.exh.ExHandle())
			>>> putil.eng.peng(100, 3, True)
			' 100.000 '
			>>> obj1 = putil.exh.get_exh_obj()
			>>> obj2 = copy.copy(obj1)
			>>> obj1 == obj2
			True

		"""
		cobj = ExHandle(
			full_cname=self._full_cname,
			exclude=self._exclude,
			_copy=True
		)
		cobj._ex_dict = copy.deepcopy(self._ex_dict)
		cobj._exclude_list = self._exclude_list[:]
		cobj._callables_obj = copy.copy(self._callables_obj)
		return cobj

	def __eq__(self, other):
		"""
		Tests object equality. For example:

			>>> import copy, putil.exh, putil.eng
			>>> exhobj = putil.exh.set_exh_obj(putil.exh.ExHandle())
			>>> putil.eng.peng(100, 3, True)
			' 100.000 '
			>>> obj1 = putil.exh.get_exh_obj()
			>>> obj2 = copy.copy(obj1)
			>>> obj1 == obj2
			True
			>>> 5 == obj1
			False

		"""
		return (isinstance(other, ExHandle) and
			   (sorted(self._ex_dict) == sorted(other._ex_dict)) and
			   (self._callables_obj == other._callables_obj))


	def __iadd__(self, other):
		"""
		Merges an object into an existing object.

		:raises: RuntimeError (Incompatible exception handlers)

		For example:

			>>> import copy, putil.exh, putil.eng, putil.tree
			>>> exhobj = putil.exh.set_exh_obj(putil.exh.ExHandle())
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
		if ((self._full_cname != other._full_cname) or
		   (self._exclude != other._exclude)):
			raise RuntimeError('Incompatible exception handlers')
		self._ex_dict.update(copy.deepcopy(other._ex_dict))
		self._callables_obj += copy.copy(other._callables_obj)
		return self

	def __nonzero__(self):
		"""
		Returns :code:`False` if exception handler does not have any exception
		defined, :code:`True` otherwise. For example:

			>>> import putil.exh
			>>> obj = putil.exh.ExHandle()
			>>> if obj:
			...     print 'Boolean test returned: True'
			... else:
			...     print 'Boolean test returned: False'
			Boolean test returned: False
			>>> def my_func(exhobj):
			...     exhobj.add_exception('test', RuntimeError, 'Message')
			>>> my_func(obj)
			>>> if obj:
			...     print 'Boolean test returned: True'
			... else:
			...     print 'Boolean test returned: False'
			Boolean test returned: True
		"""
		return bool(self._ex_dict)

	def __str__(self):
		"""
		Returns a string with a detailed description of the object's contents.
		For example:

			>>> import docs.support.exh_example
			>>> docs.support.exh_example.my_func('Tom')
			My name is Tom
			>>> print str(docs.support.exh_example.EXHOBJ) #doctest: +ELLIPSIS
			Name    : .../illegal_name
			Function: None
			Type    : TypeError
			Message : Argument `name` is not valid

		"""
		ret = []
		for key in sorted(self._ex_dict.keys()):
			rstr = 'Name    : {0}\n'.format(key)
			for fnum, func_name in enumerate(sorted(self._ex_dict[key]['function'])):
				rstr += '{0}{1}\n'.format('Function: ' if fnum == 0 else ' '*10, func_name)
			ret.append(rstr+'Type    : {0}\nMessage : {1}'.format(
				_ex_type_str(self._ex_dict[key]['type']),
				self._ex_dict[key]['msg']
			))
		return '\n\n'.join(ret)

	def _format_msg(self, msg, edata):
		""" Substitute parameters in exception message """
		edata = edata if isinstance(edata, list) else [edata]
		for field in edata:
			if '*[{0}]*'.format(field['field']) not in msg:
				raise RuntimeError(
					'Field {0} not in exception message'.format(field['field'])
				)
			msg = msg.replace(
				'*[{0}]*'.format(field['field']), '{0}'
			).format(field['value'])
		return msg

	def _get_callables_db(self):
		""" Returns database of callables """
		return self._callables_obj.callables_db

	def _get_callable_path(self):
		""" Get fully qualified calling function name """
		# pylint: disable=R0912,R0915,W0631
		# If full_cname is False, then the only thing that matters is to return
		# the ID of the calling function as fast as possible. If full_cname is
		# True, the full calling path has to be calculated because multiple
		# callables can call the same callable, thus the ID does not uniquely
		# identify the callable path
		fnum = 0
		frame = sys._getframe(fnum)
		while _invalid_frame(frame):
			fnum += 1
			frame = sys._getframe(fnum)
		callable_id = id(frame.f_code)
		if not self._full_cname:
			return callable_id, None
		# Filter stack to omit frames that are part of the exception handling
		# module, argument validation, or top level (tracing) module
		# Stack frame -> (frame object [0], filename [1], line number of
		# current line [2], function name [3], list of lines of context from
		# source code [4], index of current line within list [5])
		# Classes initialization appear as: filename = '<string>', function
		# name = '__init__', list of lines of context from source code = None,
		# index of current line within list = None
		stack, call_path = [], []
		fin, lin, fun, fuc, fui = inspect.getframeinfo(frame)
		uobj, ufin = self._unwrap_obj(frame, fun)
		if ufin in self._exclude_list:
			return callable_id, None
		tokens = frame.f_code.co_filename.split(os.sep)
		while not any([
				token.startswith(item)
				for token in tokens
				for item in _BREAK_LIST]):
			# Gobble up two frames if it is a decorator
			# 3rd tuple element indicates whether the frame corresponds to a
			# frame in a decorator
			if (fin, lin, fuc, fui) == ('<string>', 2, None, None):
				stack.pop()
				call_path.pop()
				if stack:
					stack[-1][3] = True
			stack.append([frame, fin, uobj, False])
			call_path.append(id(frame))
			fnum += 1
			try:
				frame = sys._getframe(fnum)
			except ValueError:
				# Got to top of stack
				break
			fin, lin, fun, fuc, fui = inspect.getframeinfo(frame)
			uobj, ufin = self._unwrap_obj(frame, fun)
			if ufin in self._exclude_list:
				return callable_id, None
			tokens = frame.f_code.co_filename.split(os.sep)
		# Return cached value, otherwise get full callable path
		call_path = tuple(call_path)
		try:
			return self._call_path_cache[call_path]
		except KeyError:
			stack.reverse()
			idv = [item[3] for item in stack]
			ret = [
				self._get_callable_full_name(fob, fin, uobj)
				for fob, fin, uobj, _ in stack
			]
			for num, (nme, prv_nme, in_deco) in enumerate(izip(ret[1:], ret, idv[1:])):
				if in_deco and (nme == prv_nme):
					ret.pop(num)
			ret = self._callables_separator.join(ret)
			self._call_path_cache[call_path] = (callable_id, ret)
			return callable_id, ret

	def _unwrap_obj(self, fobj, fun):
		""" Unwrap decorators """
		try:
			prev_func_obj, next_func_obj = (
				fobj.f_globals[fun],
				getattr(fobj.f_globals[fun], '__wrapped__', None)
			)
			while next_func_obj:
				prev_func_obj, next_func_obj = (
					next_func_obj,
					getattr(next_func_obj, '__wrapped__', None)
				)
			return (prev_func_obj, inspect.getfile(prev_func_obj).replace('.pyc', 'py'))
		except	(KeyError, AttributeError, TypeError):
			# KeyErrror: fun not in fobj.f_globals
			# AttributeError: fobj.f_globals does not have a __wrapped__ attribute
			# TypeError: pref_func_obj does not have a file associated with it
			return None, None

	def _get_callable_full_name(self, fob, fin, uobj):
		"""
		Get full path [module, class (if applicable) and function name]
		of callable
		"""
		# Check if object is a class property
		name = self._property_search(fob)
		if name:
			return name
		if os.path.isfile(fin):
			return self._callables_obj.get_callable_from_line(fin, fob.f_lineno)
		code_id = _get_code_id_from_obj(uobj)
		if code_id:
			self._callables_obj.trace([code_id[0]])
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

	def _get_exceptions_db(self):
		"""
		Returns a list of dictionaries suitable to be used with
		putil.tree module
		"""
		if not self._full_cname:
			return [
				{
					'name':self._ex_dict[key]['function']
						  if self._full_cname else
						  key,
					'data':'{0} ({1})'.format(
						_ex_type_str(self._ex_dict[key]['type']),
						self._ex_dict[key]['msg']
					)
				} for key in self._ex_dict.keys()
			]
		ret = []
		for key in self._ex_dict.keys():
			for func_name in self._ex_dict[key]['function']:
				ret.append(
					{
						'name':func_name,
						'data':'{0} ({1})'.format(
							_ex_type_str(self._ex_dict[key]['type']),
							self._ex_dict[key]['msg']
						)
					}
				)
		return ret

	def _get_ex_data(self, name=None):
		""" Returns hierarchical function name """
		func_id, func_name = self._get_callable_path()
		ex_name = ''.join([
			str(func_id),
			self._callables_separator if name is not None else '',
			name if name is not None else ''
		])
		return {'func_name':func_name, 'ex_name':ex_name}

	def _get_prop_actions(self, prop_obj):
		"""
		Extract property action objects (deleter, setter, getter)
		from a class object
		"""
		prop_dict = {'fdel':None, 'fget':None, 'fset':None}
		for action in prop_dict.keys():
			action_obj = getattr(prop_obj, action)
			if action_obj:
				prop_dict[action] = id(action_obj.func_code)
		return prop_dict

	def _property_search(self, fobj):
		"""
		Check if object is a class property and if so return full name,
		otherwise return None
		"""
		class_obj = _get_class_obj(fobj)
		if not class_obj:
			return
		class_props = _get_class_props_obj(class_obj)
		if not class_props:
			return
		class_file = inspect.getfile(class_obj).replace('.pyc', '.py')
		class_name = self._callables_obj.get_callable_from_line(
			class_file,
			inspect.getsourcelines(class_obj)[1]
		)
		prop_actions_dicts = {}
		for prop_name, prop_obj in class_props:
			prop_actions_dicts[prop_name] = self._get_prop_actions(prop_obj)
		func_id = id(fobj.f_code)
		desc_dict = {
			'fget':'getter',
			'fset':'setter',
			'fdel':'deleter',
		}
		for prop_name, prop_actions_dict in prop_actions_dicts.items():
			for action_name, action_id in prop_actions_dict.items():
				if action_id == func_id:
					prop_name = '.'.join([class_name, prop_name])
					return '{0}({1})'.format(
						prop_name, desc_dict[action_name]
					)

	def _raise_exception(self, eobj, edata=None):
		""" Raise exception by name """
		_, _, tbobj = sys.exc_info()
		if edata:
			emsg = eobj['type'](self._format_msg(eobj['msg'], edata))
			raise eobj['type'], emsg, tbobj
		else:
			raise eobj['type'], eobj['type'](eobj['msg']), tbobj

	def _validate_edata(self, edata):
		""" Validate edata argument of raise_exception_if method """
		if edata is None:
			return True
		if not (isinstance(edata, dict) or putil.misc.isiterable(edata)):
			return False
		edata = [edata] if isinstance(edata, dict) else edata
		for edict in edata:
			if ((not isinstance(edict, dict)) or
			   (isinstance(edict, dict) and
			   (('field' not in edict) or
			   ('field' in edict and (not isinstance(edict['field'], str))) or
	           ('value' not in edict)))):
				return False
		return True

	def add_exception(self, exname, extype, exmsg):
		r"""
		Adds an exception to the handler

		:param	exname: Exception name; has to be unique within the namespace,
		 duplicates are eliminated
		:type	exname: string
		:param	extype: Exception type; *must* be derived from the `Exception
		 <https://docs.python.org/2/library/exceptions.html#exceptions.Exception>`_
		 class
		:type	extype: Exception type object, i.e. RuntimeError, TypeError, etc.
		:param	exmsg: Exception message; it can contain fields to be replaced
		 when the exception is raised via
		 :py:meth:`putil.exh.ExHandle.raise_exception_if`. A field starts with
		 the characters :code:`'\*['` and ends with the characters
		 :code:`']\*'`, the field name follows the same rules as variable names
		 and is between these two sets of characters. For example,
		 :code:`\*[file_name]\*` defines the :code:`file_name` field
		:type	exmsg: string
		:raises:
		 * RuntimeError (Argument \`exmsg\` is not valid)

		 * RuntimeError (Argument \`exname\` is not valid)

		 * RuntimeError (Argument \`extype\` is not valid)
		"""
		# pylint: disable=R0913
		if not isinstance(exname, str):
			raise RuntimeError('Argument `exname` is not valid')
		if not str(extype).startswith("<type 'exceptions."):
			raise RuntimeError('Argument `extype` is not valid')
		if not isinstance(exmsg, str):
			raise RuntimeError('Argument `exmsg` is not valid')
		ex_data = self._get_ex_data(exname)
		entry = self._ex_dict.get(
			ex_data['ex_name'],
			{'function':[], 'type':extype, 'msg':exmsg}
		)
		entry['function'].append(ex_data['func_name'])
		self._ex_dict[ex_data['ex_name']] = entry

	def raise_exception_if(self, exname, condition, edata=None):
		"""
		Raises exception conditionally

		:param	exname: Exception name
		:type	exname: string
		:param condition: Flag that indicates whether the exception is
		 raised *(True)* or not *(False)*
		:type  condition: boolean
		:param edata: Replacement values for fields in the exception message
		 (see :py:meth:`putil.exh.ExHandle.add_exception` for how to define
		 fields). Each dictionary entry can only have these two keys:

		 * **field** *(string)* -- Field name

		 * **value** *(any)* -- Field value, to be converted into a string with
		   the `format
		   <https://docs.python.org/2/library/stdtypes.html#str.format>`_ string
		   method

		:type  edata: dictionary or iterable of dictionaries
		:raises:
		 * RuntimeError (Argument \\`condition\\` is not valid)

		 * RuntimeError (Argument \\`edata\\` is not valid)

		 * RuntimeError (Argument \\`exname\\` is not valid)

		 * RuntimeError (Field *[field_name]* not in exception message)

		 * ValueError (Exception name *[name]* not found')

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
	callables_db = property(
		_get_callables_db,
		doc='Dictionary of callables'
	)
	"""
	Returns the callables database of the modules using the exception handler,
	as reported by :py:meth:`putil.pinspect.Callables.callables_db`
	"""

	callables_separator = property(
		_get_callables_separator,
		doc='Callable separator character'
	)
	"""
	Returns the character (:code:`'/'`) used to separate the sub-parts of fully
	qualified function names in :py:meth:`putil.exh.ExHandle.callables_db` and
	**name** key in :py:meth:`putil.exh.ExHandle.exceptions_db`
	"""

	exceptions_db = property(
		_get_exceptions_db,
		doc='Formatted exceptions'
	)
	"""
	Returns the exceptions database. This database is a list of dictionaries
	that contain the following keys:

	 * **name** *(string)* -- Exception name of the form
	   :code:`'[callable_identifier]/[exception_name]'`. The contents of
	   :code:`[callable_identifier]` depend on the value of the argument
	   **full_cname** used to create the exception handler.

	   If **full_cname** is True, :code:`[callable_identifier]` is the fully
	   qualified callable name as it appears in the callables database
	   (:py:meth:`putil.exh.ExHandle.callables_db`).

	   If **full_cname** is False, then :code:`[callable_identifier]` is a decimal
	   string representation of the callable's code identifier as reported by
	   the `id() <https://docs.python.org/2/library/functions.html#id>`_
	   function.

	   In either case :code:`[exception_name]` is the name of the exception
	   provided when it was defined in
	   :py:meth:`putil.exh.ExHandle.add_exception` (**exname** argument)

	 * **data** *(string)* -- Text of the form :code:`'[exception_type]
	   ([exception_message])'` where :code:`[exception_type]` and
	   :code:`[exception_message]` are the exception type and exception
	   message, respectively, given when the exception was defined by
	   :py:meth:`putil.exh.ExHandle.add_exception` (**extype** and
	   **exmsg** arguments)
	"""
