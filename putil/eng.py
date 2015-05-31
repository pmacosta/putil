# eng.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0105,W0611

import decimal
import numpy
import textwrap

import putil.exh
from putil.ptypes import (engineering_notation_number,
						 engineering_notation_suffix,
						 non_negative_integer)


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys, __builtin__
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_eng
exobj_eng = trace_ex_eng.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Global variables
###
_POWER_TO_SUFFIX_DICT = {
	-24:'y', -21:'z', -18:'a', -15:'f', -12:'p', -9:'n', -6:'u', -3:'m',
	  0:' ',
	  3:'k', 6:'M', 9:'G', 12:'T', 15:'P', 18:'E', 21:'Z', 24:'Y'
}
_SUFFIX_TO_POWER_DICT = dict(
	[(value, key) for key, value in _POWER_TO_SUFFIX_DICT.iteritems()]
)
_SUFFIX_POWER_DICT = dict(
	[(key, float(10**value)) for key, value in _SUFFIX_TO_POWER_DICT.iteritems()]
)


###
# Functions
###
def _to_eng_tuple(number):
	"""
	Returns a string version of the number where the exponent is a
	multiple of 3
	"""
	mant, exp = to_scientific_tuple(str(number))
	mant = mant+('.00' if mant.find('.') == -1 else '00')
	new_exp = exp-(exp % 3)
	new_ppos = 1+exp-new_exp+(1 if mant[0] == '-' else 0)
	mant = mant.replace('.', '')
	new_mant = (mant[:new_ppos]+'.'+mant[new_ppos:]).rstrip('0').rstrip('.')
	return new_mant, new_exp


def _to_eng_string(number):
	"""
	Returns a string version of the number where the exponent is a
	multiple of 3
	"""
	mant, exp = _to_eng_tuple(number)
	return '{0}E{1}{2}'.format(mant, '-' if exp < 0 else '+', abs(exp))


@putil.pcontracts.contract(
	number='int|float',
	frac_length='non_negative_integer',
	rjust=bool
)
def peng(number, frac_length, rjust=True):
	r"""
	Converts a number to engineering notation. The absolute value of the
	number (if it is not exactly zero) is bounded to the interval
	[1E-24, 1E+24)

	:param	number: Number to convert
	:type	number: number
	:param	frac_length: Number of digits of fractional part
	:type	frac_length: :ref:`NonNegativeInteger`
	:param	rjust: Flag that indicates whether the number is
	 right-justified (True) or not (False)
	:type	rjust: boolean
	:rtype: string

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng

	:raises:
	 * RuntimeError (Argument \`frac_length\` is not valid)

	 * RuntimeError (Argument \`number\` is not valid)

	 * RuntimeError (Argument \`rjust\` is not valid)

	.. [[[end]]]

	The supported engineering suffixes are:

	+----------+-------+--------+
	| Exponent | Name  | Suffix |
	+==========+=======+========+
	| 1E-24    | yocto | y      |
	+----------+-------+--------+
	| 1E-21    | zepto | z      |
	+----------+-------+--------+
	| 1E-18    | atto  | a      |
	+----------+-------+--------+
	| 1E-15    | femto | f      |
	+----------+-------+--------+
	| 1E-12    | pico  | p      |
	+----------+-------+--------+
	| 1E-9     | nano  | n      |
	+----------+-------+--------+
	| 1E-6     | micro | u      |
	+----------+-------+--------+
	| 1E-3     | milli | m      |
	+----------+-------+--------+
	| 1E+0     |       |        |
	+----------+-------+--------+
	| 1E+3     | kilo  | k      |
	+----------+-------+--------+
	| 1E+6     | mega  | M      |
	+----------+-------+--------+
	| 1E+9     | giga  | G      |
	+----------+-------+--------+
	| 1E+12    | tera  | T      |
	+----------+-------+--------+
	| 1E+15    | peta  | P      |
	+----------+-------+--------+
	| 1E+18    | exa   | E      |
	+----------+-------+--------+
	| 1E+21    | zetta | Z      |
	+----------+-------+--------+
	| 1E+24    | yotta | Y      |
	+----------+-------+--------+

	For example:

		>>> import putil.eng
		>>> putil.eng.peng(1235.6789E3, 3, False)
		'1.236M'

	"""
	# Return formatted zero if number is zero, easier to not deal with this
	# special case through the rest of the algorithm
	if number == 0:
		number = '0'+('.'+('0'*frac_length) if frac_length else '')
		return number.rjust(5+frac_length)+' ' if rjust else number
	# Low-bound number
	sign = +1 if number >= 0 else -1
	number = sign*max(1e-24, abs(number))
	# Round number
	mant, exp = _to_eng_tuple(number)
	ppos = mant.find('.')
	if ppos == -1:
		new_mant = mant+('.' if frac_length else '')+('0'*frac_length)
	else:
		new_mant = mant[:ppos+1]+(mant[ppos+1:].ljust(frac_length, '0'))
	if (ppos != -1) and (len(mant)-ppos-1 > frac_length):
		ssign = '-' if sign == -1 else ''
		sexp = str(exp)
		rounder = decimal.Decimal(ssign+'0.'+('0'*frac_length)+'5E'+sexp)
		mant, exp = _to_eng_tuple(str(decimal.Decimal(new_mant+'E'+sexp)+rounder))
		ppos = mant.find('.')
		if ppos == -1:
			new_mant = mant+('.' if frac_length else '')+('0'*frac_length)
		else:
			new_mant = mant[:ppos+1]+(mant[ppos+1:].ljust(frac_length, '0'))
	if frac_length:
		ppos = new_mant.find('.')
	else:
		ppos = (len(new_mant) if new_mant.find('.') == -1 else new_mant.find('.')-1)
	new_mant = new_mant[:ppos+frac_length+1]
	# Upper-bound number
	if exp > 24:
		new_mant, exp = ('-' if sign == -1 else '')+'999.'+(frac_length*'9'), 24
	# Justify number
	if rjust:
		new_mant = new_mant.rjust(4+(1 if frac_length else 0)+frac_length)
	return '{0}{1}'.format(
		new_mant,
		_POWER_TO_SUFFIX_DICT[exp] if rjust else _POWER_TO_SUFFIX_DICT[exp].rstrip()
	)


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_float(snum):
	r"""
	Returns the floating point equivalent of a number represented
	in engineering notation

	:param	snum: Number
	:type	snum: :ref:`EngineeringNotationNumber`
	:rtype: string

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_float

	:raises: RuntimeError (Argument \`snum\` is not valid)

	.. [[[end]]]

	For example:

		>>> import putil.eng
		>>> putil.eng.peng_float(putil.eng.peng(1235.6789E3, 3, False))
		1236000.0

	"""
	# This can be coded as peng_mant(snum)*(peng_power(snum)[1]), but the
	# "function unrolling" is about 4x faster
	snum = snum.rstrip()
	power = _SUFFIX_POWER_DICT[' ' if snum[-1].isdigit() else snum[-1]]
	return float(snum if snum[-1].isdigit() else snum[:-1])*power


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_frac(snum):
	r"""
	Returns the fractional part of a number represented in engineering notation

	:param	snum: Number
	:type	snum: :ref:`EngineeringNotationNumber`
	:rtype: integer

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_frac

	:raises: RuntimeError (Argument \`snum\` is not valid)

	.. [[[end]]]

	For example:

		>>> import putil.eng
		>>> putil.eng.peng_frac(putil.eng.peng(1235.6789E3, 3, False))
		236

	"""
	snum = snum.rstrip()
	pindex = snum.find('.')
	if pindex == -1:
		return 0
	else:
		return int(snum[pindex+1:] if snum[-1].isdigit() else snum[pindex+1:-1])


def peng_int(snum):
	r"""
	Returns the integer part of a number represented in engineering notation

	:param snum: Number
	:type	snum: :ref:`EngineeringNotationNumber`
	:rtype: integer

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_int

	:raises: RuntimeError (Argument \`snum\` is not valid)

	.. [[[end]]]

	For example:

		>>> import putil.eng
		>>> putil.eng.peng_int(putil.eng.peng(1235.6789E3, 3, False))
		1

	"""
	return int(peng_mant(snum))


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_mant(snum):
	r"""
	Returns the mantissa of a number represented in engineering notation

	:param	snum: Number
	:type	snum: :ref:`EngineeringNotationNumber`
	:rtype: float

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_mant

	:raises: RuntimeError (Argument \`snum\` is not valid)

	.. [[[end]]]

	For example:

		>>> import putil.eng
		>>> putil.eng.peng_mant(putil.eng.peng(1235.6789E3, 3, False))
		1.236

	"""
	snum = snum.rstrip()
	return float(snum if snum[-1].isdigit() else snum[:-1])


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_power(snum):
	r"""
	Returns a tuple with the engineering suffix (first tuple item) and
	floating point equivalent of the suffix (second tuple item) of a
	number represented in engineering notation. :py:func:`putil.eng.peng`
	lists the correspondence between suffix and floating point exponent.

	:param	snum: Number
	:type	snum: :ref:`EngineeringNotationNumber`
	:rtype: tuple

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_power

	:raises: RuntimeError (Argument \`snum\` is not valid)

	.. [[[end]]]

	For example:

		>>> import putil.eng
		>>> putil.eng.peng_power(putil.eng.peng(1235.6789E3, 3, False))
		('M', 1000000.0)

	"""
	suffix = ' ' if snum[-1].isdigit() else snum[-1]
	return (suffix, _SUFFIX_POWER_DICT[suffix])


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_suffix(snum):
	r"""
	Returns the suffix of a number represented in engineering notation

	:param	snum: Number
	:type	snum: :ref:`EngineeringNotationNumber`
	:rtype: string

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_suffix

	:raises: RuntimeError (Argument \`snum\` is not valid)

	.. [[[end]]]

	For example:

		>>> import putil.eng
		>>> putil.eng.peng_suffix(putil.eng.peng(1235.6789E3, 3, False))
		'M'

	"""
	snum = snum.rstrip()
	return ' ' if snum[-1].isdigit() else snum[-1]


@putil.pcontracts.contract(suffix='engineering_notation_suffix', offset=int)
def peng_suffix_math(suffix, offset):
	r"""
	Returns an engineering suffix based on a starting suffix and an offset of
	number of suffixes

	:param	suffix: Engineering suffix
	:type	suffix: :ref:`EngineeringNotationSuffix`
	:param	offset: Engineering suffix offset
	:type	offset: integer
	:rtype: string

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for
	.. putil.eng.peng_suffix_math

	:raises:
	 * RuntimeError (Argument \`offset\` is not valid)

	 * RuntimeError (Argument \`suffix\` is not valid)

	 * ValueError (Argument \`offset\` is not valid)

	.. [[[end]]]

	For example:

		>>> import putil.eng
		>>> putil.eng.peng_suffix_math('u', 6)
		'T'

	"""
	# pylint: disable=W0212,W0631
	exhobj = putil.exh.get_or_create_exh_obj()
	exhobj.add_exception(
		exname='invalid_offset',
		extype=ValueError,
		exmsg='Argument `offset` is not valid'
	)
	try:
		return _POWER_TO_SUFFIX_DICT[_SUFFIX_TO_POWER_DICT[suffix]+3*offset]
	except KeyError:
		exhobj.raise_exception_if(exname='invalid_offset', condition=True)


def round_mantissa(arg, decimals=0):
	"""
	Rounds the fractional part of a floating point number mantissa or Numpy
	vector of floating point numbers to a given number of digits. Integers are
	not altered. The mantissa used is that of the floating point number(s)
	when expressed in `normalized scientific notation
	<https://en.wikipedia.org/wiki/Scientific_notation#Normalized_notation>`_

	:param	arg: Input data
	:type	arg: number, Numpy vector of numbers or None
	:param	decimals: Number of digits to round the fractional part of the
	 mantissa to.
	:type	decimals: integer
	:rtype: number, Numpy vector of numbers or None depending on the argument
	 type

	For example::

		>>> import putil.eng
		>>> putil.eng.round_mantissa(012345678E-6, 3)
		12.35
		>>> putil.eng.round_mantissa(5, 3)
		5

	"""
	if arg is None:
		return arg
	elif isinstance(arg, numpy.ndarray):
		foi = [isinstance(item, int) for item in arg]
		return numpy.array([
			item if isint else float(to_scientific_string(item, decimals))
			for isint, item in zip(foi, arg)
		])
	else:
		if isinstance(arg, int):
			return arg
		else:
			return float(to_scientific_string(arg, decimals))


def to_scientific_tuple(number):
	"""
	Returns a tuple in which the first item is the mantissa (*string*) and
	the second item is the exponent (*integer*) of a number when expressed
	in scientific notation. Full precision is maintained if the number is
	represented as a string

	:param	number: Number
	:type	number: number or string
	:rtype: tuple

	For example:

		>>> import putil.eng
		>>> putil.eng.to_scientific_tuple('135.56E-8')
		('1.3556', -6)
		>>> putil.eng.to_scientific_tuple(0.0000013556)
		('1.3556', -6)

	"""
	# pylint: disable=W0632
	convert = not isinstance(number, str)
	if ((convert and (number == 0)) or
	   ((not convert) and (not number.strip('0').strip('.')))):
		return ('0', 0)
	num_sign, digits, exp = decimal.Decimal(
		str(number) if convert else number
	).as_tuple()
	mant = ('-' if num_sign else '')+(
				str(digits[0])+
				('.'+(''.join([str(num) for num in digits[1:]]))
				if len(digits) > 1 else '')
		   ).rstrip('0').rstrip('.')
	exp += len(digits)-1
	return (mant, exp)


def to_scientific_string(
		number,
		frac_length=None,
		exp_length=None,
		sign_always=False
	):
	"""
	Converts a number or a string representing a number to a string with the
	number expressed in scientific notation. Full precision is maintained if
	the number is represented as a string

	:param	number: Number to convert
	:type	number: number or string
	:param	frac_length: Number of digits of fractional part, None indicates
	 that the fractional part of the number should not be limited
	:type	frac_length: integer or None
	:param	exp_length: Number of digits of the exponent; the actual length of
	 the exponent takes precedence if it is longer
	:type	exp_length: integer or None
	:param	sign_always: Flag that indicates whether the sign always
	 precedes the number for both non-negative and negative numbers (True) or
	 only for negative numbers (False)
	:type	sign_always: boolean
	:rtype: string

	For example:

		>>> import putil.eng
		>>> putil.eng.to_scientific_string(333)
		'3.33E+2'
		>>> putil.eng.to_scientific_string(0.00101)
		'1.01E-3'
		>>> putil.eng.to_scientific_string(99.999, 1, 2, True)
		'+1.0E+02'

	"""
	mant, exp = to_scientific_tuple(number)
	fmant = float(mant)
	sexp = (abs(exp)
		   if exp_length is None else
		   '{0}'.format(abs(exp)).rjust(exp_length, '0'))
	if not frac_length:
		return '{0}{1}E{2}{3}'.format(
			'+' if sign_always and (fmant >= 0) else '',
			mant,
			'-' if exp < 0 else '+',
			sexp
		)
	if fmant == int(fmant):
		return '{0}{1}.{2}E{3}{4}'.format(
			'+' if sign_always and (fmant >= 0) else '',
			mant,
			'0'*frac_length,
			'-' if exp < 0 else '+',
			sexp
		)
	rounded_mant = round(fmant, frac_length)
	if abs(rounded_mant) >= 10:
		return to_scientific_string(
			rounded_mant*(10**exp),
			frac_length,
			exp_length,
			sign_always
		)
	return '{0}{1}{2}E{3}{4}'.format(
		'+' if sign_always and (fmant >= 0) else '',
		rounded_mant,
		'0'*(2+(1 if (fmant < 0) else 0)+frac_length-len(str(rounded_mant))),
		'-' if exp < 0 else '+', sexp
	)


def pprint_vector(vector, limit=False, width=None, indent=0,
				  eng=False, frac_length=3):
	r"""
	Formats a list of numbers (vector) or a Numpy vector for printing. If the
	argument **vector** is :code:`None` the string :code:`'None'` is returned

	:param	vector: Vector to pretty print or None
	:type	vector: list of numbers, Numpy vector or None
	:param	limit: Flag that indicates whether at most 6 vector items are
	 printed (all vector items if its length is equal or less than 6, first
	 and last 3 vector items if it is not) (True), or the entire vector is
	 printed (False)
	:type	limit: boolean
	:param	width: Number of available characters per line. If None the vector
	 is printed in one line
	:type	width: integer or None
	:param	indent: Flag that indicates whether all subsequent lines after the
	 first one are indented (True) or not (False). Only relevant if
	 **width** is not None
	:type	indent: boolean
	:param	eng: Flag that indicates whether engineering notation is used
	 (True) or not (False)
	:type	eng: boolean
	:param	frac_length: Number of digits of fractional part (only applicable
	 if **eng** is True)
	:type	frac_length: integer
	:raises: ValueError (Argument \`width\` is too small)
	:rtype: string

	For example:

		>>> import putil.eng
		>>> header = 'Vector: '
		>>> data = [1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 8, 9]
		>>> print header+putil.eng.pprint_vector(
		...     data,
		...     width=30,
		...     eng=True,
		...     frac_length=1,
		...     limit=True,
		...     indent=len(header)
		... )
		Vector: [    1.0m,   20.0u,  300.0M,
		                     ...
		           700.0 ,    8.0 ,    9.0  ]
		>>> print header+putil.eng.pprint_vector(
		...     data,
		...     width=30,
		...     eng=True,
		...     frac_length=0,
		...     indent=len(header)
		... )
		Vector: [    1m,   20u,  300M,    4p,
		             5k,   -6n,  700 ,    8 ,
		             9  ]
		>>> print putil.eng.pprint_vector(data, eng=True, frac_length=0)
		[    1m,   20u,  300M,    4p,    5k,   -6n,  700 ,    8 ,    9  ]
		>>> print putil.eng.pprint_vector(data, limit=True)
		[ 0.001, 2e-05, 300000000.0, ..., 700, 8, 9 ]

	"""
	# pylint: disable=R0912,R0913,R0914
	def _str(element):
		""" Print a straight number or one with engineering notation """
		return element if not eng else putil.eng.peng(element, frac_length, True)

	if vector is None:
		return 'None'
	if (not limit) or (limit and (len(vector) < 7)):
		uret = '[ {0} ]'.format(', '.join([
			'{0}'.format(_str(element)) for element in vector])
		)
	else:
		uret = '[ {0}, {1}, {2}, ..., {3}, {4}, {5} ]'.format(
			_str(vector[0]),
			_str(vector[1]),
			_str(vector[2]),
			_str(vector[-3]),
			_str(vector[-2]),
			_str(vector[-1])
		)
	if (width is None) or (len(uret) < width):
		return uret
	# Figure out how long the first line needs to be
	wobj = textwrap.TextWrapper(
		initial_indent='[ ',
		width=width,
		subsequent_indent=(indent+2)*' '
	)
	wrapped_lines_list = wobj.wrap(uret[2:])
	first_line = wrapped_lines_list[0]
	elements_per_row = first_line.count(',')
	if elements_per_row == 0:
		raise ValueError('Argument `width` is too small')
	# "Manually" format limit output so that it is either 3 lines, first and
	# line with 3 elements and the middle with '...' or 7 lines, each with 1
	# element and the middle with '...'
	if limit:
		if elements_per_row < 3:
			rlist = [
				'[ {0},'.format(_str(vector[0])),
				_str(vector[1]),
				_str(vector[2]),
				'...',
				_str(vector[-3]),
				_str(vector[-2]),
				'{0} ]'.format(_str(vector[-1]))
			]
			elements_per_row = 1
		else:
			rlist = [
				'[ {0}, {1}, {2},'.format(
					_str(vector[0]),
					_str(vector[1]),
					_str(vector[2])
				),
				'...',
				'{0}, {1}, {2} ]'.format(
					_str(vector[-3]),
					_str(vector[-2]),
					_str(vector[-1])
				)
			]
		first_line = rlist[0]
	else:
		rlist = wobj.wrap(uret[2:])
	# Use output of wrap() if numbers cannot be aligned at comma (variable width)
	if not eng:
		return '\n'.join(rlist)
	# Align elements across multiple lines
	if limit:
		remainder_list = [line.lstrip() for line in rlist[1:]]
	else:
		remainder_list = _split_every(
			uret[len(first_line):],
			',',
			elements_per_row,
			lstrip=True
		)
	first_comma_index = first_line.find(',')
	actual_width = len(first_line)-2
	new_wrapped_lines_list = [first_line]
	for line in remainder_list[:-1]:
		new_wrapped_lines_list.append(
			'{0},'.format(line).rjust(actual_width)
			if line != '...' else
			line.center(actual_width).rstrip()
		)
	# Align last line on fist comma (if it exists) or on length of field if not
	if remainder_list[-1].find(',') == -1:
		marker = len(remainder_list[-1])-2
	else:
		marker = remainder_list[-1].find(',')
	new_wrapped_lines_list.append(
		'{0}{1}'.format(
			(first_comma_index-marker-2)*' ',
			remainder_list[-1]
		)
	)
	return '\n'.join([
		((indent+2)*' ')+line
		if num > 0 else line
		for num, line in enumerate(new_wrapped_lines_list)
	])


def _split_every(text, sep, count, lstrip=False, rstrip=False):
	"""
	Returns a list of the words in the string, using a count of a separator as
	the delimiter

	:param	text: String to split
	:type	text: string
	:param	sep: Separator
	:type	sep: string
	:param	count: Number of separators to use as word delimiter
	:type	count: integer
	:param	lstrip: Flag that indicates whether whitespace is removed
	 from the beginning of each list item (True) or not (False)
	:type	lstrip: boolean
	:param	rstrip: Flag that indicates whether whitespace is removed
	 from the end of each list item (True) or not (False)
	:type	rstrip: boolean
	:rtype: list
	"""
	tlist = text.split(sep)
	lines = [
		sep.join(tlist[num:min(num+count, len(tlist))])
		for num in range(0, len(tlist), count)
	]
	return [
		line.rstrip()
		if (rstrip and not lstrip) else
		(
			line.lstrip() if (lstrip and not rstrip) else
			(line.strip() if lstrip and rstrip else line)
		) for line in lines
	]
