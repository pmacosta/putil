# ptypes.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import inspect
import numpy
import os

import putil.pcontracts


###
# Global variables
###
_SUFFIX_TUPLE = (
	'y', 'z', 'a', 'f', 'p', 'n', 'u', 'm',
	' ',
	'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'
)


###
# Functions
###
@putil.pcontracts.new_contract()
def engineering_notation_number(obj):
	r"""
	Validates if an object is a number represented in engineering notation

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
	 token \*[argument_name]\* is replaced by the name of the argument the
	 contract is attached to

	:rtype: None
	"""
	try:
		obj = obj.rstrip()
		float(obj[:-1] if obj[-1] in _SUFFIX_TUPLE else obj)
		return None
	except (AttributeError, IndexError, ValueError):
		# AttributeError: obj.rstrip(), object could not be a string
		# IndexError: obj[-1], when an empty string
		# ValueError: float(), when not a string representing a number
		raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def engineering_notation_suffix(obj):
	r"""
	Validates if an object is an engineering notation suffix

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
	 token \*[argument_name]\* is replaced by the *name* of the argument the
	 contract is attached to

	:rtype: None
	"""
	try:
		assert obj in _SUFFIX_TUPLE
	except AssertionError:
		raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def non_negative_integer(obj):
	r"""
	Validates if an object is a positive integer

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
	 token \*[argument_name]\* is replaced by the *name* of the argument the
	 contract is attached to

	:rtype: None
	"""
	if isinstance(obj, int) and (obj >= 0):
		return None
	raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def real_num(obj):
	r"""
	Validates if an object is an integer, float or :code:`None`

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
	 token \*[argument_name]\* is replaced by the name of the argument the
	 contract is attached to

	:rtype: None
	"""
	if ((obj is None) or
	   ((isinstance(obj, int) or isinstance(obj, float)) and
	   (not isinstance(obj, bool)))):
		return None
	raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def positive_real_num(obj):
	r"""
	Validates if an object is a positive integer, positive float
	or :code:`None`

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
	 token \*[argument_name]\* is replaced by the name of the argument the
	 contract is attached to

	:rtype: None
	"""
	if ((obj is None) or ((isinstance(obj, int) or
	   isinstance(obj, float)) and (obj > 0) and (not isinstance(obj, bool)))):
		return None
	raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def offset_range(obj):
	r"""
	Validates if an object is a number in the [0, 1] range

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
	 token \*[argument_name]\* is replaced by the name of the argument the
	 contract is attached to

	:rtype: None
	"""
	if ((isinstance(obj, int) or isinstance(obj, float)) and
	   (not isinstance(obj, bool)) and (obj >= 0) and (obj <= 1)):
		return None
	raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def function(obj):
	r"""
	Validates if an object is a function pointer or :code:`None`

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
	 token \*[argument_name]\* is replaced by the name of the argument the
	 contract is attached to

	:rtype: None
	"""
	if (obj is None) or inspect.isfunction(obj):
		return None
	raise ValueError(putil.pcontracts.get_exdesc())


def _check_real_numpy_vector(obj):
	if ((type(obj) == numpy.ndarray) and
	   (len(obj.shape) == 1) and (obj.shape[0] > 0) and
	   ((obj.dtype.type == numpy.array([0]).dtype.type) or
	   (obj.dtype.type == numpy.array([0.0]).dtype.type))):
		return False
	return True


@putil.pcontracts.new_contract()
def real_numpy_vector(obj):
	r"""
	Validates if an object is a Numpy vector or vector with integer or
	floating point numbers

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
	 token \*[argument_name]\* is replaced by the name of the argument the
	 contract is attached to

	:rtype: None
	"""
	if _check_real_numpy_vector(obj):
		raise ValueError(putil.pcontracts.get_exdesc())


def _check_increasing_real_numpy_vector(obj):
	# pylint: disable=C0103
	if ((type(obj) != numpy.ndarray) or ((type(obj) == numpy.ndarray) and
	   ((len(obj.shape) > 1) or ((len(obj.shape) == 1) and
	   (obj.shape[0] == 0))))):
		return True
	if (((obj.dtype.type == numpy.array([0]).dtype.type) or
	   (obj.dtype.type == numpy.array([0.0]).dtype.type)) and
	   ((obj.shape[0] == 1) or ((obj.shape[0] > 1) and
	   (not min(numpy.diff(obj)) <= 0)))):
		return False
	return True


@putil.pcontracts.new_contract()
def increasing_real_numpy_vector(obj):
	r"""
	Validates if an object is a Numpy vector with numbers that
	are monotonically increasing

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
	 token \*[argument_name]\* is replaced by the name of the argument the
	 contract is attached to

	:rtype: None
	"""
	if _check_increasing_real_numpy_vector(obj):
		raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract(
	argument_invalid='Argument `*[argument_name]*` is not valid',
	argument_bad_choice=(ValueError, "Argument `*[argument_name]*` is not one "
					                 "of ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']"
					                 " (case insensitive)")
)
def interpolation_option(obj):
	r"""
	Validates if an object is a valid series interpolation type.
	Valid options are :code:`None`, :code:`'STRAIGHT'`, :code:`'STEP'`,
	:code:`'CUBIC'` or :code:`'LINREG'`

	:param	obj: Object
	:type	obj: any
	:raises:
	 * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
	   \*[argument_name]\* is replaced by the name of the argument the contract
	   is attached to

	 * RuntimeError (Argument \`*[argument_name]*\` is not one of ['STRAIGHT',
	   'STEP', 'CUBIC', 'LINREG'] (case insensitive)). The token
	   \*[argument_name]\* is replaced by the name of the argument
	   the contract is attached to

	:rtype: None
	"""
	exdesc = putil.pcontracts.get_exdesc()
	if (obj is not None) and (not isinstance(obj, str)):
		raise ValueError(exdesc['argument_invalid'])
	if ((obj is None) or
	   (obj and any([
		   item.lower() == obj.lower()
		   for item in ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']]))):
		return None
	raise ValueError(exdesc['argument_bad_choice'])


@putil.pcontracts.new_contract(
	argument_invalid='Argument `*[argument_name]*` is not valid',
	argument_bad_choice=(ValueError, "Argument `*[argument_name]*` is not one"
					                 " of ['-', '--', '-.', ':']")
)
def line_style_option(obj):
	r"""
	Validates if an object is a valid Matplotlib line style.
	Valid options are :code:`None`, :code:`'-'`, :code:`'--'`, :code:`'-.'` or
	:code:`':'`

	:param	obj: Object
	:type	obj: any
	:raises:
	 * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
	   \*[argument_name]\* is replaced by the name of the argument the contract
	   is attached to

	 * RuntimeError (Argument \`*[argument_name]*\` is not one of ['-', '--',
	   '-.', ':']). The token \*[argument_name]\* is replaced by the name of
	   the argument the contract is attached to

	:rtype: None
	"""
	exdesc = putil.pcontracts.get_exdesc()
	if (obj is not None) and (not isinstance(obj, str)):
		raise ValueError(exdesc['argument_invalid'])
	if obj in [None, '-', '--', '-.', ':']:
		return None
	raise ValueError(exdesc['argument_bad_choice'])


@putil.pcontracts.new_contract(
	argument_invalid='Argument `*[argument_name]*` is not valid',
	argument_bad_choice=(ValueError, "Argument `*[argument_name]*` is not one "
					                 "of 'binary', 'Blues', 'BuGn', 'BuPu', "
					                 "'GnBu', 'Greens', 'Greys', 'Oranges', "
					                 "'OrRd', 'PuBu', 'PuBuGn', 'PuRd', "
					                 "'Purples', 'RdPu', 'Reds', 'YlGn', "
					                 "'YlGnBu', 'YlOrBr' or 'YlOrRd' "
					                 "(case insensitive)")
)
def color_space_option(obj):
	r"""
	Validates if an object is a valid Matplotlib colors space, one of
	:code:`'binary'`, :code:`'Blues'`, :code:`'BuGn'`, :code:`'BuPu'`,
	:code:`'GnBu'`, :code:`'Greens'`, :code:`'Greys'`, :code:`'Oranges'`,
	:code:`'OrRd'`, :code:`'PuBu'`, :code:`'PuBuGn'`, :code:`'PuRd'`,
	:code:`'Purples'`, :code:`'RdPu'`, :code:`'Reds'`, :code:`'YlGn'`,
	:code:`'YlGnBu'`, :code:`'YlOrBr`', :code:`'YlOrRd'` or :code:`None`

	:param	obj: Object
	:type	obj: any
	:raises:
	 * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
	   \*[argument_name]\* is replaced by the name of the argument the contract
	   is attached to

	 * RuntimeError (Argument \`*[argument_name]*\` is not one of 'binary',
	   'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd',
	   'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu',
	   'YlOrBr' or 'YlOrRd). The token \*[argument_name]\* is replaced by the
	   name of the argument the contract is attached to

	:rtype: None
	"""
	exdesc = putil.pcontracts.get_exdesc()
	if (obj is not None) and (not isinstance(obj, str)):
		raise ValueError(exdesc['argument_invalid'])
	if (obj is None) or (obj and any([
			item.lower() == obj.lower()
			for item in [
					'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens',
					'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd',
					'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu',
					'YlOrBr', 'YlOrRd'
			]
	])):
		return None
	raise ValueError(exdesc['argument_bad_choice'])


@putil.pcontracts.new_contract(
	argument_invalid='Argument `*[argument_name]*` is not valid',
	argument_empty=(ValueError, 'Argument `*[argument_name]*` is empty')
)
def csv_data_filter(obj):
	r"""
	Validates if an object is a dictionary that represents a
	CsvDataFilter pseudo-type object

	:param	obj: Object
	:type	obj: any
	:raises:
	 * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
	   \*[argument_name]\* is replaced by the *name* of the argument the
	   contract is attached to

	 * ValueError (Argument \`*[argument_name]*\` is empty). The token
	   \*[argument_name]\* is replaced by the *name* of the argument the
	   contract is attached to

	:rtype: None
	"""
	exdesc = putil.pcontracts.get_exdesc()
	if obj is None:
		return None
	if not isinstance(obj, dict):
		raise ValueError(exdesc['argument_invalid'])
	if not len(obj):
		raise ValueError(exdesc['argument_empty'])
	if any([not isinstance(col_name, str) for col_name in obj.iterkeys()]):
		raise ValueError(exdesc['argument_invalid'])
	for col_name, col_value in obj.items():	# pragma: no branch
		if ((not isinstance(obj[col_name], list)) and
		   (not putil.misc.isnumber(obj[col_name])) and
		   (not isinstance(obj[col_name], str))):
			raise ValueError(exdesc['argument_invalid'])
		if isinstance(col_value, list):
			for element in col_value:	# pragma: no branch
				if ((not putil.misc.isnumber(element)) and
				   (not isinstance(element, str))):
					raise ValueError(exdesc['argument_invalid'])


@putil.pcontracts.new_contract()
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
	msg = putil.pcontracts.get_exdesc()
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


@putil.pcontracts.new_contract(
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
	exdesc = putil.pcontracts.get_exdesc()
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
