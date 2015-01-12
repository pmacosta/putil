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
	test_list = list()
	exobj = putil.exh.ExHandle()
	def func1():	#pylint: disable=C0111,W0612
		exobj.add_exception('first_exception', TypeError, 'This is the first exception')
	func1()
	obj = putil.exdoc.ExDoc
	test_list.append(putil.test.trigger_exception(obj, {'exh_obj':5, 'no_print':False, 'trace_name':'hello'}, TypeError, 'Argument `exh_obj` is not valid'))
	test_list.append(putil.test.trigger_exception(obj, {'exh_obj':putil.exh.ExHandle(), 'no_print':False, 'trace_name':'hello'}, ValueError, 'Object of argument `exh_obj` does not have any exception trace information'))
	test_list.append(putil.test.trigger_exception(obj, {'exh_obj':exobj, 'no_print':5, 'trace_name':'hello'}, TypeError, 'Argument `no_print` is not valid'))
	test_list.append(putil.test.trigger_exception(obj, {'exh_obj':exobj, 'no_print':False, 'trace_name':5}, TypeError, 'Argument `trace_name` is not valid'))
	putil.exdoc.ExDoc(exobj, True, 'hello', -1)
	assert test_list == [True]*len(test_list)

def test_build_ex_tree():
	""" Test _build_ex_tree() function """
	test_list = list()
	trace_class()
	exdocobj = putil.exdoc.ExDoc(exh_obj=putil.exh.get_exh_obj(), no_print=True, trace_name='exdoc_support_module_1.ExceptionAutoDocClass', _step=0)
	putil.exh.del_exh_obj()
	test_list.append(str(exdocobj._tobj) == \
		u'exdoc_support_module_1.ExceptionAutoDocClass\n'.encode('utf-8') + \
		u'├__init__ (*)\n'.encode('utf-8') + \
		u'├divide (*)\n'.encode('utf-8') + \
		u'├multiply (*)\n'.encode('utf-8') + \
		u'├temp[fset] (*)\n'.encode('utf-8') + \
		u'├value1[fget] (*)\n'.encode('utf-8') + \
		u'├value1[fset] (*)\n'.encode('utf-8') + \
		u'├value2[fset] (*)\n'.encode('utf-8') + \
		u'├value3[fdel] (*)\n'.encode('utf-8') + \
		u'├value3[fget] (*)\n'.encode('utf-8') + \
		u'└value3[fset] (*)'.encode('utf-8'))
	trace_module_functions()
	exdocobj = putil.exdoc.ExDoc(exh_obj=putil.exh.get_exh_obj(), no_print=True, trace_name='exdoc_support_module_1', _step=0)
	putil.exh.del_exh_obj()
	test_list.append(str(exdocobj._tobj) == \
		u'exdoc_support_module_1\n'.encode('utf-8') + \
		u'├probe (*)\n'.encode('utf-8') + \
		u'├read (*)\n'.encode('utf-8') + \
		u'└write (*)\n'.encode('utf-8') + \
		u' └exdoc_support_module_1._write\n'.encode('utf-8') + \
		u'  └exdoc_support_module_1._validate_arguments (*)'.encode('utf-8'))
	assert test_list == [True]*len(test_list)
