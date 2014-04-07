"""
Decorators for API parameter checks
"""

import functools

import util_misc

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

def type_match(test_obj, ref_obj):	#pylint: disable-msg=R0911
	"""
	Test if two objects match type. The reference object can be a single type, e.g. ref_obj = str or ref_obj = int, or it can be a complex defintion like ref_obj = [str, [int], dict('a':float)]
	Heterogeneous iterables are not supported in part because there is no elegant way to distinguish, for example, between a 1-element list, a list of the type [str, float, int, str] and a list
	with all elements of the same type but one in which the length of the list is not known a priori (like a list containing the independent variable of an experiment)
	"""
	# Check for pseudo-type 'number' (integer, float or complex)
	if isinstance(ref_obj, str) and (ref_obj.lower() == 'number'):
		return util_misc.isnumber(test_obj)
	# Check for pseudo-type 'real' (integer or float)
	if isinstance(ref_obj, str) and (ref_obj.lower() == 'real'):
		return util_misc.isreal(test_obj)
	# Check for non-iterable types
	if (not util_misc.isiterable(ref_obj)) or isinstance(ref_obj, str):
		return isinstance(test_obj, ref_obj)
	# Check that non-dictionary iterable types definitions are homogeneous (i.e. a single type)
	if (not isinstance(ref_obj, dict)) and (len(ref_obj) > 1):
		raise SyntaxError('Heterogeneous iterable specification')
	# Check that the iterable type is the same
	if not isinstance(test_obj, type(ref_obj)):
		return False
	# Recursively check iterable sub-types
	if isinstance(ref_obj, dict):	# Dictionaries are a special case, have to check keys _and_ value type
		for key, test_subobj in test_obj.iteritems():
			if key not in ref_obj:
				return False
			if not type_match(test_subobj, ref_obj[key]):
				return False
	else:	# Every other iterable, tuples, lists, sets, etc.
		ref_subobj = iter(ref_obj).next()	# Obtain first (and only) element of reference iterable, done this way instead of slicing because unordered iterables (like sets) do not support slicing
		for test_subobj in test_obj:
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
