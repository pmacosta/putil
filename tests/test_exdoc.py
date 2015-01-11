# test_exdoc.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212

"""
putil.exdoc unit tests
"""

import putil.exh
import putil.test
import putil.exdoc

def test_exdoc_errors():
	""" Test exdoc data validation """
	test_list = list()
	exobj = putil.exh.ExHandle()
	def func1():	#pylint: disable=C0111,W0612
		exobj.add_exception('first_exception', TypeError, 'This is the first exception')
	func1()
	test_list.append(putil.test.trigger_exception(putil.exdoc.ExDoc, {'exh_obj':5, 'no_print':False}, TypeError, 'Argument `exh_obj` is not valid'))
	test_list.append(putil.test.trigger_exception(putil.exdoc.ExDoc, {'exh_obj':putil.exh.ExHandle(), 'no_print':False}, ValueError, 'Object of argument `exh_obj` does not have any exception trace information'))
	test_list.append(putil.test.trigger_exception(putil.exdoc.ExDoc, {'exh_obj':exobj, 'no_print':5}, TypeError, 'Argument `no_print` is not valid'))
	putil.exdoc.ExDoc(exobj, True, -1)
	assert test_list == [True]*len(test_list)

def test_build_ex_tree():
	""" Test _build_ex_tree() function """
	import exdoc_support_module_1	# pylint: disable=W0612
	exobj = putil.exdoc.ExDoc(exh_obj=putil.exh.get_exh_obj(), no_print=True, _step=0)
	putil.exh.del_exh_obj()
	assert str(exobj._tobj) == \
		u'test_exdoc.test_build_ex_tree\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.__init__ (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass._del_value3 (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass._get_value3 (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass._set_value1 (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass._set_value2 (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass._set_value3 (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.divide (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.multiply (*)\n'.encode('utf-8') + \
		u'├exdoc_support_module_1.ExceptionAutoDocClass.temp(setter) (*)\n'.encode('utf-8') + \
		u'└exdoc_support_module_2.module_enclosing_func.module_closure_func (*)'.encode('utf-8')
