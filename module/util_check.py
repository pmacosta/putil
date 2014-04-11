"""
Decorators for API parameter checks
"""

import numpy
import pytest
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

class IncreasingRealNumpyVector(object):	#pylint: disable-msg=R0903
	"""
	Numpy vector where every element is a real number greater than the previous element
	"""
	def __init__(self):
		self.iter_type = type(numpy.array([]))
		self.element_type = Real()

class RealNumpyVector(object):	#pylint: disable-msg=R0903
	"""
	Numpy vector where every element is a real number
	"""
	def __init__(self):
		self.iter_type = type(numpy.array([]))
		self.element_type = Real()

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
	def __init__(self, minimum=None, maximum=None):
		if (minimum is not None) and (not util_misc.isreal(minimum)):
			raise TypeError('minimum parameter has to be None or a real number')
		if (maximum is not None) and (not util_misc.isreal(maximum)):
			raise TypeError('maximum parameter has to be None or a real number')
		if (minimum is None) and (maximum is None):
			raise TypeError('Either minimum or maximum parameters need to be specified')
		if (minimum is not None) and (maximum is not None) and (type(minimum) != type(maximum)):
			raise TypeError('minimum and maximum parameters have different types, the both have to be integers or floats')
		if (minimum is not None) and (maximum is not None) and (minimum > maximum):
			raise ValueError('minimum greater than maximum')
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

class PolymorphicType(object):	#pylint: disable-msg=R0903
	"""
	Class for polymorphic parameters
	"""
	def __init__(self, types):
		if (not isinstance(types, list)) and (not isinstance(types, tuple)) and (not isinstance(types, set)):
			raise TypeError('object parameter has to be a list, tuple or set')
		custom_types = [ArbitraryLengthList, ArbitraryLengthTuple, ArbitraryLengthSet, IncreasingRealNumpyVector, RealNumpyVector, OneOf, Range, Number, Real]
		for element_type in types:
			if (type(element_type) not in custom_types) and (not isinstance(element_type, type)) and (element_type is not None):
				raise TypeError('type element in types parameter has to be a type')
		self.instances = types
		self.types = [sub_type if type(sub_type) == type else type(sub_type) for sub_type in types]

	def __iter__(self):
		return iter(self.types)

	def find(self, req_type):
		"""
		Find sub-type in type iterable. Cannot use find since set() is supported
		"""
		for sub_type, sub_inst in zip(self.types, self.instances):
			if req_type == sub_type:
				return sub_inst
		raise ValueError('Requested sub-type not found')

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
	# Check for None pseudo-type
	if ref_obj is None:
		return test_obj is None
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
		return util_misc.isreal(test_obj) and (type(test_obj) == type(ref_obj.minimum if ref_obj.minimum is not None else ref_obj.maximum))
	# Check for poly-morphic types
	if isinstance(ref_obj, PolymorphicType):
		for ref_subobj in ref_obj.instances:
			if type_match(test_obj, ref_subobj):
				return True
		return False
	# Check for non-iterable types
	arbitrary_length_iterable = type(ref_obj) in [ArbitraryLengthList, ArbitraryLengthTuple, ArbitraryLengthSet, RealNumpyVector, IncreasingRealNumpyVector]
	if ((not util_misc.isiterable(ref_obj)) and (not arbitrary_length_iterable) and (not isinstance(ref_obj, OneOf))) or isinstance(ref_obj, str):
		return isinstance(test_obj, ref_obj)
	# At this point only iterables and dictionaries are left
	# Check build-in iterables (lists, tuples, sets, dictionaries, etc.) are of the same type
	if (not arbitrary_length_iterable) and (not isinstance(test_obj, type(ref_obj))):
		return False
	# Check that the custom iterables are of the same type
	if arbitrary_length_iterable and (not isinstance(test_obj, ref_obj.iter_type)):
		return False
	# Check that Numpy arrays are really vectors
	if (type(ref_obj) in [RealNumpyVector, IncreasingRealNumpyVector]) and (len(test_obj.shape) > 1):
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
				pseudo_types = [Range, OneOf, IncreasingRealNumpyVector]
				# Determine if a PolymorphicType definition has pseudo-types that need to be checked
				if isinstance(param_spec, PolymorphicType):
					temp_param_spec = [sub_inst for sub_type, sub_inst in zip(param_spec.types, param_spec.instances) if sub_type not in pseudo_types]	# Make a list of all types in original definition excluding pseudo-types
					check_pseudo_types = True
					if len(temp_param_spec) > 0:	# There are some sub-types in the polymorphic specification that are not pseudo-types
						# Types matching means that there are some sub-types that match the original definition minus the pseudo-types, do not need to validate the parameter against pseudo-types
						check_pseudo_types = not type_match(param, PolymorphicType(temp_param_spec))
				if (type(param_spec) in pseudo_types) or (isinstance(param_spec, PolymorphicType) and check_pseudo_types):
					# Validate custom pseudo-types
					check_list = list()
					for pseudo_type, validate_function in zip([Range, OneOf, IncreasingRealNumpyVector], [validate_range, validate_oneof, validate_increasingrealnumpyvector]):
						if (isinstance(param_spec, pseudo_type)) or (isinstance(param_spec, PolymorphicType) and (pseudo_type in param_spec.types)):
							ret = validate_function(param_name, param, param_spec if not isinstance(param_spec, PolymorphicType) else param_spec.find(pseudo_type))
							if ret is None:	# Not a polymorphic type and valid, or one of the polymorphic types and valid
								break
							if isinstance(param_spec, pseudo_type):	# Not a polymorphic type and invalid
								raise ValueError(ret)
							check_list.append(ret)
					else:	# Polymorphic type did not find a valid sub-type
						raise ValueError('\n'.join(check_list) if len(check_list) > 0 else check_list[0])
			return func(*args, **kwargs)
		return wrapper
	return actual_decorator

def validate_range(param_name, param, spec):
	"""
	Validate Range pseudo-type
	"""
	if (util_misc.isreal(param)) and (((spec.minimum is not None) and (param < spec.minimum)) or ((spec.maximum is not None) and (param > spec.maximum))):
		return 'Parameter {0} is not in the range [{1}, {2}]'.format(param_name, '-inf' if spec.minimum is None else spec.minimum, '+inf' if spec.maximum is None else spec.maximum)
	return None

def validate_oneof(param_name, param, spec):
	"""
	Validate OneOf pseudo-type
	"""
	if param not in spec.choices:
		return 'Parameter {0} is not one of {1}{2}'.format(param_name, spec.choices, (' (case {0})'.format('sensitive' if spec.case_sensitive else 'insensitive')) if spec.case_sensitive is not None else '')
	return None

def validate_increasingrealnumpyvector(param_name, param, spec):	#pylint: disable-msg=C0103,W0613
	"""
	Validate IncreasingRealNumpyVector pseudo-type
	"""
	return 'Parameter {0} is not an increasing Numpy vector'.format(param_name) if (isinstance(param, numpy.ndarray) and (len(param) > 0) and (min(numpy.diff(param)) <= 0)) else None
