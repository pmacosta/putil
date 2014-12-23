# test_exh.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212

"""
putil.exh unit tests
"""

import putil.exh
import putil.test

def test_star_exh_obj():
	""" Test [get|set|del]_exh_obj() function """
	putil.exh.set_exh_obj('Test global variable')
	test_list = list()
	test_list.append(putil.exh.get_exh_obj() == 'Test global variable')
	putil.exh.del_exh_obj()
	test_list.append(putil.exh.get_exh_obj() == None)
	assert test_list == len(test_list)*[True]

def test_add_exception_errors():
	""" Test add_exception() function errors """
	test_list = list()
	obj = putil.exh.ExHandle()
	test_list.append(putil.test.trigger_exception(obj.add_exception, {'exname':5, 'extype':RuntimeError, 'exmsg':'Message'}, TypeError, 'Argument `exname` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.add_exception, {'exname':'exception', 'extype':5, 'exmsg':'Message'}, TypeError, 'Argument `extype` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.add_exception, {'exname':'exception', 'extype':RuntimeError, 'exmsg':True}, TypeError, 'Argument `exmsg` is not valid'))
	# This should not raise an exception
	obj = putil.exh.ExHandle()
	obj.add_exception(exname='exception name', extype=RuntimeError, exmsg='exception message for exception #1')
	obj.add_exception(exname='exception name', extype=TypeError, exmsg='exception message for exception #2')
	#test_list.append(obj._ex_list == {'name':'exception name', 'type':TypeError, 'msg':'exception message for exception #2', 'checked':False})
	assert test_list == [True]*len(test_list)
