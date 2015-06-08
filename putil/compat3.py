# compat3.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0122,W0613


def _rwtb(extype, exmsg, extb):	# pragma: no cover
	""" Python 3 exception raising with traceback """
	raise extype(exmsg).with_traceback(extb)


def _raise_exception(exception_object):
	""" Raise exception with short traceback """
	exec('raise exception_object from None')


def _read(fname):
	""" Read data from file """
	with open(fname, 'r', newline='\r\n') as frobj:
		return frobj.read()


def _write(fobj, data):
	""" Write data to file """
	fobj.write(bytes(data, 'ascii'))


def _ex_type_str(exobj):
	""" Returns a string corresponding to the exception type """
	return str(exobj).split("'")[1].split('.')[-1]


def _get_func_code(obj):
	""" Get funcion code """
	return obj.__code__


def _get_ex_msg(obj):
	""" Get exception message """
	return obj.value.args[0] if hasattr(obj, 'value') else obj.args[0]


def _unicode_char(char):
	""" Returns true if character is Unicode (non-ASCII) character """
	try:
		char.encode('ascii')
	except UnicodeEncodeError:
		return True
	return False
