# eng.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import decimal

import putil.misc
#import putil.pcontracts


_UNIT_DICT = {-24:'y', -21:'z', -18:'a', -15:'f', -12:'p', -9:'n', -6:'u', -3:'m', 0:' ', 3:'k', 6:'M', 9:'G', 12:'T', 15:'P', 18:'E', 21:'Z', 24:'Y'}

def _to_eng_tuple(number):
	""" Returns a string version of the number where the exponent is a multile of 3 """
	mant, exp = putil.misc.to_scientific_tuple(str(number))
	mant = mant+('.00' if mant.find('.') == -1 else '00')
	new_exp = exp-(exp % 3)
	new_ppos = 1+exp-new_exp+(1 if mant[0] == '-' else 0)
	mant = mant.replace('.', '')
	new_mant = (mant[:new_ppos]+'.'+mant[new_ppos:]).rstrip('0').rstrip('.')
	return new_mant, new_exp


def _to_eng_string(number):
	""" Returns a string version of the number where the exponent is a multile of 3 """
	mant, exp = _to_eng_tuple(number)
	return '{0}E{1}{2}'.format(mant, '-' if exp < 0 else '+', abs(exp))


#@putil.pcontracts.contract(number='int|float', mantissa='int,>=0', rjust=bool)
def peng(number, frac_length, rjust=True):
	"""
	Returns number as a string using engineering notation. The absolute value of the number (if it is not exactly zero) is bounded to the interval [1E-24, 1E+24)

	:param	number: Number to print
	:type	number: number
	:param	frac_length: Number of digits of fractional part
	:type	frac_length: integer
	:param	rjust: Flag that indicates whether the number should be right-justified (*True*) or not
	:type	rjust: boolean
	:rtype: string

	The engineering suffixes used are:

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
	return '{0}{1}'.format(new_mant, _UNIT_DICT[exp] if rjust else _UNIT_DICT[exp].rstrip())


def peng_float(snum):
	"""
	Returns floating point number representation of number string in engineering notation

	:param	snum: Number as a string in engineering notation
	:type	snum: string
	:rtype: string

	For example:

		>>> putil.eng.peng_float(putil.eng.peng(1235.6789E3, 3, False))
		1236000.0

	"""
	return peng_mant(snum)*(peng_power(snum)[1])


def peng_frac(snum):
	"""
	Returns fractional part a number string in engineering notation

	:param	snum: Number as a string in engineering notation
	:type	snum: string
	:rtype: integer

	For example:

		>>> putil.eng.peng_frac(putil.eng.peng(1235.6789E3, 3, False))
		236

	"""
	snum = snum.replace(peng_unit(snum), '')
	return 0 if snum.find('.') == -1 else int(snum[snum.find('.')+1:])


def peng_int(snum):
	"""Returns integer part of number string in engineering notation

	:param snum: Number string in engineering notation
	:type	snum: string
	:rtype: integer

	For example:

		>>> putil.eng.peng_int(putil.eng.peng(1235.6789E3, 3, False))
		1

	"""
	return int(peng_mant(snum))


def peng_mant(snum):
	"""
	Returns mantissa of number string in engineering notation

	:param	snum: Number as a string in engineering notation
	:type	snum: string
	:rtype: integer

	For example:

		>>> putil.eng.peng_mant(putil.eng.peng(1235.6789E3, 3, False))
		1.236

	"""
	return float(snum.replace(peng_unit(snum), ''))


def peng_power(snum):
	"""
	Returns a tuple with the engineering suffix (first tuple element) and floating point representation of the suffix (second tuple element) of an number string in engineering notation

	:param snum: Number string in engineering notation
	:type	snum: string
	:rtype: tuple

	For example:

		>>> putil.eng.peng_power(putil.eng.peng(1235.6789E3, 3, False))
		('M', 1000000.0)

	"""
	unit = peng_unit(snum)
	for key, value in _UNIT_DICT.iteritems():
		if value == unit:
			return (unit, float(10**key))


def peng_unit(snum):
	"""
	Returns unit of number string in engineering notation

	:param	snum: Number as a string in engineering notation
	:type	snum: string
	:rtype: string

	For example:

		>>> putil.eng.peng_unit(putil.eng.peng(1235.6789E3, 3, False))
		'M'

	"""
	snum = snum.strip()
	return ' ' if snum[-1].isdigit() else snum[-1]


def peng_unit_math(suffix, offset):
	"""
	Returns engineering suffix based on a starting suffix and an offset of number of suffixes

	:param	suffix: Engineering suffix
	:type	suffix: string
	:param	offset: Engineering suffix offset
	:type	offset: integer
	:rtype: string

	For example:

		>>> putil.eng.peng_unit_math('u', 6)
		'T'

	"""
	for key, value in _UNIT_DICT.iteritems():
		if value == suffix:
			break
	else:
		raise RuntimeError('Unit `{0}` not recognized'.format(suffix))
	return _UNIT_DICT[key+3*offset]	#pylint: disable=W0631
