# test.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import re
import pytest


def exception_type_str(extype):
	"""
	Returns exception type string. For example:

		>>> exception_type_str(RuntimeError)
		... 'RuntimeError'

	:param	extype: Exception
	:type	extype: type
	:rtype: string
	"""
	return str(extype).split('.')[-1][:-2]


def assert_exception(obj, args, extype, exmsg):
	"""
	Asserts exception type and message within the Py.test environment. If the actual exception message and the expected exception message do not literally match then the expected exception message is
	treated as a regular expression and a match is sought with the actual exception message

	:param	obj: Object to evaluate
	:type	obj: callable
	:param	args: Keyword arguments to pass to object
	:type	args: dictionary
	:param	extype: Expected exception type
	:type	extype: type
	:param	exmsg: Expected exception message (can have regular expressions)
	:type	exmsg: string
	:rtype: None
	"""
	regexp = re.compile(exmsg)
	try:
		with pytest.raises(extype) as excinfo:
			obj(**args)	#pylint: disable=W0142
	except Exception as eobj:	#pylint: disable=W0703
		if eobj.message == 'DID NOT RAISE':
			raise
		eobj_extype = repr(eobj)[:repr(eobj).find('(')]
		if (eobj_extype == exception_type_str(extype)) and ((eobj.message == exmsg) or regexp.match(eobj.message)):
			assert True
		else:
			assert '{0} ({1})'.format(eobj_extype, eobj.message) == '{0} ({1})'.format(exception_type_str(extype), exmsg)
	if (exception_type_str(excinfo.type) == exception_type_str(extype)) and ((excinfo.value.message == exmsg) or regexp.match(excinfo.value.message)):
		assert True
	else:
		assert '{0} ({1})'.format(exception_type_str(excinfo.type), excinfo.value.message) == '{0} ({1})'.format(exception_type_str(extype), exmsg)
