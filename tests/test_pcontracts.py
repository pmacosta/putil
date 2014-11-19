# test_pcontracts.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.pcontracts unit tests
"""

import putil.test
import putil.pcontracts	#pylint: disable=W0611

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


def test_register_custom_contracts():
	""" Test register_custom_contracts """
	test_list = list()
	test_list.append(putil.test.trigger_exception(putil.pcontracts.register_custom_contracts, {'contract_name':5, 'contract_exceptions':{}}, TypeError, 'Argument `contract_name` is of the wrong type'))
	test_list.append(putil.test.trigger_exception(putil.pcontracts.register_custom_contracts, {'contract_name':'test', 'contract_exceptions':5}, TypeError, 'Argument `contract_exceptions` is of the wrong type'))
	test_list.append(putil.test.trigger_exception(putil.pcontracts.register_custom_contracts, {'contract_name':'test', 'contract_exceptions':{5:'a', 6:'b'}}, TypeError, 'Contract exception name is of the wrong type'))
	test_list.append(putil.test.trigger_exception(putil.pcontracts.register_custom_contracts, {'contract_name':'test', 'contract_exceptions':{'a':3.5}}, TypeError, 'Contract exception is of the wrong type'))
	#test_list.append(putil.test.trigger_exception(putil.pcontracts.register_custom_contracts, {'contract_name':'test', 'contract_exceptions':{'a':'b'}}, TypeError, 'Contract exception is of the wrong type'))
	test_list.append(putil.test.trigger_exception(putil.pcontracts.register_custom_contracts, {'contract_name':'test', 'contract_exceptions':{'msg':'b', 'x':RuntimeError}}, TypeError, 'Contract exception is of the wrong type'))
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
