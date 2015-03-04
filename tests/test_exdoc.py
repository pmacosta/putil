﻿# test_exdoc.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212

"""
putil.exdoc unit tests
"""

import sys
import mock
import copy
import pytest

import putil.exh
import putil.test
import putil.exdoc
import exdoc_support_module_1
import exdoc_support_module_3

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
	obj = exdoc_support_module_3.Class1()
	obj.value1	#pylint: disable=W0104


@pytest.fixture
def exdocobj():
	""" Trace support module class """
	if putil.exh.get_exh_obj():
		putil.exh.del_exh_obj()
	putil.exh.set_exh_obj(putil.exh.ExHandle(True))
	obj = exdoc_support_module_1.ExceptionAutoDocClass(10)
	obj.add(5)
	obj.subtract(3)
	obj.divide(5.2)
	obj.multiply(5.2)
	obj.value1 = 11
	print obj.value1
	obj.value2 = 33
	print obj.value2
	obj.value3 = 77
	print obj.value3
	del obj.value3
	obj.temp = 10
	print obj.temp
	del obj.temp
	exdoc_support_module_1.write()
	exdoc_support_module_1.read()
	exdoc_support_module_1.probe()
	obj = putil.exdoc.ExDoc(exh_obj=putil.exh.get_exh_obj(), _no_print=True)
	putil.exh.del_exh_obj()
	return obj


@pytest.fixture
def simple_exobj():	#pylint: disable=R0914
	""" Create simple exception handler for miscellaneous property tests """
	exobj = putil.exh.ExHandle(True)
	def func1():	#pylint: disable=C0111,W0612
		exobj.add_exception('first_exception', TypeError, 'This is the first exception')
	func1()
	return exobj

def test_exdoc_errors(simple_exobj):	#pylint: disable=W0621
	""" Test exdoc data validation """
	obj = putil.exdoc.ExDoc
	putil.test.assert_exception(obj, {'exh_obj':5, '_no_print':False}, TypeError, 'Argument `exh_obj` is not valid')
	putil.test.assert_exception(obj, {'exh_obj':simple_exobj, 'depth':'hello'}, TypeError, 'Argument `depth` is not valid')
	putil.test.assert_exception(obj, {'exh_obj':simple_exobj, 'depth':-1}, TypeError, 'Argument `depth` is not valid')
	putil.test.assert_exception(obj, {'exh_obj':simple_exobj, 'exclude':-1}, TypeError, 'Argument `exclude` is not valid')
	putil.test.assert_exception(obj, {'exh_obj':simple_exobj, 'exclude':['hello', 3]}, TypeError, 'Argument `exclude` is not valid')
	putil.test.assert_exception(obj, {'exh_obj':putil.exh.ExHandle(True), '_no_print':False}, ValueError, 'Object of argument `exh_obj` does not have any exception trace information')
	putil.test.assert_exception(obj, {'exh_obj':simple_exobj, '_no_print':5}, TypeError, 'Argument `_no_print` is not valid')
	putil.exdoc.ExDoc(simple_exobj, depth=1, exclude=[])


def test_depth_property(simple_exobj):	#pylint: disable=W0621
	""" Test depth class property """
	obj = putil.exdoc.ExDoc(simple_exobj, _no_print=True)
	assert obj.depth == None
	obj.depth = 5
	assert obj.depth == 5
	with pytest.raises(AttributeError) as excinfo:
		del obj.depth
	assert excinfo.value.message == "can't delete attribute"


def test_exclude_property(simple_exobj):	#pylint: disable=W0621
	""" Test exclude class property """
	obj = putil.exdoc.ExDoc(simple_exobj, _no_print=True)
	assert obj.exclude == None
	obj.exclude = ['a', 'b']
	assert obj.exclude == ['a', 'b']
	with pytest.raises(AttributeError) as excinfo:
		del obj.exclude
	assert excinfo.value.message == "can't delete attribute"


def test_build_ex_tree(exdocobj):	#pylint: disable=W0621
	""" Test _build_ex_tree() method """
	exobj1 = putil.exh.ExHandle(True)
	def func1():	#pylint: disable=C0111,W0612
		exobj1.add_exception('first_exception', TypeError, 'This is the first exception')
	func1()
	def mock_add_nodes1(self):	#pylint: disable=C0111,W0613
		raise ValueError('Illegal node name: _node_')
	def mock_add_nodes2(self):	#pylint: disable=C0111,W0613
		raise ValueError('General exception #1')
	def mock_add_nodes3(self):	#pylint: disable=C0111,W0613
		raise IOError('General exception #2')
	assert str(exdocobj._tobj) == \
		u'test_exdoc.exdocobj\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.__init__ (*)\n'.encode('utf-8') + \
		u'│├putil.tree.Tree.__init__ (*)\n'.encode('utf-8') + \
		u'│└putil.tree.Tree.add_nodes (*)\n'.encode('utf-8') + \
		u'│ └putil.tree.Tree._validate_nodes_with_data (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.divide (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.multiply (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.temp[fset] (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.value1[fget] (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.value1[fset] (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.value2[fset] (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.value3[fdel] (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.value3[fget] (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.value3[fset] (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.probe (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.read (*)\n'.encode('utf-8') + \
		u'└exdoc_support_module_1.write (*)\n'.encode('utf-8') + \
		u' └exdoc_support_module_1._write\n'.encode('utf-8') + \
		u'  └exdoc_support_module_1._validate_arguments (*)'.encode('utf-8')
	trace_error_class()
	exobj2 = putil.exh.get_exh_obj()
	putil.test.assert_exception(putil.exdoc.ExDoc, {'exh_obj':exobj2, '_no_print':True}, RuntimeError, 'Functions performing actions for multiple properties not supported')
	with mock.patch('putil.tree.Tree.add_nodes', side_effect=mock_add_nodes1):
		putil.test.assert_exception(putil.exdoc.ExDoc, {'exh_obj':exobj1, '_no_print':True}, RuntimeError, 'Exceptions do not have a common callable')
	with mock.patch('putil.tree.Tree.add_nodes', side_effect=mock_add_nodes2):
		putil.test.assert_exception(putil.exdoc.ExDoc, {'exh_obj':exobj1, '_no_print':True}, ValueError, 'General exception #1')
	with mock.patch('putil.tree.Tree.add_nodes', side_effect=mock_add_nodes3):
		putil.test.assert_exception(putil.exdoc.ExDoc, {'exh_obj':exobj1, '_no_print':True}, IOError, 'General exception #2')

def test_get_sphinx_doc(exdocobj):	#pylint: disable=W0621
	""" Test get_sphinx_doc() method """
	putil.test.assert_exception(exdocobj.get_sphinx_doc, {'name':'_not_found_'}, RuntimeError, 'Callable not found in exception list: _not_found_')
	putil.test.assert_exception(exdocobj.get_sphinx_doc, {'name':'callable', 'depth':'hello'}, TypeError, 'Argument `depth` is not valid')
	putil.test.assert_exception(exdocobj.get_sphinx_doc, {'name':'callable', 'depth':-1}, TypeError, 'Argument `depth` is not valid')
	putil.test.assert_exception(exdocobj.get_sphinx_doc, {'name':'callable', 'exclude':-1}, TypeError, 'Argument `exclude` is not valid')
	putil.test.assert_exception(exdocobj.get_sphinx_doc, {'name':'callable', 'exclude':['hello', 3]}, TypeError, 'Argument `exclude` is not valid')
	tstr = exdocobj.get_sphinx_doc('exdoc_support_module_1.read')
	assert tstr == ':raises: TypeError (Cannot call read)'
	tstr = exdocobj.get_sphinx_doc('exdoc_support_module_1.write')
	assert tstr == ':raises:\n * TypeError (Argument is not valid)\n\n * TypeError (Cannot call write)'
	tstr = exdocobj.get_sphinx_doc('exdoc_support_module_1.write', depth=1)
	assert tstr == ':raises: TypeError (Cannot call write)'
	tstr = exdocobj.get_sphinx_doc('exdoc_support_module_1.ExceptionAutoDocClass.__init__', depth=1)
	assert tstr == ':raises:\n * RuntimeError (Argument `node_separator` is not valid)\n\n * RuntimeError (Argument `value1` is not valid)\n\n * RuntimeError (Argument `value2` is not valid)\n\n'+\
					' * RuntimeError (Argument `value3` is not valid)\n\n * RuntimeError (Argument `value4` is not valid)\n\n * ValueError (Illegal node name: *[node_name]*)'
	tstr = exdocobj.get_sphinx_doc('exdoc_support_module_1.ExceptionAutoDocClass.__init__', depth=0)
	assert tstr == ':raises:\n * RuntimeError (Argument `value1` is not valid)\n\n * RuntimeError (Argument `value2` is not valid)\n\n * RuntimeError (Argument `value3` is not valid)\n\n'+\
					' * RuntimeError (Argument `value4` is not valid)'
	tstr = exdocobj.get_sphinx_doc('exdoc_support_module_1.ExceptionAutoDocClass.__init__', exclude=['putil.tree'])
	assert tstr == ':raises:\n * RuntimeError (Argument `value1` is not valid)\n\n * RuntimeError (Argument `value2` is not valid)\n\n * RuntimeError (Argument `value3` is not valid)\n\n'+\
					' * RuntimeError (Argument `value4` is not valid)'
	tstr = exdocobj.get_sphinx_doc('exdoc_support_module_1.ExceptionAutoDocClass.__init__', exclude=['add_nodes', '_validate_nodes_with_data'])
	assert tstr == ':raises:\n * RuntimeError (Argument `node_separator` is not valid)\n\n * RuntimeError (Argument `value1` is not valid)\n\n * RuntimeError (Argument `value2` is not valid)\n\n'+\
					' * RuntimeError (Argument `value3` is not valid)\n\n * RuntimeError (Argument `value4` is not valid)'
	tstr = exdocobj.get_sphinx_doc('exdoc_support_module_1.ExceptionAutoDocClass.value3')
	assert tstr == ':raises:\n * When assigned\n\n   * TypeError (Argument `value3` is not valid)\n\n * When deleted\n\n   * TypeError (Cannot delete value3)\n\n * When retrieved\n\n   * TypeError (Cannot get value3)'
	tstr = exdocobj.get_sphinx_doc('exdoc_support_module_1.ExceptionAutoDocClass.temp')
	assert tstr == ':raises: (when assigned) RuntimeError (Argument `value` is not valid)'
	tstr = exdocobj.get_sphinx_doc('exdoc_support_module_1.ExceptionAutoDocClass.value2')
	assert tstr == ':raises: (when assigned)\n * IOError (Argument `value2` is not a file)\n\n * TypeError (Argument `value2` is not valid)'

def test_copy_works(exdocobj):	#pylint: disable=W0621
	""" Test __copy__() method works """
	exdocobj.exclude = ['a', 'b', 'c']
	nobj = copy.copy(exdocobj)
	assert id(nobj) != id(exdocobj)
	assert nobj._depth == exdocobj._depth
	assert (nobj._exclude == exdocobj._exclude) and (id(nobj._exclude) != id(exdocobj._exclude))
	assert nobj._no_print == exdocobj._no_print
