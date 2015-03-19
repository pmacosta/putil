# test_pinspect.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212

"""
putil.pintrospect unit tests
"""

import os
import sys
import copy
import mock
import types
import random
import string
import inspect

import putil.test
import putil.pinspect


def compare_str_outputs(obj, ref_list):
	""" Produce helpful output when reference output does not match actual output """
	ref_text = '\n'.join(ref_list)
	if str(obj) != ref_text:
		print str(obj)
		print '---[Differing lines]---'
		actual_list = str(obj).split('\n')
		for actual_line, ref_line in zip(actual_list, ref_list):
			if actual_line != ref_line:
				print 'Actual line...: {0}'.format(actual_line)
				print 'Reference line: {0}'.format(ref_line)
				break
		print '-----------------------'
		if len(actual_list) != len(ref_list):
			print '{0} longer than {1}'.format('Actual' if len(actual_list) > len(ref_list) else 'Reference', 'reference' if len(actual_list) > len(ref_list) else 'actual')
			print_list = actual_list if len(actual_list) > len(ref_list) else ref_list
			print print_list[min([len(actual_list), len(ref_list)]):]
			print '-----------------------'
	return ref_text


def test_object_is_module():
	""" Test object_is_module() function """
	assert putil.pinspect.is_object_module(5) == False
	assert putil.pinspect.is_object_module(sys.modules['putil.pinspect']) == True


def test_get_module_name():
	""" Test get_module_name() function """
	putil.test.assert_exception(putil.pinspect.get_module_name, {'module_obj':5}, RuntimeError, 'Argument `module_obj` is not valid')
	mock_module_obj = types.ModuleType('mock_module_obj', 'Mock module')
	putil.test.assert_exception(putil.pinspect.get_module_name, {'module_obj':mock_module_obj}, RuntimeError, 'Module object `mock_module_obj` could not be found in loaded modules')
	assert putil.pinspect.get_module_name(sys.modules['putil.pinspect']) == 'putil.pinspect'
	assert putil.pinspect.get_module_name(sys.modules['putil']) == 'putil'


def test_get_package_name():
	""" Test get_package_name() function """
	sys.modules['no_pkg.module'] = types.ModuleType('no_pkg.module', 'Mock module')
	putil.test.assert_exception(putil.pinspect.get_package_name, {'module_obj':sys.modules['no_pkg.module']}, RuntimeError, 'Loaded package root could not be found')
	assert putil.pinspect.get_package_name(sys.modules['putil.pinspect']) == 'putil'


def test_is_special_method():
	""" Test is_special_method() function """
	assert putil.pinspect.is_special_method('func_name') == False
	assert putil.pinspect.is_special_method('_func_name_') == False
	assert putil.pinspect.is_special_method('__func_name__') == True


def test_loaded_package_modules():
	""" Test loaded_package_modules() function """
	module_name_list = ['misc', 'pinspect', 'test']
	modules_obj_list = set([sys.modules['putil']]+[sys.modules['putil.{0}'.format(module_name)] for module_name in module_name_list])
	assert set(putil.pinspect.loaded_package_modules(sys.modules['putil'])) == modules_obj_list
	assert set(putil.pinspect.loaded_package_modules(sys.modules['putil.pinspect'])) == modules_obj_list


def test_replace_tabs():
	""" Test _replace_tabs() function """
	assert putil.pinspect._replace_tabs('    def func()') == '    def func()'
	for snum in range(0, 8):
		assert putil.pinspect._replace_tabs((' '*snum)+'\tdef func()') == (' '*8)+'def func()'
	assert putil.pinspect._replace_tabs('   \t   def func()') == (' '*8)+'   def func()'
	assert putil.pinspect._replace_tabs('   \t  \t def func()') == (' '*16)+' def func()'
	assert putil.pinspect._replace_tabs('\f   \t  \t def func()') == (' '*16)+' def func()'


def test_callables():	# pylint: disable=R0915
	""" Test callables class """
	def mock_get_code_id(obj, file_name=None, offset=0):	#pylint: disable=W0612,W0613
		""" Mock function to trigger exception related to callable not found in database """
		return (''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)), random.random())
	obj = putil.pinspect.Callables()
	assert obj.callables_db == dict()
	assert obj.reverse_callables_db == dict()
	putil.test.assert_exception(obj.trace, {'obj':None}, RuntimeError, 'Argument `obj` is not valid')
	putil.test.assert_exception(obj.trace, {'obj':'not_an_object'}, RuntimeError, 'Argument `obj` is not valid')
	sys.path.append(os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), 'support'))
	import pinspect_support_module_1	#pylint: disable=F0401,W0612
	obj.trace(sys.modules['pinspect_support_module_1'])
	ref_list = list()
	ref_list.append('Modules:')
	ref_list.append('   pinspect_support_module_1')
	ref_list.append('   pinspect_support_module_2')
	ref_list.append('   pinspect_support_module_3')
	ref_list.append('   pinspect_support_module_4')
	ref_list.append('Classes:')
	ref_list.append('   pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators')
	ref_list.append('   pinspect_support_module_1.ClassWithPropertyDefinedViaFunction')
	ref_list.append('   pinspect_support_module_1.ClassWithPropertyDefinedViaLambdaAndEnclosure')
	ref_list.append('   pinspect_support_module_1.class_enclosing_func.ClosureClass')
	ref_list.append('   pinspect_support_module_1.class_enclosing_func.ClosureClass.sub_enclosure_method.SubClosureClass')
	ref_list.append('   pinspect_support_module_1.class_namespace_test_enclosing_func.NamespaceTestClosureClass')
	ref_list.append('   pinspect_support_module_2.SimpleClass')
	ref_list.append('   pinspect_support_module_3.another_class_enclosing_func.FromImportClosureClass')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators: class (101)')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.__call__: meth (106)')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.__init__: meth (103)')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.encprop: prop')
	ref_list.append('   fget: pinspect_support_module_1.simple_property_generator.fget')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.temp: prop')
	ref_list.append('   fset: pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.temp(setter)')
	ref_list.append('   fdel: pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.temp(deleter)')
	ref_list.append('   fget: pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.temp(getter)')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.temp(deleter): meth (120)')
	ref_list.append('   fdel of: pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.temp')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.temp(getter): meth (109)')
	ref_list.append('   fget of: pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.temp')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.temp(setter): meth (114)')
	ref_list.append('   fset of: pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.temp')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaFunction: class (73)')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaFunction.__init__: meth (75)')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaFunction._deleter_func: meth (91)')
	ref_list.append('   fdel of: pinspect_support_module_1.ClassWithPropertyDefinedViaFunction.state')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaFunction._getter_func: meth (87)')
	ref_list.append('   fget of: pinspect_support_module_1.ClassWithPropertyDefinedViaFunction.state')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaFunction._setter_func: meth (78)')
	ref_list.append('   fset of: pinspect_support_module_1.ClassWithPropertyDefinedViaFunction.state')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaFunction.state: prop (95)')
	ref_list.append('   fset: pinspect_support_module_1.ClassWithPropertyDefinedViaFunction._setter_func')
	ref_list.append('   fdel: pinspect_support_module_1.ClassWithPropertyDefinedViaFunction._deleter_func')
	ref_list.append('   fget: pinspect_support_module_1.ClassWithPropertyDefinedViaFunction._getter_func')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaLambdaAndEnclosure: class (52)')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaLambdaAndEnclosure.__init__: meth (54)')
	ref_list.append('pinspect_support_module_1.ClassWithPropertyDefinedViaLambdaAndEnclosure.clsvar: prop (57)')
	ref_list.append('   fset: pinspect_support_module_2.setter_enclosing_func.setter_closure_func')
	ref_list.append('   fget: pinspect_support_module_1.ClassWithPropertyDefinedViaLambdaAndEnclosure.clsvar.fget_lambda')
	ref_list.append('pinspect_support_module_1.class_enclosing_func: func (19)')
	ref_list.append('pinspect_support_module_1.class_enclosing_func.ClosureClass: class (22)')
	ref_list.append('pinspect_support_module_1.class_enclosing_func.ClosureClass.__init__: meth (24)')
	ref_list.append('pinspect_support_module_1.class_enclosing_func.ClosureClass.get_obj: meth (28)')
	ref_list.append('pinspect_support_module_1.class_enclosing_func.ClosureClass.obj: prop (47)')
	ref_list.append('   fset: pinspect_support_module_1.class_enclosing_func.ClosureClass.set_obj')
	ref_list.append('   fdel: pinspect_support_module_3.deleter')
	ref_list.append('   fget: pinspect_support_module_2.getter_func_for_closure_class')
	ref_list.append('pinspect_support_module_1.class_enclosing_func.ClosureClass.set_obj: meth (32)')
	ref_list.append('   fset of: pinspect_support_module_1.class_enclosing_func.ClosureClass.obj')
	ref_list.append('pinspect_support_module_1.class_enclosing_func.ClosureClass.sub_enclosure_method: meth (38)')
	ref_list.append('pinspect_support_module_1.class_enclosing_func.ClosureClass.sub_enclosure_method.SubClosureClass: class (40)')
	ref_list.append('pinspect_support_module_1.class_enclosing_func.ClosureClass.sub_enclosure_method.SubClosureClass.__init__: meth (42)')
	ref_list.append('pinspect_support_module_1.class_namespace_test_enclosing_func: func (131)')
	ref_list.append('pinspect_support_module_1.class_namespace_test_enclosing_func.NamespaceTestClosureClass: class (133)')
	ref_list.append('pinspect_support_module_1.class_namespace_test_enclosing_func.NamespaceTestClosureClass.__init__: meth (136)')
	ref_list.append('pinspect_support_module_1.class_namespace_test_enclosing_func.NamespaceTestClosureClass.nameprop: prop')
	ref_list.append('   fget: pinspect_support_module_4.another_property_action_enclosing_function.fget')
	ref_list.append('pinspect_support_module_1.dummy_decorator: func (60)')
	ref_list.append('pinspect_support_module_1.module_enclosing_func: func (11)')
	ref_list.append('pinspect_support_module_1.module_enclosing_func.module_closure_func: func (13)')
	ref_list.append('pinspect_support_module_1.simple_property_generator: func (65)')
	ref_list.append('pinspect_support_module_1.simple_property_generator.fget: func (67)')
	ref_list.append('   fget of: pinspect_support_module_1.ClassWithPropertyDefinedViaDecorators.encprop')
	ref_list.append('   fget of: pinspect_support_module_3.another_class_enclosing_func.FromImportClosureClass.encprop')
	ref_list.append('pinspect_support_module_2.SimpleClass: class (15)')
	ref_list.append('pinspect_support_module_2.SimpleClass.__init__: meth (17)')
	ref_list.append('pinspect_support_module_2.SimpleClass.get_mobj: meth (21)')
	ref_list.append('   fget of: pinspect_support_module_2.SimpleClass.mobj')
	ref_list.append('pinspect_support_module_2.SimpleClass.mobj: prop (29)')
	ref_list.append('   fset: pinspect_support_module_2.SimpleClass.set_mobj')
	ref_list.append('   fget: pinspect_support_module_2.SimpleClass.get_mobj')
	ref_list.append('pinspect_support_module_2.SimpleClass.set_mobj: meth (25)')
	ref_list.append('   fset of: pinspect_support_module_2.SimpleClass.mobj')
	ref_list.append('pinspect_support_module_2.getter_func_for_closure_class: func (32)')
	ref_list.append('   fget of: pinspect_support_module_1.class_enclosing_func.ClosureClass.obj')
	ref_list.append('pinspect_support_module_2.setter_enclosing_func: func (7)')
	ref_list.append('pinspect_support_module_2.setter_enclosing_func.setter_closure_func: func (9)')
	ref_list.append('   fset of: pinspect_support_module_1.ClassWithPropertyDefinedViaLambdaAndEnclosure.clsvar')
	ref_list.append('pinspect_support_module_3.another_class_enclosing_func: func (12)')
	ref_list.append('pinspect_support_module_3.another_class_enclosing_func.FromImportClosureClass: class (15)')
	ref_list.append('pinspect_support_module_3.another_class_enclosing_func.FromImportClosureClass.__init__: meth (17)')
	ref_list.append('pinspect_support_module_3.another_class_enclosing_func.FromImportClosureClass.encprop: prop')
	ref_list.append('   fget: pinspect_support_module_1.simple_property_generator.fget')
	ref_list.append('pinspect_support_module_3.another_property_action_enclosing_function: func (25)')
	ref_list.append('pinspect_support_module_3.another_property_action_enclosing_function.fget: func (27)')
	ref_list.append('pinspect_support_module_3.deleter: func (7)')
	ref_list.append('   fdel of: pinspect_support_module_1.class_enclosing_func.ClosureClass.obj')
	ref_list.append('pinspect_support_module_4.another_property_action_enclosing_function: func (16)')
	ref_list.append('pinspect_support_module_4.another_property_action_enclosing_function.fget: func (18)')
	ref_list.append('   fget of: pinspect_support_module_1.class_namespace_test_enclosing_func.NamespaceTestClosureClass.nameprop')
	ref_text = compare_str_outputs(obj, ref_list)
	assert str(obj) == ref_text
	# Test that callables_db and reverse_callables_db are in sync
	congruence_flag = True
	for key, value in obj.callables_db.items():
		if value['code_id']:
			congruence_flag = obj.reverse_callables_db[value['code_id']] == key
			if not congruence_flag:
				break
	assert congruence_flag
	# Test string and representation methods
	assert repr(obj) == "putil.pinspect.Callables([sys.modules['pinspect_support_module_1'], sys.modules['pinspect_support_module_2'], sys.modules['pinspect_support_module_3'], sys.modules['pinspect_support_module_4']])"
	assert str(putil.pinspect.Callables([sys.modules['pinspect_support_module_2'], sys.modules['pinspect_support_module_1']])) == ref_text
	assert repr(putil.pinspect.Callables([sys.modules['pinspect_support_module_2'], sys.modules['pinspect_support_module_1']])) == \
				  "putil.pinspect.Callables([sys.modules['pinspect_support_module_1'], sys.modules['pinspect_support_module_2'], sys.modules['pinspect_support_module_3'], sys.modules['pinspect_support_module_4']])"
	assert repr(putil.pinspect.Callables()) == "putil.pinspect.Callables()"
	# Test multiple enclosed classes
	obj = putil.pinspect.Callables()
	import pinspect_support_module_7	#pylint: disable=F0401,W0612
	obj.trace(sys.modules['pinspect_support_module_7'])
	ref_list = list()
	ref_list.append('Modules:')
	ref_list.append('   pinspect_support_module_7')
	ref_list.append('Classes:')
	ref_list.append('   pinspect_support_module_7.test_enclosure_class.FinalClass')
	ref_list.append('   pinspect_support_module_7.test_enclosure_class.MockFCode')
	ref_list.append('   pinspect_support_module_7.test_enclosure_class.MockGetFrame')
	ref_list.append('   pinspect_support_module_7.test_enclosure_class.MockGetFrame.sub_enclosure_method.SubClosureClass')
	ref_list.append('pinspect_support_module_7.test_enclosure_class: func (6)')
	ref_list.append('pinspect_support_module_7.test_enclosure_class.FinalClass: class (23)')
	ref_list.append('pinspect_support_module_7.test_enclosure_class.FinalClass.__init__: meth (24)')
	ref_list.append('pinspect_support_module_7.test_enclosure_class.MockFCode: class (7)')
	ref_list.append('pinspect_support_module_7.test_enclosure_class.MockFCode.__init__: meth (8)')
	ref_list.append('pinspect_support_module_7.test_enclosure_class.MockGetFrame: class (10)')
	ref_list.append('pinspect_support_module_7.test_enclosure_class.MockGetFrame.__init__: meth (11)')
	ref_list.append('pinspect_support_module_7.test_enclosure_class.MockGetFrame.sub_enclosure_method: meth (13)')
	ref_list.append('pinspect_support_module_7.test_enclosure_class.MockGetFrame.sub_enclosure_method.SubClosureClass: class (16)')
	ref_list.append('pinspect_support_module_7.test_enclosure_class.MockGetFrame.sub_enclosure_method.SubClosureClass.__init__: meth (18)')
	ref_list.append('pinspect_support_module_7.test_enclosure_class.mock_getframe: func (27)')
	ref_text = compare_str_outputs(obj, ref_list)
	assert str(obj) == ref_text
	# Test enclosed class with inheritance
	obj = putil.pinspect.Callables()
	import pinspect_support_module_8	#pylint: disable=F0401,W0612
	obj.trace(sys.modules['pinspect_support_module_8'])
	ref_list = list()
	ref_list.append('Modules:')
	ref_list.append('   pinspect_support_module_8')
	ref_list.append('Classes:')
	ref_list.append('   pinspect_support_module_8.BaseClass')
	ref_list.append('   pinspect_support_module_8.test_enclosure_derived_class.SubClassA')
	ref_list.append('   pinspect_support_module_8.test_enclosure_derived_class.SubClassB')
	ref_list.append('   pinspect_support_module_8.test_enclosure_derived_class.SubClassB.sub_enclosure_method.SubClassC')
	ref_list.append('   pinspect_support_module_8.test_enclosure_derived_class.SubClassD')
	ref_list.append('pinspect_support_module_8.BaseClass: class (6)')
	ref_list.append('pinspect_support_module_8.BaseClass.__init__: meth (8)')
	ref_list.append('pinspect_support_module_8.test_enclosure_derived_class: func (11)')
	ref_list.append('pinspect_support_module_8.test_enclosure_derived_class.SubClassA: class (13)')
	ref_list.append('pinspect_support_module_8.test_enclosure_derived_class.SubClassA.__init__: meth (14)')
	ref_list.append('pinspect_support_module_8.test_enclosure_derived_class.SubClassB: class (18)')
	ref_list.append('pinspect_support_module_8.test_enclosure_derived_class.SubClassB.__init__: meth (19)')
	ref_list.append('pinspect_support_module_8.test_enclosure_derived_class.SubClassB.sub_enclosure_method: meth (22)')
	ref_list.append('pinspect_support_module_8.test_enclosure_derived_class.SubClassB.sub_enclosure_method.SubClassC: class (26)')
	ref_list.append('pinspect_support_module_8.test_enclosure_derived_class.SubClassB.sub_enclosure_method.SubClassC.__init__: meth (28)')
	ref_list.append('pinspect_support_module_8.test_enclosure_derived_class.SubClassD: class (33)')
	ref_list.append('pinspect_support_module_8.test_enclosure_derived_class.SubClassD.__init__: meth (34)')
	ref_text = compare_str_outputs(obj, ref_list)
	assert str(obj) == ref_text

	# Test exception raised when callable is not found in database (mainly to cover potential edge cases not considered during development)
	with mock.patch('putil.pinspect._get_code_id', side_effect=mock_get_code_id):
		putil.test.assert_exception(putil.pinspect.Callables, {'obj':sys.modules['pinspect_support_module_2']}, RuntimeError, r'Attribute `([\w|\W]+)` of property `([\w|\W]+)` not found in callable database')


def test_copy():
	""" Test __copy__() magic method """
	source_obj = putil.pinspect.Callables()
	import pinspect_support_module_1	#pylint: disable=F0401,W0612
	source_obj.trace(sys.modules['pinspect_support_module_1'])
	dest_obj = copy.copy(source_obj)
	assert (source_obj._module_names == dest_obj._module_names) and (id(source_obj._module_names) != id(dest_obj._module_names))
	assert (source_obj._class_names == dest_obj._class_names) and (id(source_obj._class_names) != id(dest_obj._class_names))
	assert (source_obj._callables_db == dest_obj._callables_db) and (id(source_obj._callables_db) != id(dest_obj._callables_db))
	assert (source_obj._reverse_callables_db == dest_obj._reverse_callables_db) and (id(source_obj._reverse_callables_db) != id(dest_obj._reverse_callables_db))


def test_eq():
	""" Test __eq__() magic method """
	obj1 = putil.pinspect.Callables()
	obj2 = putil.pinspect.Callables()
	obj3 = putil.pinspect.Callables()
	import pinspect_support_module_1	#pylint: disable=F0401,W0612
	import pinspect_support_module_2	#pylint: disable=F0401,W0612
	obj1.trace(sys.modules['pinspect_support_module_1'])
	obj2.trace(sys.modules['pinspect_support_module_2'])
	obj2.trace(sys.modules['pinspect_support_module_1'])
	obj3.trace(sys.modules['putil.test'])
	assert (obj1 == obj2) and (obj1 != obj3)


def test_namespace_resolution():
	""" Test correct handling of import statements that cause errors """
	import pinspect_support_module_5	#pylint: disable=F0401,W0612
	obj = putil.pinspect.Callables()
	obj.trace(sys.modules['pinspect_support_module_5'])
	ref_list = list()
	ref_list.append('Modules:')
	ref_list.append('   pinspect_support_module_5')
	ref_list.append('Classes:')
	ref_list.append('   pinspect_support_module_5.namespace_test_enclosing_function.NamespaceTestClass')
	ref_list.append('pinspect_support_module_5.namespace_test_enclosing_function: func (14)')
	ref_list.append('pinspect_support_module_5.namespace_test_enclosing_function.NamespaceTestClass: class (16)')
	ref_list.append('pinspect_support_module_5.namespace_test_enclosing_function.NamespaceTestClass.__init__: meth (18)')
	ref_list.append('pinspect_support_module_5.namespace_test_enclosing_function.NamespaceTestClass._get_data: meth (21)')
	ref_list.append('   fget of: pinspect_support_module_5.namespace_test_enclosing_function.NamespaceTestClass.data')
	ref_list.append('pinspect_support_module_5.namespace_test_enclosing_function.NamespaceTestClass._set_data: meth (24)')
	ref_list.append('   fset of: pinspect_support_module_5.namespace_test_enclosing_function.NamespaceTestClass.data')
	ref_list.append('pinspect_support_module_5.namespace_test_enclosing_function.NamespaceTestClass.data: prop (27)')
	ref_list.append('   fset: pinspect_support_module_5.namespace_test_enclosing_function.NamespaceTestClass._set_data')
	ref_list.append('   fget: pinspect_support_module_5.namespace_test_enclosing_function.NamespaceTestClass._get_data')
	ref_text = compare_str_outputs(obj, ref_list)
	assert str(obj) == ref_text
	import pinspect_support_module_6	#pylint: disable=F0401,W0612
	obj = putil.pinspect.Callables()
	putil.test.assert_exception(obj.trace, {'obj':sys.modules['pinspect_support_module_6']}, ValueError, 'math domain error')


##
# Tests for get_function_args()
###
class TestGetFunctionArgs(object):	#pylint: disable=W0232
	""" Tests for get_function_args function """

	def test_all_positional_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when all arguments are positional arguments """
		def func(ppar1, ppar2, ppar3):	#pylint: disable=C0111,W0613
			pass
		assert putil.pinspect.get_function_args(func) == ('ppar1', 'ppar2', 'ppar3')

	def test_all_keyword_arguments(self):	#pylint: disable=R0201,C0103,W0613
		""" Test that function behaves properly when all arguments are keywords arguments """
		def func(kpar1=1, kpar2=2, kpar3=3):	#pylint: disable=C0111,R0913,W0613
			pass
		assert putil.pinspect.get_function_args(func) == ('kpar1', 'kpar2', 'kpar3')

	def test_positional_and_keyword_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when arguments are a mix of positional and keywords arguments """
		def func(ppar1, ppar2, ppar3, kpar1=1, kpar2=2, kpar3=3, **kwargs):	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert putil.pinspect.get_function_args(func) == ('ppar1', 'ppar2', 'ppar3', 'kpar1', 'kpar2', 'kpar3', '**kwargs')
		assert putil.pinspect.get_function_args(func, no_varargs=True) == ('ppar1', 'ppar2', 'ppar3', 'kpar1', 'kpar2', 'kpar3')

	def test_no_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when there are no arguments passed """
		def func():	#pylint: disable=C0111,R0913,W0613
			pass
		assert putil.pinspect.get_function_args(func) == ()

	def test_no_self(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when there are no arguments passed """
		class MyClass(object):	#pylint: disable=C0111,R0903
			def __init__(self, value, **kwargs):	#pylint: disable=C0111,R0913,W0613
				pass
		assert putil.pinspect.get_function_args(MyClass.__init__) == ('self', 'value', '**kwargs')
		assert putil.pinspect.get_function_args(MyClass.__init__, no_self=True) == ('value', '**kwargs')
		assert putil.pinspect.get_function_args(MyClass.__init__, no_self=True, no_varargs=True) == ('value', )
		assert putil.pinspect.get_function_args(MyClass.__init__, no_varargs=True) == ('self', 'value')
