"""
Decorators for API parameter checks
"""

import functools


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

def check_type(param, param_type):
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
			type_number = isinstance(param_type, str) and (param_type.lower() == 'number')
			if (param in param_dict) and (type(param_dict[param]) not in ([int, float] if type_number else [param_type])):
				raise TypeError('Parameter {0} is of the wrong type'.format(param))
			return func(*args, **kwargs)
		return wrapper
	return actual_decorator
