# test_pcontracts.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.pcontracts unit tests
"""

import sys
import contracts

import putil.test
import putil.pcontracts	#pylint: disable=W0611

def test_file_name_contract():
	""" Test for file_name custom contract """
	@contracts.contract(sfn='file_name')
	def func(sfn):
		""" Sample function to test file_name custom contract """
		return sfn
	test_list = list()
	test_list.append(putil.test.trigger_pcontract_exception(func, {'sfn':3}, 'File name is not valid'))
	test_list.append(putil.test.trigger_pcontract_exception(func, {'sfn':'test\0'}, 'File name is not valid'))
	func(sys.executable)	# Test with Python executable (should be portable across systems), file should be valid although not having permissions to write it
	assert test_list == len(test_list)*[True]

def test_file_name_exists_contract():
	""" Test for file_name_exists custom contract """
	@contracts.contract(sfn='file_name_exists')
	def func(sfn):
		""" Sample function to test file_name_exists custom contract """
		return sfn
	test_list = list()
	test_list.append(putil.test.trigger_pcontract_exception(func, {'sfn':3}, 'File name is not valid'))
	test_list.append(putil.test.trigger_pcontract_exception(func, {'sfn':'test\0'}, 'File name is not valid'))
	test_list.append(putil.test.trigger_pcontract_exception(func, {'sfn':'_file_does_not_exist'}, 'File _file_does_not_exist could not be found'))
	func(sys.executable)	# Test with Python executable (should be portable across systems)
	assert test_list == len(test_list)*[True]
