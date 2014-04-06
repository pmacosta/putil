"""
Decorators for API parameter checks
"""

import pytest
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

# Tests for check_type()
@util_check.check_type('ppar1', int)
def func_check_type(ppar1):	#pylint: disable-msg=C0111
	print ppar1

def test_check_type_simple_exception():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when a sigle (wrong) type is given (string, number, etc.)
	"""
	with pytest.raises(TypeError) as excinfo:
		func_check_type('Hello world')
	assert excinfo.value.message == 'Parameter ppar1 is of the wrong type'

def test_check_type_simple_no_exception():	#pylint: disable-msg=C0103
	"""
	Test that function behaves properly when a sigle (right) type is given (string, number, etc.)
	"""
	@util_check.check_type('ppar1', 'number')
	def func_check_type1(ppar1):	#pylint: disable-msg=C0111
		print ppar1

	func_check_type1(5.0)
