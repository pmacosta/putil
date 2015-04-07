# test_pinspect.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import copy, os, pytest, sys, types

import putil.pinspect, putil.test

TEST_DIR = os.path.dirname(__file__)
SUPPORT_DIR = os.path.join(TEST_DIR, 'support')
sys.path.append(SUPPORT_DIR)


###
# Helper functions
###
def compare_str_outputs(obj, ref_list):
	""" Produce helpful output when reference output does not match actual output """
	ref_text = '\n'.join(ref_list)
	if str(obj) != ref_text:
		actual_list = str(obj).split('\n')
		for actual_line, ref_line in zip(actual_list, ref_list):
			if actual_line != ref_line:
				print '\033[{0}m{1}\033[0m <-> {2}'.format(31, actual_line, ref_line)
			else:
				print actual_line
		print '---[Differing lines]---'
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


###
# Tests for module functions
###
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


def test_get_module_name_from_file_name():	#pylint: disable=C0103
	""" Test _get_module_name_from_file_name() function """
	putil.test.assert_exception(putil.pinspect._get_module_name_from_file_name, {'file_name':'_not_a_module'}, RuntimeError, 'Module could not be found')
	assert putil.pinspect._get_module_name_from_file_name(sys.modules['putil.pinspect'].__file__) == 'putil.pinspect'


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
	# Have to generate list dynamically because loaded modules depends on how test is run, i.e. ${PACKAGE_DIR}/sbin/test.sh pinspect produces different results than ${PACKAGE_DIR}/pytest -x -s or in virtualenvs
	pkg_dir = os.path.dirname(sys.modules['putil'].__file__)
	module_name_list = [obj for name, obj in sys.modules.iteritems() if name.startswith('putil.') and (hasattr(obj, '__file__')) and (getattr(obj, '__file__').startswith(pkg_dir))]
	modules_obj_list = set([sys.modules['putil']]+module_name_list)
	assert set(putil.pinspect.loaded_package_modules(sys.modules['putil'])) == modules_obj_list
	assert set(putil.pinspect.loaded_package_modules(sys.modules['putil'])) == modules_obj_list		# Repetition on purpose, to test what happens with multiple calls
	assert set(putil.pinspect.loaded_package_modules(sys.modules['putil.pinspect'])) == modules_obj_list


###
# Test for classes
###
class TestCallables(object):	#pylint: disable=W0232,R0903
	""" Test for Callables """
	def test_callables_errors(self):	#pylint: disable=R0201,R0915
		""" Test callables __init__ (and trace() function) data validation """
		putil.test.assert_exception(putil.pinspect.Callables, {'file_names':5}, RuntimeError, 'Argument `file_names` is not valid')
		putil.test.assert_exception(putil.pinspect.Callables, {'file_names':[5]}, RuntimeError, 'Argument `file_names` is not valid')
		putil.test.assert_exception(putil.pinspect.Callables, {'file_names':['_not_a_file_']}, IOError, 'File _not_a_file_ could not be found')

	def test_repr(self):	#pylint: disable=R0201
		""" Test __repr__() function """
		import exdoc_support_module_1, exdoc_support_module_1	#pylint: disable=F0401,W0612
		file1 = sys.modules['exdoc_support_module_1'].__file__.replace('.pyc', '.py')
		file2 = sys.modules['exdoc_support_module_2'].__file__.replace('.pyc', '.py')
		xobj = putil.pinspect.Callables([file2])
		xobj.trace([file1])
		assert repr(xobj) == "putil.pinspect.Callables(['{0}', '{1}'])".format(file1, file2)

	def test_add(self):	#pylint: disable=R0201
		""" Test __add__() and __radd__() functions """
		obj1 = putil.pinspect.Callables()
		obj1._callables_db = {'call1':{'a':5, 'b':6}, 'call2':{'a':7, 'b':8}}
		obj1._reverse_callables_db = {'rc1':5, 'rc2':7}
		obj1._modules_dict = {'key1':'alpha', 'key2':'beta'}
		obj1._file_names = ['hello']
		obj1._module_names = ['this', 'is']
		obj1._class_names = ['once', 'upon']
		#
		obj2 = putil.pinspect.Callables()
		obj2._callables_db = {'call3':{'a':10, 'b':100}, 'call4':{'a':200, 'b':300}}
		obj2._reverse_callables_db = {'rc3':0, 'rc4':-1}
		obj2._modules_dict = {'key3':'pi', 'key4':'gamma'}
		obj2._file_names = ['world']
		obj2._module_names = ['a', 'test']
		obj2._class_names = ['a', 'time']
		#
		obj1._callables_db = {'call3':{'a':5, 'b':6}, 'call2':{'a':7, 'b':8}}
		with pytest.raises(RuntimeError) as excinfo:
			obj1+obj2	#pylint: disable=W0104
		assert excinfo.value.message == 'Conflicting information between objects'
		obj1._callables_db = {'call1':{'a':5, 'b':6}, 'call2':{'a':7, 'b':8}}
		#
		obj2._reverse_callables_db = {'rc3':0, 'rc2':-1}
		with pytest.raises(RuntimeError) as excinfo:
			obj1+obj2	#pylint: disable=W0104
		assert excinfo.value.message == 'Conflicting information between objects'
		obj2._reverse_callables_db = {'rc3':0, 'rc4':-1}
		#
		obj2._modules_dict = {'key1':'pi', 'key4':'gamma'}
		with pytest.raises(RuntimeError) as excinfo:
			obj1+obj2	#pylint: disable=W0104
		assert excinfo.value.message == 'Conflicting information between objects'
		obj2._modules_dict = {'key3':'pi', 'key4':'gamma'}
		# Test when intersection is the same
		obj2._modules_dict = {'key1':'alpha', 'key4':'gamma'}
		obj1+obj2	#pylint: disable=W0104
		obj2._modules_dict = {'key3':'pi', 'key4':'gamma'}

		sobj = obj1+obj2
		assert sorted(sobj._callables_db) == sorted({'call1':{'a':5, 'b':6}, 'call2':{'a':7, 'b':8}, 'call3':{'a':10, 'b':100}, 'call4':{'a':200, 'b':300}})
		assert sorted(sobj._reverse_callables_db) == sorted({'rc1':5, 'rc2':7, 'rc3':0, 'rc4':-1})
		assert sorted(sobj._modules_dict) == sorted({'key1':'alpha', 'key2':'beta', 'key3':'pi', 'key4':'gamma'})
		assert sorted(sobj._file_names) == sorted(['hello', 'world'])
		assert sorted(sobj._module_names) == sorted(['this', 'is', 'a', 'test'])
		assert sorted(sobj._class_names) == sorted(['once', 'upon', 'a', 'time'])
		#
		obj1 += obj2
		assert sorted(obj1._callables_db) == sorted({'call1':{'a':5, 'b':6}, 'call2':{'a':7, 'b':8}, 'call3':{'a':10, 'b':100}, 'call4':{'a':200, 'b':300}})
		assert sorted(obj1._reverse_callables_db) == sorted({'rc1':5, 'rc2':7, 'rc3':0, 'rc4':-1})
		assert sorted(obj1._modules_dict) == sorted({'key1':'alpha', 'key2':'beta', 'key3':'pi', 'key4':'gamma'})
		assert sorted(obj1._file_names) == sorted(['hello', 'world'])
		assert sorted(obj1._module_names) == sorted(['this', 'is', 'a', 'test'])
		assert sorted(obj1._class_names) == sorted(['once', 'upon', 'a', 'time'])

	def test_callables_works(self):	#pylint: disable=R0201,R0915
		import exdoc_support_module_1	#pylint: disable=F0401,W0612
		xobj = putil.pinspect.Callables([sys.modules['exdoc_support_module_1'].__file__])
		ref = list()
		ref.append('Modules:')
		ref.append('   exdoc_support_module_1')
		ref.append('Classes:')
		ref.append('   exdoc_support_module_1.ExceptionAutoDocClass')
		ref.append('exdoc_support_module_1._validate_arguments: func (15-20)')
		ref.append('exdoc_support_module_1._write: func (21-25)')
		ref.append('exdoc_support_module_1.write: func (26-33)')
		ref.append('exdoc_support_module_1.read: func (34-39)')
		ref.append('exdoc_support_module_1.probe: func (40-48)')
		ref.append('exdoc_support_module_1.dummy_decorator: func (49-53)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass: class (54-130)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass.__init__: meth (56-66)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass._del_value3: meth (67-70)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass._get_value3: meth (71-75)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass._set_value1: meth (76-80)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass._set_value2: meth (81-86)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass._set_value3: meth (87-91)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass.add: meth (92-95)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass.subtract: meth (96-99)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass.multiply: meth (100-104)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass.divide: meth (105-109)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass.temp(getter): meth (110-114)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass.temp(setter): meth (115-120)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass.temp(deleter): meth (121-125)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass.value1: prop (126)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass.value2: prop (128)')
		ref.append('exdoc_support_module_1.ExceptionAutoDocClass.value3: prop (130)')
		ref_txt = '\n'.join(ref)
		actual_txt = str(xobj)
		assert actual_txt == ref_txt
		import test_exdoc	#pylint: disable=F0401,W0612
		xobj = putil.pinspect.Callables([sys.modules['test_exdoc'].__file__])
		ref = list()
		ref.append('Modules:')
		ref.append('   test_exdoc')
		ref.append('Classes:')
		ref.append('   test_exdoc.MockFCode')
		ref.append('   test_exdoc.MockGetFrame')
		ref.append('test_exdoc.load_support_module: func (19-33)')
		ref.append('test_exdoc.trace_error_class: func (34-42)')
		ref.append('test_exdoc.exdocobj: func (43-73)')
		ref.append('test_exdoc.exdocobj.multi_level_write: func (48-50)')
		ref.append('test_exdoc.exdocobj_single: func (74-83)')
		ref.append('test_exdoc.simple_exobj: func (84-93)')
		ref.append('test_exdoc.simple_exobj.func1: func (88-89)')
		ref.append('test_exdoc.MockFCode: class (96-101)')
		ref.append('test_exdoc.MockFCode.__init__: meth (97-101)')
		ref.append('test_exdoc.MockGetFrame: class (102-106)')
		ref.append('test_exdoc.MockGetFrame.__init__: meth (103-106)')
		ref.append('test_exdoc.mock_getframe: func (107-110)')
		ref.append('test_exdoc.test_exdoc_errors: func (111-123)')
		ref.append('test_exdoc.test_depth_property: func (124-134)')
		ref.append('test_exdoc.test_exclude_property: func (135-145)')
		ref.append('test_exdoc.test_build_ex_tree: func (146-212)')
		ref.append('test_exdoc.test_build_ex_tree.func1: func (153-154)')
		ref.append('test_exdoc.test_build_ex_tree.mock_add_nodes1: func (156-157)')
		ref.append('test_exdoc.test_build_ex_tree.mock_add_nodes2: func (158-159)')
		ref.append('test_exdoc.test_build_ex_tree.mock_add_nodes3: func (160-161)')
		ref.append('test_exdoc.test_get_sphinx_doc: func (213-278)')
		ref.append('test_exdoc.test_get_sphinx_autodoc: func (279-294)')
		ref.append('test_exdoc.test_copy_works: func (295-307)')
		ref.append('test_exdoc.test_exdoccxt_errors: func (308-318)')
		ref.append('test_exdoc.test_exdoccxt_multiple: func (319-338)')
		ref.append('test_exdoc.test_exdoccxt_multiple.func1: func (323-325)')
		ref_txt = '\n'.join(ref)
		actual_txt = str(xobj)
		assert actual_txt == ref_txt
		import pinspect_support_module_4	#pylint: disable=F0401,W0612
		xobj = putil.pinspect.Callables([sys.modules['pinspect_support_module_4'].__file__])
		ref = list()
		ref.append('Modules:')
		ref.append('   pinspect_support_module_4')
		ref.append('pinspect_support_module_4.another_property_action_enclosing_function: func (16-21)')
		ref.append('pinspect_support_module_4.another_property_action_enclosing_function.fget: func (18-20)')
		ref_txt = '\n'.join(ref)
		actual_txt = str(xobj)
		assert actual_txt == ref_txt
		# Test re-tries, should produce no action and raise no exception
		xobj.trace([sys.modules['pinspect_support_module_4'].__file__])

	def test_empty_str(self): #pylint: disable=R0201
		""" Test __str__() magic method when object is empty """
		obj = putil.pinspect.Callables()
		assert str(obj) == ''

	def test_copy(self): #pylint: disable=R0201
		""" Test __copy__() magic method """
		source_obj = putil.pinspect.Callables()
		import pinspect_support_module_1	#pylint: disable=F0401,W0612
		source_obj.trace([sys.modules['pinspect_support_module_1'].__file__])
		dest_obj = copy.copy(source_obj)
		assert (source_obj._module_names == dest_obj._module_names) and (id(source_obj._module_names) != id(dest_obj._module_names))
		assert (source_obj._class_names == dest_obj._class_names) and (id(source_obj._class_names) != id(dest_obj._class_names))
		assert (source_obj._callables_db == dest_obj._callables_db) and (id(source_obj._callables_db) != id(dest_obj._callables_db))
		assert (source_obj._reverse_callables_db == dest_obj._reverse_callables_db) and (id(source_obj._reverse_callables_db) != id(dest_obj._reverse_callables_db))

	def test_eq(self): #pylint: disable=R0201
		""" Test __eq__() magic method """
		obj1 = putil.pinspect.Callables()
		obj2 = putil.pinspect.Callables()
		obj3 = putil.pinspect.Callables()
		import pinspect_support_module_1	#pylint: disable=F0401,W0612
		import pinspect_support_module_2	#pylint: disable=F0401,W0612
		obj1.trace([sys.modules['pinspect_support_module_1'].__file__])
		obj2.trace([sys.modules['pinspect_support_module_1'].__file__])
		obj3.trace([sys.modules['putil.test'].__file__])
		assert (obj1 == obj2) and (obj1 != obj3)
		assert 5 != obj1

	def test_callables_db(self): #pylint: disable=R0201
		""" Test callables_db property """
		import pinspect_support_module_4	#pylint: disable=F0401,W0612
		xobj = putil.pinspect.Callables([sys.modules['pinspect_support_module_4'].__file__])
		pkg_dir = os.path.dirname(__file__)
		ref = {
			'pinspect_support_module_4.another_property_action_enclosing_function': {
				'code_id': (os.path.join(pkg_dir, 'support', 'pinspect_support_module_4.py'), 16),
				'last_lineno': 21,
				'name': 'pinspect_support_module_4.another_property_action_enclosing_function',
				'type': 'func'
			},
			'pinspect_support_module_4.another_property_action_enclosing_function.fget': {
				'code_id': (os.path.join(pkg_dir, 'support', 'pinspect_support_module_4.py'), 18),
				'last_lineno': 20,
				'name': 'pinspect_support_module_4.another_property_action_enclosing_function.fget',
				'type': 'func'
			}
		}
		assert sorted(xobj.callables_db) == sorted(ref)
		ref = {
			(os.path.join(pkg_dir, 'support', 'pinspect_support_module_4.py'), 16): 'pinspect_support_module_4.another_property_action_enclosing_function',
			(os.path.join(pkg_dir, 'support', 'pinspect_support_module_4.py'), 18): 'pinspect_support_module_4.another_property_action_enclosing_function.fget',
		}
		assert sorted(xobj.reverse_callables_db) == sorted(ref)

	def test_get_callable_from_line(self): #pylint: disable=R0201
		""" Test get_callable_from_line() function """
		xobj = putil.pinspect.Callables()
		import pinspect_support_module_4	#pylint: disable=F0401,W0612
		assert xobj.get_callable_from_line(sys.modules['pinspect_support_module_4'].__file__, 16) == 'pinspect_support_module_4.another_property_action_enclosing_function'
		xobj = putil.pinspect.Callables([sys.modules['pinspect_support_module_4'].__file__])
		assert xobj.get_callable_from_line(sys.modules['pinspect_support_module_4'].__file__, 16) == 'pinspect_support_module_4.another_property_action_enclosing_function'
		assert xobj.get_callable_from_line(sys.modules['pinspect_support_module_4'].__file__, 17) == 'pinspect_support_module_4.another_property_action_enclosing_function'
		assert xobj.get_callable_from_line(sys.modules['pinspect_support_module_4'].__file__, 21) == 'pinspect_support_module_4.another_property_action_enclosing_function'
		assert xobj.get_callable_from_line(sys.modules['pinspect_support_module_4'].__file__, 18) == 'pinspect_support_module_4.another_property_action_enclosing_function.fget'
		assert xobj.get_callable_from_line(sys.modules['pinspect_support_module_4'].__file__, 19) == 'pinspect_support_module_4.another_property_action_enclosing_function.fget'
		assert xobj.get_callable_from_line(sys.modules['pinspect_support_module_4'].__file__, 20) == 'pinspect_support_module_4.another_property_action_enclosing_function.fget'
		assert xobj.get_callable_from_line(sys.modules['pinspect_support_module_4'].__file__, 100) == 'pinspect_support_module_4'


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
