"""
Decorators for API parameter checks
"""

import numpy
import funcsigs
import functools

import util_misc

class Number(object):	#pylint: disable=R0903
	"""	Number class (integer, real or complex)	"""
	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return util_misc.isnumber(test_obj)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

class Real(object):	#pylint: disable=R0903
	"""	Number class (integer or real) """
	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return util_misc.isreal(test_obj)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

class ArbitraryLength(object):	#pylint: disable=R0903
	""" Base class for arbitrary length iterables """
	def __init__(self, element_type):
		if not isinstance(element_type, type):
			raise TypeError('Parameter `element_type` is of the wrong type')
		self.element_type = element_type

	def includes(self, test_obj):	#pylint: disable=R0201
		""" Test that an object belongs to the pseudo-type """
		if not util_misc.isiterable(test_obj):
			return False
		for test_subobj in test_obj:
			if type(test_subobj) != self.element_type:
				return False
		return True

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

class ArbitraryLengthList(ArbitraryLength):	#pylint: disable=R0903
	""" Arbitrary length lists """
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, element_type)
		self.iter_type = list

	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return False if not isinstance(test_obj, self.iter_type) else ArbitraryLength.includes(self, test_obj)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

class ArbitraryLengthTuple(ArbitraryLength):	#pylint: disable=R0903
	""" Arbitrary length tuple """
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, element_type)
		self.iter_type = tuple

	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return False if not isinstance(test_obj, self.iter_type) else ArbitraryLength.includes(self, test_obj)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

class ArbitraryLengthSet(ArbitraryLength):	#pylint: disable=R0903
	"""	Arbitrary length set """
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, element_type)
		self.iter_type = set

	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return False if not isinstance(test_obj, self.iter_type) else ArbitraryLength.includes(self, test_obj)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

class OneOf(object):	#pylint: disable=R0903
	""" Class for parmeters that can only take a value from a finite set """
	def __init__(self, choices, case_sensitive=False):
		if not isinstance(case_sensitive, bool):
			raise TypeError('Parameter `case_sensitive` is of the wrong type')
		# Check if choices parameter is an iterable with finite length, it can be made of heterogeneous, but finite, elements
		try:
			len(choices)
		except:
			raise TypeError('Parameter `choices` is of the wrong type')
		self.pseudo_types = [Number, Real, ArbitraryLengthList, ArbitraryLengthTuple, ArbitraryLengthSet, OneOf, NumberRange, IncreasingRealNumpyVector, RealNumpyVector]
		self.choices = choices
		self.types = [type(element) for element in self.choices]
		self.case_sensitive = case_sensitive if str in self.types else None

	def __contains__(self, test_obj):
		for sub_type, sub_choice in zip(self.types, self.choices):
			# Compare pseudo-types
			if (sub_type in self.pseudo_types) and sub_choice.includes(test_obj):
				return True
			# Compare string with and without case sensitivity
			if (type(sub_choice) == type(test_obj)) and (sub_type is str) and (self.case_sensitive is not None) and \
					((sub_choice.upper() if not self.case_sensitive else sub_choice) == (test_obj.upper() if not self.case_sensitive else test_obj)):
				return True
			# Rest of types
			if (type(sub_choice) == type(test_obj)) and (sub_choice == test_obj):
				return True
		return False

	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return test_obj in self

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		for sub_type, sub_choice in zip(self.types, self.choices):
			if ((sub_type in self.pseudo_types) and sub_choice.istype(test_obj)) or ((sub_type not in self.pseudo_types) and (sub_type == type(test_obj))):
				return True
		return False

	def exception(self, msg):
		"""	Returns a suitable exception message """
		return '{0} is not one of {1}{2}'.format(msg, self.choices, (' (case {0})'.format('sensitive' if self.case_sensitive else 'insensitive')) if self.case_sensitive is not None else '')

class NumberRange(object):	#pylint: disable=R0903
	"""	Class for numeric parameters that can only take values in a certain range """
	def __init__(self, minimum=None, maximum=None):
		for value, name in zip([minimum, maximum], ['minimum', 'maximum']):
			if (value is not None) and (not util_misc.isreal(value)):
				raise TypeError('Parameter `{0}` is of the wrong type'.format(name))
		if (minimum is None) and (maximum is None):
			raise TypeError('Either parameter `minimum` or parameter `maximum` needs to be specified')
		if (minimum is not None) and (maximum is not None) and (type(minimum) != type(maximum)):
			raise TypeError('Parameters `minimum` and `maximum` have different types')
		if (minimum is not None) and (maximum is not None) and (minimum > maximum):
			raise ValueError('Parameter `minimum` greater than parameter `maximum`')
		self.minimum = minimum
		self.maximum = maximum
		self.type = type(self.minimum if self.minimum is not None else self.maximum)

	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return util_misc.isreal(test_obj) and (type(test_obj) == self.type) and (test_obj >= self.minimum if self.minimum is not None else test_obj) and \
			(test_obj <= self.maximum if self.maximum is not None else test_obj)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return type(test_obj) == self.type

	def exception(self, msg):
		""" Returns a suitable exception message """
		return '{0} is not in the range [{1}, {2}]'.format(msg, '-inf' if self.minimum is None else self.minimum, '+inf' if self.maximum is None else self.maximum)

class RealNumpyVector(object):	#pylint: disable=R0903
	""" Numpy vector where every element is a real number """
	def __init__(self):
		self.iter_type = type(numpy.array([]))
		self.element_type = Real()

	def includes(self, test_obj):	#pylint: disable=R0201
		""" Test that an object belongs to the pseudo-type """
		# Discard test object that are not Numpy arrays and Numpy arrays that are not Numpy vectors or zero length Numpy vectors
		if (type(test_obj) != self.iter_type) or ((type(test_obj) == self.iter_type) and ((len(test_obj.shape) > 1) or (len(test_obj) == 0))):
			return False
		# By comparing to a Numpy array object the comparison is machine/implementation independent as to how many number of bits are used to represent integers or floats
		return (test_obj.dtype.type == numpy.array([0]).dtype.type) or (test_obj.dtype.type == numpy.array([0.0]).dtype.type)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

class IncreasingRealNumpyVector(RealNumpyVector):	#pylint: disable=R0903
	""" Numpy vector where every element is a real number greater than the previous element	"""
	def __init__(self):
		RealNumpyVector.__init__(self)

	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return False if not RealNumpyVector.includes(self, test_obj) else (not min(numpy.diff(test_obj)) <= 0)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

class PolymorphicType(object):	#pylint: disable=R0903
	""" Class for polymorphic parameters """
	def __init__(self, types):
		if (not isinstance(types, list)) and (not isinstance(types, tuple)) and (not isinstance(types, set)):
			raise TypeError('Parameter `types` is of the wrong type')
		self.pseudo_types = [Number, Real, ArbitraryLengthList, ArbitraryLengthTuple, ArbitraryLengthSet, OneOf, NumberRange, IncreasingRealNumpyVector, RealNumpyVector]
		for element_type in types:
			if (type(element_type) not in self.pseudo_types) and (not isinstance(element_type, type)) and (element_type is not None):
				raise TypeError('Parameter `types` element is of the wrong type')
		self.instances = types
		self.types = [sub_type if type(sub_type) == type else type(sub_type) for sub_type in types]	# Custom types are technically objects of a pseudo-type class, so true type extraction is necessary

	def __iter__(self):
		return iter(self.types)

	def includes(self, test_obj):	#pylint: disable=R0201
		""" Test that an object belongs to the pseudo-type """
		for sub_type, sub_inst in zip(self.types, self.instances):
			if ((sub_type in self.pseudo_types) and sub_inst.includes(test_obj)) or ((sub_type not in self.pseudo_types) and isinstance(test_obj, sub_type)):
				return True
		return False

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		for sub_type, sub_inst in zip(self.types, self.instances):
			if ((sub_type in self.pseudo_types) and sub_inst.istype(test_obj)) or ((sub_type not in self.pseudo_types) and (type(test_obj) == sub_type)):
				return True
		return False

	def exception(self, msg, test_obj):
		""" Returns a suitable exception message """
		return '\n'.join([sub_inst.exception(msg) for sub_type, sub_inst in zip(self.types, self.instances) if (sub_type in self.pseudo_types) and (not sub_inst.includes(test_obj))])

def get_function_args(func):
	"""	Returns a list of the argument names, in order, as defined by the function """
	return tuple([par for par in funcsigs.signature(func).parameters])

def create_parameter_dictionary(func, *args, **kwargs):
	"""
	Creates a dictionary where the keys are the parameter names and the values are the passed parameters values (if any)
	An empty dictionary is returned if an error is detected, such as more parameters than in the function definition, parameter(s) defined by position and keyword, etc.
	"""
	try:
		return funcsigs.signature(func).bind_partial(*args, **kwargs).arguments
	except:	#pylint: disable=W0702
		return dict()

def type_match(test_obj, ref_obj):
	"""
	Test if two objects match type. The reference object can be a single type, e.g. ref_obj = str or ref_obj = int, or it can be a complex defintion like ref_obj = [str, [int], dict('a':float)]
	Heterogeneous iterables are not supported in part because there is no elegant way to distinguish, for example, between a 1-element list, a list of the type [str, float, int, str] and a list
	with all elements of the same type but one in which the length of the list is not known a priori (like a list containing the independent variable of an experiment)
	"""
	pseudo_types = [Number, Real, ArbitraryLengthList, ArbitraryLengthTuple, ArbitraryLengthSet, OneOf, NumberRange, IncreasingRealNumpyVector, RealNumpyVector, PolymorphicType]
	if ref_obj is None:	# Check for None
		ret_val = test_obj is None
	elif type(ref_obj) in pseudo_types:	# Check for pseudo-types
		ret_val = ref_obj.istype(test_obj)
	elif (not util_misc.isiterable(ref_obj)) or isinstance(ref_obj, str):	# Check for non-iterable types annd strings
		ret_val = isinstance(test_obj, ref_obj)
	elif isinstance(ref_obj, dict):	# Dictionaries
		ret_val = type_match_dict(test_obj, ref_obj)
	else:	# Fixed length iterables
		ret_val = type_match_fixed_length_iterable(test_obj, ref_obj)
	return ret_val

def type_match_dict(test_obj, ref_obj):
	"""	Test if two dictionaries match type (keys in the test dictionary are in the reference dictionary and the value types match)	"""
	if isinstance(test_obj, dict):
		for key, test_subobj in test_obj.iteritems():
			if (key not in ref_obj) or ((key in ref_obj) and (not type_match(test_subobj, ref_obj[key]))):
				return False
		return True
	return False

def type_match_fixed_length_iterable(test_obj, ref_obj):	#pylint: disable=C0103
	"""	Test that two fixed length iterables (lists, tuples, etc.) have the right element types at the right positions """
	# Check that the iterable is not a set. Sets are un-ordered iterables, so it makes no sent to check them agains an ordered reference
	if isinstance(ref_obj, set):
		raise RuntimeError('Set is an un-ordered iterable, thus it cannot be type-checked against an ordered reference')
	# Check that both reference and test objects are of the same type and have the same length
	if (not isinstance(test_obj, type(ref_obj))) or ((isinstance(test_obj, type(ref_obj))) and (len(test_obj) != len(ref_obj))):
		return False
	# Check that each element is of the right type
	for test_subobj, ref_subobj in zip(test_obj, ref_obj):
		if not type_match(test_subobj, ref_subobj):
			return False
	return True

def check_type(param_name, param_type):
	""" Checks that a parameter is of a certain type """
	def actual_decorator(func):
		"""	Actual decorator """
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			"""	Wrapper function to test parameter type	"""
			param_dict = create_parameter_dictionary(func, *args, **kwargs)
			if (param_name in param_dict) and (not type_match(param_dict[param_name], param_type)):
				raise TypeError('Parameter {0} is of the wrong type'.format(param_name))
			return func(*args, **kwargs)
		return wrapper
	return actual_decorator

def check_parameter(param_name, param_spec):	#pylint: disable=R0912
	"""	Checks that a parameter conforms to a certain specification (type, possibly range, one of a finite number of options, etc.)	"""
	def actual_decorator(func):
		"""	Actual decorator """
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			"""	Wrapper function to test parameter specification """
			param_dict = create_parameter_dictionary(func, *args, **kwargs)
			if param_name in param_dict:
				param = param_dict[param_name]
				if not type_match(param, param_spec):
					raise TypeError('Parameter {0} is of the wrong type'.format(param_name))
				pseudo_types = [Number, Real, ArbitraryLengthList, ArbitraryLengthTuple, ArbitraryLengthSet, OneOf, NumberRange, IncreasingRealNumpyVector, RealNumpyVector, PolymorphicType]
				if (type(param_spec) in pseudo_types) and (not param_spec.includes(param)):
					msg = 'Parameter {0}'.format(param_name)
					ekwargs = {'msg':msg} if type(param_spec) != PolymorphicType else {'msg':msg, 'test_obj':param}
					raise ValueError(param_spec.exception(**ekwargs))	#pylint: disable=W0142
			return func(*args, **kwargs)
		return wrapper
	return actual_decorator
