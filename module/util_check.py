"""
Decorators for API parameter checks
"""

import functools

import util_misc

class ArbitraryLength(object):	#pylint: disable-msg=R0903
	"""
	Base class for arbitrary length iterables
	"""
	def __init__(self, element_type):
		if not isinstance(element_type, type):
			raise TypeError('element_type parameter has to be a type')
		self.element_type = element_type

class ArbitraryLengthList(ArbitraryLength):	#pylint: disable-msg=R0903
	"""
	Arbitrary length lists
	"""
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, element_type)
		self.iter_type = list

class ArbitraryLengthTuple(ArbitraryLength):	#pylint: disable-msg=R0903
	"""
	Arbitrary length tuple
	"""
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, element_type)
		self.iter_type = tuple

class ArbitraryLengthSet(ArbitraryLength):	#pylint: disable-msg=R0903
	"""
	Arbitrary length set
	"""
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, element_type)
		self.iter_type = set

class OneOf(object):	#pylint: disable-msg=R0903
	"""
	Class for parmeters that can only take a value from a finite set
	"""
	def __init__(self, choices, case_sensitive=False):
		if not isinstance(case_sensitive, bool):
			raise TypeError('case_sensitive parameter must be boolean')
		# Check if choices parameter is an iterable with finite length, it can be made of heterogeneous, but finite, elements
		try:
			len(choices)
		except:
			raise TypeError('choices parameter has to be an iterable of finite length')
		# Check that iterable implements the __contain__() method, for "in" comparisons
		self.choices = choices
		self.types = set([type(element) for element in self.choices])	# Make it a set to speed up type comparison if there are repeated types
		self.case_sensitive = case_sensitive if str in self.types else None

	def __contains__(self, value):
		for obj in self.choices:
			if ((isinstance(obj, str)) and (isinstance(value, str)) and (self.case_sensitive is not None) and (not self.case_sensitive) and (obj.upper() == value.upper())) or (obj == value):
				return True
		return False

class Range(object):	#pylint: disable-msg=R0903
	"""
	Class for numeric parameters that can only take values in a certain range
	"""
	def __init__(self, minimum, maximum):
		if (minimum is not None) and (not util_misc.isreal(minimum)):
			raise TypeError('minimum parameter has to be None or a real number')
		if (maximum is not None) and (not util_misc.isreal(maximum)):
			raise TypeError('maximum parameter has to be None or a real number')
		if (minimum is None) and (maximum is None):
			raise TypeError('Either minimum or maximum parameters need to be specified')
		if type(minimum) != type(maximum):
			raise TypeError('minimum and maximum parameters have different types, the both have to be integers or floats')
		self.minimum = minimum
		self.maximum = maximum

class Number(object):	#pylint: disable-msg=R0903
	"""
	Number class (integer, real or complex)
	"""
	pass

class Real(object):	#pylint: disable-msg=R0903
	"""
	Number class (integer or real)
	"""
	pass

def get_function_args(func):
	"""
	Returns a list of the argument names, in order, as defined by the function
	"""
	code_obj = func.__code__
	return code_obj.co_varnames[:code_obj.co_argcount]

def create_parameter_dictionary(func, *args, **kwargs):
	"""
	Creates a dictionary where the keys are the parameter names and the values are the passed parameters values (if any)
	An empty dictionary is returned if an error is detected, such as more parameters than in the function definition, parameter(s) defined by position and keyword, etc.
	"""
	# Obtain parameters from function definiton
	func_args = get_function_args(func)
	# Validate that the number of positional parameters is correct
	if len(func_args) < len(args):
		return {}
	# Assign all positional arguments
	pos_dict = dict(zip(func_args, args))
	# Validate that there are no parameters defined by position and keyword
	if sum([1 if key in pos_dict else 0 for key in kwargs]) > 0:
		return {}
	# Validate that all keyword parameters passed exist in function definition
	if sum([1 if key not in func_args else 0 for key in kwargs]) > 0:
		return {}
	# Create output dictionary with values that are unique. A parameter is ommited if there is it is a repeated keyword parameter, or if the parameter is specified both by position and keyword
	return dict(pos_dict.items()+[(key, value) for key, value in kwargs.iteritems()])

def type_match(test_obj, ref_obj):	#pylint: disable-msg=R0911,R0912
	"""
	Test if two objects match type. The reference object can be a single type, e.g. ref_obj = str or ref_obj = int, or it can be a complex defintion like ref_obj = [str, [int], dict('a':float)]
	Heterogeneous iterables are not supported in part because there is no elegant way to distinguish, for example, between a 1-element list, a list of the type [str, float, int, str] and a list
	with all elements of the same type but one in which the length of the list is not known a priori (like a list containing the independent variable of an experiment)
	"""
	# Check for pseudo-type 'number' (integer, float or complex)
	if isinstance(ref_obj, Number):
		return util_misc.isnumber(test_obj)
	# Check for pseudo-type 'real' (integer or float)
	if isinstance(ref_obj, Real):
		return util_misc.isreal(test_obj)
	# Check for parameter being one of a finite number of choices defined in an iterable
	if isinstance(ref_obj, OneOf):
		return type(test_obj) in ref_obj.types
	# Check for parameter being in a numeric range
	if isinstance(ref_obj, Range):
		return type(test_obj) == type(ref_obj.minimum if ref_obj.minimum is not None else ref_obj.maximum)
	# Check for non-iterable types
	arbitrary_length_iterable = type(ref_obj) in [ArbitraryLengthList, ArbitraryLengthTuple, ArbitraryLengthSet]
	if ((not util_misc.isiterable(ref_obj)) and (not arbitrary_length_iterable) and (not isinstance(ref_obj, OneOf))) or isinstance(ref_obj, str):
		return isinstance(test_obj, ref_obj)
	# Check that the iterable type is the same
	if ((not arbitrary_length_iterable) and (not isinstance(test_obj, type(ref_obj)))) or (arbitrary_length_iterable and (not isinstance(test_obj, ref_obj.iter_type))):
		return False
	# Recursively check iterable sub-types
	if isinstance(ref_obj, dict):	# Dictionaries are a special case, have to check keys _and_ value type
		for key, test_subobj in test_obj.iteritems():
			if key not in ref_obj:
				return False
			if not type_match(test_subobj, ref_obj[key]):
				return False
	elif arbitrary_length_iterable:	# Arbitrary length lists, tuples or sets
		# Check elements of iterable are all of the right type
		ref_subobj = ref_obj.element_type
		for test_subobj in test_obj:
			if not type_match(test_subobj, ref_subobj):
				return False
	else:	# Fixed length iterables
		# Check that the iterable is not a set. Sets are un-ordered iterables, so it makes no sent to check them agains an ordered reference
		if isinstance(ref_obj, set):
			raise RuntimeError('Set is an un-ordered iterable, thus it cannot be type-checked against an ordered reference')
		# Check that both reference and test objects have the same length, otherwise abort
		if len(test_obj) != len(ref_obj):
			return False
		# Check that each element is of the right type
		for test_subobj, ref_subobj in zip(test_obj, ref_obj):
			if not type_match(test_subobj, ref_subobj):
				return False
	return True

def check_type(param_name, param_type):
	"""
	Checks that a parameter is of a certain type
	"""
	def actual_decorator(func):
		"""
		Actual decorator
		"""
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			"""
			Wrapper function to test parameter type
			"""
			# Obtain parameter dictionary, with the passed parameters and their values, an empty dictionary if there is an error in the parameter passing
			param_dict = create_parameter_dictionary(func, *args, **kwargs)
			# Check type and raise exception if necessary
			if (param_name in param_dict) and (not type_match(param_dict[param_name], param_type)):
				raise TypeError('Parameter {0} is of the wrong type'.format(param_name))
			return func(*args, **kwargs)
		return wrapper
	return actual_decorator

def check_parameter(param_name, param_spec):
	"""
	Checks that a parameter conforms to a certain specification (type, possibly range, one of a finite number of options, etc.)
	"""
	def actual_decorator(func):
		"""
		Actual decorator
		"""
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			"""
			Wrapper function to test parameter specification
			"""
			# Obtain parameter dictionary, with the passed parameters and their values, an empty dictionary if there is an error in the parameter passing
			param_dict = create_parameter_dictionary(func, *args, **kwargs)
			if param_name in param_dict:
				param = param_dict[param_name]
				# Check type and raise exception if necessary
				if not type_match(param, param_spec):
					raise TypeError('Parameter {0} is of the wrong type'.format(param_name))
				# Check range (if specified)
				if isinstance(param_spec, Range) and ((param_spec.minimum is not None) and (param < param_spec.minimum)) or ((param_spec.maximum is not None) and (param > param_spec.maximum)):
					raise ValueError('Parameter {0} is not in the range [{1}, {2}]'.format(param_name, '-inf' if param_spec.minimum is None else param_spec.minimum, '+inf' if param_spec.maximum is None else param_spec.maximum))
				# Check one of finite number of choices (if specified)
				if isinstance(param_spec, OneOf) and (param not in param_spec):
					raise ValueError('Parameter {0} is not one of {1} {2}'.format(param_name, param_spec.choices,
						('(case {0})'.format('sensitive' if param_spec.case_sensitive else 'insensitive')) if param_spec.case_sensitive is not None else ''))
			return func(*args, **kwargs)
		return wrapper
	return actual_decorator

