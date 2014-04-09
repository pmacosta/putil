﻿"""
Decorators for API parameter checks
"""

import pytest
import decimal
import fractions
import functools

import util_check


# Dummy functions representing the actual function to be decorated
def func_all_positional_parameters(ppar1, ppar2, ppar3):	#pylint: disable-msg=C0111,W0613
	pass

def func_all_keyword_parameters(kpar1=1, kpar2=2, kpar3=3):	#pylint: disable-msg=C0111,R0913,W0613
	pass

def func_positional_and_keyword_parameters(ppar1, ppar2, ppar3, kpar1=1, kpar2=2, kpar3=3):	#pylint: disable-msg=C0103,C0111,R0913,W0613
	pass

def func_no_parameters():	#pylint: disable-msg=C0111,R0913,W0613
	pass

# Tests for get_function_args()
def test_get_function_args_all_positional_parameters():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when all parameters are positional parameters
	"""
	assert util_check.get_function_args(func_all_positional_parameters) == ('ppar1', 'ppar2', 'ppar3')

def test_get_function_args_all_keyword_parameters():	#pylint: disable-msg=C0103,W0613
	"""
	Test that function behaves properly when all parameters are keywords parameters
	"""
	assert util_check.get_function_args(func_all_keyword_parameters) == ('kpar1', 'kpar2', 'kpar3')

def test_get_function_args_positional_and_keyword_parameters():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when parameters are a mix of positional and keywords parameters
	"""
	assert util_check.get_function_args(func_positional_and_keyword_parameters) == ('ppar1', 'ppar2', 'ppar3', 'kpar1', 'kpar2', 'kpar3')

def test_get_function_args_no_parameters():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when there are no parameters passed
	"""
	assert util_check.get_function_args(func_no_parameters) == ()

# Tests for create_parameter_dictionary()
def ret_func(par):
	"""
	Returns the passed parameter
	"""
	return par

def decfunc(func):
	""""
	Decorator function to test create_parameter_dictionary function
	"""
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		"""
		Wrapper function that creates the parameter dictionary and returns a ret_func, which in turn just returns the parameter passed. This is for testing only, obviously
		in an actual environment the dedcorator would return the original (called) function with the passed parameters
		"""
		return ret_func(util_check.create_parameter_dictionary(func, *args, **kwargs))
	return wrapper

def test_create_parameter_dictionary_all_positional_parameters():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when all parameters are positional parameters
	"""
	@decfunc
	def orig_func_all_positional_parameters(ppar1, ppar2, ppar3):	#pylint: disable-msg=C0103,C0111,W0613
		pass
	assert orig_func_all_positional_parameters(1, 2, 3) == {'ppar1':1, 'ppar2':2, 'ppar3':3}

def test_create_parameter_dictionary_all_keyword_parameters():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when all parameters are keyword parameters
	"""
	@decfunc
	def orig_func_all_keyword_parameters(kpar1, kpar2, kpar3):	#pylint: disable-msg=C0103,C0111,W0613
		pass
	assert orig_func_all_keyword_parameters(kpar3=3, kpar2=2, kpar1=1) == {'kpar1':1, 'kpar2':2, 'kpar3':3}


def test_create_parameter_dictionary_positional_and_keyword_parameters():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when parameters are a mix of positional and keywords parameters
	"""
	@decfunc
	def orig_func_positional_and_keyword_parameters(ppar1, ppar2, ppar3, kpar1=1, kpar2=2, kpar3=3):	#pylint: disable-msg=C0103,C0111,R0913,W0613
		pass
	assert orig_func_positional_and_keyword_parameters(10, 20, 30, kpar2=1.5, kpar3='x', kpar1=[1, 2]) == {'ppar1':10, 'ppar2':20, 'ppar3':30, 'kpar1':[1, 2], 'kpar2':1.5, 'kpar3':'x'}

def test_create_parameter_dictionary_no_parameters():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when there are no parameters passed
	"""
	@decfunc
	def orig_func_no_parameters():	#pylint: disable-msg=C0103,C0111,R0913,W0613
		pass
	assert orig_func_no_parameters() == {}

def test_create_parameter_dictionary_more_positional_parameters_passed_than_defined():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when there are more parameters passed by position than in the function definition
	"""
	@decfunc
	def orig_func(ppar1):	#pylint: disable-msg=C0103,C0111,R0913,W0613
		pass
	assert orig_func(1, 2, 3) == {}	#pylint: disable-msg=E1121

def test_create_parameter_dictionary_more_keyword_parameters_passed_than_defined():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when there are more parameters passed by keyword than in the function definition
	"""
	@decfunc
	def orig_func(kpar1=0, kpar2=2):	#pylint: disable-msg=C0103,C0111,R0913,W0613
		pass
	assert orig_func(kpar1=1, kpar2=2, kpar3=3) == {}	#pylint: disable-msg=E1123

def test_create_parameter_dictionary_parameter_passed_by_position_and_keyword():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when there are parameters passed both by position and keyword
	"""
	@decfunc
	def orig_func(ppar1, ppar2, kpar1=1, kpar2=2):	#pylint: disable-msg=C0103,C0111,R0913,W0613
		pass
	assert orig_func(1, 2, ppar1=5) == {}	#pylint: disable-msg=E1124

# Tests for type_match()
def test_type_match_str():
	"""
	Test if function behaves proprely for string type
	"""
	assert (util_check.type_match('hello', str), util_check.type_match(135, str)) == (True, False)

def test_type_match_float():
	"""
	Test if function behaves proprely for float type
	"""
	assert (util_check.type_match(1.5, float), util_check.type_match(135, float)) == (True, False)

def test_type_match_int():
	"""
	Test if function behaves proprely for integer type
	"""
	assert (util_check.type_match(8, int), util_check.type_match(135.0, int)) == (True, False)

def test_type_match_number():
	"""
	Test if function behaves proprely for number pseudo-type (integer, real or complex)
	"""
	assert (util_check.type_match(1, util_check.Number()), util_check.type_match(135.0, util_check.Number()), util_check.type_match(1+1j, util_check.Number()), util_check.type_match('hello', util_check.Number())) == \
		(True, True, True, False)

def test_type_match_real():
	"""
	Test if function behaves proprely for real pseudo-type (integer or real)
	"""
	assert (util_check.type_match(1, util_check.Real()), util_check.type_match(135.0, util_check.Real()), util_check.type_match(1+1j, util_check.Real())) == (True, True, False)

def test_type_match_boolean():
	"""
	Test if function behaves proprely for boolean type
	"""
	assert (util_check.type_match(True, bool), util_check.type_match(12.5, bool)) == (True, False)

def test_type_match_decimal():
	"""
	Test if function behaves proprely for decimal type
	"""
	assert (util_check.type_match(decimal.Decimal(1.25), decimal.Decimal), util_check.type_match(12.5, decimal.Decimal)) == (True, False)

def test_type_match_fraction():
	"""
	Test if function behaves proprely for fraction type
	"""
	assert (util_check.type_match(fractions.Fraction(4, 6), fractions.Fraction), util_check.type_match(12.5, fractions.Fraction)) == (True, False)

def test_type_match_arbitrary_length_list():	#pylint: disable-msg=C0103
	"""
	Test if function behaves proprely for arbitrary length list type
	"""
	assert (util_check.type_match([1, 2, 3], util_check.ArbitraryLengthList(int)), util_check.type_match('hello', util_check.ArbitraryLengthList(int))) == (True, False)

def test_type_match_arbitrary_length_tuple():	#pylint: disable-msg=C0103
	"""
	Test if function behaves proprely for arbitrary length tuple type
	"""
	assert (util_check.type_match((1, 2, 3), util_check.ArbitraryLengthTuple(int)), util_check.type_match((1, 2, 'a'), util_check.ArbitraryLengthTuple(int))) == (True, False)

def test_type_match_arbitrary_length_set():	#pylint: disable-msg=C0103
	"""
	Test if function behaves proprely for arbitrary length set type
	"""
	assert (util_check.type_match(set([1, 2, 3]), util_check.ArbitraryLengthSet(int)), util_check.type_match(set([1, 2, 'a']), util_check.ArbitraryLengthSet(int))) == (True, False)

def test_type_match_fixed_length_list():	#pylint: disable-msg=C0103
	"""
	Test if function behaves proprely for fixed-length list type
	"""
	assert (util_check.type_match([1, 'a', 3.0], [int, str, float]), util_check.type_match([1, 'a', 3.0, 4.0], [int, str, float]), util_check.type_match([1, 'a', 3.0], [int, str, float, int]),
		 util_check.type_match([1, 2, 3.0], [int, str, float])) == (True, False, False, False)

def test_type_match_fixed_length_tuple():	#pylint: disable-msg=C0103
	"""
	Test if function behaves proprely for fixed-length tuple type
	"""
	assert (util_check.type_match((1, 'a', 3.0), (int, str, float)), util_check.type_match((1, 'a', 3.0, 4.0), (int, str, float)), util_check.type_match((1, 'a', 3.0), (int, str, float, int)),
		 util_check.type_match((1, 2, 3.0), (int, str, float))) == (True, False, False, False)

def test_type_match_fixed_length_set():	#pylint: disable-msg=C0103
	"""
	Test if function behaves proprely for fixed-length set type
	"""
	with pytest.raises(RuntimeError) as excinfo:
		util_check.type_match(set([1, 'a', 3.0]), set([int, str, float]))
	assert excinfo.value.message == 'Set is an un-ordered iterable, thus it cannot be type-checked against an ordered reference'


def test_type_match_one_of():	#pylint: disable-msg=C0103
	"""
	Test if function behaves proprely for one of a fixed number of finite choices
	"""
	assert (util_check.type_match('HELLO', util_check.OneOf(['HELLO', 45, 'WORLD'])), util_check.type_match(45, util_check.OneOf(['HELLO', 45, 'WORLD'])), util_check.type_match(1.0, util_check.OneOf(['HELLO', 45, 'WORLD']))) == \
		 (True, True, False)

def test_type_match_range():	#pylint: disable-msg=C0103
	"""
	Test if function behaves proprely for a numeric range
	"""
	assert (util_check.type_match(12, util_check.Range(minimum=2, maximum=5)), util_check.type_match('a', util_check.Range(minimum=2, maximum=5))) == (True, False)

def test_type_match_dict():
	"""
	Test if function behaves proprely for dictionary type
	"""
	assert (util_check.type_match({'a':'hello', 'b':12.5, 'c':[1]}, {'a':str, 'b':float, 'c':[int]}),	# 'Regular' match
		 util_check.type_match({'a':'hello', 'c':[1]}, {'a':str, 'b':float, 'c':[int]}),	# One key-value pair missing in test object, useful where parameter is omitted to get default
		 util_check.type_match({'x':'hello', 'y':{'n':[1.5, 2.3]}, 'z':[1]}, {'x':str, 'y':{'n':util_check.ArbitraryLengthList(float), 'm':str}, 'z':[int]}), # Nested
		 util_check.type_match({'a':'hello', 'b':35, 'c':[1]}, {'a':str, 'b':float, 'c':[int]}),	# Value of one key in test object does not match
		 util_check.type_match({'a':'hello', 'd':12.5, 'c':[1]}, {'a':str, 'b':float, 'c':[int]})) == (True, True, True, False, False)	# One key in test object does not appear in reference object

# Tests for check_type()
def test_check_type_simple_exception():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when a sigle (wrong) type is given (string, number, etc.)
	"""
	@util_check.check_type('ppar1', int)
	def func_check_type(ppar1):	#pylint: disable-msg=C0111
		print ppar1
	with pytest.raises(TypeError) as excinfo:
		func_check_type('Hello world')
	assert excinfo.value.message == 'Parameter ppar1 is of the wrong type'

def test_check_type_simple_no_exception():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when a sigle (right) type is given (string, number, etc.)
	"""
	@util_check.check_type(param_name='ppar1', param_type=util_check.Number())
	def func_check_type(ppar1):	#pylint: disable-msg=C0111
		print ppar1
	func_check_type(5.0)

def test_check_type_parameter_not_specified():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when the parameter to be checked is not specified in the function call
	"""
	@util_check.check_type(param_name='ppar2', param_type=util_check.Number())
	def func_check_type(ppar1, ppar2=None, ppar3=5):	#pylint: disable-msg=C0111
		print ppar1, ppar2, ppar3
	func_check_type(3, ppar3=12)

def test_check_type_parameter_specified_by_position_and_keyword():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when a parameter is specified both by position and keyword
	"""
	@util_check.check_type(param_name='ppar2', param_type=util_check.Number())
	def func_check_type(ppar1, ppar2=None, ppar3=5):	#pylint: disable-msg=C0111
		print ppar1, ppar2, ppar3
	with pytest.raises(TypeError) as excinfo:
		func_check_type(3, ppar3=12, ppar1=12)	#pylint: disable-msg=E1124
	assert excinfo.value.message == "func_check_type() got multiple values for keyword argument 'ppar1'"

def test_check_type_parameter_repeated_keyword_arguments():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when a parameter is specified multiple times by keyword
	"""
	@util_check.check_type(param_name='ppar2', param_type=util_check.Number())
	def func_check_type(ppar1, ppar2=None, ppar3=5):	#pylint: disable-msg=C0111
		print ppar1, ppar2, ppar3
	with pytest.raises(TypeError) as excinfo:
		func_check_type(3, ppar3=12, **{'ppar3':12})	#pylint: disable-msg=W0142
	assert excinfo.value.message == "func_check_type() got multiple values for keyword argument 'ppar3'"
