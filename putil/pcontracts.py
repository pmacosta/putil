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

import putil.exh

_CUSTOM_CONTRACTS = dict()

###
# Functions
###
def isexception(obj):
	""" Tests whether an object is an exception object """
	return False if not inspect.isclass(obj) else issubclass(obj, Exception)


def format_arg(arg):
	""" Validate one exception specification contract tuple/list """
	if not (isinstance(arg, str) or isexception(arg) or isinstance(arg, tuple) or isinstance(arg, list)):
		raise TypeError('Illegal custom contract exception definition')
	if (isinstance(arg, tuple) or isinstance(arg, list)) and ((len(arg) == 0) or (len(arg) > 2)):
		raise TypeError('Illegal custom contract exception definition')
	if isinstance(arg, str) and (len(arg) == 0):
		raise ValueError('Empty custom contract exception message')
	if isinstance(arg, str):
		return {'msg':arg, 'type':RuntimeError}
	if isexception(arg):
		return {'msg':'Argument `*[argument_name]*` is not valid', 'type':arg}
	if (len(arg) == 1) and (not isinstance(arg[0], str)) and (not isexception(arg[0])):
		raise TypeError('Illegal custom contract exception definition')
	if (len(arg) == 2) and (not ((isinstance(arg[0], str) and isexception(arg[1])) or (isinstance(arg[1], str) and isexception(arg[0])))):
		raise TypeError('Illegal custom contract exception definition')
	if (len(arg) == 1) and isinstance(arg[0], str) and (len(arg[0]) == 0):
		raise ValueError('Empty custom contract exception message')
	if (len(arg) == 2) and ((isinstance(arg[0], str) and (len(arg[0]) == 0)) or (isinstance(arg[1], str) and (len(arg[1]) == 0))):
		raise ValueError('Empty custom contract exception message')
	if len(arg) == 1:
		return {'msg':arg[0] if isinstance(arg[0], str) else 'Argument `*[argument_name]*` is not valid', 'type':arg[0] if isexception(arg[0]) else RuntimeError}
	if len(arg) == 2:
		return {'msg':arg[0] if isinstance(arg[0], str) else arg[1], 'type':arg[0] if isexception(arg[0]) else arg[1]}


def parse_new_contract_args(*args, **kwargs):
	""" Parse argument for new_contract() function """
	# No arguments
	if (len(args) == 0) and (len(kwargs) == 0):
		return [{'name':'argument_invalid', 'msg':'Argument `*[argument_name]*` is not valid', 'type':RuntimeError}]
	# Process args
	if (len(args) > 1) or ((len(args) == 1) and (len(kwargs) > 0)):
		raise TypeError('Illegal custom contract exception definition')
	elif len(args) == 1:
		return [dict([('name', 'default')]+format_arg(args[0]).items())]
	# Process kwargs
	return [dict([('name', name)]+format_arg(kwargs[name]).items()) for name in sorted(kwargs.keys())]


def new_contract(*args, **kwargs):	#pylint: disable=R0912
	"""	New contract decorator constructor """
	def wrapper(func):	#pylint: disable=R0912,R0914
		""" Decorator """
		contract_name = func.__name__
		exdesc = parse_new_contract_args(*args, **kwargs)
		# Pass to the custom contract, via a property, only the exception descriptions
		func.exdesc = dict([(value['name'], '[START CONTRACT MSG: {0}]{1}[STOP CONTRACT MSG]'.format(contract_name, value['msg'])) for value in exdesc])
		# Register custom contract
		register_custom_contracts(contract_name, exdesc)
		# Apply PyContract decorator
		return contracts.new_contract(func)
	return wrapper


def contract(**contract_args):	#pylint: disable=R0912
	"""	Decorator constructor """
	@decorator.decorator
	def wrapper(func, *args, **kwargs):	#pylint: disable=R0912,R0914
		""" Decorator """
		param_dict = create_argument_dictionary(func, *args, **kwargs)
		# Register exceptions if exception handler object exists
		exhobj = putil.exh._get_exh_obj()	#pylint: disable=W0212
		if exhobj:
			for param_name, param_contract in contract_args.items():	# param_name=param_value, as in num='str|float'
				custom_contracts_dict = [item for sublist in [_CUSTOM_CONTRACTS[custom_contract].values() for custom_contract in _CUSTOM_CONTRACTS if re.search(r'\b{0}\b'.format(custom_contract), param_contract)] for item in sublist]
				for exdict in custom_contracts_dict:
					exname = 'contract_{0}_{1}_{2}'.format(func.__name__, param_name, exdict['num'])
					exhobj.add_exception(name=exname, extype=exdict['type'], exmsg=exdict['msg'].replace('*[argument_name]*', param_name))
		# Actually validate arguments
		try:
			return contracts.contract_decorator(func, **contract_args)(*args, **kwargs)
		except contracts.ContractNotRespected as eobj:
			_, _, tbobj = sys.exc_info()
			# Extract which function parameter triggered exception
			param_name = re.search(r"'\w+'", eobj.error).group()[1:-1]	# re.search returns the string with quotes in it
			# Raise exception
			exdict = get_contract_exception_dict(eobj.error)
			exname = 'contract_{0}_{1}_{2}'.format(func.__name__, param_name, exdict['num'])
			edata = {'field':exdict['field'], 'value':param_dict[param_name]} if (exdict['field'] and (exdict['field'] != 'argument_name')) else None
			if exhobj:
				exhobj.raise_exception_if(name=exname, condition=True, edata=edata)
			else:
				msg = exdict['msg'].replace('*[{0}]*'.format(exdict['field']), param_name if exdict['field'] == 'argument_name' else '{0}'.format(param_dict[param_name]))	#pylint: disable=W0631
				raise exdict['type'], exdict['type'](msg), tbobj
		except:
			# Re-raise exception if it was not due to invalid argument
			raise
	return wrapper


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


def get_exdesc():
	""" Get function attribute within function """
	sobj = inspect.stack()
	# First frame is own function (get_exdesc), next frame is the calling function, of which its name is needed
	fname = sobj[1][3]
	# Get globals variables, where function attributes reside
	for sitem in sobj[1:]:
		fobj = sitem[0].f_locals[fname] if fname in sitem[0].f_locals else (sitem[0].f_globals[fname] if fname in sitem[0].f_globals else None)
		if fobj and hasattr(fobj, 'exdesc'):
			break
	else:
		raise RuntimeError('Function object could not be found for function `{0}`'.format(fname))
	# Return function attribute created by new contract decorator
	exdesc = getattr(fobj, 'exdesc')
	return exdesc if len(exdesc) > 1 else exdesc[exdesc.keys()[0]]


def get_replacement_token(msg):
	""" Extract replacement token from exception message """
	return None if not re.search(r'\*\[[\w|\W]+\]\*', msg) else re.search(r'\*\[[\w|\W]+\]\*', msg).group()[2:-2]


def register_custom_contracts(contract_name, contract_exceptions):
	""" Homogenize custom contract exception definition """
	global _CUSTOM_CONTRACTS	#pylint: disable=W0602
	# Validate arguments and homogenize contract exceptions
	if not isinstance(contract_name, str):
		raise TypeError('Argument `contract_name` is of the wrong type')
	# A contract exceptin can be a string (only one exception, default exception type) or a dictionary of exception definitions, if there is more than one or if the type if different than the default
	if (not isinstance(contract_exceptions, list)) and (not isinstance(contract_exceptions, str)) and (not isinstance(contract_exceptions, dict)):
		raise TypeError('Argument `contract_exceptions` is of the wrong type')
	if isinstance(contract_exceptions, dict):
		contract_exceptions = [contract_exceptions]
	if isinstance(contract_exceptions, list) and any([not isinstance(key, str) for item in contract_exceptions for key in item.keys()]):
		raise TypeError('Contract exception definition is of the wrong type')
	# Validate individual exception definitions
	if isinstance(contract_exceptions, list) and any([not ((set(item.keys()) == set(['name', 'msg'])) or (set(item.keys()) == set(['name', 'msg', 'type']))) for item in contract_exceptions]):
		raise TypeError('Contract exception definition is of the wrong type')
	extype = type(ValueError)
	if isinstance(contract_exceptions, list) and any([(not isinstance(item['name'], str)) or (not isinstance(item['msg'], str)) or (not isinstance(item.get('type', extype), extype)) for item in contract_exceptions]):
		raise TypeError('Contract exception definition is of the wrong type')
	# Homegenize exception definitions
	if isinstance(contract_exceptions, list):
		homogenized_exdict = dict([(exdict['name'], {'num':exnum, 'msg':exdict['msg'], 'type':exdict.get('type', RuntimeError), 'field':get_replacement_token(exdict['msg'])}) for exnum, exdict in enumerate(contract_exceptions)])
	else:
		homogenized_exdict = {'default':{'num':0, 'msg':contract_exceptions, 'type':RuntimeError, 'field':get_replacement_token(contract_exceptions)}}
	# Verify exception names are unique
	if isinstance(contract_exceptions, list) and (len(homogenized_exdict) != len(contract_exceptions)):
		raise ValueError('Contract exception names are not unique')
	# Verify that exception messages are unique
	msgs = [exvalue['msg'] for exvalue in homogenized_exdict.values()]
	if len(set(msgs)) != len(msgs):
		raise ValueError('Contract exception messages are not unique')
	# Verify that a custom contract is not being redefined
	if (contract_name in _CUSTOM_CONTRACTS) and (_CUSTOM_CONTRACTS[contract_name] != contract_exceptions):
		raise RuntimeError('Attemp to redefine custom contract `{0}`'.format(contract_name))
	# Verify that there are at most only two replacemente fields, and one of them should be argument_name
	fields = [exdict['field'] for exdict in homogenized_exdict.values() if exdict['field'] != None]
	if (len(fields) > 2) or ((len(fields) == 2) and (fields[0] != 'argument_name') and  (fields[1] != 'argument_name')):
		raise ValueError('Multiple replacement fields to be substituted by argument value')
	# Register new contract
	_CUSTOM_CONTRACTS[contract_name] = homogenized_exdict
	return contract_exceptions


def get_contract_exception_dict(contract_msg):
	""" Generate message for exception """
	# Get contract name:
	start_token = '[START CONTRACT MSG: '
	stop_token = '[STOP CONTRACT MSG]'
	if contract_msg.find(start_token) == -1:
		return {'num':0, 'msg':'Argument `*[argument_name]*` is not valid', 'type':RuntimeError, 'field':'argument_name'}
	else:
		contract_msg = contract_msg[contract_msg.find(start_token)+len(start_token):]
		contract_name = contract_msg[:contract_msg.find(']')]
		contract_msg = contract_msg[contract_msg.find(']')+1:contract_msg.find(stop_token)]
		exdict = _CUSTOM_CONTRACTS[contract_name]
		for exvalue in exdict.values():
			if exvalue['msg'] == contract_msg:
				return exvalue


###
# Custom contracts definition
###
@new_contract()
def file_name(name):
	""" Contract to validate a file name (i.e. file name does not have extraneous characters, etc.) """
	msg = get_exdesc()
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


@new_contract(argument_invalid='Argument `*[argument_name]*` is not valid', file_not_found=(IOError, 'File `*[file_name]*` could not be found'))
def file_name_exists(name):
	""" Contract to validate that a file name is valid (i.e. file name does not have extraneous characters, etc.) and that the file exists """
	exdesc = get_exdesc()
	msg = exdesc['argument_invalid']
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
		msg = exdesc['file_not_found']
		raise ValueError(msg)
