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


@new_contract({\
	'argument_invalid':{'msg':'Argument `*[argument_name]*` is not valid'},
	'file_not_found': {'msg':'File `*[file_name]*` could not be found', 'type':IOError} \
})
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


###
# Functions
###
def get_exdesc():
	""" Get function attribute within function """
	sobj = inspect.stack()
	# First frame is own function (get_exdesc), next frame is the calling function, of which its name is needed
	fname = sobj[1][3]
	# Get globals variables, where function attributes reside
	fobj = sobj[2][0].f_globals[fname]
	# Return function attribute created by new contract decorator
	exdesc = getattr(fobj, 'exdesc')
	return exdesc if len(exdesc) > 1 else exdesc[exdesc.keys()[0]]


def new_contract(exdesc=None):	#pylint: disable=R0912
	"""	New contract decorator constructor """
	def wrapper(func):	#pylint: disable=R0912,R0914
		""" Decorator """
		# Make exdesc default if no argument passed
		exdesc_int = exdesc if exdesc != None else {'argument_invalid':{'msg':'Argument `*[argument_name]*` is not valid'}}
		# Pass to the custom contract, via a property, only the exception descriptions
		func.exdesc = dict([(name, value['msg']) for name, value in exdesc_int.items()])
		# Register custom contract
		register_custom_contracts(func.__name__, exdesc_int)
		# Apply PyContract decorator
		return contracts.new_contract(func)
	return wrapper


def register_custom_contracts(contract_name, contract_exceptions):
	""" Homogenize custom contract exception definition """
	global _CUSTOM_CONTRACTS	#pylint: disable=W0602
	# Validate arguments and homogenize contract exceptions
	if not isinstance(contract_name, str):
		raise TypeError('Argument `contract_name` is of the wrong type')
	if not isinstance(contract_exceptions, dict):
		raise TypeError('Argument `contract_exceptions` is of the wrong type')
	if any(not isinstance(key, str) for key in contract_exceptions.keys()):
		raise TypeError('Contract exception name is of the wrong type')
	for exname, exvalue in contract_exceptions.items():
		if ((not isinstance(exvalue, str)) and (not isinstance(exvalue, dict))) or (isinstance(exvalue, dict) and ((set(exvalue.keys()) != set(['msg'])) or (set(exvalue.keys()) != set(['msg', 'type'])))) or \
			(isinstance(exvalue, dict) and ((not isinstance(exvalue.get('msg', ''), str)) or (not isinstance(exvalue.get('type', type), str)))):
			raise TypeError('Contract exception `{0}` is of the wrong type'.format(exname))
		if isinstance(exvalue, str):
			contract_exceptions[exname] = {'msg':exvalue, 'type':RuntimeError}
		else:
			contract_exceptions[exname] = {'msg':exvalue['msg'], 'type':exvalue.get('type', RuntimeError)}
	# Verify that a custom contract is not being redefined
	if (contract_name in _CUSTOM_CONTRACTS) and (_CUSTOM_CONTRACTS[contract_name] != contract_exceptions):
		raise RuntimeError('Attemp to redefine custrom contract `{0}`'.format(contract_name))
	# Register new contract
	_CUSTOM_CONTRACTS[contract_name] = contract_exceptions
	return contract_exceptions

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
		exmsgs = [exvalue['msg'] for exvalue in custom_exceptions.values()]
		exfound = False
		for exmsg in exmsgs:
			if exmsg in param_contracts[param_name]:
				contract_exceptions = contract_exceptions if isinstance(contract_exceptions, list) else [contract_exceptions]
				ret = dict([(exmsg, (num, extype, get_replacement_token(exmsg), param_name if get_replacement_token(exmsg) == '*[argument_name]*' else param_value)) for num, (extype, exmsg) in enumerate(contract_exceptions)])
				exfound = True
				break
		if exfound:
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
