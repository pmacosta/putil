# pcontracts.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
PyContracts custom contracts
"""

import os
import contracts

@contracts.new_contract
def file_name(name):
	""" Contract to validate a file name (i.e. file name does not have extraneous characters, etc.) """
	msg = 'File name is not valid '
	# Check that argument is a string
	if not isinstance(name, str):
		raise ValueError(msg)
	# If file exists, argment is a valid file name, otherwise test if file can be created
	# User may not have permission to write file, but call to os.access should not fail
	# if the file name is corect
	try:
		if not os.path.exists(name):
			os.access(name, os.W_OK)
	except:
		raise ValueError(msg)

@contracts.new_contract
def file_name_exists(name):
	""" Contract to validate that a file name is valid (i.e. file name does not have extraneous characters, etc.) and that the file exists """
	msg = 'File name is not valid '
	# Check that argument is a string
	if not isinstance(name, str):
		raise ValueError(msg)
	# Check that file name is valid
	try:
		os.path.exists(name)
	except:
		raise ValueError(msg)
	# Check that file exists
	if not os.path.exists(name):
		raise ValueError('File {0} could not be found'.format(name))

