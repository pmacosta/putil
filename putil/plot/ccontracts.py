# ccontracts.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302

import inspect
import numpy

import putil.pcontracts


###
# Contracts
###
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
	if ((type(obj) != numpy.ndarray) or ((type(obj) == numpy.ndarray) and
	   ((len(obj.shape) > 1) or ((len(obj.shape) == 1) and
	   (obj.shape[0] == 0))))):
		return True
	if ((obj.dtype.type == numpy.array([0]).dtype.type) or
	   (obj.dtype.type == numpy.array([0.0]).dtype.type)):
		return False
	return True


@putil.pcontracts.new_contract()
def real_numpy_vector(obj):
	r"""
	Validates if an object is a Numpy vector with integer or
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
	Validates if an object is a valid Matplotlib colors space.
	Valid options are None, :code:`'binary'`, :code:`'Blues'`, :code:`'BuGn'`,
	:code:`'BuPu'`, :code:`'GnBu'`, :code:`'Greens'`, :code:`'Greys'`,
	:code:`'Oranges'`, :code:`'OrRd'`, :code:`'PuBu'`, :code:`'PuBuGn'`,
	:code:`'PuRd'`, :code:`'Purples'`, :code:`'RdPu'`, :code:`'Reds'`,
	:code:`'YlGn'`, :code:`'YlGnBu'`, :code:`'YlOrBr`'
	or :code:`'YlOrRd'`

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
