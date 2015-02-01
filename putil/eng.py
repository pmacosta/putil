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
def peng(number, mantissa, rjust=True):
	"""
	Print number in engineering notation
	"""
	# Return formatted zero if number is zero, easier to not deal with this special case through the rest of the algorithm
	if number == 0:
		number = '0'+('.'+('0'*mantissa) if mantissa else '')
		return (number.rjust(5+mantissa) if rjust else number)+' '
	# Low-bound number
	sign = +1 if number >= 0 else -1
	number = sign*max(1e-24, abs(number))
	# Round number
	mant, exp = _to_eng_tuple(number)
	ppos = mant.find('.')
	new_mant = mant+('.' if mantissa else '')+('0'*mantissa) if ppos == -1 else mant[:ppos+1]+(mant[ppos+1:].ljust(mantissa, '0'))
	if (ppos != -1) and (len(mant)-ppos-1 > mantissa):
		mant, exp = _to_eng_tuple(str(decimal.Decimal(new_mant+'E'+str(exp))+decimal.Decimal(('-' if sign == -1 else '')+'0.'+('0'*mantissa)+'5E'+str(exp))))
		ppos = mant.find('.')
		new_mant = mant+('.' if mantissa else '')+('0'*mantissa) if ppos == -1 else mant[:ppos+1]+(mant[ppos+1:].ljust(mantissa, '0'))
	ppos = new_mant.find('.') if mantissa else (len(new_mant) if new_mant.find('.') == -1 else new_mant.find('.')-1)
	new_mant = new_mant[:ppos+mantissa+1]
	# Upper-bound number
	if exp > 24:
		new_mant, exp = ('-' if sign == -1 else '')+'999.'+(mantissa*'9'), 24
	# Justify number
	if rjust:
		new_mant = new_mant.rjust(4+(1 if mantissa else 0)+mantissa)
	return '{0}{1}'.format(new_mant, _UNIT_DICT[exp])

def peng_unit(text):
	""" Return unit of number string in engineering notation """
	text = text.strip()
	return ' ' if text[-1].isdigit() else text[-1]

def peng_unit_math(center, offset):
	""" Return engineering unit letter based on a center/start unit and an offset of units """
	for key, value in _UNIT_DICT.iteritems():
		if value == center:
			break
	else:
		raise RuntimeError('Unit `{0}` not recognized'.format(center))
	return _UNIT_DICT[key+3*offset]	#pylint: disable=W0631

def peng_power(text):
	""" Return exponent of number string in engineering notation """
	unit = peng_unit(text)
	for key, value in _UNIT_DICT.iteritems():
		if value == unit:
			return (unit, 10**key)

def peng_int(text):
	""" Return integer part of number string in engineering notation """
	return int(peng_float(text))

def peng_mant(text):
	""" Return mantissa part of number string in engineering notation """
	text = text.replace(peng_unit(text), '')
	return 0 if text.find('.') == -1 else int(text[text.find('.')+1:])

def peng_float(text):
	""" Return number without engineering unit of number string in engineering notation """
	return float(text.replace(peng_unit(text), ''))

def peng_num(text):
	""" Return float from number string in engineering notation """
	return peng_float(text)*peng_power(text)[1]
