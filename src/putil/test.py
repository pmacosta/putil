# test.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Helper methods for unit testing
"""

import sys
import pytest

import putil.check
import putil.misc


def full_callable_name(cmd):
	""" Introspect full name of command """
	cmd_module = cmd.__module__
	cmd_class = cmd.im_class.__name__ if hasattr(cmd, 'im_class') and getattr(cmd, 'im_class') else ''
	cmd_function = cmd.__name__
	cmd_name = '.'.join(filter(None, [cmd_module, cmd_class, cmd_function]))	#pylint: disable=W0141
	return cmd_name


def exception_type_str(extype):
	""" Returns a string with the exception type """
	return str(extype).split('.')[-1][:-2]


def trigger_exception(obj, args, extype, exmsg):
	""" Triggers exception withing the Py.test environment and records value """
	with pytest.raises(extype) as excinfo:
		obj(**args)	#pylint: disable=W0142
	return excinfo.value.message == exmsg


def evaluate_value_series(cmd, pairs, offset=0, return_or_assert=True):
	""" Evaluates results of a command with multiple argument/value pairs """
	pairs = pairs if isinstance(pairs, list) else [pairs]
	# Evaluate pairs and produce readable test list
	expected_list = list()
	actual_list = list()
	comp_text = '[{0}] {1}({2}) == {3}'
	for num, (value, expected_result) in enumerate(pairs):
		actual_result = cmd(value)
		expected_list.append(comp_text.format(num+offset, cmd.im_self, value, expected_result))
		actual_list.append(comp_text.format(num+offset, cmd.im_self, value, actual_result))
	expected_msg, actual_msg = '\n'.join(expected_list), '\n'.join(actual_list)
	if not return_or_assert:
		return expected_msg, actual_msg
	else:
		assert expected_msg == actual_msg

def evaluate_contains_series(cspec_list, cobj=None, offset=0):
	""" Evaluates results of a command with multiple argument/value cspec_list """
	# Convert to list if a single tuples is given (if necessary)
	cspec_list = cspec_list if isinstance(cspec_list, list) else [cspec_list]
	# Add object to list of tuples (if necessary)
	cspec_list = [(cobj, )+cspec_item for cspec_item in cspec_list] if cobj else cspec_list
	# Evaluate contains specification list and produce readable test list
	expected_list = list()
	actual_list = list()
	comp_text = '[{0}] {1} in {2} == {3}'
	for num, (cobj, value, expected_result) in enumerate(cspec_list):
		# Test __contains__
		actual_result = value in cobj
		# Produce expected and actual pretty printed results
		expected_list.append(comp_text.format(num+offset, value, cobj, expected_result))
		actual_list.append(comp_text.format(num+offset, value, cobj, actual_result))
	# Produce final actual vs. expected pretty printed list
	expected_msg, actual_msg = '\n'.join(expected_list), '\n'.join(actual_list)
	# Evaluate results
	assert expected_msg == actual_msg


def evaluate_command_value_series(cmd_pairs, cobj=None):
	""" Evaluates results of a series of command/value/result cases """
	# Convert to list if a single tuples is given (if necessary)
	cmd_pairs = cmd_pairs if isinstance(cmd_pairs, list) else [cmd_pairs]
	# Add object to list of tuples (if necessary)
	cmd_pairs = [(cobj, )+cmd_item for cmd_item in cmd_pairs] if cobj else cmd_pairs
	# Create list of (expected values, actual values) pretty printed tuples
	exolist = [evaluate_value_series(cmd, (value, result), num, return_or_assert=False) for num, (cmd, value, result) in enumerate(cmd_pairs)]
	expected_msg, actual_msg = '\n'.join(element[0] for element in exolist), '\n'.join(element[1] for element in exolist)
	# Evaluate results
	assert expected_msg, actual_msg


def evaluate_exception_series(init_list, cobj=None, offset=0):	#pylint: disable=R0914
	"""
	Monitgor callable(s) for exception raising (exception raised or not, and if it is, type and message)

	:param	init_list: Initialization specification tuple or list of initialization specification tuples. An initialization tuple is of the form (argument dictionary [of the **kwargs form], exception type, exception message) if \
	callable is not specified or (initialization object, argument dictionary, exception type, exception message) otherwise
	:type	init_list: 3 (4)-item tuple or list of 3 (4)-item tuples
	:param	cobj: Object to be called whilst being monitored for exception raising
	:type	cobj: callable
	"""
	# Convert to list if a single tuples is given (if necessary)
	init_list = init_list if isinstance(init_list, list) else [init_list]
	# Add callable object to list of tuples (if necessary)
	init_list = [(cobj, )+init_item for init_item in init_list] if cobj else init_list
	new_init_list = list()
	for init_item in init_list:
		if (len(init_item) == 1) or ((len(init_item) == 2) and (isinstance(init_item[1], dict))):
			init_item = list(init_item)
			init_item += [None, None]
			init_item = tuple(init_item)
		new_init_list.append(init_item)
	init_list = new_init_list
	# Evaluate pairs and produce readable test list
	expected_list = list()
	actual_list = list()
	comp_text = '[{0}] {1}({2}) -> {3}'
	ex_text = '{0} ({1})'
	for num, (cobj, args, extype, exmsg) in enumerate(init_list):
		callable_name = full_callable_name(cobj)
		# Arguments, in the form [argument name]=[argument value] for pretty printing callable call
		arg_text = ', '.join(['{0}={1}'.format(key, putil.misc.quote_str(value)) for key, value in args.items()])
		# Exception text of the form [exception type] ([exception message]) for pretty printing result of callable call
		expected_msg = 'DID NOT RAISE' if (extype, exmsg) == (None, None) else ex_text.format(exception_type_str(extype), exmsg)
		# Monitor callable call for exception raising
		try:
			cobj(**args)	#pylint: disable=W0142
		except:	#pylint: disable=W0702
			eobj = sys.exc_info()
			actual_msg = ex_text.format(exception_type_str(eobj[0]), eobj[1])
		else:
			actual_msg = 'DID NOT RAISE'
		# Produce expected and actual pretty printed results
		expected_list.append(comp_text.format(num+offset, callable_name, arg_text, expected_msg))
		actual_list.append(comp_text.format(num+offset, callable_name, arg_text, actual_msg))
	# Produce final actual vs. expected pretty printed list
	expected_msg, actual_msg = '\n'.join(expected_list), '\n'.join(actual_list)
	# Evaluate results
	assert expected_msg == actual_msg
