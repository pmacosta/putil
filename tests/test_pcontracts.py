# test_pcontracts.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.pcontracts unit tests
"""

import sys
import pytest
import contracts

import putil.pcontracts	#pylint: disable=W0611

def check_pcontract_exception(obj, args, extype, exmsg):
	""" Triggers exception withing the Py.test environment and records value """
	with pytest.raises(extype) as excinfo:
		obj(**args)	#pylint: disable=W0142
	if exmsg not in excinfo.value.error:
		print excinfo.value.error
	return exmsg in excinfo.value.error

def test_file_name_contract():
	""" Test for file_name custom contract """
	@contracts.contract(sfn='file_name')
	def func(sfn):
		""" Sample function to test file_name custom contract """
		return sfn
	test_list = list()
	test_list.append(check_pcontract_exception(func, {'sfn':3}, contracts.ContractNotRespected, 'File name is not valid'))
	test_list.append(check_pcontract_exception(func, {'sfn':'test\0'}, contracts.ContractNotRespected, 'File name is not valid'))
	func(sys.executable)	# Test with Python executable (should be portable across systems), file should be valid although not having permissions to write it
	assert test_list == len(test_list)*[True]

def test_file_name_exists_contract():
	""" Test for file_name_exists custom contract """
	@contracts.contract(sfn='file_name_exists')
	def func(sfn):
		""" Sample function to test file_name_exists custom contract """
		return sfn
	test_list = list()
	test_list.append(check_pcontract_exception(func, {'sfn':3}, contracts.ContractNotRespected, 'File name is not valid'))
	test_list.append(check_pcontract_exception(func, {'sfn':'test\0'}, contracts.ContractNotRespected, 'File name is not valid'))
	test_list.append(check_pcontract_exception(func, {'sfn':'_file_does_not_exist'}, contracts.ContractNotRespected, 'File does not exist'))
	func(sys.executable)	# Test with Python executable (should be portable across systems)
	assert test_list == len(test_list)*[True]
