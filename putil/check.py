# check.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212,C0111

import os
import sys
import numpy
import inspect
import funcsigs
import decorator
import itertools

import putil.exh
import putil.misc


def get_function_args(func, no_self=False, no_varargs=False):
	"""	Returns a list of the argument names, in order, as defined by the function """
	par_dict = funcsigs.signature(func).parameters
	args = ['{0}{1}'.format('*' if par_dict[par].kind == par_dict[par].VAR_POSITIONAL else ('**' if par_dict[par].kind == par_dict[par].VAR_KEYWORD else ''), par) for par in par_dict]
	self_filtered_args = args if not args else (args[1 if (args[0] == 'self') and no_self else 0:])
	varargs_filtered_args = tuple([arg for arg in self_filtered_args if (not no_varargs) or (no_varargs and (not is_parg(arg)) and (not is_kwarg(arg)))])
	return varargs_filtered_args


def is_parg(arg):
	""" Returns True if arg argument is the name of a positional variable argument (i.e. *pargs) """
	return (len(arg) > 1) and (arg[0] == '*') and (arg[1] != '*')


def is_kwarg(arg):
	""" Returns True if arg argument is the name of a keyword variable argument (i.e. **kwargs) """
	return (len(arg) > 2) and (arg[:2] == '**')


def has_varargs(func):
	""" Returns True if function call includes variable arguments (i.e. *pargs and/or **kwargs) """
	return any([is_parg(arg) or is_kwarg(arg) for arg in get_function_args(func)])


_BASE_TYPES = list()
_BASE_DESC = list()

def _get_pseudo_types(base=True):
	""" Returns all pseduo-types available """
	return {'type':_BASE_TYPES, 'desc':_BASE_DESC} if base else {'type':_BASE_TYPES+[PolymorphicType], 'desc':_BASE_DESC+['polymorphic type']}


def register_new_type(cls, desc):
	""" Register new pseudo-data type """
	# Validate pseudo-type implementation correctness
	if not inspect.isclass(cls):
		raise TypeError('Pseudo type has to be a class')
	class_name = str(cls)[8:-2]
	for method in ['istype', 'includes', 'exception']:
		if getattr(cls, method, -1) == -1:
			raise TypeError('Pseudo type {0} must have an {1}() method'.format(class_name, method))
	nargs = len(get_function_args(cls.istype, no_self=True, no_varargs=True))
	if ((nargs == 0) and (not has_varargs(cls.istype))) or (nargs > 1):
		raise RuntimeError('Method {0}.istype() must have only one argument'.format(class_name))
	nargs = len(get_function_args(cls.includes, no_self=True, no_varargs=True))
	if ((nargs == 0) and (not has_varargs(cls.includes))) or (nargs > 1):
		raise RuntimeError('Method {0}.includes() must have only one argument'.format(class_name))
	args = get_function_args(cls.exception, no_self=True, no_varargs=True)
	if ((len(args) == 0) and (not has_varargs(cls.exception))) or ((len(args) > 1) and (not any([arg in ['param', 'param_name'] for arg in args]))):
		raise RuntimeError('Method {0}.exception() must have only `param` and/or `param_name` arguments'.format(class_name))
	_BASE_TYPES.append(cls)
	_BASE_DESC.append(desc)


class Any(object):	#pylint: disable=R0903
	""" Any data type class """
	def includes(self, test_obj):	#pylint: disable=R0201,W0613
		"""	Test that an object belongs to the pseudo-type """
		return True

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		return self.includes(test_obj)

	def exception(self, param_name):	#pylint: disable=R0201,W0613
		"""	Returns a suitable exception message """
		return {'type':None, 'msg':''}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.Any()'
register_new_type(Any, 'any')


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
		return {'type':ValueError, 'msg':'Argument `{0}` is not a number'.format(param_name)}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.Number()'
register_new_type(Number, 'number (real, integer or complex)')


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
		return {'type':ValueError, 'msg':'Argument `{0}` is not a positive integer'.format(param_name)}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.PositiveInteger()'
register_new_type(PositiveInteger, 'positive integer')

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
		return {'type':ValueError, 'msg':'Argument `{0}` is not a real number'.format(param_name)}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.Real()'
register_new_type(Real, 'real number')

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
		return {'type':ValueError, 'msg':'Argument `{0}` is not a positive real number'.format(param_name)}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.PositiveReal()'
register_new_type(PositiveReal, 'positive real number')


class ArbitraryLength(object):	#pylint: disable=R0903
	""" Base class for arbitrary length iterables """
	def __init__(self, iter_type, element_type, check_keys=True):
		if iter_type not in [list, tuple, set, dict]:
			raise TypeError('Argument `iter_type` is of the wrong type')
		if not is_type_def(element_type):
			raise TypeError('Argument `element_type` is of the wrong type')
		self.element_type = element_type
		self.iter_type = iter_type
		self.check_keys = check_keys

	def includes(self, test_obj):	#pylint: disable=R0201
		""" Test that an object belongs to the pseudo-type """
		if not isinstance(test_obj, self.iter_type):
			return False
		pseudo_types = _get_pseudo_types(False)['type']
		if isinstance(self.element_type, dict):
			for test_subobj in test_obj:
				if (not isinstance(test_subobj, dict)) or (isinstance(test_subobj, dict) and self.check_keys and (self.element_type.keys() != test_subobj.keys())):
					return False
				for key in self.element_type:
					robj = self.element_type[key]
					tobj = test_subobj[key]
					if ((type(robj) in pseudo_types) and (not get_includes(robj, tobj))) or ((type(robj) not in pseudo_types) and (robj != type(tobj))):
						return False
			return True
		else:
			for test_subobj in test_obj if not isinstance(test_obj, dict) else test_obj.values():
				if ((type(self.element_type) in pseudo_types) and (not get_includes(self.element_type, test_subobj))) or ((type(self.element_type) not in pseudo_types) and (self.element_type != type(test_subobj))):
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
		return {'type':TypeError, 'msg':'Argument `{0}` is of the wrong type'.format(param_name)}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.ArbitraryLength(iter_type={0}, element_type={1}, check_keys={2})'.format(putil.misc.strtype(self.iter_type), putil.misc.strtype(self.element_type), self.check_keys)


class ArbitraryLengthList(ArbitraryLength):	#pylint: disable=R0903
	""" Arbitrary length lists """
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, list, element_type)

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.ArbitraryLengthList(element_type={0})'.format(putil.misc.strtype(self.element_type))
register_new_type(ArbitraryLengthList, 'list')


class ArbitraryLengthTuple(ArbitraryLength):	#pylint: disable=R0903
	""" Arbitrary length tuple """
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, tuple, element_type)

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.ArbitraryLengthTuple(element_type={0})'.format(putil.misc.strtype(self.element_type))
register_new_type(ArbitraryLengthTuple, 'tuple')


class ArbitraryLengthSet(ArbitraryLength):	#pylint: disable=R0903
	"""	Arbitrary length set """
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, set, element_type)

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.ArbitraryLengthSet(element_type={0})'.format(putil.misc.strtype(self.element_type))
register_new_type(ArbitraryLengthSet, 'set')


class ArbitraryLengthDict(ArbitraryLength):	#pylint: disable=R0903
	"""	Arbitrary length set """
	def __init__(self, element_type):
		ArbitraryLength.__init__(self, dict, element_type, False)

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.ArbitraryLengthDict(element_type={0})'.format(putil.misc.strtype(self.element_type))
register_new_type(ArbitraryLengthDict, 'dictionary')


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
		for sub_type, sub_choice in itertools.izip(self.types, self.choices):
			# Compare pseudo-types
			if (sub_type in self.pseudo_types) and get_includes(sub_choice, test_obj):
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
		for sub_type, sub_choice in itertools.izip(self.types, self.choices):
			if ((sub_type in self.pseudo_types) and get_istype(sub_choice, test_obj)) or ((sub_type not in self.pseudo_types) and (sub_type == type(test_obj))):
				return True
		return False

	def exception(self, param_name):
		"""	Returns a suitable exception message """
		return {'type':ValueError, 'msg':'Argument `{0}` is not one of {1}{2}'.format(param_name, self.desc, (' (case {0})'.format('sensitive' if self.case_sensitive else 'insensitive')) if self.case_sensitive is not None else '')}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.OneOf(choices={0}, case_sensitive={1})'.format(putil.misc.strtype(self.choices), self.case_sensitive)
register_new_type(OneOf, 'one of many options')


class NumberRange(object):	#pylint: disable=R0903
	"""	Class for numeric arguments that can only take values in a certain range """
	def __init__(self, minimum=None, maximum=None):
		for value, name in itertools.izip([minimum, maximum], ['minimum', 'maximum']):
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
		return putil.misc.isreal(test_obj) and (test_obj >= (self.minimum if self.minimum is not None else test_obj)) and \
			(test_obj <= (self.maximum if self.maximum is not None else test_obj))

	def istype(self, test_obj):	#pylint: disable=R0201
		"""	Checks to see if object is of the same class type """
		return (type(test_obj) == int) or (type(test_obj) == float)

	def exception(self, param_name):
		""" Returns a suitable exception message """
		return {'type':ValueError, 'msg':'Argument `{0}` is not in the range [{1}, {2}]'.format(param_name, '-inf' if self.minimum is None else self.minimum, '+inf' if self.maximum is None else self.maximum)}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.NumberRange(minimum={0}, maximum={1})'.format('-infinity' if not self.minimum else self.minimum, '+infinity' if not self.maximum else self.maximum)
register_new_type(NumberRange, 'number interval')


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
		return {'type':ValueError, 'msg':'Argument `{0}` is not a Numpy vector of real numbers'.format(param_name)}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.RealNumpyVector()'
register_new_type(RealNumpyVector, 'real Numpy Vector')


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
		return {'type':ValueError, 'msg':'Argument `{0}` is not a Numpy vector of increasing real numbers'.format(param_name)}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.IncreasingRealNumpyVector()'
register_new_type(IncreasingRealNumpyVector, 'increasing real Numpy Vector')


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
		return {'type':IOError, 'msg':'File *[file_name]* could not be found', 'edata':{'field':'file_name', 'value':param}}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.File(check_existance={0})'.format(self.check_existance)
register_new_type(File, 'file')


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
		return {'type':ValueError, 'msg':'Argument `{0}` is not a function with {1} argument{2}'.format(param, self.num_pars, 's' if (self.num_pars is not None) and (self.num_pars > 1) else '')}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.Function(num_pars={0})'.format(self.num_pars)
register_new_type(Function, 'function')


class PolymorphicType(object):	#pylint: disable=R0903
	""" Class for polymorphic arguments """
	def __init__(self, types):
		if (not isinstance(types, list)) and (not isinstance(types, tuple)) and (not isinstance(types, set)):
			raise TypeError('Argument `types` is of the wrong type')
		self.pseudo_types = _get_pseudo_types()['type']
		for element_type in types:
			if (not is_type_def(element_type)) and (element_type is not None):
				raise TypeError('Argument `types` element is of the wrong type')
		self.instances = types
		self.types = [sub_type if type(sub_type) == type else type(sub_type) for sub_type in types]	# Custom types are technically objects of a pseudo-type class, so true type extraction is necessary

	def __iter__(self):
		return iter(self.types)

	def includes(self, test_obj):	#pylint: disable=R0201
		""" Test that an object belongs to the pseudo-type """
		for sub_type, sub_inst in itertools.izip(self.types, self.instances):
			if ((sub_type in self.pseudo_types) and get_includes(sub_inst, test_obj)) or ((sub_type not in self.pseudo_types) and isinstance(test_obj, sub_type)):
				return True
		return False

	def istype(self, test_obj):
		"""	Checks to see if object is of the same class type """
		for sub_inst in self.instances:
			if type_match(test_obj, sub_inst, strict_dict=isinstance(sub_inst, dict)):
				return True
		return False

	def exception(self, param_name, param=None, test_obj=None):
		""" Returns a suitable exception message """
		exp_dict = {'type':None, 'msg':''}
		if Any not in self.types:
			exp_dict_list = [get_exception(sub_inst, **({'param_name':param_name} if sub_type != File else {'param':param})) for sub_type, sub_inst in itertools.izip(self.types, self.instances) if \
					(sub_type in self.pseudo_types) and (get_istype(sub_inst, test_obj)) and (not get_includes(sub_inst, test_obj))]
			if exp_dict_list:
				# Check if all exceptions are of the same type, in which case raise an exception of that type, otherwise raise RuntimeError
				same_exp = all(item['type'] == exp_dict_list[0]['type'] for item in exp_dict_list)
				exp_type = exp_dict_list[0]['type'] if same_exp  else RuntimeError
				exp_msg = [('('+str(exp_dict['type'])[str(exp_dict['type']).rfind('.')+1:str(exp_dict['type']).rfind("'")]+') ' if not same_exp else '')+exp_dict['msg'] for exp_dict in exp_dict_list]
				exp_dict['type'] = exp_type
				exp_dict['msg'] = '\n'.join(exp_msg)
		return exp_dict

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.check.PolymorphicType(types={0})'.format(putil.misc.strtype(self.instances))


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

def is_type_def(obj):
	""" Check if object is a valid type definition """
	pseudo_types = _get_pseudo_types(False)['type']
	# Check for basic and pseudo-types
	if isinstance(obj, str):
		return False
	if (type(obj) in pseudo_types) or isinstance(obj, type):
		return True
	# Check for dictionaries and check keys recursively
	if isinstance(obj, dict):
		return all([is_type_def(obj[key]) for key in obj])
	else:
		# Other iterators should use pseudo-types
		return False


def type_match(test_obj, ref_obj, strict_dict=False):
	"""
	Test if two objects match type. The reference object can be a single type, e.g. ref_obj = str or ref_obj = int, or it can be a complex defintion like ref_obj = [str, [int], dict('a':float)]
	Heterogeneous iterables are not supported in part because there is no elegant way to distinguish, for example, between a 1-element list, a list of the type [str, float, int, str] and a list
	with all elements of the same type but one in which the length of the list is not known a priori (like a list containing the independent variable of an experiment)
	"""
	pseudo_types = _get_pseudo_types(False)['type']
	if ref_obj is None:	# Check for None
		ret_val = test_obj is None
	elif type(ref_obj) in pseudo_types:	# Check for pseudo-types
		ret_val = get_istype(ref_obj, test_obj)
	elif (not putil.misc.isiterable(ref_obj)) or isinstance(ref_obj, str):	# Check for non-iterable types annd strings
		ret_val = isinstance(test_obj, ref_obj)
	elif isinstance(ref_obj, dict):	# Dictionaries
		ret_val = type_match_dict(test_obj, ref_obj, strict_dict=strict_dict)
	else:	# Fixed length iterables
		ret_val = type_match_fixed_length_iterable(test_obj, ref_obj)
	return ret_val


def type_match_dict(test_obj, ref_obj, strict_dict=False):
	"""	Test if two dictionaries match type (keys in the test dictionary are in the reference dictionary and the value types match)	"""
	if isinstance(test_obj, dict) and ((not strict_dict) or (strict_dict and sorted(test_obj.keys()) == sorted(ref_obj.keys()))):
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
	for test_subobj, ref_subobj in itertools.izip(test_obj, ref_obj):
		if not type_match(test_subobj, ref_subobj):
			return False
	return True


def check_argument_type_internal(param_name, param_type, func, exhobj, *args, **kwargs):
	""" Checks that a argument is of a certain type """
	arg_dict = create_argument_dictionary(func, *args, **kwargs)
	if exhobj:
		ex_name = 'check_argument_type_internal_{0}'.format(param_name)
		exhobj.add_exception(name=ex_name, extype=TypeError, exmsg='Argument `{0}` is of the wrong type'.format(param_name))
		exhobj.raise_exception_if(name=ex_name, condition=(len(arg_dict) > 0) and (not type_match(arg_dict.get(param_name), param_type, strict_dict=isinstance(param_type, dict))))
	elif (len(arg_dict) > 0) and (not type_match(arg_dict.get(param_name), param_type, strict_dict=isinstance(param_type, dict))):
		raise TypeError('Argument `{0}` is of the wrong type'.format(param_name))


def check_argument_internal(param_name, param_spec, func, exhobj, *args, **kwargs):	#pylint: disable=R0914
	"""	Checks that a argument conforms to a certain specification (type, possibly range, one of a finite number of options, etc.)	"""
	check_argument_type_internal(param_name, param_spec, func, exhobj, *args, **kwargs)
	pseudo_types = _get_pseudo_types(False)['type']
	param = create_argument_dictionary(func, *args, **kwargs).get(param_name)
	if (param is not None) and (type(param_spec) in pseudo_types):
		sub_param_spec = [param_spec] if type(param_spec) != PolymorphicType else [sub_inst for sub_type, sub_inst in itertools.izip(param_spec.types, param_spec.instances) if \
			(sub_type in pseudo_types) and (get_istype(sub_inst, param)) and (Any not in param_spec.types)]
		if sub_param_spec:	# Eliminate PolymorphicType definitions that do not have any pseudo-type
			# Find out parameter expected by exception() method
			exparam_dict_list = list()
			for param_spec in sub_param_spec:
				if (not get_includes(param_spec, param)) or exhobj:
					exparam = funcsigs.signature(param_spec.exception).parameters
					fiter = iter(exparam.items())
					exparam_name = next(fiter)[0]
					exparam_dict_list.append({'param':param} if exparam_name == 'param' else {'param_name':param_name})
			ex_dict_list = [get_exception(param_spec, **exparam_dict) for param_spec, exparam_dict in itertools.izip(sub_param_spec, exparam_dict_list) if not get_includes(param_spec, param)]	#pylint: disable=W0142
			if exhobj:
				ex_dict_list_full = [get_exception(param_spec, **exparam_dict) for param_spec, exparam_dict in itertools.izip(sub_param_spec, exparam_dict_list)]	#pylint: disable=W0142
				for num, ex in enumerate(ex_dict_list_full):
					ex_name = 'check_argument_internal_{0}{1}'.format(param_name, '' if len(ex_dict_list_full) == 1 else num)
					exhobj.add_exception(name=ex_name, extype=ex['type'], exmsg=ex['msg'])
					if ('edata' in ex) and len(ex['edata']):
						exhobj.raise_exception_if(name=ex_name, condition=False, edata=ex['edata'])
					else:
						exhobj.raise_exception_if(name=ex_name, condition=False)
			exp_dict = dict()
			if len(ex_dict_list) == len(sub_param_spec):
				same_exp = all(item['type'] == ex_dict_list[0]['type'] for item in ex_dict_list)
				exp_dict['type'] = ex_dict_list[0]['type'] if same_exp else RuntimeError
				exp_dict['msg'] = '\n'.join(['{0}{1}'.format('('+str_exception(exp_dict['type'])+') ' if not same_exp else '', \
						format_msg(exp_dict['msg'], exp_dict['edata']) if ('edata' in exp_dict) and len(exp_dict['edata']) else exp_dict['msg']) for exp_dict in ex_dict_list])
				raise exp_dict['type'](exp_dict['msg'])


def str_exception(obj):
	""" Returns string with exception type from exception type objct """
	sobj = str(obj)
	return sobj[sobj.rfind('.')+1:sobj.rfind("'")]


def format_msg(msg, edata):
	""" Substitute parameters in exception message """
	edata = edata if isinstance(edata, list) else [edata]
	for field in edata:
		if 'field' not in field:
			raise ValueError('Key `field` not in field definition')
		if 'value' not in field:
			raise ValueError('Key `value` not in field definition')
		if '*[{0}]*'.format(field['field']) not in msg:
			raise RuntimeError('Field {0} not in exception message'.format(field['field']))
		msg = msg.replace('*[{0}]*'.format(field['field']), field['value'])
	return msg


def check_argument_type(param_name, param_type):
	""" Decorator to check that a argument is of a certain type """
	@decorator.decorator
	def wrapper(func, *args, **kwargs):
		"""	Wrapper function to test argument type """
		check_argument_type_internal(param_name, param_type, func, putil.exh.get_exh_obj(), *args, **kwargs)
		return func(*args, **kwargs)
	return wrapper


def check_argument(param_spec):	#pylint: disable=R0912
	"""	Decorator to check that a argument conforms to a certain specification (type, possibly range, one of a finite number of options, etc.)	"""
	@decorator.decorator
	def wrapper(func, *args, **kwargs):
		"""	Wrapper function to test argument specification """
		arguments = funcsigs.signature(func).parameters
		if not arguments:
			raise RuntimeError('Function {0} has no arguments'.format(func.__name__))
		fiter = iter(arguments.items())
		param_name = next(fiter)[0]
		if param_name == 'self':
			if len(arguments) == 1:
				raise RuntimeError('Function {0} has no arguments after self'.format(func.__name__))
			param_name = next(fiter)[0]
		check_argument_internal(param_name, param_spec, func, putil.exh.get_exh_obj(), *args, **kwargs)
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
			check_argument_internal(param_name, param_spec, func, putil.exh.get_exh_obj(), *args, **kwargs)
		return func(*args, **kwargs)
	return wrapper


def get_istype(ptype, obj):
	""" Get pseudo-type istype result with error checking """
	class_name = str(ptype.__class__)[8:-2]
	try:
		ret = ptype.istype(obj)
	except:
		raise RuntimeError('Error trying to obtain pseudo type {0}.istype() result'.format(class_name))
	if isinstance(ret, bool):
		return ret
	raise TypeError('Pseudo type {0}.istype() method needs to return a boolean value'.format(class_name))


def get_includes(ptype, obj):
	""" Get pseudo-type includes result with error checking """
	class_name = str(ptype.__class__)[8:-2]
	try:
		ret = ptype.includes(obj)
	except:
		raise RuntimeError('Error trying to obtain pseudo type {0}.includes() result'.format(class_name))
	if isinstance(ret, bool):
		return ret
	raise TypeError('Pseudo type {0}.includes() method needs to return a boolean value'.format(class_name))


def get_exception(ptype, **kwargs):
	""" Get pseudo-type exception result with error checking """
	class_name = str(ptype.__class__)[8:-2]
	try:
		ret = ptype.exception(**kwargs)
	except:
		raise RuntimeError('Error trying to obtain pseudo type {0}.exception() result'.format(class_name))
	if isinstance(ret, dict) and (((len(ret) == 2) and ('type' in ret) and ('msg' in ret) and isinstance(ret['msg'], str)) or \
							      ((len(ret) == 3) and ('type' in ret) and ('msg' in ret) and isinstance(ret['msg'], str) and ('edata' in ret))):
		if (ret['type'] is None) and (ret['msg'] == ''):
			return ret
		try:
			raise ret['type'](ret['msg'])
		except:	#pylint: disable=W0702
			if sys.exc_info()[1].message == ret['msg']:
				return ret
	raise TypeError('Pseudo type {0}.exception() method needs to return a dictionary with keys "type" and "msg", with the exception type object and exception message respectively'.format(class_name))
