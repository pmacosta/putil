# misc.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Miscellaneous utility classes, methods, functions and constants
"""

import os
import sys
import numpy
import inspect
import textwrap
import tempfile

import putil.eng
import putil.check

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

def binary_string_to_octal_string(text):	#pylint: disable=C0103
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
	return (num is not None) and (not isinstance(num, bool)) and (isinstance(num, int) or isinstance(num, float) or isinstance(num, complex))

def isreal(num):
	"""
	Checks if the argument is a real number: float or integer
	"""
	return (num is not None) and (not isinstance(num, bool)) and (isinstance(num, int) or isinstance(num, float))

def per(numa, numb, prec=10):
	"""
	Calculates percentage difference between two numbers
	"""
	numa_type = 1 if isreal(numa) is True else (2 if (isinstance(numa, numpy.ndarray) is True) or (isinstance(numa, list) is True) else 0)	#pylint: disable=E1101
	numb_type = 1 if isreal(numb) is True else (2 if (isinstance(numb, numpy.ndarray) is True) or (isinstance(numb, list) is True) else 0)	#pylint: disable=E1101
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
		num_max = numpy.maximum(numa, numb)	#pylint: disable=E1101
		num_min = numpy.minimum(numa, numb)	#pylint: disable=E1101
		delta_vector = 1e-20*numpy.ones(len(num_max))	#pylint: disable=E1101
		num_min = numpy.where(num_min != 0, num_min, delta_vector)	#pylint: disable=E1101
		return numpy.where(numa == numb, 0, (num_max/num_min)-1)	#pylint: disable=E1101

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

class Bundle(object):	#pylint: disable=R0903
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
	Scale a series to the [0, 1] interval
	"""
	if (offset < 0) or (offset > 1):
		raise ValueError('Argument `offset` has to be in the [0.0, 1.0] range')
	if (value < min(series)) or (value > max(series)):
		raise ValueError('Argument `value` has to be within the bounds of the argument `series`')
	return offset+(((value-float(min(series)))/(float(max(series))-float(min(series))))*(1.0-offset))

def gcd(vector, precision=None):
	"""
	Calculates the greatest common divisor of an integer vector
	"""
	if len(vector) == 0:
		return None
	elif len(vector) == 1:
		return vector[0]
	elif len(vector) == 2:
		return pgcd(vector[0], vector[1]) if precision is None else smart_round(pgcd(vector[0], vector[1]), precision)
	else:
		current_gcd = pgcd(vector[0], vector[1])
		for element in vector[2:]:
			current_gcd = pgcd(current_gcd, element) if precision is None else smart_round(pgcd(current_gcd, element), precision)
		return current_gcd

def pgcd(num_a, num_b):
	"""Calculate the Greatest Common Divisor of a and b """
	while num_b:
		num_a, num_b = num_b, round(num_a % num_b, 10)
	return num_a

def isalpha(text):
	"""
	Returns True if the text has at least one alphabetic character
	"""
	try:
		float(text)
		return True
	except ValueError:
		return False

def ishex(char):
	"""
	Returns True if character is a valid hexadecimal digit
	"""
	return True if (isinstance(char, str) is True) and (len(char) == 1) and (char.upper() in '0123456789ABCDEF') else False

def smart_round(num, ndigits):
	"""
	Rounds a floating point number or Numpy vector
	"""
	if num is None:
		return num
	elif isinstance(num, numpy.ndarray):
		num = num.astype(float)
		sign = numpy.sign(num)	# sign() is zero where element is zero, will zero out results
		num = numpy.where(num == 0, 1.0, num)	# Replace zero elements with a dummy value that will not produce an error with log10(), the values will be zero out in the result when multiplied by sign
		exp = (numpy.log10(numpy.abs(num)).astype(int)).astype(float)
		return sign*numpy.round(numpy.abs(num)*(10**-exp), ndigits)*(10**exp)
	else:
		if num == 0:
			return num
		else:
			index = str(num).find('.')
			return round(num, ndigits-(0 if index == -1 else index)+(1 if num < 0.0 else 0)+1)

def isiterable(obj):
	"""
	Tests whether an objects is an iterable
	"""
	try:
		iter(obj)
	except:	#pylint: disable=W0702
		return False
	else:
		return True

def numpy_pretty_print(vector, limit=False, width=None, indent=0, eng=False, mant=None):	#pylint: disable=R0913
	"""
	Formats Numpy vectors for printing
	"""
	if vector is None:
		return 'None'
	mant = 3 if eng and (mant is None) else mant
	token = '{0:.'+str(mant)+'f}' if (mant is not None) and (not eng) else '{0}'
	if (not limit) or (limit and (len(vector) < 7)):
		uret = '[ '+(', '.join([token.format(_oprint(element, eng, mant)) for element in vector]))+' ]'
	else:
		fstring = '[ '+(' '.join([token.replace('0:', str(num)+':') for num in range(3)]))+' ... '+(' '.join([token.replace('0:', str(num)+':') for num in range(3, 6)]))+' ]' \
			if (mant is not None) and (not eng) else '[ {0} {1} {2} ... {3} {4} {5} ]'
		uret = fstring.format(_oprint(vector[0], eng, mant), _oprint(vector[1], eng, mant), _oprint(vector[2], eng, mant), _oprint(vector[-3], eng, mant), _oprint(vector[-2], eng, mant), _oprint(vector[-1], eng, mant))
	if width is None:
		return uret
	# Add indent for lines after first one, cannot use subsequent_indent of textwrap.wrap() method as this function counts the indent as part of the line
	return '\n'.join([((indent+2)*' ')+line if num > 0 else line for num, line in enumerate(textwrap.wrap(uret, width=width))])

def _oprint(element, eng, mant):
	"""
	Print a straigth number or one with engineering notation
	"""
	return element if not eng else putil.eng.peng(element, mant, True)

def elapsed_time_string(start_time, stop_time):
	""" Returns a formatted string with the ellapsed time between two time points. The string includes years (365 days), months (30 days), days (24 hours), hours (60 minutes), minutes (60 seconds) and seconds.
	If **start_time** is greater than the **stop_time**, the string returned is 'Invalid time delta specification'. If **start_time** and **stop_time** are equal, the string returned
	is 'None'. Otherwise, the string returned is [YY year[s], [MM month[s], [DD day[s], [HH hour[s], [MM minute[s] [and SS second[s]]]]]]. Any piece (year[s], month[s], etc.) is omitted if the number of the
	token is null/zero.

	:param	start_time:	Starting time point
	:type	start_time:	`datetime <https://docs.python.org/2/library/datetime.html#datetime-objects>`_ object
	:param	stop_time:	Ending time point
	:type	stop_time:	`datetime`_ object
	:rtype:				string
	"""
	if start_time > stop_time:
		return 'Invalid time delta specification'
	delta_time = stop_time-start_time
	tot_seconds = int(delta_time.total_seconds())
	years, remainder = divmod(tot_seconds, 365*24*60*60)
	months, remainder = divmod(remainder, 30*24*60*60)
	days, remainder = divmod(remainder, 24*60*60)
	hours, remainder = divmod(remainder, 60*60)
	minutes, seconds = divmod(remainder, 60)
	ret_list = ['{0} {1}{2}'.format(num, desc, 's' if num > 1 else '') for num, desc in zip([years, months, days, hours, minutes, seconds], ['year', 'month', 'day', 'hour', 'minute', 'second']) if num > 0]
	if len(ret_list) == 0:
		return 'None'
	elif len(ret_list) == 1:
		return ret_list[0]
	elif len(ret_list) == 2:
		return ret_list[0]+' and '+ret_list[1]
	else:
		return (', '.join(ret_list[0:-1]))+' and '+ret_list[-1]

###
# Context manager to create temporary files and delete them after it has been read
###
class TmpFile(object):	#pylint: disable=R0903
	"""
	Context manager for temporary files

	:param	fpointer: Function pointer to a function that writes data to file
	:type	fpointer: function pointer
	:returns:	File name of temporary file
	:rtype:		string
	:raises:	TypeError (Argument `fpointer` is of the wrong type)
	"""
	def __init__(self, fpointer=None):
		putil.check.check_arguments({'fpointer':putil.check.PolymorphicType([None, putil.check.Function()])})
		self.file_name = None
		self.fpointer = fpointer

	def __enter__(self):
		with tempfile.NamedTemporaryFile(delete=False) as fobj:
			if self.fpointer is not None:
				self.fpointer(fobj)
			self.file_name = fobj.name
		return self.file_name

	def __exit__(self, exc_type, exc_value, exc_tb):
		os.remove(self.file_name)
		if exc_type is not None:
			return False


def strframe(obj, extended=False):
	"""
	Pretty prints a stack frame

	:param	obj: Frame record, typically an item of a list produced by ``inspect.stack()``
	:type	obj: frame record
	:rtype:		string
	"""
	# Stack frame -> (frame object [0], filename [1], line number of current line [2], function name [3], list of lines of context from source code [4], index of current line within list [5])
	ret = list()
	ret.append('Frame object ID: {0}'.format(hex(id(obj[0]))))
	ret.append('File name......: {0}'.format(obj[1]))
	ret.append('Line number....: {0}'.format(obj[2]))
	ret.append('Functon name...: {0}'.format(obj[3]))
	ret.append('Context........: {0}'.format(obj[4]))
	ret.append('Index..........: {0}'.format(obj[5]))
	if extended:
		ret.append('f_back ID......: {0}'.format(hex(id(obj[0].f_back))))
		ret.append('f_builtins.....: {0}'.format(obj[0].f_builtins))
		ret.append('f_code.........: {0}'.format(obj[0].f_code))
		ret.append('f_globals......: {0}'.format(obj[0].f_globals))
		ret.append('f_lasti........: {0}'.format(obj[0].f_lasti))
		ret.append('f_lineno.......: {0}'.format(obj[0].f_lineno))
		ret.append('f_locals.......: {0}'.format(obj[0].f_locals))
		ret.append('f_restricted...: {0}'.format(obj[0].f_restricted))
		ret.append('f_trace........: {0}'.format(obj[0].f_trace))
	return '\n'.join(ret)


# From https://mail.python.org/pipermail/tutor/2006-August/048596.html
def delete_module(modname, paranoid=None):
	""" Deletes a previously imported module

	:param	modname: Module name
	:type	modname: string
	:param	paranoid: Symbols where it is desired to explicitly delete module reference
	:type	paranoid: list
	:raises:
	 * ValueError (Argument `paranoid` is not a finite list of symbols')

	 * ValueError (Module *[modname]* is not imported)
	"""
	try:
		thismod = sys.modules[modname]
	except KeyError:
		raise ValueError('Module {0} is not imported'.format(modname))
	these_symbols = dir(thismod)
	if paranoid:
		try:
			paranoid[:]  # sequence support
		except:
			raise ValueError('Argument `paranoid` is not a finite list of symbols')
		else:
			these_symbols = paranoid[:]
	del sys.modules[modname]
	for mod in sys.modules.values():
		try:
			delattr(mod, modname)
		except AttributeError:
			pass
		if paranoid:
			for symbol in these_symbols:
				if symbol[:2] == '__':  # ignore special symbols
					continue
				try:
					delattr(mod, symbol)
				except AttributeError:
					pass


def quote_str(obj):
	"""
	Adds extra quotes to string object

	:param	obj: Object to be quoted if string
	:type	obj: any
	:rtype:	Same as **obj**
	"""
	return obj if not isinstance(obj, str) else ("'{0}'".format(obj) if '"' in obj else '"{0}"'.format(obj))


def strtype_item(type_obj):
	""" Generates a string of a type definition (int, str, etc.) otherwise returns the sting of the object via the str() function """
	return str(type_obj).replace("<type '", '').replace("<class '", '')[:-2] if isinstance(type_obj, type) else (quote_str(type_obj) if isinstance(type_obj, str) else str(type_obj))


def strtype(type_obj):
	""" Generates a string of a type definition (int, str, etc.) or type definition list otherwise returns the sting or list of the object(s) via the str() function """
	if (not isiterable(type_obj)) or (type(type_obj) not in [dict, list, set, tuple]):
		return strtype_item(type_obj)
	if isinstance(type_obj, dict):
		return '{'+(', '.join(['"{0}":{1}'.format(key, strtype(value)) for key, value in type_obj.items()]))+'}'
	prefix = '[' if isinstance(type_obj, list) else ('(' if isinstance(type_obj, tuple) else 'set(')
	suffix = ']' if isinstance(type_obj, list) else ')'
	ret_list = [strtype(type_obj_item) for type_obj_item in type_obj]
	return '{0}{1}{2}'.format(prefix, ', '.join(ret_list), suffix)
