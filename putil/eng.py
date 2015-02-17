# eng.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import decimal

import putil.exh
import putil.misc
import putil.pcontracts


_POWER_TO_SUFFIX_DICT = {-24:'y', -21:'z', -18:'a', -15:'f', -12:'p', -9:'n', -6:'u', -3:'m', 0:' ', 3:'k', 6:'M', 9:'G', 12:'T', 15:'P', 18:'E', 21:'Z', 24:'Y'}
_SUFFIX_TO_POWER_DICT = {'y':-24, 'z':-21, 'a':-18, 'f':-15, 'p':-12, 'n':-9, 'u':-6, 'm':-3, ' ':0, 'k':3, 'M':6, 'G':9, 'T':12, 'P':15, 'E':18, 'Z':21, 'Y':24}
_SUFFIX_TUPLE = ['y', 'z', 'a', 'f', 'p', 'n', 'u', 'm', ' ', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']


@putil.pcontracts.new_contract()
def engineering_notation_number(snum):
	r"""
	Number string in engineering notation

	:param	snum: Number
	:type	snum: EngineeringNotationNumber
	:raises: :code:`RuntimeError ('Argument \`*[argument_name]*\` is not valid')`. The token :code:`'*[argument_name]*'` is replaced by the *name* of the argument the contract is attached to

	:rtype: None
	"""
	try:
		snum = snum.rstrip()
		float(snum[:-1] if snum[-1] in _SUFFIX_TUPLE else snum)
	except:
		raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def engineering_notation_suffix(suffix):
	r"""
	Engineering notation suffix

	:param	suffix: Suffix
	:type	suffix: EngineerngNotationSuffix
	:raises: :code:`RuntimeError ('Argument \`*[argument_name]*\` is not valid')`. The token :code:`'*[argument_name]*'` is replaced by the *name* of the argument the contract is attached to

	:rtype: None
	"""
	if suffix not in _SUFFIX_TUPLE:
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


@putil.pcontracts.contract(number='int|float', frac_length='int,>=0', rjust=bool)
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
	:raises:
	 * RuntimeError (Argument `frac_length` is not valid)

	 * RuntimeError (Argument `number` is not valid)

	 * RuntimeError (Argument `rjust` is not valid)

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
	return '{0}{1}'.format(new_mant, _POWER_TO_SUFFIX_DICT[exp] if rjust else _POWER_TO_SUFFIX_DICT[exp].rstrip())


def peng_float(snum):
	"""
	Returns floating point number representation of number string in engineering notation

	:param	snum: Number
	:type	snum: EngineeringNotationNumber
	:rtype: string
	:raises: RuntimeError (Argument `snum` is not valid)

	For example:

		>>> putil.eng.peng_float(putil.eng.peng(1235.6789E3, 3, False))
		1236000.0

	"""
	return peng_mant(snum)*(peng_power(snum)[1])


def peng_frac(snum):
	"""
	Returns fractional part a number string in engineering notation

	:param	snum: Number
	:type	snum: EngineeringNotationNumber
	:rtype: integer
	:raises: RuntimeError (Argument `snum` is not valid)

	For example:

		>>> putil.eng.peng_frac(putil.eng.peng(1235.6789E3, 3, False))
		236

	"""
	suffix = peng_suffix(snum)
	snum = snum.replace(suffix, '')
	pindex = snum.find('.')
	return 0 if pindex == -1 else int(snum[pindex+1:])


def peng_int(snum):
	"""Returns integer part of number string in engineering notation

	:param snum: Number
	:type	snum: EngineeringNotationNumber
	:rtype: integer
	:raises: RuntimeError (Argument `snum` is not valid)

	For example:

		>>> putil.eng.peng_int(putil.eng.peng(1235.6789E3, 3, False))
		1

	"""
	return int(peng_mant(snum))


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_mant(snum):
	"""
	Returns mantissa of number string in engineering notation

	:param	snum: Number
	:type	snum: EngineeringNotationNumber
	:rtype: integer
	:raises: RuntimeError (Argument `snum` is not valid)

	For example:

		>>> putil.eng.peng_mant(putil.eng.peng(1235.6789E3, 3, False))
		1.236

	"""
	snum = snum.rstrip()
	return float(snum if snum[-1].isdigit() else snum[:-1])


def peng_power(snum):
	"""
	Returns a tuple with the engineering suffix (first tuple element) and floating point representation of the suffix (second tuple element) of an number string in engineering notation

	:param	snum: Number
	:type	snum: EngineeringNotationNumber
	:rtype: tuple
	:raises: RuntimeError (Argument `snum` is not valid)

	For example:

		>>> putil.eng.peng_power(putil.eng.peng(1235.6789E3, 3, False))
		('M', 1000000.0)

	"""
	suffix = peng_suffix(snum)
	return (suffix, 1.0*(10**_SUFFIX_TO_POWER_DICT[suffix]))


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_suffix(snum):
	"""
	Returns suffix of number string in engineering notation

	:param	snum: Number
	:type	snum: EngineeringNotationNumber
	:rtype: string
	:raises: RuntimeError (Argument `snum` is not valid)

	For example:

		>>> putil.eng.peng_suffix(putil.eng.peng(1235.6789E3, 3, False))
		'M'

	"""
	snum = snum.rstrip()
	return ' ' if snum[-1].isdigit() else snum[-1]


@putil.pcontracts.contract(suffix='engineering_notation_suffix', offset=int)
def peng_suffix_math(suffix, offset):
	"""
	Returns engineering suffix based on a starting suffix and an offset of number of suffixes

	:param	suffix: Engineering suffix
	:type	suffix: EngineeringNotationSuffix
	:param	offset: Engineering suffix offset
	:type	offset: integer
	:rtype: string
	:raises:
	 * RuntimeError (Argument `offset` is not valid)

	 * RuntimeError (Argument `suffix` is not valid)

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
