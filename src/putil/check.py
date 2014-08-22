# check.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Decorators for API argument checks
"""

import os
import numpy
import inspect
import funcsigs
import decorator

import putil.misc


class Number(object):	#pylint: disable=R0903
	"""	Number class (integer, real or complex)	"""
	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return putil.misc.isnumber(test_obj)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

	def exception(self, param_name):	#pylint: disable=R0201
		"""	Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = ValueError
		exp_dict['msg'] = 'Argument `{0}` is not a number'.format(param_name)
		return exp_dict


class PositiveInteger(object):	#pylint: disable=R0903
	"""	PositiveInteger class (Integer greater than zero) """
	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return isinstance(test_obj, int) and (test_obj > 0)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

	def exception(self, param_name):	#pylint: disable=R0201
		"""	Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = ValueError
		exp_dict['msg'] = 'Argument `{0}` is not a positive integer'.format(param_name)
		return exp_dict


class Real(object):	#pylint: disable=R0903
	"""	Real class (integer or real) """
	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return putil.misc.isreal(test_obj)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

	def exception(self, param_name):	#pylint: disable=R0201
		"""	Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = ValueError
		exp_dict['msg'] = 'Argument `{0}` is not a real number'.format(param_name)
		return exp_dict


class PositiveReal(object):	#pylint: disable=R0903
	"""	PositiveReal class (integer or real greater than zero) """
	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return putil.misc.isreal(test_obj) and (test_obj > 0)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

	def exception(self, param_name):	#pylint: disable=R0201
		"""	Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = ValueError
		exp_dict['msg'] = 'Argument `{0}` is not a positive real number'.format(param_name)
		return exp_dict


class ArbitraryLength(object):	#pylint: disable=R0903
	""" Base class for arbitrary length iterables """
	def __init__(self, iter_type, element_type):
		if iter_type not in [list, tuple, set, dict]:
			raise TypeError('Argument `iter_type` is of the wrong type')
		pseudo_types = _get_pseudo_types(False)['type']
		if (type(element_type) not in pseudo_types) and (not isinstance(element_type, type)):
			raise TypeError('Argument `element_type` is of the wrong type')
		self.element_type = element_type
		self.iter_type = iter_type

	def includes(self, test_obj):	#pylint: disable=R0201
		""" Test that an object belongs to the pseudo-type """
		if not isinstance(test_obj, self.iter_type):
			return False
		pseudo_types = _get_pseudo_types(False)['type']
		for test_subobj in test_obj if not isinstance(test_obj, dict) else test_obj.values():
			if ((type(self.element_type) in pseudo_types) and (not self.element_type.includes(test_subobj))) or ((type(self.element_type) not in pseudo_types) and (self.element_type != type(test_subobj))):
				return False
		return True

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		if not isinstance(test_obj, self.iter_type):
			return False
		for test_subobj in test_obj if not isinstance(test_obj, dict) else test_obj.values():
			if not type_match(test_subobj, self.element_type):
				return False
		return True

	def exception(self, param_name):	#pylint: disable=R0201
		"""	Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = ValueError
		exp_dict['msg'] = 'Argument `{0}` is not a {1} of {2} objects'.format(param_name, str(self.iter_type)[7:-2], str(self.element_type)[7:-2])
		return exp_dict


class ArbitraryLengthList(ArbitraryLength):	#pylint: disable=R0903
	""" Arbitrary length lists """
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, list, element_type)


class ArbitraryLengthTuple(ArbitraryLength):	#pylint: disable=R0903
	""" Arbitrary length tuple """
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, tuple, element_type)


class ArbitraryLengthSet(ArbitraryLength):	#pylint: disable=R0903
	"""	Arbitrary length set """
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, set, element_type)


class ArbitraryLengthDict(ArbitraryLength):	#pylint: disable=R0903
	"""	Arbitrary length set """
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, dict, element_type)


class OneOf(object):	#pylint: disable=R0903
	""" Class for parmeters that can only take a value from a finite set """
	def __init__(self, choices, case_sensitive=False):
		if not isinstance(case_sensitive, bool):
			raise TypeError('Argument `case_sensitive` is of the wrong type')
		# Check if choices argument is an iterable with finite length, it can be made of heterogeneous, but finite, elements
		try:
			len(choices)
		except:
			raise TypeError('Argument `choices` is of the wrong type')
		pseudo_types_dict = _get_pseudo_types()
		self.pseudo_types = pseudo_types_dict['type']
		self.choices = choices
		str_choice_list = ["'"+choice+"'" if isinstance(choice, str) else (str(choice) if type(choice) not in self.pseudo_types else pseudo_types_dict['desc'][self.pseudo_types.index(type(choice))]) for choice in self.choices]
		self.desc = '['+ (', '.join(str_choice_list))+']'
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

	def exception(self, param_name):
		"""	Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = ValueError
		exp_dict['msg'] = 'Argument `{0}` is not one of {1}{2}'.format(param_name, self.desc, (' (case {0})'.format('sensitive' if self.case_sensitive else 'insensitive')) if self.case_sensitive is not None else '')
		return exp_dict


class NumberRange(object):	#pylint: disable=R0903
	"""	Class for numeric arguments that can only take values in a certain range """
	def __init__(self, minimum=None, maximum=None):
		for value, name in zip([minimum, maximum], ['minimum', 'maximum']):
			if (value is not None) and (not putil.misc.isreal(value)):
				raise TypeError('Argument `{0}` is of the wrong type'.format(name))
		if (minimum is None) and (maximum is None):
			raise TypeError('Either argument `minimum` or argument `maximum` needs to be specified')
		if (minimum is not None) and (maximum is not None) and (minimum > maximum):
			raise ValueError('Argument `minimum` greater than argument `maximum`')
		self.minimum = float(minimum) if minimum is not None else minimum
		self.maximum = float(maximum) if maximum is not None else maximum
		self.type = float

	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return putil.misc.isreal(test_obj) and (test_obj >= self.minimum if self.minimum is not None else test_obj) and \
			(test_obj <= self.maximum if self.maximum is not None else test_obj)

	def istype(self, test_obj):	#pylint: disable=R0201
		"""	Checks to see if object is of the same class type """
		return (type(test_obj) == int) or (type(test_obj) == float)

	def exception(self, param_name):
		""" Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = ValueError
		exp_dict['msg'] = 'Argument `{0}` is not in the range [{1}, {2}]'.format(param_name, '-inf' if self.minimum is None else self.minimum, '+inf' if self.maximum is None else self.maximum)
		return exp_dict


class RealNumpyVector(object):	#pylint: disable=R0903
	""" Numpy vector where every element is a real number """
	def __init__(self):
		self.iter_type = type(numpy.array([]))
		self.element_type = Real()

	def includes(self, test_obj):	#pylint: disable=R0201
		""" Test that an object belongs to the pseudo-type """
		# Discard test object that are not Numpy arrays and Numpy arrays that are not Numpy vectors or zero length Numpy vectors
		if (type(test_obj) != numpy.ndarray) or ((type(test_obj) == numpy.ndarray) and ((len(test_obj.shape) > 1) or ((len(test_obj.shape) == 1) and (test_obj.shape[0] == 0)))):
			return False
		# By comparing to a Numpy array object the comparison is machine/implementation independent as to how many number of bits are used to represent integers or floats
		return (test_obj.dtype.type == numpy.array([0]).dtype.type) or (test_obj.dtype.type == numpy.array([0.0]).dtype.type)

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

	def exception(self, param_name):	#pylint: disable=R0201
		"""	Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = ValueError
		exp_dict['msg'] = 'Argument `{0}` is not a Numpy vector of real numbers'.format(param_name)
		return exp_dict


class IncreasingRealNumpyVector(RealNumpyVector):	#pylint: disable=R0903
	""" Numpy vector where every element is a real number greater than the previous element	"""
	def __init__(self):
		RealNumpyVector.__init__(self)

	def includes(self, test_obj):	#pylint: disable=R0201
		"""	Test that an object belongs to the pseudo-type """
		return False if not RealNumpyVector.includes(self, test_obj) else (True if test_obj.shape[0] == 1 else (not min(numpy.diff(test_obj)) <= 0))

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

	def exception(self, param_name):	#pylint: disable=R0201
		"""	Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = ValueError
		exp_dict['msg'] = 'Argument `{0}` is not a Numpy vector of increasing real numbers'.format(param_name)
		return exp_dict


class File(object):	#pylint: disable=R0903
	""" File name string """
	def __init__(self, check_existance=False):
		if not isinstance(check_existance, bool):
			raise TypeError('Argument `check_existance` is of the wrong type')
		self.check_existance = check_existance

	def includes(self, test_obj):
		""" Test that an object belongs to the pseudo-type """
		return isinstance(test_obj, str) and ((not self.check_existance) or (self.check_existance and os.path.exists(test_obj)))

	def istype(self, test_obj):	#pylint: disable=R0201
		"""	Checks to see if object is of the same class type """
		return isinstance(test_obj, str)

	def exception(self, param):	#pylint: disable=R0201
		"""	Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = IOError
		exp_dict['msg'] = 'File {0} could not be found'.format(param)
		return exp_dict


class Function(object):	#pylint: disable=R0903
	""" Function pointer """
	def __init__(self, num_pars=None):
		if (num_pars is not None) and (not isinstance(num_pars, int)):
			raise TypeError('Argument `num_pars` is of the wrong type')
		self.num_pars = num_pars

	def includes(self, test_obj):
		""" Test that an object belongs to the pseudo-type """
		if not inspect.isfunction(test_obj):
			return False
		par_tuple = get_function_args(test_obj)
		multi_par = '*' in [par[0] for par in par_tuple]
		return multi_par or (self.num_pars is None) or ((not multi_par) and (self.num_pars is not None) and (len(par_tuple) == self.num_pars))

	def istype(self, test_obj):	#pylint: disable=R0201
		"""	Checks to see if object is of the same class type """
		return inspect.isfunction(test_obj)

	def exception(self, param):	#pylint: disable=R0201
		"""	Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = ValueError
		exp_dict['msg'] = 'Argument `{0}` is not a function with {1} argument{2}'.format(param, self.num_pars, 's' if (self.num_pars is not None) and (self.num_pars > 1) else '')
		return exp_dict


class PolymorphicType(object):	#pylint: disable=R0903
	""" Class for polymorphic arguments """
	def __init__(self, types):
		if (not isinstance(types, list)) and (not isinstance(types, tuple)) and (not isinstance(types, set)):
			raise TypeError('Argument `types` is of the wrong type')
		self.pseudo_types = _get_pseudo_types()['type']
		for element_type in types:
			if (type(element_type) not in self.pseudo_types) and (not isinstance(element_type, type)) and (element_type is not None):
				raise TypeError('Argument `types` element is of the wrong type')
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

	def exception(self, param_name, param=None, test_obj=None):
		""" Returns a suitable exception message """
		exp_dict_list = [sub_inst.exception(param_name if sub_type != File else param) for sub_type, sub_inst in zip(self.types, self.instances) if (sub_type in self.pseudo_types) and (not sub_inst.includes(test_obj))]
		same_exp = all(item['type'] == exp_dict_list[0]['type'] for item in exp_dict_list)
		exp_type = exp_dict_list[0]['type'] if same_exp  else RuntimeError
		exp_msg = [('('+str(exp_dict['type'])[str(exp_dict['type']).rfind('.')+1:str(exp_dict['type']).rfind("'")]+') ' if not same_exp else '')+exp_dict['msg'] for exp_dict in exp_dict_list]
		exp_dict = dict()
		exp_dict['type'] = exp_type
		exp_dict['msg'] = '\n'.join(exp_msg)
		return exp_dict


def get_function_args(func):
	"""	Returns a list of the argument names, in order, as defined by the function """
	par_dict = funcsigs.signature(func).parameters
	return tuple(['{0}{1}'.format('*' if par_dict[par].kind == par_dict[par].VAR_POSITIONAL else ('**' if par_dict[par].kind == par_dict[par].VAR_KEYWORD else ''), par) for par in par_dict])

def create_argument_dictionary(func, *args, **kwargs):
	"""
	Creates a dictionary where the keys are the argument names and the values are the passed arguments values (if any)
	An empty dictionary is returned if an error is detected, such as more arguments than in the function definition, argument(s) defined by position and keyword, etc.
	"""
	# Capture parameters that have been explicitly specified in function call
	try:
		arg_dict = funcsigs.signature(func).bind_partial(*args, **kwargs).arguments
	except:	#pylint: disable=W0702
		return dict()
	# Capture parameters that have not been explicitly specified but have default values
	arguments = funcsigs.signature(func).parameters
	for arg_name in arguments:
		if (arguments[arg_name].default != funcsigs.Parameter.empty) and (arguments[arg_name].name not in arg_dict):
			arg_dict[arguments[arg_name].name] = arguments[arg_name].default
	return arg_dict

def type_match(test_obj, ref_obj):
	"""
	Test if two objects match type. The reference object can be a single type, e.g. ref_obj = str or ref_obj = int, or it can be a complex defintion like ref_obj = [str, [int], dict('a':float)]
	Heterogeneous iterables are not supported in part because there is no elegant way to distinguish, for example, between a 1-element list, a list of the type [str, float, int, str] and a list
	with all elements of the same type but one in which the length of the list is not known a priori (like a list containing the independent variable of an experiment)
	"""
	pseudo_types = _get_pseudo_types(False)['type']
	if ref_obj is None:	# Check for None
		ret_val = test_obj is None
	elif type(ref_obj) in pseudo_types:	# Check for pseudo-types
		ret_val = ref_obj.istype(test_obj)
	elif (not putil.misc.isiterable(ref_obj)) or isinstance(ref_obj, str):	# Check for non-iterable types annd strings
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
	# Check that the iterable is not a set. Sets are un-ordered iterables, so it makes no sense to check them against an ordered reference
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

def check_argument_type_internal(param_name, param_type, func, *args, **kwargs):
	""" Checks that a argument is of a certain type """
	arg_dict = create_argument_dictionary(func, *args, **kwargs)
	if (len(arg_dict) > 0) and (not type_match(arg_dict.get(param_name), param_type)):
		raise TypeError('Argument `{0}` is of the wrong type'.format(param_name))

def check_argument_internal(param_name, param_spec, func, *args, **kwargs):
	"""	Checks that a argument conforms to a certain specification (type, possibly range, one of a finite number of options, etc.)	"""
	check_argument_type_internal(param_name, param_spec, func, *args, **kwargs)
	param = create_argument_dictionary(func, *args, **kwargs).get(param_name)
	if param is not None:
		pseudo_types = _get_pseudo_types(False)['type']
		if (type(param_spec) in pseudo_types) and (not param_spec.includes(param)):
			ekwargs = {'param':param} if type(param_spec) == File else ({'param_name':param_name} if type(param_spec) != PolymorphicType else {'param_name':param_name, 'param':param, 'test_obj':param_spec})
			exp_dict = param_spec.exception(**ekwargs)	#pylint: disable=W0142
			raise exp_dict['type'](exp_dict['msg'])

def check_argument_type(param_name, param_type):
	""" Decorator to check that a argument is of a certain type """
	@decorator.decorator
	def wrapper(func, *args, **kwargs):
		"""	Wrapper function to test argument type """
		check_argument_type_internal(param_name, param_type, func, *args, **kwargs)
		return func(*args, **kwargs)
	return wrapper

def check_argument(param_spec):	#pylint: disable=R0912
	"""	Decorator to check that a argument conforms to a certain specification (type, possibly range, one of a finite number of options, etc.)	"""
	@decorator.decorator
	def wrapper(func, *args, **kwargs):
		"""	Wrapper function to test argument specification """
		arguments = funcsigs.signature(func).parameters
		if len(arguments) == 0:
			raise RuntimeError('Function {0} has no arguments'.format(func.__name__))
		fiter = iter(arguments.items())
		param_name = next(fiter)[0]
		if param_name == 'self':
			if len(arguments) == 1:
				raise RuntimeError('Function {0} has no arguments after self'.format(func.__name__))
			param_name = next(fiter)[0]
		check_argument_internal(param_name, param_spec, func, *args, **kwargs)
		return func(*args, **kwargs)
	return wrapper

def check_arguments(param_dict):	#pylint: disable=R0912
	"""	Decorator to check that a argument conforms to a certain specification (type, possibly range, one of a finite number of options, etc.)	"""
	@decorator.decorator
	def wrapper(func, *args, **kwargs):
		"""	Wrapper function to test argument specification """
		arguments = funcsigs.signature(func).parameters
		if len(arguments) == 0:
			raise RuntimeError('Function {0} has no arguments'.format(func.__name__))
		fiter = iter(arguments.items())
		param_name = next(fiter)[0]
		if param_name == 'self':
			if len(arguments) == 1:
				raise RuntimeError('Function {0} has no arguments after self'.format(func.__name__))
		for param_name, param_spec in param_dict.items():
			if param_name not in arguments:
				raise RuntimeError('Argument {0} is not an argument of function {1}'.format(param_name, func.__name__))
			check_argument_internal(param_name, param_spec, func, *args, **kwargs)
		return func(*args, **kwargs)
	return wrapper

def _get_pseudo_types(base=True):
	""" Returns all pseduo-types available """
	base_types = [Number, PositiveInteger, Real, PositiveReal, ArbitraryLengthList, ArbitraryLengthTuple, ArbitraryLengthSet, OneOf, NumberRange, IncreasingRealNumpyVector, RealNumpyVector, File, Function]
	all_types = base_types+[PolymorphicType]
	base_desc = ['number (real, integer or complex)', 'positive integer', 'real number', 'positive real number', 'list', 'tuple', 'set', 'one of many types', 'increasing Numpy vector', 'real Numpy Vector', 'file', 'function']
	all_desc = base_desc+['polymorphic type']
	return {'type':base_types, 'desc':base_desc} if base else {'type':all_types, 'desc':all_desc}
