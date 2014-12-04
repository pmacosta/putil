# test_pcontracts.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212

"""
putil.pcontracts unit tests
"""
import sys
import copy
import pytest
import functools

import putil.exh
import putil.test
import putil.pcontracts	#pylint: disable=W0611

_ORIGINAL_CUSTOM_CONTRACTS = copy.deepcopy(putil.pcontracts._CUSTOM_CONTRACTS)

def sample_func_global():
	""" Global test function to test get_exdesc() function """
	tmp_global = putil.pcontracts.get_exdesc()
	return tmp_global

def test_get_exdesc():
	""" Test get_exdesc() function """
	def sample_func_local():
		""" Local test function to test get_exdesc() function """
		tmp_local = putil.pcontracts.get_exdesc()
		return tmp_local
	test_list = list()
	sample_func_local.exdesc = 'Test local function property'
	sample_func_global.exdesc = 'Test global function property'
	test_list.append(sample_func_local() == 'Test local function property')
	test_list.append(sample_func_global() == 'Test global function property')
	del globals()['sample_func_global']
	test_list.append(putil.test.trigger_exception(putil.pcontracts.get_exdesc, {}, RuntimeError, 'Function object could not be found for function `trigger_exception`'))
	assert test_list == len(test_list)*[True]


def test_get_replacement_token():
	""" Test _get_replacement_token() function """
	test_list = list()
	test_list.append(putil.pcontracts._get_replacement_token('Argument `*[argument_name]*` could not be found') == 'argument_name')
	test_list.append(putil.pcontracts._get_replacement_token('Argument `*file_name*` could not be found') == None)
	assert test_list == len(test_list)*[True]


def test_format_arg_errors():
	""" Test _format_arg() function exceptions """
	exdesc = list()
	exdesc.append(({'arg':''}, ValueError, 'Empty custom contract exception message'))
	exdesc.append(({'arg':[RuntimeError, '']}, ValueError, 'Empty custom contract exception message'))
	exdesc.append(({'arg':['', RuntimeError]}, ValueError, 'Empty custom contract exception message'))
	exdesc.append(({'arg':['']}, ValueError, 'Empty custom contract exception message'))
	exdesc.append(({'arg':set([RuntimeError, 'Message'])}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':[]}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':(RuntimeError, 'Message', 3)}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':[3]}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':['a', 3]}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':[3, 'a']}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':[ValueError, 3]}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':[3, ValueError]}, TypeError, 'Illegal custom contract exception definition'))
	putil.test.evaluate_exception_series(exdesc, putil.pcontracts._format_arg)


def test_format_arg_works():
	""" Test _format_arg() function """
	fobj = putil.pcontracts._format_arg
	test_list = list()
	test_list.append(cmp(fobj('Message'), {'msg':'Message', 'type':RuntimeError}) == 0)
	test_list.append(cmp(fobj(IOError), {'msg':'Argument `*[argument_name]*` is not valid', 'type':IOError}) == 0)
	test_list.append(cmp(fobj((ValueError, 'Description 1')), {'msg':'Description 1', 'type':ValueError}) == 0)
	test_list.append(cmp(fobj(('Description 2', TypeError)), {'msg':'Description 2', 'type':TypeError}) == 0)
	assert test_list == len(test_list)*[True]


def test_parse_new_contract_args():
	""" Test _parse_new_contract_args() function """
	fobj = putil.pcontracts._parse_new_contract_args
	test_list = list()
	# Validate *args
	with pytest.raises(TypeError) as excinfo:
		fobj('Desc1', file_not_found='Desc2')
	test_list.append(excinfo.value.message == 'Illegal custom contract exception definition')
	with pytest.raises(TypeError) as excinfo:
		fobj('Desc1', 'Desc2')
	test_list.append(excinfo.value.message == 'Illegal custom contract exception definition')
	with pytest.raises(TypeError) as excinfo:
		fobj(5)
	test_list.append(excinfo.value.message == 'Illegal custom contract exception definition')
	# Normal behavior
	test_list.append(fobj() == [{'name':'argument_invalid', 'msg':'Argument `*[argument_name]*` is not valid', 'type':RuntimeError}])
	test_list.append(fobj('Desc') == [{'name':'default', 'msg':'Desc', 'type':RuntimeError}])
	test_list.append(fobj(IOError) == [{'name':'default', 'msg':'Argument `*[argument_name]*` is not valid', 'type':IOError}])
	test_list.append(fobj(('a', )) == [{'name':'default', 'msg':'a', 'type':RuntimeError}])
	test_list.append(fobj((IOError, )) == [{'name':'default', 'msg':'Argument `*[argument_name]*` is not valid', 'type':IOError}])
	test_list.append(fobj([TypeError, 'bcd']) == [{'name':'default', 'msg':'bcd', 'type':TypeError}])
	test_list.append(fobj(['xyz', ValueError]) == [{'name':'default', 'msg':'xyz', 'type':ValueError}])
	# Validate **kwargs
	test_list.append(putil.test.trigger_exception(fobj, {'a':45}, TypeError, 'Illegal custom contract exception definition'))
	test_list.append(fobj(char='Desc1', other=['a', ValueError]) == [{'name':'char', 'msg':'Desc1', 'type':RuntimeError}, {'name':'other', 'msg':'a', 'type':ValueError}])
	assert test_list == len(test_list)*[True]

def test_register_custom_contracts():
	""" Test _register_custom_contracts() function """
	fobj = putil.pcontracts._register_custom_contracts
	ftest = putil.test.trigger_exception
	key1 = 'contract_name'
	key2 = 'contract_exceptions'
	test_list = list()
	# Test data validation
	test_list.append(ftest(fobj, {key1:5, key2:{}}, TypeError, 'Argument `contract_name` is of the wrong type'))
	test_list.append(ftest(fobj, {key1:'test', key2:5}, TypeError, 'Argument `contract_exceptions` is of the wrong type'))
	test_list.append(ftest(fobj, {key1:'test', key2:{'msg':'b', 'key':'hole'}}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(ftest(fobj, {key1:'test', key2:[{5:'b'}]}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(ftest(fobj, {key1:'test', key2:[{'a':'b'}]}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(ftest(fobj, {key1:'test', key2:[{'name':'a', 'msg':'b', 'x':RuntimeError}]}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(ftest(fobj, {key1:'test', key2:[{'name':5, 'msg':'b', 'type':RuntimeError}]}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(ftest(fobj, {key1:'test', key2:[{'name':'a', 'msg':5, 'type':RuntimeError}]}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(ftest(fobj, {key1:'test', key2:[{'name':'a', 'msg':'b', 'type':5}]}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(ftest(fobj, {key1:'test', key2:[{'name':'a', 'msg':'b'}, {'name':'a', 'msg':'c',}]}, ValueError, 'Contract exception names are not unique'))
	test_list.append(ftest(fobj, {key1:'test', key2:[{'name':'a', 'msg':'desc'}, {'name':'b', 'msg':'desc',}]}, ValueError, 'Contract exception messages are not unique'))
	test_list.append(ftest(fobj, {key1:'test', key2:[{'name':'x', 'msg':'I am *[spartacus]*'}, {'name':'y', 'msg':'A move is *[spartacus]*',}]}, ValueError, 'Multiple replacement fields to be substituted by argument value'))
	putil.pcontracts._register_custom_contracts(contract_name='test1', contract_exceptions=[{'name':'a', 'msg':'desc'}])
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':'test1', 'contract_exceptions':[{'name':'a', 'msg':'other desc'}]}, RuntimeError, 'Attempt to redefine custom contract `test1`'))
	# Test homogenization of exception definitions
	putil.pcontracts._CUSTOM_CONTRACTS = dict()
	fobj('test_contract1', 'my description')
	test_list.append(cmp(putil.pcontracts._CUSTOM_CONTRACTS, {'test_contract1':{'default':{'num':0, 'msg':'my description', 'type':RuntimeError, 'field':None}}}) == 0)
	putil.pcontracts._CUSTOM_CONTRACTS = dict()
	fobj('test_contract2', [{'name':'mex1', 'msg':'msg1', 'type':ValueError}, {'name':'mex2', 'msg':'msg2 *[token_name]* hello world'}])
	test_list.append(cmp(putil.pcontracts._CUSTOM_CONTRACTS, {'test_contract2':{'mex1':{'num':0, 'msg':'msg1', 'type':ValueError, 'field':None}, \
														                        'mex2':{'num':1, 'msg':'msg2 *[token_name]* hello world', 'type':RuntimeError, 'field':'token_name'}}}) == 0)
	putil.pcontracts._CUSTOM_CONTRACTS = dict()
	fobj('test_contract3', [{'name':'mex1', 'msg':'msg1', 'type':ValueError}])
	fobj('test_contract4', [{'name':'mex2', 'msg':'msg2 *[token_name]* hello world'}])
	test_list.append(cmp(putil.pcontracts._CUSTOM_CONTRACTS, {'test_contract3':{'mex1':{'num':0, 'msg':'msg1', 'type':ValueError, 'field':None}}, \
														      'test_contract4':{'mex2':{'num':0, 'msg':'msg2 *[token_name]* hello world', 'type':RuntimeError, 'field':'token_name'}}}) == 0)
	putil.pcontracts._CUSTOM_CONTRACTS = dict()
	fobj('test_contract5', {'name':'mex5', 'msg':'msg5', 'type':ValueError})
	test_list.append(cmp(putil.pcontracts._CUSTOM_CONTRACTS, {'test_contract5':{'mex5':{'num':0, 'msg':'msg5', 'type':ValueError, 'field':None}}}) == 0)
	putil.pcontracts._CUSTOM_CONTRACTS = dict()
	assert test_list == len(test_list)*[True]

def test_new_contract():
	""" Tests for new_contract decorator """
	@putil.pcontracts.new_contract()
	def func1(name1):	#pylint: disable=C0111
		return name1, putil.pcontracts.get_exdesc()
	test_list = list()
	test_list.append(func1('a') == ('a', '[START CONTRACT MSG: func1]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]'))
	test_list.append(cmp(putil.pcontracts._CUSTOM_CONTRACTS, {'func1':{'argument_invalid':{'num':0, 'msg':'Argument `*[argument_name]*` is not valid', 'type':RuntimeError, 'field':'argument_name'}}}) == 0)
	putil.pcontracts._CUSTOM_CONTRACTS = dict()
	@putil.pcontracts.new_contract('Simple message')
	def func2(name2):	#pylint: disable=C0111
		return name2, putil.pcontracts.get_exdesc()
	test_list.append(func2('bc') == ('bc', '[START CONTRACT MSG: func2]Simple message[STOP CONTRACT MSG]'))
	test_list.append(cmp(putil.pcontracts._CUSTOM_CONTRACTS, {'func2':{'default':{'num':0, 'msg':'Simple message', 'type':RuntimeError, 'field':None}}}) == 0)
	putil.pcontracts._CUSTOM_CONTRACTS = dict()
	@putil.pcontracts.new_contract(ex1='Medium message', ex2=('Complex *[data]*', TypeError))
	def func3(name3):	#pylint: disable=C0111
		return name3, putil.pcontracts.get_exdesc()
	test_list.append(func3('def') == ('def', {'ex1':'[START CONTRACT MSG: func3]Medium message[STOP CONTRACT MSG]', 'ex2':'[START CONTRACT MSG: func3]Complex *[data]*[STOP CONTRACT MSG]'}))
	test_list.append(cmp(putil.pcontracts._CUSTOM_CONTRACTS, {'func3':{'ex1':{'num':0, 'msg':'Medium message', 'type':RuntimeError, 'field':None}, 'ex2':{'num':1, 'msg':'Complex *[data]*', 'type':TypeError, 'field':'data'}}}) == 0)
	assert test_list == len(test_list)*[True]

###
# Tests for _create_argument_value_pairs()
###
def ret_func(par):
	""" Returns the passed argument """
	return par

def decfunc(func):
	"""" Decorator function to test _create_argument_value_pairs function """
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		"""
		Wrapper function that creates the argument dictionary and returns a ret_func, which in turn just returns the argument passed. This is for testing only, obviously
		in an actual environment the dedcorator would return the original (called) function with the passed arguments
		"""
		return ret_func(putil.pcontracts._create_argument_value_pairs(func, *args, **kwargs))
	return wrapper

class TestCreateArgumentValuePairs(object):	#pylint: disable=W0232
	""" Tests for _create_argument_value_pairs function """

	def test_all_positional_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when all arguments are positional arguments """
		@decfunc
		def orig_func_all_positional_arguments(ppar1, ppar2, ppar3):	#pylint: disable=C0103,C0111,W0613
			pass
		assert orig_func_all_positional_arguments(1, 2, 3) == {'ppar1':1, 'ppar2':2, 'ppar3':3}

	def test_all_keyword_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when all arguments are keyword arguments """
		@decfunc
		def orig_func_all_keyword_arguments(kpar1, kpar2, kpar3):	#pylint: disable=C0103,C0111,W0613
			pass
		assert orig_func_all_keyword_arguments(kpar3=3, kpar2=2, kpar1=1) == {'kpar1':1, 'kpar2':2, 'kpar3':3}

	def test_positional_and_keyword_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when arguments are a mix of positional and keywords arguments """
		@decfunc
		def orig_func_positional_and_keyword_arguments(ppar1, ppar2, ppar3, kpar1=1, kpar2=2, kpar3=3):	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert orig_func_positional_and_keyword_arguments(10, 20, 30, kpar2=1.5, kpar3='x', kpar1=[1, 2]) == {'ppar1':10, 'ppar2':20, 'ppar3':30, 'kpar1':[1, 2], 'kpar2':1.5, 'kpar3':'x'}

	def test_no_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when there are no arguments passed """
		@decfunc
		def orig_func_no_arguments():	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert orig_func_no_arguments() == {}

	def test_more_positional_arguments_passed_than_defined(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when there are more arguments passed by position than in the function definition """
		@decfunc
		def orig_func(ppar1):	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert orig_func(1, 2, 3) == {}	#pylint: disable=E1121

	def test_more_keyword_arguments_passed_than_defined(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when there are more arguments passed by keyword than in the function definition """
		@decfunc
		def orig_func(kpar1=0, kpar2=2):	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert orig_func(kpar1=1, kpar2=2, kpar3=3) == {}	#pylint: disable=E1123

	def test_argument_passed_by_position_and_keyword(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when there are arguments passed both by position and keyword """
		@decfunc
		def orig_func(ppar1, ppar2, kpar1=1, kpar2=2):	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert orig_func(1, 2, ppar1=5) == {}	#pylint: disable=E1124

	def test_default_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when omitting keyword arguments that have defaults"""
		@decfunc
		def orig_func(ppar1, ppar2, kpar1='a', kpar2=2):	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert orig_func(1, 2, kpar2=20) == {'ppar1':1, 'ppar2':2, 'kpar1':'a', 'kpar2':20}	#pylint: disable=E1124


putil.pcontracts._CUSTOM_CONTRACTS = dict()
def test_contract():	#pylint: disable=C0103,R0912
	""" Test contract decorator """
	@putil.pcontracts.new_contract('Illegal number: *[number]*')
	def not_zero(number):	#pylint: disable=C0111,W0612
		exdesc = putil.pcontracts.get_exdesc()
		if number == 0:
			raise ValueError(exdesc)
		return True
	@putil.pcontracts.new_contract(wrong_file_name='The argument *[argument_name]* is wrong', file_not_found=(IOError, 'File name `*[file_name]*` not found'))
	def file_name_valid(name):	#pylint: disable=C0111,W0612
		exdesc = putil.pcontracts.get_exdesc()
		if name == 'a':
			raise ValueError(exdesc['wrong_file_name'])
		if name == 'b':
			raise ValueError(exdesc['file_not_found'])
		return True
	@putil.pcontracts.contract(number='int|float')
	def func1(number):	#pylint: disable=C0111
		return number
	@putil.pcontracts.contract(number='not_zero')
	def func2(number):	#pylint: disable=C0111
		if number == 1:
			raise TypeError('Unfathomable')
		return number
	@putil.pcontracts.contract(fname='str,file_name_valid', flag=bool)
	def func3(fname, fnumber, flag=False):	#pylint: disable=C0111,W0613
		return fname, fnumber
	@putil.pcontracts.new_contract('Illegal number: unity')
	def not_one(number):	#pylint: disable=C0111,W0612
		exdesc = putil.pcontracts.get_exdesc()
		if number == 1:
			raise ValueError(exdesc)
		return True
	test_list = list()
	test_list.append(putil.test.trigger_exception(func1, {'number':'a string'}, RuntimeError, 'Argument `number` is not valid'))
	test_list.append(putil.test.trigger_exception(func2, {'number':0}, RuntimeError, 'Illegal number: 0'))
	test_list.append(putil.test.trigger_exception(func2, {'number':1}, TypeError, 'Unfathomable'))
	test_list.append(putil.test.trigger_exception(func3, {'fname':'a', 'fnumber':5, 'flag':False}, RuntimeError, 'The argument fname is wrong'))
	test_list.append(putil.test.trigger_exception(func3, {'fname':'b', 'fnumber':5, 'flag':False}, IOError, 'File name `b` not found'))
	test_list.append(putil.test.trigger_exception(func3, {'fname':'zzz', 'fnumber':5, 'flag':45}, RuntimeError, 'Argument `flag` is not valid'))
	with pytest.raises(TypeError) as excinfo:
		func2(2, 5, 10)	#pylint: disable=E1121
	test_list.append(excinfo.value.message == 'func2() takes exactly 1 argument (3 given)')
	test_list.append(func1(5) == 5)
	test_list.append(func2(10) == 10)
	test_list.append(func3('hello', 'world', False) == ('hello', 'world'))
	putil.exh.set_exh_obj(putil.exh.ExHandle())
	@putil.pcontracts.contract(fname='str,file_name_valid')
	def func4(fname, fnumber):	#pylint: disable=C0111
		return fname, fnumber
	@putil.pcontracts.contract(num='float|not_one', flag=bool, fudge='str|int')
	def func5(num, flag=True, fudge=5):	#pylint: disable=C0111,W0613
		return num
	# Register exceptions
	func4('x', 5)
	func5(0)
	exlist = putil.exh.get_exh_obj()._ex_list
	pexlist = list()
	for exitem in exlist:
		pexlist.append({'name':exitem['name'][exitem['name'].rfind('.')+1:], 'type':exitem['type'], 'msg':exitem['msg']})
	test_list.append(sorted(pexlist) == sorted([{'name':'contract_func5_flag_0', 'type':RuntimeError, 'msg':'Argument `flag` is not valid'}, \
												{'name':'contract_func5_fudge_0', 'type':RuntimeError, 'msg':'Argument `fudge` is not valid'}, \
												{'name':'contract_func5_num_0', 'type':RuntimeError, 'msg':'Illegal number: unity'}, \
									            {'name':'contract_func4_fname_0', 'type':IOError, 'msg':'File name `*[file_name]*` not found'}, \
									            {'name':'contract_func4_fname_1', 'type':RuntimeError, 'msg':'The argument fname is wrong'}]))
	test_list.append(putil.test.trigger_exception(func4, {'fname':'a', 'fnumber':5}, RuntimeError, 'The argument fname is wrong'))
	test_list.append(putil.test.trigger_exception(func4, {'fname':'b', 'fnumber':5}, IOError, 'File name `b` not found'))
	test_list.append(putil.test.trigger_exception(func5, {'num':1}, RuntimeError, 'Illegal number: unity'))
	test_list.append(putil.test.trigger_exception(func5, {'num':1.0, 'flag':45}, RuntimeError, 'Argument `flag` is not valid'))
	test_list.append(putil.test.trigger_exception(func5, {'num':1.0, 'fudge':1.0}, RuntimeError, 'Argument `fudge` is not valid'))
	putil.exh.del_exh_obj()
	assert test_list == len(test_list)*[True]

def test_file_name_contract():
	""" Test for file_name custom contract """
	putil.pcontracts._CUSTOM_CONTRACTS = _ORIGINAL_CUSTOM_CONTRACTS
	@putil.pcontracts.contract(sfn='file_name')
	def func(sfn):
		""" Sample function to test file_name custom contract """
		return sfn
	test_list = list()
	test_list.append(putil.test.trigger_exception(func, {'sfn':3}, RuntimeError, 'Argument `sfn` is not valid'))
	test_list.append(putil.test.trigger_exception(func, {'sfn':'test\0'}, RuntimeError, 'Argument `sfn` is not valid'))
	func('some_file.txt')
	func(sys.executable)	# Test with Python executable (should be portable across systems), file should be valid although not having permissions to write it
	assert test_list == len(test_list)*[True]


def test_file_name_exists_contract():
	""" Test for file_name_exists custom contract """
	@putil.pcontracts.contract(sfn='file_name_exists')
	def func(sfn):
		""" Sample function to test file_name_exists custom contract """
		return sfn
	test_list = list()
	test_list.append(putil.test.trigger_exception(func, {'sfn':3}, RuntimeError, 'Argument `sfn` is not valid'))
	test_list.append(putil.test.trigger_exception(func, {'sfn':'test\0'}, RuntimeError, 'Argument `sfn` is not valid'))
	test_list.append(putil.test.trigger_exception(func, {'sfn':'_file_does_not_exist'}, IOError, 'File `_file_does_not_exist` could not be found'))
	func(sys.executable)	# Test with Python executable (should be portable across systems)
	assert test_list == len(test_list)*[True]


def test_enable_disable_contracts():
	""" Test wrappers around disable_all(), enable_all() and all_disabled() functions """
	test_list = list()
	test_list.append(putil.pcontracts.all_disabled() == False)
	putil.pcontracts.disable_all()
	test_list.append(putil.pcontracts.all_disabled() == True)
	putil.pcontracts.enable_all()
	test_list.append(putil.pcontracts.all_disabled() == False)
	assert test_list == len(test_list)*[True]
