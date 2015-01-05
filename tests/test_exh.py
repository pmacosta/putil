# test_exh.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212

"""
putil.exh unit tests
"""

import copy
import mock
import pytest

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

def test_ex_type_str():
	""" test _ex_type_str() function """
	test_list = list()
	test_list.append(putil.exh._ex_type_str(RuntimeError) == 'RuntimeError')
	test_list.append(putil.exh._ex_type_str(IOError) == 'IOError')
	assert test_list == [True]*len(test_list)

def test_add_exception_errors():
	""" Test add_exception() function errors """
	def mock_get_code_id(obj):	#pylint: disable=W0612,W0613
		""" Return unique identity tuple to individualize callable object """
		return None
	test_list = list()
	obj = putil.exh.ExHandle()
	test_list.append(putil.test.trigger_exception(obj.add_exception, {'exname':5, 'extype':RuntimeError, 'exmsg':'Message'}, TypeError, 'Argument `exname` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.add_exception, {'exname':'exception', 'extype':5, 'exmsg':'Message'}, TypeError, 'Argument `extype` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.add_exception, {'exname':'exception', 'extype':RuntimeError, 'exmsg':True}, TypeError, 'Argument `exmsg` is not valid'))
	# These should not raise an exception
	obj = putil.exh.ExHandle()
	obj.add_exception(exname='exception name', extype=RuntimeError, exmsg='exception message for exception #1')
	obj.add_exception(exname='exception name', extype=TypeError, exmsg='exception message for exception #2')
	# Test case where callable is not found in callable database
	with mock.patch('putil.exh._get_code_id') as mock_get_code_id:
		test_list.append(putil.test.trigger_exception(obj.add_exception, {'exname':'exception name', 'extype':RuntimeError, 'exmsg':'exception message for exception #1'}, RuntimeError, 'Callable full name could not be obtained'))
	assert test_list == [True]*len(test_list)

def test_add_exception_works():
	""" Test add_exception() function works """
	test_list = list()
	exobj = putil.exh.ExHandle()
	def func1():	#pylint: disable=C0111,W0612
		exobj.add_exception('first_exception', TypeError, 'This is the first exception')
		print "Hello"
	def func2():	#pylint: disable=C0111,W0612
		exobj.add_exception('second_exception', ValueError, 'This is the second exception')
		exobj.add_exception('third_exception', IOError, 'This is the third exception')
		print "World"
	func1()
	func2()
	cdb = exobj._ex_dict
	if not cdb:
		assert False
	for exname in cdb:
		erec = cdb[exname]
		if exname.endswith('test_exh.test_add_exception_works.func1.first_exception'):
			test_list.append(erec['function'].endswith('test_exh.test_add_exception_works.func1') and (erec['type'] == TypeError) and (erec['msg'] == 'This is the first exception') and (erec['checked'] == False))
		elif exname.endswith('test_exh.test_add_exception_works.func2.second_exception'):
			test_list.append(erec['function'].endswith('test_exh.test_add_exception_works.func2') and (erec['type'] == ValueError) and (erec['msg'] == 'This is the second exception') and (erec['checked'] == False))
		elif exname.endswith('test_exh.test_add_exception_works.func2.third_exception'):
			test_list.append(erec['function'].endswith('test_exh.test_add_exception_works.func2') and (erec['type'] == IOError) and (erec['msg'] == 'This is the third exception') and (erec['checked'] == False))
		else:
			test_list.append(False)
	assert test_list == [True]*len(test_list)

def test_raise_exception():
	""" Test raise_exception_if() function errors """
	test_list = list()
	obj = putil.exh.ExHandle()
	def func3(cond1=False, cond2=False, cond3=False, cond4=False):	#pylint: disable=C0111,W0612
		exobj = putil.exh.ExHandle()
		exobj.add_exception('my_exception1', RuntimeError, 'This is an exception')
		exobj.add_exception('my_exception2', IOError, 'This is an exception with a *[file_name]* field')
		exobj.raise_exception_if('my_exception1', cond1, edata=None)
		exobj.raise_exception_if('my_exception2', cond2, edata={'field':'file_name', 'value':'my_file.txt'})
		if cond3:
			exobj.raise_exception_if('my_exception3', False)
		if cond4:
			exobj.raise_exception_if('my_exception2', cond4, edata={'field':'not_a_field', 'value':'my_file.txt'})
		return exobj
	test_list.append(putil.test.trigger_exception(obj.raise_exception_if, {'exname':5, 'condition':False}, TypeError, 'Argument `exname` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.raise_exception_if, {'exname':'my_exception', 'condition':5}, TypeError, 'Argument `condition` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.raise_exception_if, {'exname':'my_exception', 'condition':False, 'edata':354}, TypeError, 'Argument `edata` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.raise_exception_if, {'exname':'my_exception', 'condition':False, 'edata':{'field':'my_field'}}, TypeError, 'Argument `edata` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.raise_exception_if, {'exname':'my_exception', 'condition':False, 'edata':{'field':3, 'value':5}}, TypeError, 'Argument `edata` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.raise_exception_if, {'exname':'my_exception', 'condition':False, 'edata':{'value':5}}, TypeError, 'Argument `edata` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.raise_exception_if, {'exname':'my_exception', 'condition':False, 'edata':[{'field':'my_field1', 'value':5}, {'field':'my_field'}]}, TypeError, 'Argument `edata` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.raise_exception_if, {'exname':'my_exception', 'condition':False, 'edata':[{'field':'my_field1', 'value':5}, {'field':3, 'value':5}]}, TypeError, 'Argument `edata` is not valid'))
	test_list.append(putil.test.trigger_exception(obj.raise_exception_if, {'exname':'my_exception', 'condition':False, 'edata':[{'field':'my_field1', 'value':5}, {'value':5}]}, TypeError, 'Argument `edata` is not valid'))
	test_list.append(putil.test.trigger_exception(func3, {'cond1':True, 'cond2':False}, RuntimeError, 'This is an exception'))
	test_list.append(putil.test.trigger_exception(func3, {'cond2':True}, IOError, 'This is an exception with a my_file.txt field'))
	test_list.append(putil.test.trigger_exception(func3, {'cond3':True}, ValueError, 'Exception name my_exception3 not found'))
	test_list.append(putil.test.trigger_exception(func3, {'cond4':True}, RuntimeError, 'Field not_a_field not in exception message'))
	exobj = func3()	# Test that edata=None works
	cdb = exobj._ex_dict
	if not cdb:
		assert False
	for exname, erec in cdb.items():
		if exname.endswith('test_exh.test_raise_exception.func3.my_exception1'):
			test_list.append(erec['function'].endswith('test_exh.test_raise_exception.func3') and (erec['type'] == RuntimeError) and (erec['msg'] == 'This is an exception') and (erec['checked'] == True))
		if exname.endswith('test_exh.test_raise_exception.func3.my_exception2'):
			test_list.append(erec['function'].endswith('test_exh.test_raise_exception.func3') and (erec['type'] == IOError) and (erec['msg'] == 'This is an exception with a *[file_name]* field') and (erec['checked'] == True))
	assert test_list == [True]*len(test_list)

def test_exceptions_db():
	""" Test _exceptions_db() property """
	# Functions definitions
	def func4(exobj):	#pylint: disable=C0111,W0612
		exobj.add_exception('my_exception1', RuntimeError, 'This is exception #1')
	def func5(exobj):	#pylint: disable=C0111,W0612
		exobj.add_exception('my_exception2', ValueError, 'This is exception #2, *[result]*')
		exobj.add_exception('my_exception3', TypeError, 'This is exception #3')
	exobj = putil.exh.ExHandle()
	func4(exobj)
	func5(exobj)
	# Actual tests
	# Test that property cannot be deleted
	with pytest.raises(AttributeError) as excinfo:
		del exobj.exceptions_db
	test_list = list()
	test_list.append(excinfo.value.message == "can't delete attribute")
	# Test contents
	tdata_in = exobj.exceptions_db
	if (not tdata_in) or (len(tdata_in) != 3):
		assert False
	tdata_out = list()
	for erec in tdata_in:
		if erec['name'].endswith('test_exh.test_exceptions_db.func4'):
			name = 'test_exh.test_exceptions_db.func4'
		elif erec['name'].endswith('test_exh.test_exceptions_db.func5'):
			name = 'test_exh.test_exceptions_db.func5'
		tdata_out.append({'name':name, 'data':erec['data']})
	test_list.append(sorted(tdata_out) == sorted([{'name':'test_exh.test_exceptions_db.func4', 'data':'RuntimeError (This is exception #1)'},
											      {'name':'test_exh.test_exceptions_db.func5', 'data':'ValueError (This is exception #2, *[result]*)'},
		                                          {'name':'test_exh.test_exceptions_db.func5', 'data':'TypeError (This is exception #3)'}]))
	#
	assert test_list == [True]*len(test_list)

def test_callables_db():
	""" Test callables_db property """
	# Function definitions
	def func6(exobj):	#pylint: disable=C0111,W0612
		exobj.add_exception('my_exception', RuntimeError, 'This is an exception')
		return exobj
	# Actual tests
	exobj = func6(putil.exh.ExHandle())
	# Actual contents of what is returned should be checked in pinspect module
	test_list = list()
	test_list.append(exobj.callables_db is not None)
	# Test that property cannot be deleted
	with pytest.raises(AttributeError) as excinfo:
		del exobj.callables_db
	test_list.append(excinfo.value.message == "can't delete attribute")
	#
	assert test_list == [True]*len(test_list)

def test_str():
	""" Test str() function """
	# Functions definition
	def func7(exobj):	#pylint: disable=C0111,W0612
		exobj.add_exception('my_exception7', RuntimeError, 'This is exception #7')
		exobj.raise_exception_if('my_exception7', False)
	def func8(exobj):	#pylint: disable=C0111,W0612
		exobj.add_exception('my_exception8', ValueError, 'This is exception #8, *[fname]*')
		exobj.add_exception('my_exception9', TypeError, 'This is exception #9')
	exobj = putil.exh.ExHandle()
	func7(exobj)
	func8(exobj)
	# Actual tests
	str_in = str(exobj).split('\n\n')
	str_out = list()
	for str_element in str_in:
		str_list = str_element.split('\n')
		if str_list[0].endswith('test_exh.test_str.func7.my_exception7'):
			str_list[0] = 'Name....: test_exh.test_str.func7.my_exception7'
		elif str_list[0].endswith('test_exh.test_str.func8.my_exception8'):
			str_list[0] = 'Name....: test_exh.test_str.func8.my_exception8'
		elif str_list[0].endswith('test_exh.test_str.func8.my_exception9'):
			str_list[0] = 'Name....: test_exh.test_str.func8.my_exception9'
		if str_list[1].endswith('test_exh.test_str.func7'):
			str_list[1] = 'Function: test_exh.test_str.func7'
		elif str_list[1].endswith('test_exh.test_str.func8'):
			str_list[1] = 'Function: test_exh.test_str.func8'
		str_out.append('\n'.join(str_list))
	#
	str_check = list()
	str_check.append('Name....: test_exh.test_str.func7.my_exception7\nFunction: test_exh.test_str.func7\nType....: RuntimeError\nMessage.: This is exception #7\nChecked.: True')
	str_check.append('Name....: test_exh.test_str.func8.my_exception8\nFunction: test_exh.test_str.func8\nType....: ValueError\nMessage.: This is exception #8, *[fname]*\nChecked.: False')
	str_check.append('Name....: test_exh.test_str.func8.my_exception9\nFunction: test_exh.test_str.func8\nType....: TypeError\nMessage.: This is exception #9\nChecked.: False')
	assert sorted(str_out) == sorted(str_check)

def test_copy():
	""" Test __copy__() magic method """
	# Functions definition
	def funca(exobj):	#pylint: disable=C0111,W0612
		exobj.add_exception('my_exceptionA', RuntimeError, 'This is exception #A')
	def funcb(exobj):	#pylint: disable=C0111,W0612
		exobj.add_exception('my_exceptionB', ValueError, 'This is exception #B')
		exobj.add_exception('my_exceptionC', TypeError, 'This is exception #C')
	source_obj = putil.exh.ExHandle()
	funca(source_obj)
	funcb(source_obj)
	# Actual tests
	dest_obj = copy.copy(source_obj)
	test_list = list()
	test_list.append((source_obj._ex_dict == dest_obj._ex_dict) and (id(source_obj._ex_dict) != id(dest_obj._ex_dict)))
	test_list.append((source_obj._callables_obj == dest_obj._callables_obj) and (id(source_obj._callables_obj) != id(dest_obj._callables_obj)))
	assert test_list == [True]*len(test_list)
