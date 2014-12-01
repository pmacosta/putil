# pinspect.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Introspection helper functions
"""

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


def is_module(obj):
	""" Determines whether an object is a module or not """
	return hasattr(obj, '__name__') and (obj.__name__ in sys.modules)


def make_modules_obj_list(obj):
	""" Creates a list of package modules """
	sub_module_obj_list = [sub_module_obj for sub_module_obj in package_submodules(obj)]
	for sub_module_obj in sub_module_obj_list:
		sub_module_obj_list += make_modules_obj_list(sub_module_obj)
	return list(set(sub_module_obj_list))


def obj_type(obj, prop):
	""" Determines if prop is part of class obj, and if so if it is a member or an attribute """
	if not hasattr(obj, prop):
		return None
	return 'meth' if type(getattr(obj, prop)) == types.MethodType else 'attr'


def package_submodules(module_obj):
	""" Generator of package sub-modules """
	top_module_name = module_obj.__name__.split('.')[0]
	for element_name in dir(module_obj):
		element_obj = getattr(module_obj, element_name)
		if (element_name[0] != '_') and hasattr(element_obj, '__name__') and (element_obj.__name__.split('.')[0] == top_module_name) and (element_obj.__name__ != top_module_name):
			yield element_obj


def public_callables(obj):
	""" Generator of 'callable' (functions, methods or properties) objects in argument """
	for element_name in dir(obj):
		# Get only __init__ method of classes that have name
		# if (element_name == '__init__') or ((not (element_name.startswith('__') and element_name.endswith('__'))) and (not (element_name.startswith('_') and element_name.endswith('_')))):
		if (element_name == '__init__') or ((not (element_name.startswith('__') and element_name.endswith('__'))) and (not (element_name.startswith('_') and element_name.endswith('_')))):
			element_obj = getattr(obj, element_name)
			if (hasattr(element_obj, '__call__') or isinstance(element_obj, property)) and (not inspect.isclass(element_obj)) and (not is_module(element_obj)):
				yield element_name, element_obj, (element_obj if not isinstance(element_obj, property) else obj)
