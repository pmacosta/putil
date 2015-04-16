# test.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import pytest
import re


###
# Functions
###
def exception_type_str(extype):
	"""
	Returns an exception type string

	:param	extype: Exception
	:type	extype: type
	:rtype: string

	For example:

		>>> import putil.test
		>>> exception_type_str(RuntimeError)
		'RuntimeError'
	"""
	return str(extype).split('.')[-1][:-2]


def assert_exception(obj, args, extype, exmsg):
	"""
	Asserts an exception type and message within the Py.test environment. If
	the actual exception message and the expected exception message do not
	literally match then the expected exception message is treated as a
	regular expression and a match is sought with the actual exception message

	:param	obj: Object to evaluate
	:type	obj: callable
	:param	args: Keyword arguments to pass to object
	:type	args: dictionary
	:param	extype: Expected exception type
	:type	extype: type
	:param	exmsg: Expected exception message (can have regular expressions)
	:type	exmsg: string
	:rtype: None

	For example:

		>>> import putil.test, putil.eng
		>>> try:
		...     putil.test.assert_exception(
		...         putil.eng.peng,
		...         {'number':5, 'frac_length':3, 'rjust':True},
		...         RuntimeError,
		...         'Argument `number` is not valid'
		...     )	#doctest: +ELLIPSIS
		... except AssertionError:
		...     raise RuntimeError('Test failed')
		Traceback (most recent call last):
		    ...
		RuntimeError: Test failed
	"""
	# pylint: disable=W0142,W0703
	regexp = re.compile(exmsg)
	try:
		with pytest.raises(extype) as excinfo:
			obj(**args)
	except Exception as eobj:
		if eobj.message == 'DID NOT RAISE':
			raise AssertionError
		eobj_extype = repr(eobj)[:repr(eobj).find('(')]
		assert '{0} ({1})'.format(
			eobj_extype,
			eobj.message
		) == '{0} ({1})'.format(exception_type_str(extype), exmsg)
	if ((exception_type_str(excinfo.type) == exception_type_str(extype)) and
	   ((excinfo.value.message == exmsg) or regexp.match(excinfo.value.message))):
		assert True
	else:
		assert '{0} ({1})'.format(
			exception_type_str(excinfo.type),
			excinfo.value.message
		) == '{0} ({1})'.format(exception_type_str(extype), exmsg)
