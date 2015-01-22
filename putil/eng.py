# eng.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import math


_UNIT_LIST = ['y', 'z', 'a', 'f', 'p', 'n', 'u', 'm', ' ', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']

def peng(number, mantissa, rjust=True):
	""" Print number in engineering notation """
	if (isinstance(number, int) is False) and (isinstance(number, float) is False) and (isinstance(number, complex) is False):
		raise TypeError('number argument has to be an integer, float or complex in function peng')
	if isinstance(mantissa, int) is False:
		raise TypeError('mantissa argument has to be an integer or a float in function peng')
	if isinstance(rjust, bool) is False:
		raise TypeError('rjust argument has to be boolean in function peng')
	# Process data
	if isinstance(number, complex) is True:
		return peng(number.real, mantissa, rjust)+('-' if number.imag < 0 else '+')+'j'+peng(abs(number.imag), mantissa, rjust)
	prefix_string = 'yzafpnum kMGTPEZY'
	sign_text = '-' if number < 0 else ' '
	number = 0 if abs(number) <= 1e-25 else abs(max(-1e26, min(1e26, number))) # Bound number
	if number != 0:
		while True:
			exponent = math.floor(math.log10(number)/3)*3	# Exponent quantized to 3
			divider = exponent-mantissa
			bounded_number = round(number/(pow(10, divider)))*pow(10, divider)*pow(10, -exponent)
			if bounded_number < 1e3:
				break
			number = bounded_number*pow(10, exponent) # For cases like peng(999.999m, 0)
		bounded_number = str(float(bounded_number))
		# Remove .0000 for number really close to 0 or for numbers where the operation to get bounded_number make it very close, but not exactly an integer
		bounded_number = bounded_number[:bounded_number.find('.')] if int(bounded_number[bounded_number.find('.')+1:]) == 0 else bounded_number
		prefix_letter = prefix_string[int(8+math.floor(exponent/3))]
		period_index = bounded_number.find('.')
		mantissa_append = '' if ((period_index == -1) and (mantissa == 0)) else ('.'+('0'*mantissa) if ((period_index == -1) and (mantissa > 0)) else '0'*(mantissa-(len(bounded_number)-period_index-1)))
		prepend_text = ' '*(3-len(bounded_number)) if period_index == -1 else ' '*(3-period_index)
	ret = prepend_text+sign_text+bounded_number+mantissa_append+prefix_letter if number != 0 else ' '*3+'0'+('.' if mantissa > 0 else '')+('0'*mantissa)+' '
	return ret.strip() if rjust is False else ret

def peng_unit(text):
	""" Return unit of number string in engineering notation """
	unit = text.strip()[-1]
	return unit if unit.isdigit() is False else ' '

def peng_unit_math(center, offset):
	""" Return engineering unit letter based on a center/start unit and an offset of units """
	cindex = _UNIT_LIST.index(center)
	oindex = max(0, min(len(_UNIT_LIST)-1, cindex+offset))
	return _UNIT_LIST[oindex]

def peng_power(text):
	""" Return exponent of number string in engineering notation """
	text = text.strip()
	if len(text) > 0:
		unit = peng_unit(text)
		if unit in _UNIT_LIST:
			return (unit, float(pow(10, 3*(_UNIT_LIST.index(unit)-8))))
		else:
			raise Exception('Unrecognized unit '+unit+' in fucntion peng_scale')
	else:
		raise Exception('Empty number passed to function peng_scale')

def peng_int(text):
	""" Return integer part of number string in engineering notation """
	text = text.strip()
	return int(text[:text.find('.')]) if text.find('.') != -1 else int(text[:len(text) if peng_unit(text) == ' ' else -1])

def peng_mant(text):
	""" Return mantissa part of number string in engineering notation """
	text = text.strip()
	return 0 if text.find('.') == -1 else int(text[text.find('.')+1:len(text) if peng_unit(text) == ' ' else -1])

def peng_float(text):
	""" Return number without engineering unit of number string in engineering notation """
	text = text.strip()
	return float(text[:len(text) if peng_unit(text) == ' ' else -1])

def peng_num(text):
	""" Return float from number string in engineering notation """
	_, scale = peng_power(text)
	return peng_float(text)*scale
