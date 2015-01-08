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
