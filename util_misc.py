"""
Miscellaneous utility classes, methods, functions and constants
"""

import numpy

def pcolor(text, color, tab=0):
	"""
	Print to terminal in a limited amount of colors
	"""
	esc_dict = {'black':30, 'red':31, 'green':32, 'yellow':33, 'blue':34, 'magenta':35, 'cyan':36, 'white':37}
	if isinstance(text, str) is False:
		raise TypeError('text has to be a string in pcolor function')
	if isinstance(color, str) is False:
		raise TypeError('color has to be a string in pcolor function')
	if isinstance(tab, int) is False:
		raise TypeError('tab has to be an intenger in pcolor function')
	color = color.lower()
	if color not in esc_dict.keys():
		raise RuntimeError('Color '+color+' not supported by pcolor function')
	return '\033['+str(esc_dict[color])+'m'+' '*tab+text+'\033[0m'

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

def per(numa, numb):
	"""
	Calculates percentage difference between two numbers
	"""
	numa_type = 1 if isreal(numa) is True else (2 if (isinstance(numa, numpy.ndarray) is True) or (isinstance(numa, list) is True) else 0)
	numb_type = 1 if isreal(numb) is True else (2 if (isinstance(numb, numpy.ndarray) is True) or (isinstance(numb, list) is True) else 0)
	if numa_type != numb_type:
		raise TypeError('Arguments are not of the same type in function per')
	if numa_type == 1:
		num_max = max(numa, numb)
		num_min = min(numa, numb)
		num_min = num_min if num_min != 0 else 1e-20
		return (num_max/num_min)-1
	else:
		num_max = numpy.maximum(numa, numb)
		num_min = numpy.minimum(numa, numb)
		min_vector = 1e-20*numpy.ones(len(num_max))
		num_min = numpy.where(num_min != 0, num_min, min_vector)
		return (num_max/num_min)-1
