# test_pinspect.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212

"""
putil.pintrospect unit tests
"""

import sys
import types

import putil.test
import putil.pinspect

def test_object_is_module():
	""" Test object_is_module() function """
	test_list = list()
	test_list.append(putil.pinspect.is_object_module(5) == False)
	test_list.append(putil.pinspect.is_object_module(sys.modules['putil.pinspect']) == True)
	assert test_list == [True]*len(test_list)


def test_get_module_name():
	""" Test get_module_name() function """
	test_list = list()
	test_list.append(putil.test.trigger_exception(putil.pinspect.get_module_name, {'module_obj':5}, TypeError, 'Argument `module_obj` is not a module object'))
	mock_module_obj = types.ModuleType('mock_module_obj', 'Mock module')
	test_list.append(putil.test.trigger_exception(putil.pinspect.get_module_name, {'module_obj':mock_module_obj}, RuntimeError, 'Module object `mock_module_obj` could not be found in loaded modules'))
	test_list.append(putil.pinspect.get_module_name(sys.modules['putil.pinspect']) == 'putil.pinspect')
	test_list.append(putil.pinspect.get_module_name(sys.modules['putil']) == 'putil')
	assert test_list == [True]*len(test_list)


def test_get_package_name():
	""" Test get_package_name() function """
	test_list = list()
	sys.modules['no_pkg.module'] = types.ModuleType('no_pkg.module', 'Mock module')
	test_list.append(putil.test.trigger_exception(putil.pinspect.get_package_name, {'module_obj':sys.modules['no_pkg.module']}, RuntimeError, 'Loaded package root could not be found'))
	test_list.append(putil.pinspect.get_package_name(sys.modules['putil.pinspect']) == 'putil')
	assert test_list == [True]*len(test_list)


def test_is_magic_method():
	""" Test is_magic_method() function """
	test_list = list()
	test_list.append(putil.pinspect.is_magic_method('func_name') == False)
	test_list.append(putil.pinspect.is_magic_method('_func_name_') == False)
	test_list.append(putil.pinspect.is_magic_method('__func_name__') == True)
	assert test_list == [True]*len(test_list)


def test_loaded_package_modules():
	""" Test loaded_package_modules() function """
	test_list = list()
	module_name_list = ['check', 'eng', 'misc', 'pinspect', 'test']
	modules_obj_list = set([sys.modules['putil']]+[sys.modules['putil.{0}'.format(module_name)] for module_name in module_name_list])
	test_list.append(set(putil.pinspect.loaded_package_modules(sys.modules['putil'])) == modules_obj_list)
	test_list.append(set(putil.pinspect.loaded_package_modules(sys.modules['putil.pinspect'])) == modules_obj_list)
	assert test_list == [True]*len(test_list)

def test_replace_tabs():
	""" Test _replace_tabs() function """
	test_list = list()
	test_list.append(putil.pinspect._replace_tabs('    def func()') == '    def func()')
	for snum in range(0, 8):
		test_list.append(putil.pinspect._replace_tabs((' '*snum)+'\tdef func()') == (' '*8)+'def func()')
	test_list.append(putil.pinspect._replace_tabs('   \t   def func()') == (' '*8)+'   def func()')
	test_list.append(putil.pinspect._replace_tabs('   \t  \t def func()') == (' '*16)+' def func()')
	test_list.append(putil.pinspect._replace_tabs('\f   \t  \t def func()') == (' '*16)+' def func()')
	assert test_list == [True]*len(test_list)

