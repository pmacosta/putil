# pinspect.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Introspection helper functions
"""

import re
import os
import sys
import types
import inspect

def _get_code_id(obj):
	""" Return unique identity tuple to individualize callable object """
	if hasattr(obj, 'func_code'):
		code_obj = getattr(obj, 'func_code')
		return (code_obj.co_filename, code_obj.co_firstlineno)
	return None


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
	for module_name in ['.'.join(obj_name_tokens[:num+1]) for num in range(len(obj_name_tokens)-1)]:
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
	root_dir = _rarg[0] if recursive else os.path.split(getattr(root_obj, '__file__'))[0]
	modules_covered, modules_list = _rarg[1] if recursive else list(), _rarg[2] if recursive else list()
	modules_covered += [root_name]
	modules_list += [root_obj]
	for module_obj, module_name in [(getattr(root_obj, module_name), module_name) for module_name in dir(root_obj)]:
		if is_object_module(module_obj) and hasattr(module_obj, '__file__') and os.path.split(getattr(module_obj, '__file__'))[0].startswith(root_dir) and (module_name not in modules_covered):
			modules_covered, modules_list = loaded_package_modules(module_obj, (root_dir, modules_covered, modules_list))
	return (modules_covered, modules_list) if recursive else modules_list


def _replace_tabs(text):
	""" Section 2.1.8 Indentation of Python 2.7.9 documentation:
	First, tabs are replaced (from left to right) by one to eight spaces such that the total number of characters up to and including the replacement is a multiple of eight (this is intended to be the same rule as used by Unix).
	A form feed character may be present at the start of the line; it will be ignored for the indentation calculations above. Form feed characters occurring elsewhere in the leading whitespace have an undefined effect
	(for instance, they may reset the space count to zero)
	"""
	return text.lstrip('\f').expandtabs()


class Callables(object):	#pylint: disable=R0903,R0902
	""" Trace module to get callable names and objects """
	def __init__(self):
		self._modules = []
		self._classes = []
		self._prop_dict = {}
		self._callables_db = {}
		# Regular expressions to detect class definition, function definition and decorator-defined properties
		self._class_regexp = re.compile(r'^(\s*)class\s*(\w+)\s*\(')
		self._decorator_regex = re.compile(r'^(\s*)@(\w+)')
		self._func_regexp = re.compile(r'^(\s*)def\s*(\w+)\s*\(')
		self._getter_prop_regex = re.compile(r'^(\s*)@(property|property\.getter)\s*$')
		self._setter_prop_regex = re.compile(r'^(\s*)@(\w+)\.setter\s*$')
		self._deleter_prop_regex = re.compile(r'^(\s*)@(\w+)\.deleter\s*$')


	def __repr__(self):
		ret = list()
		ret.append('Modules: {0}'.format(', '.join([mdl for mdl in self._modules])))
		ret.append('Classes: {0}'.format(', '.join([cls for cls in self._classes])))
		for key in sorted(self._callables_db.keys()):
			ret.append('{0}: {1}{2}'.format(key, self._callables_db[key]['type'], ' ({0})'.format(self._callables_db[key]['code_id'][1]) if self._callables_db[key]['code_id'] else ''))
			if self._callables_db[key]['type'] == 'prop':
				for attr in self._callables_db[key]['attr']:
					ret.append('   {0}: {1}'.format(attr, self._callables_db[key]['attr'][attr]))
		return '\n'.join(ret)

	def _get_callables_db(self):
		""" Getter for callables_db property """
		return self._callables_db

	def trace(self, obj):
		""" Generate a list of object callables """
		if not (inspect.ismodule(obj) or inspect.isclass(obj)):
			raise TypeError('Argument `obj` is not valid')
		self._prop_dict = {}
		element_module = obj.__name__ if inspect.ismodule(obj) else obj.__module__
		element_class = obj.__name__ if inspect.isclass(obj) else None
		if (element_module not in self._modules) or (element_class and (element_class not in self._classes)):
			self._modules += [element_module] if inspect.ismodule(obj) else []
			self._classes += ['{0}.{1}'.format(element_module, element_class)] if inspect.isclass(obj) else []
			self.get_closures(obj)	# Find closures, need to be done before class tracing because some class properties might use closures
			for element_name in [element_name for element_name in dir(obj) if (element_name == '__init__') or (not is_magic_method(element_name))]:
				element_obj = getattr(obj, element_name)
				is_prop = isinstance(element_obj, property)
				if inspect.isclass(element_obj):
					self.trace(element_obj)
				elif hasattr(element_obj, '__call__') or is_prop:
					element_type = 'meth' if isinstance(element_obj, types.MethodType) else ('prop' if is_prop else 'func')
					element_full_name = ('{0}.{1}.{2}'.format(element_module, element_class, element_name) if element_class else '{0}.{1}').format(element_module, element_name)
					if element_full_name not in self._callables_db:
						self._callables_db[element_full_name] = {'type':element_type, 'code_id':_get_code_id(element_obj)}
					if is_prop:
						self._prop_dict[element_full_name] = element_obj
			self.get_prop_components()	# Find out which callables re the setter/getter/deleter of properties

	def get_closures(self, obj):	#pylint: disable=R0914,R0915
		""" Find closures within module """
		if inspect.ismodule(obj):
			element_module = obj.__name__
			# Read module file
			module_file_name = '{0}.py'.format(os.path.splitext(obj.__file__)[0])
			with open(module_file_name, 'rb') as file_obj:
				module_lines = file_obj.read().split('\n')
			# Initialize parser variables
			indent_stack = [{'level':0, 'prefix':element_module, 'type':'module'}]
			decorator_num = None
			attr_name = ''
			for num, line in enumerate(module_lines, start=1):
				class_match = self._class_regexp.match(line)
				func_match = self._func_regexp.match(line)
				# To allow for nested decorators when a property is defined via a decorator, remember property decorator line and use that for the callable line number
				attr_name = attr_name if attr_name else '(getter)' if self._getter_prop_regex.match(line) else ('(setter)' if self._setter_prop_regex.match(line) else ('(deleter)' if self._deleter_prop_regex.match(line) else ''))
				decorator_num = num if self._decorator_regex.match(line) and (decorator_num == None) else decorator_num
				element_num = decorator_num if decorator_num else num
				#
				if class_match or func_match:
					class_name = class_match.group(2) if class_match else None
					func_name = func_match.group(2) if func_match else None
					if class_name or (func_name and (func_name == '__init__' or (not is_magic_method(func_name)))):
						indent = len(_replace_tabs(class_match.group(1) if class_match else func_match.group(1)))
						# Remove all blocks at the same level to find out the indentation "parent"
						while (indent <= indent_stack[-1]['level']) and (indent_stack[-1]['type'] != 'module'):
							indent_stack.pop()
						element_full_name = '{0}.{1}{2}'.format(indent_stack[-1]['prefix'], class_name if class_name else func_name, attr_name)
						if func_name and (element_full_name not in self._callables_db):
							self._callables_db[element_full_name] = {'type':'meth' if indent_stack[-1]['type'] == 'class' else 'func', 'code_id':(module_file_name, element_num)}
						indent_stack.append({'level':indent, 'prefix':element_full_name, 'type':'class' if class_name else 'func'})
					# Clear property variables
					decorator_num = None
					attr_name = ''

	def get_prop_components(self):
		""" Finds of getter, setter, deleter functions of a property """
		for prop_name, prop_obj in self._prop_dict.items():
			attr_dict = self._callables_db[prop_name].get('attr', {})
			for attr in ['fset', 'fget', 'fdel']:
				if hasattr(prop_obj, attr):
					attr_obj = getattr(prop_obj, attr)
					if getattr(attr_obj, '__call__', None):
						if attr_obj.__name__ == '<lambda>':
							name = '{0}.{1}_lambda'.format(prop_name, attr)
						else:
							if attr_obj.__module__ not in self._modules:
								self.trace(sys.modules[attr_obj.__module__])
							# Get to the object of the actual, undecorated function. Adjust for line number, because object function code always reports line where decorators start
							while getattr(attr_obj, 'undecorated', None):
								attr_obj = getattr(attr_obj, 'undecorated')
							attr_code_id = _get_code_id(attr_obj)
							for name in self._callables_db:
								if (self._callables_db[name]['type'] != 'prop') and (attr_code_id == self._callables_db[name]['code_id']):
									break
							else:
								# for name in sorted(self._callables_db.keys()):
								# 	print '{0}: {1}'.format(name, self._callables_db[name])
								# print 'Attribute `{0}` of property `{1}` is a closure, do not know how to deal with it\ncode_id: {2}'.format(attr, prop_name, attr_code_id)
								raise RuntimeError('Attribute `{0}` of property `{1}` not found in callable database'.format(attr, prop_name))
						attr_dict[attr] = name	#pylint: disable=W0631
			self._callables_db[prop_name]['attr'] = attr_dict

	# Managed attributes
	callables_db = property(_get_callables_db, None, None, doc='Module(s) callables database')
