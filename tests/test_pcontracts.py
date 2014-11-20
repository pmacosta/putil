# test_pcontracts.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212

"""
putil.pcontracts unit tests
"""
import pytest
import functools

import putil.test
import putil.pcontracts	#pylint: disable=W0611

def test_isexception():
	""" Test isexception() function """
	test_list = list()
	test_list.append(putil.pcontracts.isexception(str) == False)
	test_list.append(putil.pcontracts.isexception(3) == False)
	test_list.append(putil.pcontracts.isexception(RuntimeError) == True)
	assert test_list == len(test_list)*[True]


_EXH = 'Test global variable'
def test_get_exh_obj():
	""" Test get_txh_obj() function """
	test_list = list()
	test_list.append(putil.pcontracts.get_exh_obj() == 'Test global variable')
	del globals()['_EXH']
	test_list.append(putil.pcontracts.get_exh_obj() == None)


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
	test_list.append(putil.test.trigger_exception(putil.pcontracts.get_exdesc, {}, RuntimeError, 'Function object could not be found'))
	assert test_list == len(test_list)*[True]


def test_get_replacement_token():
	""" Test get_replacement_token() function """
	test_list = list()
	test_list.append(putil.pcontracts.get_replacement_token('Argument `*[argument_name]*` could not be found') == 'argument_name')
	test_list.append(putil.pcontracts.get_replacement_token('Argument `*file_name*` could not be found') == None)
	assert test_list == len(test_list)*[True]


def test_format_arg_errors():
	""" Test format_arg() function exceptions """
	exdesc = list()
	exdesc.append(({'arg':set([RuntimeError, 'Message'])}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':[]}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':(RuntimeError, 'Message', 3)}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':[3]}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':['a', 3]}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':[3, 'a']}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':[ValueError, 3]}, TypeError, 'Illegal custom contract exception definition'))
	exdesc.append(({'arg':[3, ValueError]}, TypeError, 'Illegal custom contract exception definition'))
	putil.test.evaluate_exception_series(exdesc, putil.pcontracts.format_arg)


def test_format_arg_works():
	""" Test format_arg() function """
	fobj = putil.pcontracts.format_arg
	test_list = list()
	test_list.append(cmp(fobj('Message'), {'msg':'Message', 'type':RuntimeError}) == 0)
	test_list.append(cmp(fobj(IOError), {'msg':'Argument `*[argument_name]*` is not valid', 'type':IOError}) == 0)
	test_list.append(cmp(fobj((ValueError, 'Description 1')), {'msg':'Description 1', 'type':ValueError}) == 0)
	test_list.append(cmp(fobj(('Description 2', TypeError)), {'msg':'Description 2', 'type':TypeError}) == 0)
	assert test_list == len(test_list)*[True]


def test_parse_new_contract_args():
	""" Test parse_new_contract_args() function """
	fobj = putil.pcontracts.parse_new_contract_args
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
	""" Test register_custom_contracts() function """
	fobj = putil.pcontracts.register_custom_contracts
	test_list = list()
	# Test data validation
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':5, 'contract_exceptions':{}}, TypeError, 'Argument `contract_name` is of the wrong type'))
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':'test', 'contract_exceptions':5}, TypeError, 'Argument `contract_exceptions` is of the wrong type'))
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':'test', 'contract_exceptions':{'msg':'b', 'key':'hole'}}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':'test', 'contract_exceptions':[{5:'b'}]}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':'test', 'contract_exceptions':[{'a':'b'}]}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':'test', 'contract_exceptions':[{'name':'a', 'msg':'b', 'x':RuntimeError}]}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':'test', 'contract_exceptions':[{'name':5, 'msg':'b', 'type':RuntimeError}]}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':'test', 'contract_exceptions':[{'name':'a', 'msg':5, 'type':RuntimeError}]}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':'test', 'contract_exceptions':[{'name':'a', 'msg':'b', 'type':5}]}, TypeError, 'Contract exception definition is of the wrong type'))
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':'test', 'contract_exceptions':[{'name':'a', 'msg':'b'}, {'name':'a', 'msg':'c',}]}, ValueError, 'Contract exception names are not unique'))
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':'test', 'contract_exceptions':[{'name':'a', 'msg':'desc'}, {'name':'b', 'msg':'desc',}]}, ValueError, 'Contract exception messages are not unique'))
	putil.pcontracts.register_custom_contracts(contract_name='test1', contract_exceptions=[{'name':'a', 'msg':'desc'}])
	test_list.append(putil.test.trigger_exception(fobj, {'contract_name':'test1', 'contract_exceptions':[{'name':'a', 'msg':'other desc'}]}, RuntimeError, 'Attemp to redefine custom contract `test1`'))
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
	test_list.append(func1('a') == ('a', 'Argument `*[argument_name]*` is not valid'))
	test_list.append(cmp(putil.pcontracts._CUSTOM_CONTRACTS, {'func1':{'argument_invalid':{'num':0, 'msg':'Argument `*[argument_name]*` is not valid', 'type':RuntimeError, 'field':'argument_name'}}}) == 0)
	putil.pcontracts._CUSTOM_CONTRACTS = dict()
	@putil.pcontracts.new_contract('Simple message')
	def func2(name2):	#pylint: disable=C0111
		return name2, putil.pcontracts.get_exdesc()
	test_list.append(func2('bc') == ('bc', 'Simple message'))
	test_list.append(cmp(putil.pcontracts._CUSTOM_CONTRACTS, {'func2':{'default':{'num':0, 'msg':'Simple message', 'type':RuntimeError, 'field':None}}}) == 0)
	putil.pcontracts._CUSTOM_CONTRACTS = dict()
	@putil.pcontracts.new_contract(ex1='Medium message', ex2=('Complex *[data]*', TypeError))
	def func3(name3):	#pylint: disable=C0111
		return name3, putil.pcontracts.get_exdesc()
	test_list.append(func3('def') == ('def', {'ex1':'Medium message', 'ex2':'Complex *[data]*'}))
	test_list.append(cmp(putil.pcontracts._CUSTOM_CONTRACTS, {'func3':{'ex1':{'num':0, 'msg':'Medium message', 'type':RuntimeError, 'field':None}, 'ex2':{'num':1, 'msg':'Complex *[data]*', 'type':TypeError, 'field':'data'}}}) == 0)
	assert test_list == len(test_list)*[True]

###
# Tests for create_argument_dictionary()
###
def ret_func(par):
	""" Returns the passed argument """
	return par

def decfunc(func):
	"""" Decorator function to test create_argument_dictionary function """
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		"""
		Wrapper function that creates the argument dictionary and returns a ret_func, which in turn just returns the argument passed. This is for testing only, obviously
		in an actual environment the dedcorator would return the original (called) function with the passed arguments
		"""
		return ret_func(putil.pcontracts.create_argument_dictionary(func, *args, **kwargs))
	return wrapper

class TestCreateArgumentDictionary(object):	#pylint: disable=W0232
	""" Tests for create_argument_dictionary function """

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


putil.pcontracts._CUSTOM_CONTRACTS = dict()
def test_contract_no_exception_handler():	#pylint: disable=C0103
	""" Test contract decorator """
	@putil.pcontracts.contract(number='int|float')
	def func1(number):	#pylint: disable=C0111
		return number
	test_list = list()
	test_list.append(putil.test.trigger_exception(func1, {'number':'a string'}, RuntimeError, 'Argument `number` is not valid'))
	assert test_list == len(test_list)*[True]


#def test_file_name_contract():
#	""" Test for file_name custom contract """
#	@contracts.contract(sfn='file_name')
#	def func(sfn):
#		""" Sample function to test file_name custom contract """
#		return sfn
#	test_list = list()
#	test_list.append(putil.test.trigger_pcontract_exception(func, {'sfn':3}, 'File name is not valid'))
#	test_list.append(putil.test.trigger_pcontract_exception(func, {'sfn':'test\0'}, 'File name is not valid'))
#	func(sys.executable)	# Test with Python executable (should be portable across systems), file should be valid although not having permissions to write it
#	assert test_list == len(test_list)*[True]
#
#def test_file_name_exists_contract():
#	""" Test for file_name_exists custom contract """
#	@contracts.contract(sfn='file_name_exists')
#	def func(sfn):
#		""" Sample function to test file_name_exists custom contract """
#		return sfn
#	test_list = list()
#	test_list.append(putil.test.trigger_pcontract_exception(func, {'sfn':3}, 'File name is not valid'))
#	test_list.append(putil.test.trigger_pcontract_exception(func, {'sfn':'test\0'}, 'File name is not valid'))
#	test_list.append(putil.test.trigger_pcontract_exception(func, {'sfn':'_file_does_not_exist'}, 'File _file_does_not_exist could not be found'))
#	func(sys.executable)	# Test with Python executable (should be portable across systems)
#	assert test_list == len(test_list)*[True]
