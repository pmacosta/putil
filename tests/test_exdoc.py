# test_exdoc.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,F0401,R0903,W0104,W0212,W0612,W0613,W0621

import imp
import copy
import mock
import os
import pytest
import sys
import __builtin__

import putil.exdoc
import putil.exh
import putil.misc
import putil.test
import tests.support.exdoc_support_module_1
import tests.support.exdoc_support_module_3
import tests.support.exdoc_support_module_4


###
# Functions
###
def load_support_module():
	""" (Re)load support module(s) """
	module_name = 'exdoc_support_module_1'
	if module_name in sys.modules:
		modobj = sys.modules[module_name]
		old_dict = modobj.__dict__.copy()
		try:
			modobj = reload(modobj)
		except:
			modobj.__dict__.update(old_dict)
			raise
	else:
		__import__(module_name)


def trace_error_class():
	""" Trace classes that use the same getter function """
	if putil.exh.get_exh_obj():
		putil.exh.del_exh_obj()
	putil.exh.set_exh_obj(putil.exh.ExHandle(True))
	obj = tests.support.exdoc_support_module_3.Class1()
	obj.value1


@pytest.fixture
def exdocobj():
	""" Trace support module class """
	if putil.exh.get_exh_obj():
		putil.exh.del_exh_obj()
	def multi_level_write():
		"""
		Test that multiple calls to the same function with different hierarchy
		levels get correctly aggregated
		"""
		tests.support.exdoc_support_module_1.write(True)
	with putil.exdoc.ExDocCxt(_no_print=True, exclude=['_pytest']) as exdoc_obj:
		obj = tests.support.exdoc_support_module_1.ExceptionAutoDocClass(10)
		obj.add(5)
		obj.subtract(3)
		obj.divide(5.2)
		obj.multiply(5.2)
		obj.value1 = 11
		obj.value1
		obj.value2 = 33
		obj.value2
		obj.value3 = 77
		obj.value3
		del obj.value3
		obj.temp = 10
		obj.temp
		del obj.temp
		tests.support.exdoc_support_module_1.write()
		multi_level_write()
		tests.support.exdoc_support_module_1.read()
		tests.support.exdoc_support_module_1.probe()
	return exdoc_obj


@pytest.fixture
def exdocobj_single():
	""" Trace support module that only has one callable """
	if putil.exh.get_exh_obj():
		putil.exh.del_exh_obj()
	with putil.exdoc.ExDocCxt(_no_print=True) as exdoc_single_obj:
		tests.support.exdoc_support_module_4.func('John')
	return exdoc_single_obj


@pytest.fixture
def simple_exobj():
	""" Create simple exception handler for miscellaneous property tests """
	# pylint: disable=R0914
	exobj = putil.exh.ExHandle(True)
	def func1():
		exobj.add_exception(
			'first_exception',
			TypeError,
			'This is the first exception'
		)
	func1()
	return exobj


TEST_DIR = os.path.realpath(os.path.dirname(__file__))
SEQ = [
	(os.path.join(TEST_DIR, 'support', 'exdoc_support_module_1.py+{0}'), 99),
	(os.path.join(TEST_DIR, 'support', 'exdoc_support_module_1.py+{0}'), 167),
	(os.path.join(TEST_DIR, 'support', 'exdoc_support_module_4.py+{0}'), 23),
	(os.path.join(TEST_DIR, 'support', 'exdoc_support_module_1.py+{0}'), 1000)
]
class MockFCode(object):
	def __init__(self):
		text, line_no = SEQ.pop(0)
		self.co_filename = text.format(line_no)


class MockGetFrame(object):
	def __init__(self):
		self.f_code = MockFCode()


def mock_getframe(num):
	return MockGetFrame()


def test_exdoc_errors(simple_exobj):
	""" Test exdoc data validation """
	obj = putil.exdoc.ExDoc
	putil.test.assert_exception(
		obj,
		{'exh_obj':5, '_no_print':False},
		RuntimeError,
		'Argument `exh_obj` is not valid'
	)
	putil.test.assert_exception(
		obj,
		{'exh_obj':simple_exobj, 'depth':'hello'},
		RuntimeError,
		'Argument `depth` is not valid'
	)
	putil.test.assert_exception(
		obj,
		{'exh_obj':simple_exobj, 'depth':-1},
		RuntimeError,
		'Argument `depth` is not valid'
	)
	putil.test.assert_exception(
		obj,
		{'exh_obj':simple_exobj, 'exclude':-1},
		RuntimeError,
		'Argument `exclude` is not valid'
	)
	putil.test.assert_exception(
		obj,
		{'exh_obj':simple_exobj, 'exclude':['hello', 3]},
		RuntimeError,
		'Argument `exclude` is not valid'
	)
	putil.test.assert_exception(
		obj,
		{'exh_obj':putil.exh.ExHandle(True), '_no_print':False},
		ValueError,
		'Object of argument `exh_obj` does not have any exception trace information'
	)
	putil.test.assert_exception(
		obj,
		{'exh_obj':simple_exobj, '_no_print':5},
		RuntimeError,
		'Argument `_no_print` is not valid'
	)
	putil.exdoc.ExDoc(simple_exobj, depth=1, exclude=[])


def test_depth_property(simple_exobj):
	""" Test depth class property """
	obj = putil.exdoc.ExDoc(simple_exobj, _no_print=True)
	assert obj.depth is None
	obj.depth = 5
	assert obj.depth == 5
	with pytest.raises(AttributeError) as excinfo:
		del obj.depth
	assert excinfo.value.message == "can't delete attribute"


def test_exclude_property(simple_exobj):
	""" Test exclude class property """
	obj = putil.exdoc.ExDoc(simple_exobj, _no_print=True)
	assert obj.exclude is None
	obj.exclude = ['a', 'b']
	assert obj.exclude == ['a', 'b']
	with pytest.raises(AttributeError) as excinfo:
		del obj.exclude
	assert excinfo.value.message == "can't delete attribute"


def test_build_ex_tree(exdocobj):
	""" Test _build_ex_tree() method """
	with pytest.raises(RuntimeError) as excinfo:
		with putil.exdoc.ExDocCxt():
			pass
	assert excinfo.value.message == 'Exceptions database is empty'
	exobj1 = putil.exh.ExHandle(full_cname=True)
	def func1():
		exobj1.add_exception(
			'first_exception',
			TypeError,
			'This is the first exception'
		)
	func1()
	def mock_add_nodes1(self):
		raise ValueError('Illegal node name: _node_')
	def mock_add_nodes2(self):
		raise ValueError('General exception #1')
	def mock_add_nodes3(self):
		raise IOError('General exception #2')
	ref = (
		u'tests.test_exdoc.exdocobj\n'
		u'├mod.ExceptionAutoDocClass.__init__ (*)\n'
		u'│├putil.tree.Tree.__init__ (*)\n'
		u'│└putil.tree.Tree.add_nodes (*)\n'
		u'│ └putil.tree.Tree._validate_nodes_with_data (*)\n'
		u'├mod.ExceptionAutoDocClass.divide (*)\n'
		u'├mod.ExceptionAutoDocClass.multiply (*)\n'
		u'├mod.ExceptionAutoDocClass.temp(setter) (*)\n'
		u'├mod.ExceptionAutoDocClass.value1(getter) (*)\n'
		u'├mod.ExceptionAutoDocClass.value1(setter) (*)\n'
		u'├mod.ExceptionAutoDocClass.value2(setter) (*)\n'
		u'├mod.ExceptionAutoDocClass.value3(deleter) (*)\n'
		u'├mod.ExceptionAutoDocClass.value3(getter) (*)\n'
		u'├mod.ExceptionAutoDocClass.value3(setter) (*)\n'
		u'├mod.probe (*)\n'
		u'├mod.read (*)\n'
		u'├mod.write (*)\n'
		u'└tests.test_exdoc.exdocobj.multi_level_write\n'
		u' └mod.write (*)\n'
		u'  └mod._write\n'
		u'   └mod._validate_arguments (*)'
	).encode('utf-8')
	ref = ref.replace('mod.', 'tests.support.exdoc_support_module_1.')
	if str(exdocobj._tobj) != ref:
		print putil.misc.pcolor('\nActual tree:', 'yellow')
		print str(exdocobj._tobj)
		print putil.misc.pcolor('Reference tree:', 'yellow')
		print ref
	assert str(exdocobj._tobj) == ref
	trace_error_class()
	with mock.patch('putil.tree.Tree.add_nodes', side_effect=mock_add_nodes1):
		putil.test.assert_exception(
			putil.exdoc.ExDoc,
			{'exh_obj':exobj1, '_no_print':True},
			RuntimeError,
			'Exceptions do not have a common callable'
		)
	with mock.patch('putil.tree.Tree.add_nodes', side_effect=mock_add_nodes2):
		putil.test.assert_exception(
			putil.exdoc.ExDoc,
			{'exh_obj':exobj1, '_no_print':True},
			ValueError,
			'General exception #1'
		)
	with mock.patch('putil.tree.Tree.add_nodes', side_effect=mock_add_nodes3):
		putil.test.assert_exception(
			putil.exdoc.ExDoc,
			{'exh_obj':exobj1, '_no_print':True},
			IOError,
			'General exception #2'
		)
	# Create exception tree where branching is right at root node
	exobj = putil.exh.ExHandle()
	exobj._ex_dict = {
		'root/leaf1':{
			'function':'root/leaf1',
			'type':RuntimeError,
			'msg': 'Exception 1'
		},
		'root/leaf2':{
			'function':'root.leaf2',
			'type':IOError,
			'msg': 'Exception 2'
		}
	}
	exobj._callables_obj._callables_db = {
		'root':{'type':'func', 'code_id':('file', 50), 'attr':None, 'link':[]},
		'leaf1':{'type':'func', 'code_id':('file', 50), 'attr':None, 'link':[]},
		'leaf2':{'type':'func', 'code_id':('file', 60), 'attr':None, 'link':[]}
	}
	exdocobj = putil.exdoc.ExDoc(exobj, _no_print=True, _empty=True)
	exdocobj._build_ex_tree()
	assert str(exdocobj._tobj) == (
		u'root\n'
		u'├leaf1 (*)\n'
		u'└leaf2 (*)'
	).encode('utf-8')


def test_get_sphinx_doc(exdocobj):
	""" Test get_sphinx_doc() method """
	# pylint: disable=R0915
	putil.test.assert_exception(
		exdocobj.get_sphinx_doc,
		{'name':'_not_found_', 'error':True},
		RuntimeError,
		'Callable not found in exception list: _not_found_'
	)
	putil.test.assert_exception(
		exdocobj.get_sphinx_doc,
		{'name':'callable', 'depth':'hello'},
		RuntimeError,
		'Argument `depth` is not valid'
	)
	putil.test.assert_exception(
		exdocobj.get_sphinx_doc,
		{'name':'callable', 'depth':-1}
		, RuntimeError,
		'Argument `depth` is not valid'
	)
	putil.test.assert_exception(
		exdocobj.get_sphinx_doc,
		{'name':'callable', 'exclude':-1},
		RuntimeError,
		'Argument `exclude` is not valid'
	)
	putil.test.assert_exception(
		exdocobj.get_sphinx_doc,
		{'name':'callable', 'exclude':['hello', 3]},
		RuntimeError,
		'Argument `exclude` is not valid'
	)
	putil.test.assert_exception(
		exdocobj.get_sphinx_doc,
		{'name':'callable', 'width':1.0},
		RuntimeError,
		'Argument `width` is not valid'
	)
	putil.test.assert_exception(
		exdocobj.get_sphinx_doc,
		{'name':'callable', 'width':5},
		RuntimeError,
		'Argument `width` is not valid'
	)
	putil.test.assert_exception(
		exdocobj.get_sphinx_doc,
		{'name':'callable', 'error':5},
		RuntimeError,
		'Argument `error` is not valid'
	)
	minwidth = putil.exdoc._MINWIDTH
	assert exdocobj.get_sphinx_doc('_not_found_') == ''
	tstr = exdocobj.get_sphinx_doc('tests.support.exdoc_support_module_1.read')
	assert tstr == (
		'.. Auto-generated exceptions documentation for\n'
		'.. tests.support.exdoc_support_module_1.read\n'
		'\n'
		':raises: TypeError (Cannot call read)\n'
		'\n'
	)
	putil.exdoc._MINWIDTH = 16
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.read',
		width=16
	)
	assert tstr == (
		'.. Auto-\n'
		'.. generated\n'
		'.. exceptions\n'
		'.. documentation\n'
		'.. for tests.sup\n'
		'.. port.exdoc_su\n'
		'.. pport_module_\n'
		'.. 1.read\n'
		'\n'
		':raises:\n'
		' TypeError\n'
		' (Cannot call\n'
		' read)\n'
		'\n'
	)
	putil.exdoc._MINWIDTH = minwidth
	tstr = exdocobj.get_sphinx_doc('tests.support.exdoc_support_module_1.write')
	assert tstr == (
		'.. Auto-generated exceptions documentation for\n'
		'.. tests.support.exdoc_support_module_1.write'
		'\n\n:raises:\n * TypeError (Argument is not valid)'
		'\n\n * TypeError (Cannot call write)\n\n'
	)
	putil.exdoc._MINWIDTH = 16
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.write',
		width=16
	)
	assert tstr == (
		'.. Auto-\n'
		'.. generated\n'
		'.. exceptions\n'
		'.. documentation\n'
		'.. for tests.sup\n'
		'.. port.exdoc_su\n'
		'.. pport_module_\n'
		'.. 1.write\n'
		'\n'
		':raises:\n'
		' * TypeError\n'
		'   (Argument is\n'
		'   not valid)\n'
		'\n'
		' * TypeError\n'
		'   (Cannot call\n'
		'   write)\n'
		'\n'
	)
	putil.exdoc._MINWIDTH = minwidth
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.write',
		depth=1
	)
	assert tstr == (
		'.. Auto-generated exceptions documentation for\n'
		'.. tests.support.exdoc_support_module_1.write'
		'\n\n:raises: TypeError (Cannot call write)\n\n'
	)
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.ExceptionAutoDocClass.__init__',
		depth=1
	)
	assert tstr == (
		'.. Auto-generated exceptions documentation for\n'
		'.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
		'__init__\n\n:raises:\n'
		' * RuntimeError '
		'(Argument \\`node_separator\\` is not valid)\n\n '
		'* RuntimeError (Argument \\`value1\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value2\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value3\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value4\\` is not valid)\n\n'
		' * ValueError (Illegal node name: *[node_name]*)\n\n'
	)
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.ExceptionAutoDocClass.__init__',
		depth=0
	)
	assert tstr == (
		'.. Auto-generated exceptions documentation for\n'
		'.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
		'__init__\n\n'
		':raises:\n'
		' * RuntimeError (Argument \\`value1\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value2\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value3\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value4\\` is not valid)\n\n'
	)
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.ExceptionAutoDocClass.__init__',
		exclude=['putil.tree']
	)
	assert tstr == (
		'.. Auto-generated exceptions documentation for\n'
		'.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
		'__init__\n\n'
		':raises:\n'
		' * RuntimeError (Argument \\`value1\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value2\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value3\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value4\\` is not valid)\n\n'
	)
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.ExceptionAutoDocClass.__init__',
		exclude=['add_nodes', '_validate_nodes_with_data']
	)
	assert tstr == (
		'.. Auto-generated exceptions documentation for\n'
		'.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
		'__init__\n\n'
		':raises:\n'
		' * RuntimeError (Argument \\`node_separator\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value1\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value2\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value3\\` is not valid)\n\n'
		' * RuntimeError (Argument \\`value4\\` is not valid)\n\n'
	)
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.ExceptionAutoDocClass.value3'
	)
	assert tstr == (
		'.. Auto-generated exceptions documentation for\n'
		'.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
		'value3\n\n'
		':raises:\n'
		' * When assigned\n\n'
		'   * TypeError (Argument \\`value3\\` is not valid)\n\n'
		' * When deleted\n\n'
		'   * TypeError (Cannot delete value3)\n\n'
		' * When retrieved\n\n'
		'   * TypeError (Cannot get value3)\n\n'
	)
	putil.exdoc._MINWIDTH = 16
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.ExceptionAutoDocClass.value3',
		width=16
	)
	assert tstr == (
		'.. Auto-\n'
		'.. generated\n'
		'.. exceptions\n'
		'.. documentation\n'
		'.. for tests.sup\n'
		'.. port.exdoc_su\n'
		'.. pport_module_\n'
		'.. 1.ExceptionAu\n'
		'.. toDocClass.va\n'
		'.. lue3\n'
		'\n'
		':raises:\n'
		' * When assigned\n'
		'\n'
		'   * TypeError\n'
		'     (Argument\n'
		'     \\`value3\\`\n'
		'     is not\n'
		'     valid)\n'
		'\n'
		' * When deleted\n'
		'\n'
		'   * TypeError\n'
		'     (Cannot\n'
		'     delete\n'
		'     value3)\n'
		'\n'
		' * When retrieved\n'
		'\n'
		'   * TypeError\n'
		'     (Cannot get\n'
		'     value3)\n'
		'\n'
	)
	putil.exdoc._MINWIDTH = minwidth
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.ExceptionAutoDocClass.temp'
	)
	assert tstr == (
		'.. Auto-generated exceptions documentation for\n'
		'.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
		'temp\n\n'
		':raises: (when assigned) RuntimeError (Argument \\`value\\`'
		' is not\n'
		' valid)\n\n'
	)
	putil.exdoc._MINWIDTH = 16
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.ExceptionAutoDocClass.temp',
		width=16
	)
	assert tstr == (
		'.. Auto-\n'
		'.. generated\n'
		'.. exceptions\n'
		'.. documentation\n'
		'.. for tests.sup\n'
		'.. port.exdoc_su\n'
		'.. pport_module_\n'
		'.. 1.ExceptionAu\n'
		'.. toDocClass.te\n'
		'.. mp\n'
		'\n'
		':raises: (when\n'
		' assigned)\n'
		' RuntimeError\n'
		' (Argument\n'
		' \\`value\\` is\n'
		' not valid)\n'
		'\n'
	)
	putil.exdoc._MINWIDTH = minwidth
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.ExceptionAutoDocClass.value2'
	)
	assert tstr == (
		'.. Auto-generated exceptions documentation for\n'
		'.. tests.support.exdoc_support_module_1.ExceptionAutoDocClass.'
		'value2\n\n'
		':raises: (when assigned)\n\n'
		' * IOError (Argument \\`value2\\` is not a file)\n\n'
		' * TypeError (Argument \\`value2\\` is not valid)\n\n'
	)
	putil.exdoc._MINWIDTH = 16
	tstr = exdocobj.get_sphinx_doc(
		'tests.support.exdoc_support_module_1.ExceptionAutoDocClass.value2',
		width=16
	)
	assert tstr == (
		'.. Auto-\n'
		'.. generated\n'
		'.. exceptions\n'
		'.. documentation\n'
		'.. for tests.sup\n'
		'.. port.exdoc_su\n'
		'.. pport_module_\n'
		'.. 1.ExceptionAu\n'
		'.. toDocClass.va\n'
		'.. lue2\n'
		'\n'
		':raises: (when assigned)\n'
		'\n'
		' * IOError\n'
		'   (Argument\n'
		'   \\`value2\\` is\n'
		'   not a file)\n'
		'\n'
		' * TypeError\n'
		'   (Argument\n'
		'   \\`value2\\` is\n'
		'   not valid)\n'
		'\n'
	)
	putil.exdoc._MINWIDTH = minwidth


def test_get_sphinx_autodoc(exdocobj, exdocobj_single):
	""" Test get_sphinx_autodoc() method """
	mobj = sys.modules['putil.exdoc']
	delattr(mobj, 'sys')
	del sys.modules['sys']
	nsys = imp.load_module('sys_patched', *imp.find_module('sys'))
	setattr(mobj, 'sys', nsys)
	with mock.patch('putil.exdoc.sys._getframe', side_effect=mock_getframe):
		tstr = exdocobj.get_sphinx_autodoc()
		assert tstr == ''
		tstr = exdocobj.get_sphinx_autodoc()
		assert tstr == (
			'.. Auto-generated exceptions documentation for\n'
			'.. tests.support.exdoc_support_module_1.'
			'ExceptionAutoDocClass.multiply\n\n'
			':raises: ValueError (Overflow)\n\n'
		)
		tstr = exdocobj_single.get_sphinx_autodoc()
		assert tstr == (
			'.. Auto-generated exceptions documentation for\n'
			'.. tests.support.exdoc_support_module_4.func\n\n'
			':raises: TypeError (Argument \\`name\\` is not valid)\n\n'
		)


def test_copy_works(exdocobj):
	""" Test __copy__() method works """
	exdocobj.exclude = ['a', 'b', 'c']
	nobj = copy.copy(exdocobj)
	assert id(nobj) != id(exdocobj)
	assert nobj._depth == exdocobj._depth
	assert nobj._exclude == exdocobj._exclude
	assert id(nobj._exclude) != id(exdocobj._exclude)
	assert nobj._no_print == exdocobj._no_print
	assert id(nobj._exh_obj) != id(exdocobj._exh_obj)
	assert id(nobj._tobj) != id(exdocobj._tobj)
	assert nobj._module_obj_db == exdocobj._module_obj_db
	assert id(nobj._module_obj_db) != id(exdocobj._module_obj_db)


def test_exdoccxt_errors():
	""" Test that ExDocCxt context manager correctly handles exceptions """
	if putil.exh.get_exh_obj():
		putil.exh.del_exh_obj()
	with pytest.raises(IOError) as excinfo:
		with putil.exdoc.ExDocCxt(True):
			raise IOError('This is bad')
	assert excinfo.value.message == 'This is bad'
	assert putil.exh.get_exh_obj() is None


def test_exdoccxt_multiple():
	""" Emulate multiple CPU tracing """
	def func1():
		exobj = putil.exh.get_or_create_exh_obj(full_cname=True, exclude=['_pytest'])
		exobj.add_exception(
			'first_exception',
			TypeError,
			'This is the first exception'
		)
	def test_trace():
		with putil.exdoc.ExDocCxt(_no_print=True, exclude=['_pytest']) as tobj:
			tests.support.exdoc_support_module_4.func('John')
			obj1 = copy.copy(putil.exh.get_exh_obj())
			putil.exh.del_exh_obj()
			putil.exh.get_or_create_exh_obj(full_cname=True, exclude=['_pytest'])
			func1()
			obj2 = copy.copy(putil.exh.get_exh_obj())
			setattr(__builtin__, '_EXH_LIST', [obj1, obj2])
		assert tobj._exh_obj == obj1+obj2
		assert not hasattr(__builtin__, '_EXH_LIST')
		assert not hasattr(__builtin__, '_EXDOC_FULL_CNAME')
		assert not hasattr(__builtin__, '_EXDOC_EXCLUDE')
	# Test without prior exception handler
	putil.exh.del_exh_obj()
	test_trace()
	assert not hasattr(__builtin__, '_EXH')
	# Test with prior exception handler
	from putil.eng import peng
	putil.exh.get_or_create_exh_obj()
	peng(3.125, 1)
	prev_exhobj = copy.copy(putil.exh.get_exh_obj())
	test_trace()
	assert prev_exhobj == putil.exh.get_exh_obj()
