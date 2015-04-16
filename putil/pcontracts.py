# pcontracts.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0912,R0914

import contracts
import decorator
import funcsigs
import inspect
import os
import re

import putil.exh
import putil.misc


###
# Global variables
###
_CUSTOM_CONTRACTS = dict()


###
# Functions
###
def all_disabled():
	"""
	Wraps PyContracts `all_disabled()
	<http://andreacensi.github.io/contracts/api/contracts.html#
	module-contracts.enabling>`_ function. From the PyContracts documentation:
	"Returns true if all contracts are disabled"
	"""
	return contracts.all_disabled()


def _create_argument_value_pairs(func, *args, **kwargs):
	"""
	Creates a dictionary where the keys are the argument names and the values
	are the passed arguments values (if any)

	An empty dictionary is returned if an error is detected, such as more
	arguments than in the function definition, argument(s) defined by position
	and keyword, etc.
	"""
	# Capture parameters that have been explicitly specified in function call
	try:
		arg_dict = funcsigs.signature(func).bind_partial(*args, **kwargs).arguments
	except TypeError:
		return dict()
	# Capture parameters that have not been explicitly specified
	# but have default values
	arguments = funcsigs.signature(func).parameters
	for arg_name in arguments:
		if ((arguments[arg_name].default != funcsigs.Parameter.empty) and
		   (arguments[arg_name].name not in arg_dict)):
			arg_dict[arguments[arg_name].name] = arguments[arg_name].default
	return arg_dict


def disable_all():
	"""
	Wraps PyContracts `disable_all()
	<http://andreacensi.github.io/contracts/api/contracts.html#
	module-contracts.enabling>`_ function. From the PyContracts documentation:
	"Disables all contract checks"
	"""
	contracts.disable_all()


def enable_all():
	"""
	Wraps PyContracts `enable_all()
	<http://andreacensi.github.io/contracts/api/contracts.html#
	module-contracts.enabling>`_ function. From the PyContracts documentation:
	"Enables all contract checks. Can be overridden by an environment variable"
	"""
	contracts.enable_all()


def _format_arg(arg):
	""" Validate one exception specification contract tuple/list """
	if (not (isinstance(arg, str) or putil.misc.isexception(arg) or
	   isinstance(arg, tuple) or isinstance(arg, list))):
		raise TypeError('Illegal custom contract exception definition')
	if ((isinstance(arg, tuple) or isinstance(arg, list)) and
	   ((len(arg) == 0) or (len(arg) > 2))):
		raise TypeError('Illegal custom contract exception definition')
	if isinstance(arg, str) and (len(arg) == 0):
		raise ValueError('Empty custom contract exception message')
	if isinstance(arg, str):
		return {'msg':arg, 'type':RuntimeError}
	if putil.misc.isexception(arg):
		return {'msg':'Argument `*[argument_name]*` is not valid', 'type':arg}
	if ((len(arg) == 1) and
	   (not isinstance(arg[0], str)) and
	   (not putil.misc.isexception(arg[0]))):
		raise TypeError('Illegal custom contract exception definition')
	if ((len(arg) == 2) and
	   (not ((isinstance(arg[0], str) and
	   putil.misc.isexception(arg[1])) or
	   (isinstance(arg[1], str) and putil.misc.isexception(arg[0]))))):
		raise TypeError('Illegal custom contract exception definition')
	if (len(arg) == 1) and isinstance(arg[0], str) and (len(arg[0]) == 0):
		raise ValueError('Empty custom contract exception message')
	if ((len(arg) == 2) and ((isinstance(arg[0], str) and (len(arg[0]) == 0)) or
	   (isinstance(arg[1], str) and (len(arg[1]) == 0)))):
		raise ValueError('Empty custom contract exception message')
	if len(arg) == 1:
		return {
			'msg':arg[0] if isinstance(arg[0], str) else
			'Argument `*[argument_name]*` is not valid',
			'type':arg[0] if putil.misc.isexception(arg[0]) else RuntimeError
		}
	else:	# len(arg) == 2
		return {
			'msg':arg[0] if isinstance(arg[0], str) else arg[1],
			'type':arg[0] if putil.misc.isexception(arg[0]) else arg[1]
		}


def _get_contract_exception_dict(contract_msg):
	""" Generate message for exception """
	# Get contract name:
	start_token = '[START CONTRACT MSG: '
	stop_token = '[STOP CONTRACT MSG]'
	if contract_msg.find(start_token) == -1:
		return {
			'num':0,
			'msg':'Argument `*[argument_name]*` is not valid',
			'type':RuntimeError, 'field':'argument_name'
		}
	else:
		contract_msg = contract_msg[contract_msg.find(start_token)+len(start_token):]
		contract_name = contract_msg[:contract_msg.find(']')]
		contract_msg = contract_msg[
			contract_msg.find(']')+1:contract_msg.find(stop_token)
		]
		exdict = _CUSTOM_CONTRACTS[contract_name]
		for exvalue in exdict.values():	# pragma: no branch
			if exvalue['msg'] == contract_msg:
				return exvalue


def _get_custom_contract(param_contract):
	"""
	Returns True if the parameter contract is a custom contract,
	False otherwise
	"""
	if not isinstance(param_contract, str):
		return None
	for custom_contract in _CUSTOM_CONTRACTS:
		if re.search(r'\b{0}\b'.format(custom_contract), param_contract):
			return custom_contract
	return None


def get_exdesc():
	"""
	Retrieves the contract exception(s) message(s). If the custom contract is
	specified with only one exception the return value is the message
	associated with that exception; if the custom contract is specified with
	several exceptions, the return value is a dictionary whose keys are the
	exception names and whose values are the exception messages.

	:raises: RuntimeError (Function object could not be found for
	 function *[function_name]*)
	:rtype: string or dictionary

	For example:

	.. =[=cog
	.. import docs.support.incfile
	.. docs.support.incfile.incfile('pcontracts_example_2.py', cog)
	.. =]=
	.. code-block:: python

	    # pcontracts_example_2.py
	    import putil.pcontracts

	    @putil.pcontracts.new_contract('Only one exception')
	    def custom_contract_a(name):
	        msg = putil.pcontracts.get_exdesc()
	        if not name:
	            raise ValueError(msg)

	    @putil.pcontracts.new_contract(ex1='Empty name', ex2='Invalid name')
	    def custom_contract_b(name):
	        msg = putil.pcontracts.get_exdesc()
	        if not name:
	            raise ValueError(msg['ex1'])
	        elif name.find('[') != -1:
	            raise ValueError(msg['ex2'])

	.. =[=end=]=


	In :code:`custom_contract1()` the variable :code:`msg` contains the string
	``'Only one exception'``, in :code:`custom_contract2()` the variable
	:code:`msg` contains the dictionary
	:code:`{'ex1':'Empty name', 'ex2':'Invalid name'}`.

	"""
	sobj = inspect.stack()
	# First frame is own function (get_exdesc), next frame is the calling
	# function, of which its name is needed
	fname = sobj[1][3]
	# Get globals variables, where function attributes reside
	for sitem in sobj[1:]:
		fobj = (sitem[0].f_locals[fname]
			   if fname in sitem[0].f_locals else
			   (sitem[0].f_globals[fname] if fname in sitem[0].f_globals else None))
		if fobj and hasattr(fobj, 'exdesc'):
			break
	else:
		raise RuntimeError(
			'Function object could not be found for function `{0}`'.format(fname)
		)
	# Return function attribute created by new contract decorator
	exdesc = getattr(fobj, 'exdesc')
	return exdesc if len(exdesc) > 1 else exdesc[exdesc.keys()[0]]


def _get_num_contracts(contracts_list, param_name):
	"""
	Returns the number of simple/default contracts (the ones which raise a
	RuntimeError with message 'Argument `*[argument_name]*` is not valid'
	"""
	msg = 'Argument `*[argument_name]*` is not valid'
	return sum([
		1 if item['msg'] == msg.replace('*[argument_name]*', param_name) else 0
		for item in contracts_list
	])


def _get_replacement_token(msg):
	""" Extract replacement token from exception message """
	return (None
		   if not re.search(r'\*\[[\w|\W]+\]\*', msg) else
		   re.search(r'\*\[[\w|\W]+\]\*', msg).group()[2:-2])


def _parse_new_contract_args(*args, **kwargs):
	""" Parse argument for new_contract() function """
	# No arguments
	if (len(args) == 0) and (len(kwargs) == 0):
		return [{
			'name':'argument_invalid',
			'msg':'Argument `*[argument_name]*` is not valid',
			'type':RuntimeError
		}]
	# Process args
	if (len(args) > 1) or ((len(args) == 1) and (len(kwargs) > 0)):
		raise TypeError('Illegal custom contract exception definition')
	elif len(args) == 1:
		return [dict([('name', 'default')]+_format_arg(args[0]).items())]
	# Process kwargs
	return [
		dict([('name', name)]+_format_arg(kwargs[name]).items())
		for name in sorted(kwargs.keys())
	]


def _register_custom_contracts(contract_name, contract_exceptions):
	""" Homogenize custom contract exception definition """
	# pylint: disable=W0602
	global _CUSTOM_CONTRACTS
	# Validate arguments and homogenize contract exceptions
	if not isinstance(contract_name, str):
		raise TypeError('Argument `contract_name` is of the wrong type')
	# A contract exception can be a string (only one exception, default
	# exception type) or a dictionary of exception definitions, if there is
	# more than one or if the type if different than the default
	if ((not isinstance(contract_exceptions, list)) and
	   (not isinstance(contract_exceptions, str)) and
	   (not isinstance(contract_exceptions, dict))):
		raise TypeError('Argument `contract_exceptions` is of the wrong type')
	if isinstance(contract_exceptions, dict):
		contract_exceptions = [contract_exceptions]
	if (isinstance(contract_exceptions, list) and
	   any([not isinstance(key, str)
			for item in contract_exceptions
			for key in item.iterkeys()])):
		raise TypeError('Contract exception definition is of the wrong type')
	# Validate individual exception definitions
	if (isinstance(contract_exceptions, list) and
	   any([not ((set(item.keys()) == set(['name', 'msg'])) or
		    (set(item.keys()) == set(['name', 'msg', 'type'])))
			for item in contract_exceptions])):
		raise TypeError('Contract exception definition is of the wrong type')
	extype = type(ValueError)
	if (isinstance(contract_exceptions, list) and
	   any([(not isinstance(item['name'], str)) or
			(not isinstance(item['msg'], str)) or
			(not isinstance(item.get('type', extype), extype))
			for item in contract_exceptions])):
		raise TypeError('Contract exception definition is of the wrong type')
	# Homogenize exception definitions
	if isinstance(contract_exceptions, list):
		homogenized_exdict = dict([(
			exdict['name'], {
				'num':exnum,
				'msg':exdict['msg'],
				'type':exdict.get('type', RuntimeError),
				'field':_get_replacement_token(exdict['msg'])
			}) for exnum, exdict in enumerate(contract_exceptions)])
	else:
		homogenized_exdict = {
			'default':{
				'num':0,
				'msg':contract_exceptions,
				'type':RuntimeError,
				'field':_get_replacement_token(contract_exceptions)
			}
		}
	# Verify exception names are unique
	if (isinstance(contract_exceptions, list) and
	   (len(homogenized_exdict) != len(contract_exceptions))):
		raise ValueError('Contract exception names are not unique')
	# Verify that exception messages are unique
	msgs = [exvalue['msg'] for exvalue in homogenized_exdict.values()]
	if len(set(msgs)) != len(msgs):
		raise ValueError('Contract exception messages are not unique')
	# Verify that a custom contract is not being redefined
	if ((contract_name in _CUSTOM_CONTRACTS) and
	   (_CUSTOM_CONTRACTS[contract_name] != contract_exceptions)):
		raise RuntimeError(
			'Attempt to redefine custom contract `{0}`'.format(contract_name)
		)
	# Verify that there are at most only two replacement fields, and one of
	# them should be argument_name
	fields = [
		exdict['field'] for exdict in homogenized_exdict.values()
		if exdict['field'] is not None
	]
	if ((len(fields) > 2) or
	   ((len(fields) == 2) and (fields[0] != 'argument_name') and
	   (fields[1] != 'argument_name'))):
		raise ValueError(
			'Multiple replacement fields to be substituted by argument value'
		)
	# Register new contract
	_CUSTOM_CONTRACTS[contract_name] = homogenized_exdict
	return contract_exceptions


###
# Decorators
###
def contract(**contract_args):
	r"""
	Wraps PyContracts `contract() <http://andreacensi.github.io/contracts/
	api_reference.html#module-contracts>`_ decorator (only the decorator way
	of specifying a contract is supported and tested). A :code:`RuntimeError`
	exception with the message :code:`'Argument \`*[argument_name]*\` is not
	valid'` is raised when a contract is breached (:code:`'*[argument_name]*'`
	is replaced by the argument name the contract is attached to) unless the
	contract is custom and specified with the
	:py:func:`putil.pcontracts.new_contract` decorator. In this case the
	exception type and message are controlled by the custom
	contract specification.
	"""
	# pylint: disable=W0212,W0631
	@decorator.decorator
	def wrapper(func, *args, **kwargs):
		""" Decorator """
		# Register exceptions if exception handler object exists
		if all_disabled():
			return func(*args, **kwargs)
		exhobj = putil.exh.get_exh_obj()
		if exhobj is not None:
			for param_name, param_contract in contract_args.iteritems():
				# param_name=param_value, as in num='str|float'
				contracts_dicts = list()
				# Create dictionary of custom contracts
				if _get_custom_contract(param_contract):
					key = _get_custom_contract(param_contract)
					contracts_dicts += _CUSTOM_CONTRACTS[key].values()
				else: # Add regular PyContracts contracts
					msg = 'Argument `*[argument_name]*` is not valid'
					contracts_dicts += [{
						'num':_get_num_contracts(contracts_dicts, param_name),
						'type':RuntimeError,
						'msg':msg.replace('*[argument_name]*', param_name)
					}]
				for exdict in contracts_dicts:
					exname = 'contract_{0}_{1}_{2}'.format(
						func.__name__,
						param_name,
						exdict['num']
					)
					exhobj.add_exception(
						exname=exname,
						extype=exdict['type'],
						exmsg=exdict['msg'].replace('*[argument_name]*', param_name)
					)
		# Argument validation. PyContracts "entry" is the
		# contracts.contract_decorator, which has some logic to figure out
		# which way the contract was specified. Since this module (pcontracts)
		# supports only the decorator way of specifying the contracts, all the
		# mentioned logic can be bypassed by calling
		# contracts.contracts_decorate, which is renamed to contracts.decorate
		# in the contracts __init__.py file
		try:
			return contracts.decorate(func, False, **contract_args)(*args, **kwargs)
		except contracts.ContractSyntaxError:
			raise
		except contracts.ContractNotRespected as eobj:
			# Extract which function parameter triggered exception
			param_dict = _create_argument_value_pairs(func, *args, **kwargs)
			# re.search returns the string with quotes in it
			param_name = re.search(r"'\w+'", eobj.error).group()[1:-1]
			# Raise exception
			exdict = _get_contract_exception_dict(eobj.error)
			exname = 'contract_{0}_{1}_{2}'.format(
				func.__name__,
				param_name,
				exdict['num']
			)
			edata = {
				'field':exdict['field'],
				'value':param_dict[param_name]
			} if (exdict['field'] and (exdict['field'] != 'argument_name')) else None
			if exhobj is not None:
				exhobj.raise_exception_if(exname=exname, condition=True, edata=edata)
			else:
				# Pick "nice" variable names because the raise line is going to
				# be shown in the exception traceback
				exception_type = exdict['type']
				exception_message = exdict['msg'].replace(
					'*[{0}]*'.format(exdict['field']),
					param_name if exdict['field'] == 'argument_name' else
					'{0}'.format(param_dict[param_name])
				)
				raise exception_type(exception_message)
	return wrapper


def new_contract(*args, **kwargs):
	r"""
	Defines a new (custom) contract with custom exceptions.

	:raises:
	 * RuntimeError (Attempt to redefine custom contract \`*[contract_name]*\`)

	 * TypeError (Argument \`contract_exceptions\` is of the wrong type)

	 * TypeError (Argument \`contract_name\` is of the wrong type)

	 * TypeError (Contract exception definition is of the wrong type)

	 * TypeError (Illegal custom contract exception definition)

	 * ValueError (Empty custom contract exception message)

	 * ValueError (Contract exception messages are not unique)

	 * ValueError (Contract exception names are not unique)

	 * ValueError (Multiple replacement fields to be substituted by
	   argument value)


	The decorator argument(s) is(are) the exception(s) that can be raised by
	the contract. The most general way to define an exception is using a
	2-item tuple with the following members:

	 * **exception type** *(type)* -- Either a built-in exception or
	   sub-classed from Exception. Default is ``RuntimeError``

	 * **exception message** *(string)* -- Default is
	   ``'Argument `*[argument_name]*` is not valid'``, where the token
	   :code:`*[argument_name]*` is replaced by the argument name the contract
	   is attached to

	The order of the tuple elements is not important, i.e. the following are
	valid exception specifications and define the same exception:

	.. =[=cog
	.. import docs.support.incfile
	.. docs.support.incfile.incfile('pcontracts_example_3.py', cog, '8-16')
	.. =]=
	.. code-block:: python

	    @putil.pcontracts.new_contract(ex1=(RuntimeError, 'Invalid name'))
	    def custom_contract1(arg):
	        if not arg:
	            raise ValueError(putil.pcontracts.get_exdesc())

	    @putil.pcontracts.new_contract(ex1=('Invalid name', RuntimeError))
	    def custom_contract2(arg):
	        if not arg:
	            raise ValueError(putil.pcontracts.get_exdesc())

	.. =[=end=]=

	The exception definition simplifies to just one of the exception definition
	tuple items if the other exception definition tuple item takes its
	default value. For example, the same exception is defined in these two
	contracts:

	.. =[=cog
	.. import docs.support.incfile
	.. docs.support.incfile.incfile('pcontracts_example_3.py', cog, '18-29')
	.. =]=
	.. code-block:: python

	    @putil.pcontracts.new_contract(ex1=ValueError)
	    def custom_contract3(arg):
	        if not arg:
	            raise ValueError(putil.pcontracts.get_exdesc())

	    @putil.pcontracts.new_contract(ex1=(
	        ValueError,
	        'Argument `*[argument_name]*` is not valid'
	    ))
	    def custom_contract4(arg):
	        if not arg:
	            raise ValueError(putil.pcontracts.get_exdesc())

	.. =[=end=]=

	and these contracts also define the same exception (but different from that
	of the previous example):

	.. =[=cog
	.. import docs.support.incfile
	.. docs.support.incfile.incfile('pcontracts_example_3.py', cog, '31-39')
	.. =]=
	.. code-block:: python

	    @putil.pcontracts.new_contract(ex1='Invalid name')
	    def custom_contract5(arg):
	        if not arg:
	            raise ValueError(putil.pcontracts.get_exdesc())

	    @putil.pcontracts.new_contract(ex1=('Invalid name', RuntimeError))
	    def custom_contract6(arg):
	        if not arg:
	            raise ValueError(putil.pcontracts.get_exdesc())

	.. =[=end=]=

	In fact the exception need not be specified by keyword if the contract only
	uses one exception. All of the following are valid one-exception contract
	specifications:

	.. =[=cog
	.. import docs.support.incfile
	.. docs.support.incfile.incfile('pcontracts_example_3.py', cog, '41-57')
	.. =]=
	.. code-block:: python

	    @putil.pcontracts.new_contract((IOError, 'File could not be opened'))
	    def custom_contract7(arg):
	        if not arg:
	            raise ValueError(putil.pcontracts.get_exdesc())

	    # Define contract that uses exception (RuntimeError, 'Invalid name')
	    @putil.pcontracts.new_contract('Invalid name')
	    def custom_contract8(arg):
	        if not arg:
	            raise ValueError(putil.pcontracts.get_exdesc())

	    # Define contract that uses exception
	    # (TypeError, 'Argument `*[argument_name]*` is not valid')
	    @putil.pcontracts.new_contract(TypeError)
	    def custom_contract9(arg):
	        if not arg:
	            raise ValueError(putil.pcontracts.get_exdesc())

	.. =[=end=]=

	No arguments are needed if a contract only needs a single exception and the
	default exception type and message suffice:

	.. =[=cog
	.. import docs.support.incfile
	.. docs.support.incfile.incfile('pcontracts_example_3.py', cog, '59-64')
	.. =]=
	.. code-block:: python

	    # Define contract that uses exception
	    # (RuntimeError, 'Argument `*[argument_name]*` is not valid')
	    @putil.pcontracts.new_contract()
	    def custom_contract10(arg):
	        if not arg:
	            raise ValueError(putil.pcontracts.get_exdesc())

	.. =[=end=]=

	For code conciseness and correctness the exception message(s) should be
	retrieved via the :py:func:`putil.pcontracts.get_exdesc` function.

	A `PyContracts new contract <http://andreacensi.github.io/contracts/
	new_contract.html#new-contract>`_ can return False or raise a
	:code:`ValueError` exception to indicate a contract breach, however a new
	contract specified via the :py:func:`putil.pcontracts.new_contract`
	decorator *has* to raise a :code:`ValueError` exception to indicate a
	contract breach.

	The exception message can have substitution "tokens" of the form
	:code:`*[token_name]*`. The token :code:`*[argument_name]*` it is
	substituted with the argument name the contract is attached to.
	For example:

	.. =[=cog
	.. import docs.support.incfile
	.. docs.support.incfile.incfile('pcontracts_example_3.py', cog, '66-76')
	.. =]=
	.. code-block:: python

	    @putil.pcontracts.new_contract((
	        TypeError,
	        'Argument `*[argument_name]*` has to be a string'
	    ))
	    def custom_contract11(city):
	        if not isinstance(city, str):
	            raise ValueError(putil.pcontracts.get_exdesc())

	    @putil.pcontracts.contract(city_name='custom_contract11')
	    def print_city_name(city_name):
	        return 'City: {0}'.format(city_name)

	.. =[=end=]=

	.. code-block:: python

		>>> from docs.support.pcontracts_example_3 import print_city_name
		>>> print print_city_name('Omaha')
		City: Omaha
		>>> print print_city_name(5)	#doctest: +ELLIPSIS
		Traceback (most recent call last):
		    ...
		TypeError: Argument `city_name` has to be a string

	Any other token is substituted with the argument *value*. For example:

	.. =[=cog
	.. import docs.support.incfile
	.. docs.support.incfile.incfile('pcontracts_example_3.py', cog, '78-')
	.. =]=
	.. code-block:: python

	    @putil.pcontracts.new_contract((
	        IOError, 'File `*[file_name]*` not found'
	    ))
	    def custom_contract12(file_name):
	        if not os.path.exists(file_name):
	            raise ValueError(putil.pcontracts.get_exdesc())

	    @putil.pcontracts.contract(file_name='custom_contract12')
	    def print_file_name(file_name):
	        print 'File name to find: {0}'.format(file_name)

	.. =[=end=]=

	.. code-block:: python

		>>> import os
		>>> from docs.support.pcontracts_example_3 import print_file_name
		>>> file_name = os.path.join(os.sep, 'dev', 'null', '_not_a_file_')
		>>> print print_file_name(file_name)	#doctest: +ELLIPSIS
		Traceback (most recent call last):
		    ...
		IOError: File `/dev/null/_not_a_file_` not found

	"""
	def wrapper(func):
		""" Decorator """
		contract_name = func.__name__
		exdesc = _parse_new_contract_args(*args, **kwargs)
		# Pass to the custom contract, via a property, only the
		# exception descriptions
		func.exdesc = dict([
			(value['name'],
			 '[START CONTRACT MSG: {0}]{1}[STOP CONTRACT MSG]'.format(
					contract_name,
					value['msg']
				)
			) for value in exdesc
		])
		# Register custom contract
		_register_custom_contracts(contract_name, exdesc)
		# Apply PyContracts decorator
		return contracts.new_contract(func)
	return wrapper


###
# Custom contracts
###
@new_contract()
def file_name(obj):
	r"""
	Validates if an object is a legal name for a file
	(i.e. does not have extraneous characters, etc.)

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not
	 valid). The token \*[argument_name]\* is replaced by the name
	 of the argument the contract is attached to
	:rtype: None
	"""
	msg = get_exdesc()
	# Check that argument is a string
	if not isinstance(obj, str):
		raise ValueError(msg)
	# If file exists, argument is a valid file name, otherwise test
	# if file # can be created. User may not have permission to
	# write file, but call to os.access should not fail if the file
	# name is correct
	try:
		if not os.path.exists(obj):
			os.access(obj, os.W_OK)
	except TypeError:
		raise ValueError(msg)


@new_contract(
	argument_invalid='Argument `*[argument_name]*` is not valid',
	file_not_found=(
		IOError,
		'File `*[file_name]*` could not be found'
	)
)
def file_name_exists(obj):
	r"""
	Validates if an object is a legal name for a file
	(i.e. does not have extraneous characters, etc.) *and* that the
	file exists

	:param	obj: Object
	:type	obj: any
	:raises:
	 * IOError (File \`*[file_name]*\` could not be found). The
	   token \*[file_name]\* is replaced by the *value* of the
	   argument the contract is attached to

	 * RuntimeError (Argument \`*[argument_name]*\` is not valid).
	   The token \*[argument_name]\* is replaced by the name of
	   the argument the contract is attached to

	:rtype: None
	"""
	exdesc = get_exdesc()
	msg = exdesc['argument_invalid']
	# Check that argument is a string
	if not isinstance(obj, str):
		raise ValueError(msg)
	# Check that file name is valid
	try:
		os.path.exists(obj)
	except TypeError:
		raise ValueError(msg)
	# Check that file exists
	if not os.path.exists(obj):
		msg = exdesc['file_not_found']
		raise ValueError(msg)
