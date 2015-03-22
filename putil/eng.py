# eng.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import decimal

import putil.exh, putil.misc, putil.pcontracts


###
# Exception tracing initialization code
###
"""
[[[cog
import trace_ex_eng
exobj_eng = trace_ex_eng.trace_module(no_print=True)
]]]
[[[end]]]
"""	#pylint: disable=W0105


###
# Global variables
###
_POWER_TO_SUFFIX_DICT = {-24:'y', -21:'z', -18:'a', -15:'f', -12:'p', -9:'n', -6:'u', -3:'m', 0:' ', 3:'k', 6:'M', 9:'G', 12:'T', 15:'P', 18:'E', 21:'Z', 24:'Y'}
_SUFFIX_TO_POWER_DICT = dict([(value, key) for key, value in _POWER_TO_SUFFIX_DICT.iteritems()])
_SUFFIX_TUPLE = tuple(_SUFFIX_TO_POWER_DICT.keys())
_SUFFIX_POWER_DICT = dict([(key, float(10**value)) for key, value in _SUFFIX_TO_POWER_DICT.iteritems()])


###
# Functions
###
@putil.pcontracts.new_contract()
def engineering_notation_number(obj):
	r"""
	Contract that validates if an object is a number represented in engineering notation

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The token \*[argument_name]\* is replaced by the name of the argument the contract is attached to

	:rtype: None
	"""
	try:
		obj = obj.rstrip()
		float(obj[:-1] if obj[-1] in _SUFFIX_TUPLE else obj)
		return None
	except:
		raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def engineering_notation_suffix(obj):
	r"""
	Contract that validates if an object is an engineering notation suffix

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The token \*[argument_name]\* is replaced by the *name* of the argument the contract is attached to

	:rtype: None
	"""
	try:
		assert obj in _SUFFIX_TUPLE
	except:
		raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def pos_integer(obj):
	r"""
	Contract that validates if an object is a positive integer

	:param	obj: Object
	:type	obj: any
	:raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The token \*[argument_name]\* is replaced by the *name* of the argument the contract is attached to

	:rtype: None
	"""
	if isinstance(obj, int) and (obj >= 0):
		return None
	raise ValueError(putil.pcontracts.get_exdesc())


def _to_eng_tuple(number):
	""" Returns a string version of the number where the exponent is a multiple of 3 """
	mant, exp = putil.misc.to_scientific_tuple(str(number))
	mant = mant+('.00' if mant.find('.') == -1 else '00')
	new_exp = exp-(exp % 3)
	new_ppos = 1+exp-new_exp+(1 if mant[0] == '-' else 0)
	mant = mant.replace('.', '')
	new_mant = (mant[:new_ppos]+'.'+mant[new_ppos:]).rstrip('0').rstrip('.')
	return new_mant, new_exp


def _to_eng_string(number):
	""" Returns a string version of the number where the exponent is a multiple of 3 """
	mant, exp = _to_eng_tuple(number)
	return '{0}E{1}{2}'.format(mant, '-' if exp < 0 else '+', abs(exp))


@putil.pcontracts.contract(number='int|float', frac_length='pos_integer', rjust=bool)
def peng(number, frac_length, rjust=True):
	r"""
	Converts a number to engineering notation. The absolute value of the number (if it is not exactly zero) is bounded to the interval [1E-24, 1E+24)

	:param	number: Number to convert
	:type	number: number
	:param	frac_length: Number of digits of fractional part
	:type	frac_length: integer
	:param	rjust: Flag that indicates whether the number should be right-justified (True) or not (False)
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
	+----------+-------+--------+
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

		>>> putil.eng.peng(1235.6789E3, 3, False)
		'1.236M'

	"""
	# Return formatted zero if number is zero, easier to not deal with this special case through the rest of the algorithm
	if number == 0:
		number = '0'+('.'+('0'*frac_length) if frac_length else '')
		return number.rjust(5+frac_length)+' ' if rjust else number
	# Low-bound number
	sign = +1 if number >= 0 else -1
	number = sign*max(1e-24, abs(number))
	# Round number
	mant, exp = _to_eng_tuple(number)
	ppos = mant.find('.')
	new_mant = mant+('.' if frac_length else '')+('0'*frac_length) if ppos == -1 else mant[:ppos+1]+(mant[ppos+1:].ljust(frac_length, '0'))
	if (ppos != -1) and (len(mant)-ppos-1 > frac_length):
		mant, exp = _to_eng_tuple(str(decimal.Decimal(new_mant+'E'+str(exp))+decimal.Decimal(('-' if sign == -1 else '')+'0.'+('0'*frac_length)+'5E'+str(exp))))
		ppos = mant.find('.')
		new_mant = mant+('.' if frac_length else '')+('0'*frac_length) if ppos == -1 else mant[:ppos+1]+(mant[ppos+1:].ljust(frac_length, '0'))
	ppos = new_mant.find('.') if frac_length else (len(new_mant) if new_mant.find('.') == -1 else new_mant.find('.')-1)
	new_mant = new_mant[:ppos+frac_length+1]
	# Upper-bound number
	if exp > 24:
		new_mant, exp = ('-' if sign == -1 else '')+'999.'+(frac_length*'9'), 24
	# Justify number
	if rjust:
		new_mant = new_mant.rjust(4+(1 if frac_length else 0)+frac_length)
	return '{0}{1}'.format(new_mant, _POWER_TO_SUFFIX_DICT[exp] if rjust else _POWER_TO_SUFFIX_DICT[exp].rstrip())


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_float(snum):
	r"""
	Returns the floating point representation of a number in engineering notation

	:param	snum: Number
	:type	snum: EngineeringNotationNumber
	:rtype: string

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_float

	:raises: RuntimeError (Argument \`snum\` is not valid)

	.. [[[end]]]

	For example:

		>>> putil.eng.peng_float(putil.eng.peng(1235.6789E3, 3, False))
		1236000.0

	"""
	# This can be coded as peng_mant(snum)*(peng_power(snum)[1]), but the "function unrolling" is about 4x faster
	snum = snum.rstrip()
	suffix = ' ' if snum[-1].isdigit() else snum[-1]
	return float(snum if snum[-1].isdigit() else snum[:-1])*_SUFFIX_POWER_DICT[suffix]


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_frac(snum):
	r"""
	Returns the fractional part of a number represented in engineering notation

	:param	snum: Number
	:type	snum: EngineeringNotationNumber
	:rtype: integer

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_frac

	:raises: RuntimeError (Argument \`snum\` is not valid)

	.. [[[end]]]

	For example:

		>>> putil.eng.peng_frac(putil.eng.peng(1235.6789E3, 3, False))
		236

	"""
	snum = snum.rstrip()
	pindex = snum.find('.')
	return 0 if pindex == -1 else int(snum[pindex+1:] if snum[-1].isdigit() else snum[pindex+1:-1])


def peng_int(snum):
	r"""
	Returns the integer part of a number represented in engineering notation

	:param snum: Number
	:type	snum: EngineeringNotationNumber
	:rtype: integer

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_int

	:raises: RuntimeError (Argument \`snum\` is not valid)

	.. [[[end]]]

	For example:

		>>> putil.eng.peng_int(putil.eng.peng(1235.6789E3, 3, False))
		1

	"""
	return int(peng_mant(snum))


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_mant(snum):
	r"""
	Returns the mantissa of a number represented in engineering notation

	:param	snum: Number
	:type	snum: EngineeringNotationNumber
	:rtype: integer

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_mant

	:raises: RuntimeError (Argument \`snum\` is not valid)

	.. [[[end]]]

	For example:

		>>> putil.eng.peng_mant(putil.eng.peng(1235.6789E3, 3, False))
		1.236

	"""
	snum = snum.rstrip()
	return float(snum if snum[-1].isdigit() else snum[:-1])


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_power(snum):
	r"""
	Returns a tuple with the engineering suffix (first tuple element) and floating point equivalent of the suffix (second tuple element) of an number represented in engineering notation. :py:func:`putil.eng.peng` lists
	the correspondence between suffix and floating point exponent.

	:param	snum: Number
	:type	snum: EngineeringNotationNumber
	:rtype: tuple

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_power

	:raises: RuntimeError (Argument \`snum\` is not valid)

	.. [[[end]]]

	For example:

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
	:type	snum: EngineeringNotationNumber
	:rtype: string

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_suffix

	:raises: RuntimeError (Argument \`snum\` is not valid)

	.. [[[end]]]

	For example:

		>>> putil.eng.peng_suffix(putil.eng.peng(1235.6789E3, 3, False))
		'M'

	"""
	snum = snum.rstrip()
	return ' ' if snum[-1].isdigit() else snum[-1]


@putil.pcontracts.contract(suffix='engineering_notation_suffix', offset=int)
def peng_suffix_math(suffix, offset):
	r"""
	Returns an engineering suffix based on a starting suffix and an offset of number of suffixes

	:param	suffix: Engineering suffix
	:type	suffix: EngineeringNotationSuffix
	:param	offset: Engineering suffix offset
	:type	offset: integer
	:rtype: string

	.. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.eng.peng_suffix_math

	:raises:
	 * RuntimeError (Argument \`offset\` is not valid)

	 * RuntimeError (Argument \`suffix\` is not valid)

	 * ValueError (Argument \`offset\` is not valid)

	.. [[[end]]]

	For example:

		>>> putil.eng.peng_suffix_math('u', 6)
		'T'

	"""
	exhobj = putil.exh.get_exh_obj()	#pylint: disable=W0212
	exhobj = exhobj if exhobj else putil.exh.ExHandle()
	exhobj.add_exception(exname='invalid_offset', extype=ValueError, exmsg='Argument `offset` is not valid')
	try:
		return _POWER_TO_SUFFIX_DICT[_SUFFIX_TO_POWER_DICT[suffix]+3*offset]	#pylint: disable=W0631
	except:	#pylint: disable=W0702
		exhobj.raise_exception_if(exname='invalid_offset', condition=True)
