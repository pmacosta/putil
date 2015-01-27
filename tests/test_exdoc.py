# test_exdoc.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212

"""
putil.exdoc unit tests
"""

import sys

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
	putil.exh.set_exh_obj(putil.exh.ExHandle())
	obj = exdoc_support_module_3.Class1()
	obj.value1	#pylint: disable=W0104

def trace_class():
	""" Trace support module class """
	if putil.exh.get_exh_obj():
		putil.exh.del_exh_obj()
	putil.exh.set_exh_obj(putil.exh.ExHandle())
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

def trace_module_functions():
	""" Trace support module class """
	if putil.exh.get_exh_obj():
		putil.exh.del_exh_obj()
	putil.exh.set_exh_obj(putil.exh.ExHandle())
	exdoc_support_module_1.write()
	exdoc_support_module_1.read()
	exdoc_support_module_1.probe()

def test_exdoc_errors():
	""" Test exdoc data validation """
	exobj = putil.exh.ExHandle()
	def func1():	#pylint: disable=C0111,W0612
		exobj.add_exception('first_exception', TypeError, 'This is the first exception')
	func1()
	obj = putil.exdoc.ExDoc
	putil.test.assert_exception(obj, {'exh_obj':5, 'no_print':False, 'trace_name':'hello'}, TypeError, 'Argument `exh_obj` is not valid')
	putil.test.assert_exception(obj, {'exh_obj':putil.exh.ExHandle(), 'no_print':False, 'trace_name':'hello'}, ValueError, 'Object of argument `exh_obj` does not have any exception trace information')
	putil.test.assert_exception(obj, {'exh_obj':exobj, 'no_print':5, 'trace_name':'hello'}, TypeError, 'Argument `no_print` is not valid')
	putil.test.assert_exception(obj, {'exh_obj':exobj, 'no_print':False, 'trace_name':5}, TypeError, 'Argument `trace_name` is not valid')
	putil.exdoc.ExDoc(exobj, True, 'hello', -1)

def test_build_ex_tree():
	""" Test _build_ex_tree() function """
	trace_class()
	exdocobj = putil.exdoc.ExDoc(exh_obj=putil.exh.get_exh_obj(), no_print=True, trace_name='exdoc_support_module_1.ExceptionAutoDocClass', _step=0)
	putil.exh.del_exh_obj()
	assert str(exdocobj._tobj) == \
		u'exdoc_support_module_1.ExceptionAutoDocClass\n'.encode('utf-8') + \
		u'├__init__ (*)\n'.encode('utf-8') + \
		u'│├putil.tree.Tree.__init__ (*)\n'.encode('utf-8') + \
		u'│└putil.tree.Tree.add_nodes (*)\n'.encode('utf-8') + \
		u'│ └putil.tree.Tree._validate_nodes_with_data (*)\n'.encode('utf-8') + \
		u'├divide (*)\n'.encode('utf-8') + \
		u'├multiply (*)\n'.encode('utf-8') + \
		u'├temp[fset] (*)\n'.encode('utf-8') + \
		u'├value1[fget] (*)\n'.encode('utf-8') + \
		u'├value1[fset] (*)\n'.encode('utf-8') + \
		u'├value2[fset] (*)\n'.encode('utf-8') + \
		u'├value3[fdel] (*)\n'.encode('utf-8') + \
		u'├value3[fget] (*)\n'.encode('utf-8') + \
		u'└value3[fset] (*)'.encode('utf-8')
	trace_module_functions()
	exdocobj = putil.exdoc.ExDoc(exh_obj=putil.exh.get_exh_obj(), no_print=True, trace_name='exdoc_support_module_1', _step=0)
	putil.exh.del_exh_obj()
	assert str(exdocobj._tobj) == \
		u'exdoc_support_module_1\n'.encode('utf-8') + \
		u'├probe (*)\n'.encode('utf-8') + \
		u'├read (*)\n'.encode('utf-8') + \
		u'└write (*)\n'.encode('utf-8') + \
		u' └exdoc_support_module_1._write\n'.encode('utf-8') + \
		u'  └exdoc_support_module_1._validate_arguments (*)'.encode('utf-8')
	trace_error_class()
	exobj = putil.exh.get_exh_obj()
	putil.test.assert_exception(putil.exdoc.ExDoc, {'exh_obj':exobj, 'trace_name':'exdoc_support_module_3', 'no_print':True, '_step':0}, RuntimeError, 'Functions performing actions for multiple properties not supported')

def test_create_ex_table():
	""" Test _create_ex_table() function """
	trace_module_functions()
	exdocobj = putil.exdoc.ExDoc(exh_obj=putil.exh.get_exh_obj(), no_print=False, trace_name='exdoc_support_module_1', _step=1)
	empty_entry = {'native_exceptions':[], 'flat_exceptions':[], 'cross_hierarchical_exceptions':[], 'cross_flat_exceptions':[], 'cross_names':[]}
	ref_table = dict()
	ref_table['probe'] = empty_entry
	ref_table['probe']['native_exceptions'] = ref_table['probe']['flat_exceptions'] = ['TypeError (Cannot call probe)']
	ref_table['read'] = empty_entry
	ref_table['read']['native_exceptions'] = ref_table['read']['flat_exceptions'] = ['TypeError (Cannot call read)']
	ref_table['write'] = empty_entry
	ref_table['write']['native_exceptions'] = ['TypeError (Cannot call write)']
	ref_table['write']['flat_exceptions'] = sorted(['TypeError (Cannot call write)', 'TypeError (Argument is not valid)'])
	ref_table['exdoc_support_module_1._validate_arguments'] = empty_entry
	ref_table['exdoc_support_module_1._validate_arguments']['native_exceptions'] = ['TypeError (Argument is not valid)']
	ref_table['exdoc_support_module_1._validate_arguments']['flat_exceptions'] = ['TypeError (Argument is not valid)']
	putil.exh.del_exh_obj()
	print exdocobj._extable
	assert exdocobj._extable == ref_table

