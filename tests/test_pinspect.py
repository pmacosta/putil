# test_pinspect.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212

"""
putil.pintrospect unit tests
"""

import os
import sys
import copy
import mock
import time
import types
import inspect

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

def test_callables():
	""" Test callables class """
	def mock_get_code_id(obj):	#pylint: disable=W0612
		""" Return unique identity tuple to individualize callable object """
		if hasattr(obj, 'func_code'):
			code_obj = getattr(obj, 'func_code')
			return (code_obj.co_filename, time.time())	# Ensure that each method has a unique number and thus one that will not be found
		return None

	test_list = list()
	obj = putil.pinspect.Callables()
	test_list.append(obj.callables_db == dict())
	test_list.append(putil.test.trigger_exception(obj.trace, {'obj':None}, TypeError, 'Argument `obj` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.trace, {'obj':'not_an_object'}, TypeError, 'Argument `obj` is not valid'))
	sys.path.append(os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), 'support'))
	import my_module1	#pylint: disable=F0401,W0612
	obj.trace(sys.modules['my_module1'])
	ref_list = list()
	ref_list.append('Modules: my_module1, my_module2')
	ref_list.append('Classes: my_module1.TraceClass1, my_module1.TraceClass2, my_module1.TraceClass3')
	ref_list.append('my_module1.TraceClass1.__init__: meth (18)')
	ref_list.append('my_module1.TraceClass1.value1: prop')
	ref_list.append('   fset: my_module2.setter_enclosing_func.setter_closure_func')
	ref_list.append('   fget: my_module1.TraceClass1.value1.fget_lambda')
	ref_list.append('my_module1.TraceClass2.__init__: meth (29)')
	ref_list.append('my_module1.TraceClass2._deleter_func2: meth (43)')
	ref_list.append('my_module1.TraceClass2._getter_func2: meth (39)')
	ref_list.append('my_module1.TraceClass2._setter_func2: meth (32)')
	ref_list.append('my_module1.TraceClass2.value2: prop')
	ref_list.append('   fset: my_module1.TraceClass2._setter_func2')
	ref_list.append('   fdel: my_module1.TraceClass2._deleter_func2')
	ref_list.append('   fget: my_module1.TraceClass2._getter_func2')
	ref_list.append('my_module1.TraceClass3.__init__: meth (52)')
	ref_list.append('my_module1.TraceClass3.value3: prop')
	ref_list.append('   fset: my_module1.TraceClass3.value3(setter)')
	ref_list.append('   fdel: my_module1.TraceClass3.value3(deleter)')
	ref_list.append('   fget: my_module1.TraceClass3.value3(getter)')
	ref_list.append('my_module1.TraceClass3.value3(deleter): meth (67)')
	ref_list.append('my_module1.TraceClass3.value3(getter): meth (55)')
	ref_list.append('my_module1.TraceClass3.value3(setter): meth (60)')
	ref_list.append('my_module1.module_enclosing_func: func (9)')
	ref_list.append('my_module1.module_enclosing_func.module_closure_func: func (11)')
	ref_list.append('my_module1.prop_decorator: func (23)')
	ref_list.append('my_module2.setter_enclosing_func: func (6)')
	ref_list.append('my_module2.setter_enclosing_func.setter_closure_func: func (8)')
	ref_text = '\n'.join(ref_list)
	test_list.append(str(obj) == ref_text)
	test_list.append(repr(obj) == "putil.pinspect.Callables([sys.modules['my_module1'], sys.modules['my_module2']])")
	test_list.append(str(putil.pinspect.Callables([sys.modules['my_module2'], sys.modules['my_module1']])) == ref_text)
	test_list.append(repr(putil.pinspect.Callables([sys.modules['my_module2'], sys.modules['my_module1']])) == "putil.pinspect.Callables([sys.modules['my_module2'], sys.modules['my_module1']])")
	test_list.append(repr(putil.pinspect.Callables()) == "putil.pinspect.Callables()")
	with mock.patch('putil.pinspect._get_code_id') as mock_get_code_id:
		test_list.append(putil.test.trigger_exception(putil.pinspect.Callables, {'obj':sys.modules['my_module1']}, RuntimeError, 'Attribute `fset` of property `my_module1.TraceClass1.value1` not found in callable database'))
	assert test_list == [True]*len(test_list)

def test_copy():
	""" Test __copy__() magic method """
	source_obj = putil.pinspect.Callables()
	import my_module1	#pylint: disable=F0401,W0612
	source_obj.trace(sys.modules['my_module1'])
	dest_obj = copy.copy(source_obj)
	test_list = list()
	test_list.append((source_obj._modules == dest_obj._modules) and (id(source_obj._modules) != id(dest_obj._modules)))
	test_list.append((source_obj._classes == dest_obj._classes) and (id(source_obj._classes) != id(dest_obj._classes)))
	test_list.append((source_obj._prop_dict == dest_obj._prop_dict) and (id(source_obj._prop_dict) != id(dest_obj._prop_dict)))
	test_list.append((source_obj._callables_db == dest_obj._callables_db) and (id(source_obj._callables_db) != id(dest_obj._callables_db)))
	assert test_list == [True]*len(test_list)

def test_eq():
	""" Test __eq__() magic method """
	obj1 = putil.pinspect.Callables()
	obj2 = putil.pinspect.Callables()
	obj3 = putil.pinspect.Callables()
	import my_module1	#pylint: disable=F0401,W0612
	import my_module2	#pylint: disable=F0401,W0612
	obj1.trace(sys.modules['my_module1'])
	obj2.trace(sys.modules['my_module2'])
	obj2.trace(sys.modules['my_module1'])
	obj3.trace(sys.modules['putil.test'])
	assert (obj1 == obj2) and (obj1 != obj3)

