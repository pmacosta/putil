# pcontracts.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
PyContracts custom contracts
"""

import os
import re
import sys
import inspect
import funcsigs
import contracts
import decorator

_CUSTOM_CONTRACTS = dict()

###
# Custom contracts definition
###

@contracts.new_contract
def file_name(name):
	""" Contract to validate a file name (i.e. file name does not have extraneous characters, etc.) """
	msg = 'Argument `*[argument_name]*` is not valid'
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
register_custom_contracts('file_name', 'Argument `*[argument_name]*` is not valid')

@contracts.new_contract
def file_name_exists(name):
	""" Contract to validate that a file name is valid (i.e. file name does not have extraneous characters, etc.) and that the file exists """
	msg = 'Argument `*[argument_name]*` is not valid'
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
		raise ValueError('[START CUSTOM EXCEPTION MESSAGE]File *[file_name]* could not be found[STOP CUSTOM EXCEPTION MESSAGE]')
register_custom_contracts('file_name_exists', ['Argument `*[argument_name]*` is not valid', ['File `*[file_name]*` could not be found', IOError]])


###
# Functions
###
def register_custom_contracts(contract_name, contract_exceptions):
	""" Homogenize custom contract exception definition """
	global _CUSTOM_CONTRACTS	#pylint: disable=W0602
	if not isinstance(contract_name, str):
		raise TypeError('Argument `contract_name` is of the wrong type')
	if (not isinstance(contract_exceptions, str)) and (not isinstance(contract_exceptions, list)):
		raise TypeError('Argument `contract_exceptions` is of the wrong type')
	contract_exceptions = contract_exceptions if isinstance(contract_exceptions, list) else [contract_exceptions]
	for exception in contract_exceptions:
		if ((not isinstance(exception, str)) and (not isinstance(exception, list))) or \
			(isinstance(exception, list) and (len(exception) != 2)) or \
			(isinstance(exception, list) and ((not isinstance(exception[0], str)) or (not isinstance(exception[0], type(RuntimeError))))):
			raise TypeError('Argument `contract_exceptions` is of the wrong type')
	_CUSTOM_CONTRACTS[contract_name] = [(RuntimeError, exception) if isinstance(exception, str) else exception for exception in contract_exceptions]


def get_exh_obj():
	""" Get exception handler object (if any) """
	root_module = inspect.stack()[-1][0]
	return root_module.f_locals.get('_EXH', None) if root_module else None


def get_replacement_token(msg):
	""" Extract replacement token from exception message """
	return None if not re.search(r'\*\[[\w|\W]+\]\*', msg).group() else re.search(r'\*\[[\w|\W]+\]\*', msg).group()[2:-2]


def get_contract_exception_message(param_name, param_value, param_contracts):
	""" Generate message for exception """
	for custom_contract, contract_exceptions in _CUSTOM_CONTRACTS.items():
		if custom_contract in param_contracts[param_name]:
			contract_exceptions = contract_exceptions if isinstance(contract_exceptions, list) else [contract_exceptions]
			ret = dict([(exmsg, (num, extype, get_replacement_token(exmsg), param_name if get_replacement_token(exmsg) == '*[argument_name]*' else param_value)) for num, (extype, exmsg) in enumerate(contract_exceptions)])
			break
	else:
		ret = {'Argument `*[argument_name]*` is not valid':(0, RuntimeError, 'argument_name', param_name)}
	return ret


def create_argument_dictionary(func, *args, **kwargs):
	"""
	Creates a dictionary where the keys are the argument names and the values are the passed arguments values (if any)
	An empty dictionary is returned if an error is detected, such as more arguments than in the function definition, argument(s) defined by position and keyword, etc.
	"""
	# Capture parameters that have been explicitly specified in function call
	try:
		arg_dict = funcsigs.signature(func).bind_partial(*args, **kwargs).arguments
	except:	#pylint: disable=W0702
		return dict()
	# Capture parameters that have not been explicitly specified but have default values
	arguments = funcsigs.signature(func).parameters
	for arg_name in arguments:
		if (arguments[arg_name].default != funcsigs.Parameter.empty) and (arguments[arg_name].name not in arg_dict):
			arg_dict[arguments[arg_name].name] = arguments[arg_name].default
	return arg_dict


def contract(**contract_args):	#pylint: disable=R0912
	"""	Decorator constructor """
	@decorator.decorator
	def wrapper(func, *args, **kwargs):	#pylint: disable=R0912,R0914
		""" Decorator """
		param_dict = create_argument_dictionary(func, *args, **kwargs)
		if not param_dict:
			# An empty param_dict means there is a mimatch between passed parameters and defined function
			# parameters, let Python interpreter take care of that case by returning function undecorated
			return func
		else:
			exhobj = get_exh_obj()
			if exhobj:
				for param_name in contract_args:
					for exmsg, (exnum, extype, _, exvalue) in get_contract_exception_message(param_name, param_dict[param_name], contract_args).items():
						exname = 'contract_{0}_{1}'.format(param_name, exnum)
						exhobj.add_exception(name=exname, extype=extype, exmsg=exmsg.replace('*[argument_name]*', exvalue))
			try:
				return contracts.contract_decorator(func, **contract_args)(*args, **kwargs)
			except contracts.ContractNotRespected as eobj:
				_, _, tbobj = sys.exc_info()
				# Extract which function parameter triggered exception
				param_name = re.search(r"'\w+'", eobj.error).group()[1:-1]	# re.search returns the string with quotes in it
				# Raise exception
				for exmsg, (exnum, extype, exfield, exvalue) in get_contract_exception_message(param_name, param_dict[param_name], contract_args).items():
					if exmsg in eobj.error:
						exname = 'contract_{0}_{1}'.format(param_name, exnum)
						edata = {'field':exfield, 'value':exvalue}
						break
				else:
					raise RuntimeError('Unable to translate contract exception message')
				if exhobj:
					exhobj.raise_exception_if(name=exname, condition=True, edata=edata)
				else:
					msg = exmsg.replace('*[{0}]*'.format(exfield), exvalue)	#pylint: disable=W0631
					# Extract custom message from long PyContracts exception message (needed if exception handler is not used)
					raise extype, extype(msg), tbobj
			except:
				# Re-raise exception if it was not due to invalid argument
				raise
	return wrapper
