# pinspect.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Introspection helper functions
"""

import os
import sys
import types
import inspect

def get_callable_path(frame_obj, func_obj):
	""" Get full path of callable """
	comp = dict()
	# Most of this code refactored from pycallgraph/tracer.py of the Python Call Graph project (https://github.com/gak/pycallgraph/#python-call-graph)
	code = frame_obj.f_code
	scontext = frame_obj.f_locals.get('self', None)
	# Module name
	module = inspect.getmodule(code)
	comp['module'] = module.__name__ if module else (scontext.__module__ if scontext else sys.modules[func_obj.__module__].__name__)
	ret = [comp['module']]
	# Class name
	comp['class'] = scontext.__class__.__name__ if scontext else ''
	ret.append(comp['class'])
	# Function/method/attribute name
	func_name = code.co_name
	comp['function'] = '__main__' if func_name == '?' else (func_obj.__name__ if func_name == '' else func_name)
	ret.append(comp['function'])
	return '' if ret[:2] == ['', ''] else '.'.join(filter(None, ret)), comp	#pylint: disable=W0141


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


def obj_type(obj, prop):
	""" Determines if prop is part of class obj, and if so if it is a member or an attribute """
	if not hasattr(obj, prop):
		return None
	return 'meth' if type(getattr(obj, prop)) == types.MethodType else 'attr'


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


def public_callables(module_obj):
	""" Generate a list of public callables of a module """
	public_callables_list = list()
	for element_obj, element_name in [(getattr(module_obj, element_name), element_name) for element_name in dir(module_obj) if (element_name == '__init__') or (not is_magic_method(element_name))]:
		if hasattr(element_obj, '__call__') or isinstance(element_obj, property):
			public_callables_list.append((element_name, element_obj, (element_obj if not isinstance(element_obj, property) else module_obj)))
	return public_callables_list
