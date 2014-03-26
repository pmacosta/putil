"""
Miscellaneous utility classes, methods, functions and constants
"""

import os
import numpy
import inspect
import fractions

def pcolor(text, color, tab=0):
	"""
	Print to terminal in a limited amount of colors
	"""
	esc_dict = {'black':30, 'red':31, 'green':32, 'yellow':33, 'blue':34, 'magenta':35, 'cyan':36, 'white':37, 'none':-1}
	if isinstance(text, str) is False:
		raise TypeError('text has to be a string in pcolor function')
	if isinstance(color, str) is False:
		raise TypeError('color has to be a string in pcolor function')
	if isinstance(tab, int) is False:
		raise TypeError('tab has to be an intenger in pcolor function')
	color = color.lower()
	if color not in esc_dict.keys():
		raise RuntimeError('Color "'+color+'" not supported by pcolor function')
	return '\033['+str(esc_dict[color])+'m'+' '*tab+text+'\033[0m' if esc_dict[color] != -1 else (' '*tab)+text

def binary_string_to_octal_string(text):	#pylint: disable-msg=C0103
	"""
	Prints binary string in octal representation replacing typical codes with their escape sequences
	"""
	octal_alphabet = [chr(num) if (num >= 32) and (num <= 126) else '\\'+str(oct(num)).lstrip('0') for num in xrange(0, 256)]
	octal_alphabet[0] = '\\0'	# Null character
	octal_alphabet[7] = '\\a'	# Bell/alarm
	octal_alphabet[8] = '\\b'	# Back space
	octal_alphabet[9] = '\\t'	# Horizontal tab
	octal_alphabet[10] = '\\n'	# Line feed
	octal_alphabet[11] = '\\v'	# Vertical tab
	octal_alphabet[12] = '\\f'	# Form feed
	octal_alphabet[13] = '\\r'	# Carriage return
	return ''.join([octal_alphabet[ord(char)] for char in text])

def char_to_decimal(text):
	"""
	Converts a string to its decimal ASCII representation, with spaces between characters
	"""
	return ' '.join([str(ord(char)) for char in text])

def isnumber(num):
	"""
	Checks if the argument is a number: complex, float or integer
	"""
	return True if (isinstance(num, int) is True) or (isinstance(num, float) is True) or (isinstance(num, complex) is True) else False

def isreal(num):
	"""
	Checks if the argument is a real number: float or integer
	"""
	return True if (isinstance(num, int) is True) or (isinstance(num, float) is True) else False

def per(numa, numb, prec=10):
	"""
	Calculates percentage difference between two numbers
	"""
	numa_type = 1 if isreal(numa) is True else (2 if (isinstance(numa, numpy.ndarray) is True) or (isinstance(numa, list) is True) else 0)	#pylint: disable-msg=E1101
	numb_type = 1 if isreal(numb) is True else (2 if (isinstance(numb, numpy.ndarray) is True) or (isinstance(numb, list) is True) else 0)	#pylint: disable-msg=E1101
	if numa_type != numb_type:
		raise TypeError('Arguments are not of the same type in function per')
	if numa_type == 1:
		numa = round(numa, prec)
		numb = round(numa, prec)
		num_max = max(numa, numb)
		num_min = min(numa, numb)
		num_min = num_min if num_min != 0 else 1e-20
		return 0 if numa == numb else (num_max/num_min)-1
	else:
		numa = numpy.round(numa, prec)
		numb = numpy.round(numb, prec)
		num_max = numpy.maximum(numa, numb)	#pylint: disable-msg=E1101
		num_min = numpy.minimum(numa, numb)	#pylint: disable-msg=E1101
		delta_vector = 1e-20*numpy.ones(len(num_max))	#pylint: disable-msg=E1101
		num_min = numpy.where(num_min != 0, num_min, delta_vector)	#pylint: disable-msg=E1101
		return numpy.where(numa == numb, 0, (num_max/num_min)-1)	#pylint: disable-msg=E1101

def get_method_obj(req_class_obj, method_name):
	"""
	Returns method executable object from a given class
	"""
	class_methods = inspect.getmembers(req_class_obj, predicate=inspect.ismethod)
	method_obj = None
	method_found = False
	for (name, method_obj) in class_methods:
		if name == method_name:
			method_found = True
			break
	if method_found is False:
		raise RuntimeError('method not found in class')
	return method_obj

class Bundle(object):	#pylint: disable-msg=R0903
	"""
	Bundle a collection of variables in one object
	"""
	def __init__(self, **kwds):
		self.__dict__.update(kwds)

	def __getitem__(self, elem):
		return self.__dict__[elem]

	def __setitem__(self, elem, value):
		self.__dict__[elem] = value

	def __delitem__(self, elem):
		self.__dict__.pop(elem)

	def __len__(self):
		return len(self.__dict__)

def b2s(var):
	"""
	Translates 1s and 0s to True's and False's
	"""
	if isinstance(var, bool) is False:
		raise TypeError('argument has to be boolean in function b2s')
	return 'True' if var is True else 'False'

def make_dir(file_name):
	"""
	Creates the directory of a fully qualified file name if it does not exists
	"""
	file_path, file_name = os.path.split(file_name)
	if os.path.exists(file_path) is False:
		os.makedirs(file_path)

def normalize(value, series, offset=0):
	"""
	Normalize a value based on the minimum and maximum of a series
	"""
	return offset+(((value-min(series))/float(max(series)-min(series)))/(1.0-offset))

def gcd(vector):
	"""
	Calculates the greatest common divisor of an integer vector
	"""
	if len(vector) == 0:
		return None
	elif len(vector) == 1:
		return vector[0]
	elif len(vector) == 2:
		return fractions.gcd(vector[0], vector[1])
	else:
		current_gcd = fractions.gcd(vector[0], vector[1])
		for element in vector[2:]:
			current_gcd = fractions.gcd(current_gcd, element)
		return current_gcd

def isalpha(text):
	"""
	Returns True if the text has at least one alphabetic character
	"""
	return True if (text.isalpha() is True) or ((text.isalnum() is True) and (text.isalpha() is False) and (text.isdigit() is False)) else False
