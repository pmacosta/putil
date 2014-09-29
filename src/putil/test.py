# test.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Helper methods for unit testing
"""

import sys
import pytest

import putil.misc


def full_command_name(cmd):
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


def evaluate_value_series(cmd, pairs, offset=0):
	""" Evaluates results of a command with multiple argument/value pairs """
	pairs = pairs if isinstance(pairs, list) else [pairs]
	cmd_name = full_command_name(cmd)
	# Evaluate pairs and produce readable test list
	expected_list = list()
	actual_list = list()
	comp_text = '[{0}] {1}({2}) == {3}'
	for num, (value, expected_result) in enumerate(pairs):
		actual_result = cmd(value)
		expected_list.append(comp_text.format(num+offset, cmd_name, value, expected_result))
		actual_list.append(comp_text.format(num+offset, cmd_name, value, actual_result))
	expected_msg, actual_msg = '\n'.join(expected_list), '\n'.join(actual_list)
	return expected_msg, actual_msg

def evaluate_command_value_series(cmd_pairs):
	""" Evaluates results of a series of command/value/result cases """
	exolist = [evaluate_value_series(cmd, (value, result), num) for num, (cmd, value, result) in enumerate(cmd_pairs)]
	expected_msg, actual_msg = '\n'.join(element[0] for element in exolist), '\n'.join(element[1] for element in exolist)
	return expected_msg, actual_msg

def evaluate_exception_series(cmd, exdesc, offset=0):	#pylint: disable=R0914
	""" Evaluates commands that should raise an exception """
	exdesc = exdesc if isinstance(exdesc, list) else [exdesc]
	cmd_name = full_command_name(cmd)
	# Evaluate pairs and produce readable test list
	expected_list = list()
	actual_list = list()
	comp_text = '[{0}] {1}({2}) -> {3}'
	ex_text = '{0} ({1})'
	for num, (args, extype, exmsg) in enumerate(exdesc):
		arg_text = ', '.join(['{0}={1}'.format(key, putil.misc.quote_str(value)) for key, value in args.items()])
		expected_msg = 'DID NOT RAISE' if (extype, exmsg) == (None, None) else ex_text.format(exception_type_str(extype), exmsg)
		try:
			cmd(**args)	#pylint: disable=W0142
		except:	#pylint: disable=W0702
			eobj = sys.exc_info()
			actual_msg = ex_text.format(exception_type_str(eobj[0]), eobj[1])
		else:
			actual_msg = 'DID NOT RAISE'
		expected_list.append(comp_text.format(num+offset, cmd_name, arg_text, expected_msg))
		actual_list.append(comp_text.format(num+offset, cmd_name, arg_text, actual_msg))
	expected_msg, actual_msg = '\n'.join(expected_list), '\n'.join(actual_list)
	return expected_msg, actual_msg

