# pinspect.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Introspection helper functions
"""

import re
import os
import sys
import copy
import types
import inspect

import putil.misc


def _get_code_id(obj, file_name=None, offset=0):
	""" Return unique identity tuple to individualize callable object """
	if hasattr(obj, 'func_code') and (obj.func_code.co_filename != '<string>'):
		return (obj.func_code.co_filename, obj.func_code.co_firstlineno)
	elif file_name:
		return (file_name, obj.func_code.co_firstlineno+offset)


def _private_props(obj):
	""" Generator to yield private properties of object """
	private_prop_regexp = re.compile('_[^_]+')
	for obj_name in [obj_name for obj_name in dir(obj) if private_prop_regexp.match(obj_name) and (not callable(getattr(obj, obj_name))) and ('regexp' not in obj_name)]:
		yield obj_name


def is_magic_method(name):
	"""
	Determines if a method is a magic method or not (with a '__' prefix and suffix)

	:param	name: Method name
	:type	name: string
	:rtype: boolean
	"""
	return name.startswith('__')


def is_object_module(obj):
	"""
	Determines whether an object is a module object

	:param	obj: Object
	:type	obj: object
	:rtype: boolean
	"""
	return isinstance(obj, types.ModuleType)


def get_module_name(module_obj):
	"""
	Get module name from module object with validation

	:param	module_obj: Module object
	:type	module_obj: object
	:rtype: string
	"""
	if not is_object_module(module_obj):
		raise TypeError('Argument `module_obj` is not a module object')
	name = module_obj.__name__
	if name not in sys.modules:
		raise RuntimeError('Module object `{0}` could not be found in loaded modules'.format(name))
	return name


def get_package_name(module_obj):
	"""
	Find loaded root package name of module object

	:param	module_obj: Module object
	:type	module_obj: object
	:rtype: string
	"""
	name = get_module_name(module_obj)
	obj_name_tokens = name.split('.')
	if len(obj_name_tokens) == 1:
		return name
	for module_name in ['.'.join(obj_name_tokens[:num+1]) for num in xrange(len(obj_name_tokens)-1)]:
		if module_name in sys.modules:
			return module_name
	raise RuntimeError('Loaded package root could not be found')


def loaded_package_modules(module_obj, _rarg=None):
	"""
	Generates a list of loaded package module objects from a module object of a package

	:param	module_obj: Module object
	:type	module_obj: object
	:rtype: list of module objects
	"""
	recursive = bool(_rarg)
	root_name = (get_module_name if recursive else get_package_name)(module_obj)
	root_obj = sys.modules.get(root_name, None)
	root_dir, modules_traced, modules_list = _rarg[0] if recursive else os.path.split(getattr(root_obj, '__file__'))[0], _rarg[1] if recursive else list(), _rarg[2] if recursive else list()
	modules_traced.append(root_name)
	modules_list.append(root_obj)
	for module_obj, module_name in [(getattr(root_obj, module_name), module_name) for module_name in dir(root_obj)]:
		if is_object_module(module_obj) and hasattr(module_obj, '__file__') and os.path.split(getattr(module_obj, '__file__'))[0].startswith(root_dir) and (module_name not in modules_traced):
			modules_traced, modules_list = loaded_package_modules(module_obj, (root_dir, modules_traced, modules_list))
	return (modules_traced, modules_list) if recursive else modules_list


def _replace_tabs(text):
	""" Section 2.1.8 Indentation of Python 2.7.9 documentation:
	First, tabs are replaced (from left to right) by one to eight spaces such that the total number of characters up to and including the replacement is a multiple of eight (this is intended to be the same rule as used by Unix).
	A form feed character may be present at the start of the line; it will be ignored for the indentation calculations above. Form feed characters occurring elsewhere in the leading whitespace have an undefined effect
	(for instance, they may reset the space count to zero)
	"""
	return text.lstrip('\f').expandtabs()


class Callables(object):	#pylint: disable=R0903,R0902
	"""
	Generates list of module callables (functions and properties) and gets their attributes (type, file name, starting line number). Information from multiple modules can be stored in the callables database of the object by
	repeatedly calling :py:meth:`putil.pinspect.Callables.trace()` with different module objects. A :py:class:`putil.pinspect.Callables()` object retains knowledge of which modules have been traced so repeated calls to
	:py:meth:`putil.pinspect.Callables.trace()` with the *same* module object will *not* result in module re-traces (and the consequent performance hit).

	:param obj: Module object(s)
	:type	obj: object or iterable of objects
	:rtype: :py:class:`putil.pinspect.Callables()` object
	:raises: TypeError (Argument `obj` is not valid)
	"""
	def __init__(self, obj=None):
		self._module_names, self._class_names, self._callables_db, self._reverse_callables_db, self._closure_class_obj_list = set(), set(), {}, {}, []
		self._class_regexp = re.compile(r'^(\s*)class\s*(\w+)\s*\(')
		self._func_regexp = re.compile(r'^(\s*)def\s*(\w+)\s*\(')
		self._getter_prop_regexp = re.compile(r'^(\s*)@(property|property\.getter)\s*$')
		self._setter_prop_regexp = re.compile(r'^(\s*)@(\w+)\.setter\s*$')
		self._deleter_prop_regexp = re.compile(r'^(\s*)@(\w+)\.deleter\s*$')
		self._decorator_regexp = re.compile(r'^(\s*)@(.+)')
		self._whitespace_regexp = re.compile(r'^(\s*)(\w*)')
		self._namespece_regexp = re.compile(r"name '(\w+)' is not defined")
		self._import_regexp = re.compile(r'^(\s*)import\s+')
		self._from_regexp = re.compile(r'^(\s*)from\s+')
		if obj:
			self.trace(obj)

	def __copy__(self):
		cobj = Callables()
		for prop_name in _private_props(self):
			setattr(cobj, prop_name, copy.deepcopy(getattr(self, prop_name)))
		return cobj

	def __eq__(self, other):
		# _prop_dict is a class variable used to pass data between sub-functions in the trace operation, not material to determine if two objects are the same
		return all([sorted(getattr(self, attr)) == sorted(getattr(other, attr)) for attr in _private_props(self) if attr != '_prop_dict'])

	def __repr__(self):
		return 'putil.pinspect.Callables({0})'.format('[{0}]'.format(', '.join(["sys.modules['{0}']".format(module_name) for module_name in sorted(self._module_names)])) if self._module_names else '')

	def __str__(self):
		ret = list()
		ret.append('Modules:')
		for module_name in sorted(self._module_names):
			ret.append('   {0}'.format(module_name))
		ret.append('Classes:')
		for class_name in sorted(self._class_names):
			ret.append('   {0}'.format(class_name))
		for key in sorted(self._callables_db.keys()):
			ret.append('{0}: {1}{2}'.format(key, self._callables_db[key]['type'], ' ({0})'.format(self._callables_db[key]['code_id'][1]) if self._callables_db[key]['code_id'] else ''))
			if self._callables_db[key]['type'] == 'prop':
				for attr in self._callables_db[key]['attr']:
					ret.append('   {0}: {1}'.format(attr, self._callables_db[key]['attr'][attr]))
			elif self._callables_db[key].get('link', None):
				for link_dict in self._callables_db[key]['link']:
					ret.append('   {0} of: {1}'.format(link_dict['action'], link_dict['prop']))
		return '\n'.join(ret)

	def _get_callables_db(self):
		""" Getter for callables_db property """
		return self._callables_db

	def _get_closures(self, obj):	#pylint: disable=R0912,R0914,R0915
		""" Find closures within module. Implement a mini-parser, finding "@", "def" or "class" start of lines while keeping track of indentation levels """
		# Read module file
		module_file_name = '{0}.py'.format(os.path.splitext(obj.__file__)[0])
		with open(module_file_name, 'rb') as file_obj:
			module_lines = file_obj.read().split('\n')
		# Initialize mini-parser variables
		indent_stack, decorator_num, attr_name, closure_class, import_stack, closure_class_list = [{'level':0, 'prefix':obj.__name__, 'type':'module'}], None, '', False, [{'level':0, 'type':'module', 'line':None}], []
		for num, line in enumerate(module_lines, start=1):
			class_match = self._class_regexp.match(line)
			class_indent, class_name = class_match.groups() if class_match else (None, None)
			func_match = self._func_regexp.match(line)
			func_indent, func_name = func_match.groups() if func_match else (None, None)
			getter_match, setter_match, deleter_match = self._getter_prop_regexp.match(line), self._setter_prop_regexp.match(line), self._deleter_prop_regexp.match(line)
			decorator_match = self._decorator_regexp.match(line)
			import_match = self._import_regexp.match(line)
			from_match = self._from_regexp.match(line)
			# To allow for nested decorators when a property is defined via a decorator, remember property decorator line and use that for the callable line number
			attr_name = attr_name if attr_name else '(getter)' if getter_match else ('(setter)' if setter_match else ('(deleter)' if deleter_match else ''))
			decorator_num = num if decorator_match and (decorator_num == None) else decorator_num
			element_num = decorator_num if decorator_num else num
			if import_match or from_match:
				namspace_indent = len(_replace_tabs(import_match.group(1) if import_match else from_match.group(1)))
				while (namspace_indent < import_stack[-1]['level']) and (import_stack[-1]['type'] != 'module'):
					import_stack.pop()
				import_stack.append({'level':namspace_indent, 'line':line.lstrip(), 'type':'not module'})
			if class_match or func_match:
				indent = len(_replace_tabs(class_indent if class_match else func_indent))
				# Remove all blocks at the same level to find out the indentation "parent"
				while (indent <= indent_stack[-1]['level']) and (indent_stack[-1]['type'] != 'module'):
					indent_stack.pop()
				if class_match:
					closure_class = indent_stack[-1]['type'] != 'module'
					self._class_names.add('{0}.{1}'.format(indent_stack[-1]['prefix'], class_name))
					if closure_class:
						closure_class_list.append({'file':module_file_name, 'name':'{0}.{1}'.format(indent_stack[-1]['prefix'], class_name), 'code':[], 'namespace':[import_dict['line'] for import_dict in import_stack[1:]],
								                   'indent':indent, 'eval':'tvar = {0}'.format(class_name), 'lineno':num})
				element_full_name = '{0}.{1}{2}'.format(indent_stack[-1]['prefix'], class_name if class_name else func_name, attr_name)
				if func_name and (element_full_name not in self._callables_db):
					self._callables_db[element_full_name] = {'type':'meth' if indent_stack[-1]['type'] == 'class' else 'func', 'code_id':(module_file_name, element_num), 'attr':None, 'link':[]}
					self._reverse_callables_db[(module_file_name, element_num)] = element_full_name
				indent_stack.append({'level':indent, 'prefix':element_full_name, 'type':'class' if class_name else 'func'})
				# Reset property variables
				decorator_num, attr_name = None, ''
			if closure_class:
				line = _replace_tabs(line)
				start_space, content = self._whitespace_regexp.match(line).groups()
				for class_dict in closure_class_list:
					if class_dict['code'] and content and ((len(start_space) <= class_dict['indent']) or (start_space == 0)):
						class_dict['code'].append(class_dict['eval'])
						self._closure_class_obj_list.append({'code':'\n'.join(class_dict['namespace']+class_dict['code']), 'file':class_dict['file'], 'name':class_dict['name'], 'lineno':class_dict['lineno']-len(class_dict['namespace'])})
						closure_class_list.pop()
						closure_class = bool(closure_class_list)
					else:
						class_dict['code'].append(line[class_dict['indent']:])

	def _get_prop_components(self, prop_name, prop_obj, closure_file_name=None, closure_offset=0):
		""" Find getter, setter, deleter functions of a property """
		attr_dict = {}
		for attr_name, attr_obj in [(attr_name, getattr(prop_obj, attr_name)) for attr_name in ['fdel', 'fget', 'fset'] if hasattr(prop_obj, attr_name) and getattr(getattr(prop_obj, attr_name), '__call__', None)]:
			if attr_obj.__name__ == '<lambda>':
				func_name = '{0}.{1}_lambda'.format(prop_name, attr_name)
			else:
				if attr_obj.__module__  and (attr_obj.__module__ not in self._module_names):
					self._trace_module(sys.modules[attr_obj.__module__])
				# Get to the object of the actual, undecorated function
				while getattr(attr_obj, '__wrapped__', None):
					attr_obj = getattr(attr_obj, '__wrapped__')
				attr_code_id = _get_code_id(attr_obj, closure_file_name, closure_offset)
				if attr_code_id not in self._reverse_callables_db:
					#for name in sorted(self._callables_db.keys()):
					#	print '{0}: {1}'.format(name, self._callables_db[name])
					#print 'Attribute `{0}` of property `{1}` is a closure, do not know how to deal with it\ncode_id: {2}'.format(attr_name, prop_name, attr_code_id)
					raise RuntimeError('Attribute `{0}` of property `{1}` not found in callable database'.format(attr_name, prop_name))
				func_name = self._reverse_callables_db[attr_code_id]
				prop_dict = {'prop':prop_name, 'action':attr_name}
				if prop_dict not in self._callables_db[func_name]['link']:
					self._callables_db[func_name]['link'].append(prop_dict)
			attr_dict[attr_name] = func_name	#pylint: disable=W0631
		self._callables_db[prop_name]['attr'] = attr_dict if attr_dict else None

	def _get_reverse_callables_db(self):
		""" Getter for reverse_callables_db property """
		return self._reverse_callables_db

	def _trace_class(self, obj, closure_file_name=None, closure_name=None, closure_offset=0):
		""" Trace class properties, methods have already been added to database by mini-parser """
		class_name = closure_name if closure_name else '.'.join([obj.__module__, obj.__name__])
		self._class_names.add(class_name)	# Classes are only traced once because modules are only traced once, no need to check if they are already traced
		for prop_name, prop_obj in [('.'.join([class_name, prop_name]), prop_obj) for prop_name, prop_obj in inspect.getmembers(obj) if isinstance(prop_obj, property)]:
			self._callables_db[prop_name] = {'type':'prop', 'code_id':None, 'attr':None, 'link':[]}
			self._get_prop_components(prop_name, prop_obj, closure_file_name, closure_offset)	# Find out which callables re the setter/getter/deleter of properties

	def _trace_module(self, obj):
		""" Generate a list of object callables (internal function, no argument validation)"""
		if obj.__name__ not in self._module_names:
			self._module_names.add(obj.__name__)
			self._get_closures(obj)	# Find closures, need to be done before class tracing because some class properties might use closures
			for class_obj in [class_obj for _, class_obj in inspect.getmembers(obj) if inspect.isclass(class_obj)]:
				self._trace_class(class_obj)
			for class_obj in self._closure_class_obj_list:
				exec class_obj['code'] in locals()	#pylint: disable=W0122
				self._trace_class(tvar, class_obj['file'], class_obj['name'], class_obj['lineno']-1)	#pylint: disable=E0602

	def trace(self, obj):
		"""
		Generates list of module callables (functions and properties) and gets their attributes (type, file name, starting line number).

		:param obj: Module object(s)
		:type	obj: object or iterable of objects
		:raises: TypeError (Argument `obj` is not valid)
		"""
		if (obj == None) or (not (inspect.ismodule(obj) or putil.misc.isiterable(obj))):
			raise TypeError('Argument `obj` is not valid')
		for obj in obj if putil.misc.isiterable(obj) else [obj]:
			if not inspect.ismodule(obj):
				raise TypeError('Argument `obj` is not valid')
			self._trace_module(obj)

	# Managed attributes
	callables_db = property(_get_callables_db, None, None, doc='Module(s) callables database')
	"""
	Returns callable database

	:rtype: dictionary

	The callable database is a dictionary that has the following structure:

	 * **full callable name** *(string)* -- Dictionary key. Elements in the callable path are separated by periods ('.'). For example, method `my_method` from class `MyClass` from module `my_module` appears as
	   `my_module.MyClass.my_method`

	 * **callable properties** *(dictionary)* -- Dictionary value. The elements of this dictionary are:

	  * **type** *(string)* -- 'meth' for methods, 'func' for functions or 'prop' for properties

	  * **code_id** *(tuple or None)* -- *None* if **type** is 'prop', otherwise a tuple with the following elements:

	    * **file name** *(string)* -- the first element contains the file name where the callable can be found

	    * **line number** *(integer)* -- the second element contains the line number in which the callable code starts (including decorators) within **file name**

	  * **attr** *(dictionary or None)* -- *None* if **type** is 'meth' or 'func', otherwise a dictionary with the following elements:

	   * **fget** *(string or None)* -- Name of the getter function or method associated with the property (if any)

	   * **fset** *(string or None)* -- Name of the setter function or method associated with the property (if any)

	   * **fdel** *(string or None)* -- Name of the deleter function or method associated with the property (if any)

	  * **link** *(dictionary or None)* -- *None* if callable is not the getter, setter or deleter of a property, otherwise a dictionary with the following elements:

	   * **prop** *(string)* -- Property the callable is associated with

	   * **action** *(string)* -- Property action the callable performs, one of `['fget', 'fset', 'fdel']`

	"""
	reverse_callables_db = property(_get_reverse_callables_db, None, None, doc='Reverse module(s) callables database')
	"""
	Returns reverse callable database

	:rtype: dictionary

	The reverse callable database is a dictionary that has the following structure:

	 * **callable id** *(tuple)* -- Dictionary key. 2-element tuple of the format ([file name], [line number]) wehere [file name] is the file name where the callable is defined and [line number] is the line number within
	   [file name] where the callable definition starts

	 * **full callable name** *(string)* -- Dictionary value. Elements in the callable path are separated by periods ('.'). For example, method `my_method` from class `MyClass` from module `my_module` appears as
	   `my_module.MyClass.my_method`
	"""
