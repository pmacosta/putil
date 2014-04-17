"""
Decorators for API parameter checking unit tests
"""

import numpy
import pytest
import decimal
import fractions
import functools
import itertools

import util_check


###
# Test for Number class
###
def test_number_no_exception():
	"""	Test that Number class behaves appropriately when all parameters are correctly specified """
	util_check.Number()

def test_number_includes():
	"""	Test that the includes method of Number class behaves appropriately	"""
	ref_obj = util_check.Number()
	assert (ref_obj.includes(1), ref_obj.includes(2.0), ref_obj.includes(1+2j), ref_obj.includes('a'), ref_obj.includes([1, 2, 3])) == (True, True, True, False, False)

def test_number_istype():
	"""	Test that the istype method of Number class behaves appropriately """
	ref_obj = util_check.Number()
	assert (ref_obj.istype(1), ref_obj.istype(2.0), ref_obj.istype(1+2j), ref_obj.istype('a'), ref_obj.istype([1, 2, 3])) == (True, True, True, False, False)

###
# Test for Real class
###
def test_real_no_exception():
	"""	Test that Real class behaves appropriately when all parameters are correctly specified	"""
	util_check.Real()

def test_real_includes():
	"""	Test that the includes method of Real class behaves appropriately """
	ref_obj = util_check.Real()
	assert (ref_obj.includes(1), ref_obj.includes(2.0), ref_obj.includes(1+2j), ref_obj.includes('a'), ref_obj.includes([1, 2, 3])) == (True, True, False, False, False)

def test_real_istype():
	"""	Test that the istype method of Real class behaves appropriately """
	ref_obj = util_check.Real()
	assert (ref_obj.istype(1), ref_obj.istype(2.0), ref_obj.istype(1+2j), ref_obj.istype('a'), ref_obj.istype([1, 2, 3])) == (True, True, False, False, False)

###
# Test for ArbitraryLength class
###
def test_arbitrary_length_no_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLength class behaves appropriately when all parameters are correctly specified """
	obj_type = str
	obj = util_check.ArbitraryLength(obj_type)
	assert obj.element_type == obj_type

def test_arbitrary_length_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLength class behaves appropriately when inproper parameter type is passed """
	with pytest.raises(TypeError) as excinfo:
		util_check.ArbitraryLength('a')
	assert excinfo.value.message == 'Parameter `element_type` is of the wrong type'

def test_arbitrary_length_includes():
	"""	Test that the includes method of ArbitraryLength class behaves appropriately """
	ref_obj = util_check.ArbitraryLength(int)
	assert (ref_obj.includes([1, 2]), ref_obj.includes((1, 2)), ref_obj.includes(set([1.0, 2.0])), ref_obj.includes(1+2j), ref_obj.includes('a')) == (True, True, False, False, False)

def test_arbitrary_length_istype():
	"""	Test that the istype method of ArbitraryLength class behaves appropriately """
	ref_obj = util_check.ArbitraryLength(int)
	assert (ref_obj.istype([1, 2]), ref_obj.istype((1, 2)), ref_obj.istype(set([1.0, 2.0])), ref_obj.istype(1+2j), ref_obj.istype('a')) == (True, True, False, False, False)

###
# Test for ArbitraryLengthList class
###
def test_arbitrary_length_list_no_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLengthList class behaves appropriately when all parameters are correctly specified """
	obj_type = int
	obj = util_check.ArbitraryLengthList(obj_type)
	assert (obj.element_type == obj_type, obj.iter_type == list) == (True, True)

def test_arbitrary_length_list_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLengthList class behaves appropriately when inproper parameter type is passed """
	with pytest.raises(TypeError) as excinfo:
		util_check.ArbitraryLengthList('a')
	assert excinfo.value.message == 'Parameter `element_type` is of the wrong type'

def test_arbitrary_length_list_includes():	#pylint: disable=C0103
	"""	Test that the includes method of ArbitraryLengthList class behaves appropriately """
	ref_obj = util_check.ArbitraryLengthList(int)
	assert (ref_obj.includes([1, 2]), ref_obj.includes(set([1, 2])), ref_obj.includes((1, 2)), ref_obj.includes('a')) == (True, False, False, False)

def test_arbitrary_length_list_istype():	#pylint: disable=C0103
	"""	Test that the istype method of ArbitraryLengthList class behaves appropriately """
	ref_obj = util_check.ArbitraryLengthList(int)
	assert (ref_obj.istype([1, 2]), ref_obj.istype(set([1, 2])), ref_obj.istype((1, 2)), ref_obj.istype('a')) == (True, False, False, False)

###
# Test for ArbitraryLengthTuple class
###
def test_arbitrary_length_tuple_no_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLengthTuple class behaves appropriately when all parameters are correctly specified	"""
	obj_type = int
	obj = util_check.ArbitraryLengthTuple(obj_type)
	assert (obj.element_type == obj_type, obj.iter_type == tuple) == (True, True)

def test_arbitrary_length_tuple_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLengthTuple class behaves appropriately when inproper parameter type is passed """
	with pytest.raises(TypeError) as excinfo:
		util_check.ArbitraryLengthTuple('a')
	assert excinfo.value.message == 'Parameter `element_type` is of the wrong type'

def test_arbitrary_length_tuple_includes():	#pylint: disable=C0103
	"""	Test that the includes method of ArbitraryLengthTuple class behaves appropriately """
	ref_obj = util_check.ArbitraryLengthTuple(float)
	assert (ref_obj.includes((1.0, 2.0)), ref_obj.includes([1, 2]), ref_obj.includes(set([1, 2])), ref_obj.includes('a')) == (True, False, False, False)

def test_arbitrary_length_tuple_type():	#pylint: disable=C0103
	"""	Test that the istype method of ArbitraryLengthTuple class behaves appropriately """
	ref_obj = util_check.ArbitraryLengthTuple(float)
	assert (ref_obj.istype((1.0, 2.0)), ref_obj.istype([1, 2]), ref_obj.istype(set([1, 2])), ref_obj.istype('a')) == (True, False, False, False)

###
# Test for ArbitraryLengthSet class
###
def test_arbitrary_length_set_no_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLengthSet class behaves appropriately when all parameters are correctly specified """
	obj_type = int
	obj = util_check.ArbitraryLengthSet(obj_type)
	assert (obj.element_type == obj_type, obj.iter_type == set) == (True, True)

def test_arbitrary_length_set_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLengthSet class behaves appropriately when inproper parameter type is passed """
	with pytest.raises(TypeError) as excinfo:
		util_check.ArbitraryLengthSet('a')
	assert excinfo.value.message == 'Parameter `element_type` is of the wrong type'

def test_arbitrary_length_set_includes():	#pylint: disable=C0103
	""" Test that the includes method of ArbitraryLengthSet class behaves appropriately """
	ref_obj = util_check.ArbitraryLengthSet(float)
	assert (ref_obj.includes(set([1.0, 2.0])), ref_obj.includes([1, 2]), ref_obj.includes((1, 2)), ref_obj.includes('a')) == (True, False, False, False)

def test_arbitrary_length_set_istype():	#pylint: disable=C0103
	""" Test that the istype method of ArbitraryLengthSet class behaves appropriately """
	ref_obj = util_check.ArbitraryLengthSet(float)
	assert (ref_obj.istype(set([1.0, 2.0])), ref_obj.istype([1, 2]), ref_obj.istype((1, 2)), ref_obj.istype('a')) == (True, False, False, False)

###
# Test for OneOf class
###
def test_one_of_case_insensitive_exception():	#pylint: disable=C0103
	""" Tests that OneOf class behaves properly when an improper case_insensitive type is given """
	with pytest.raises(TypeError) as excinfo:
		util_check.OneOf(['a', 'b', 'c'], case_sensitive=3)
	assert excinfo.value.message == 'Parameter `case_sensitive` is of the wrong type'

def test_one_of_case_insensitive_none_if_no_strings_in_choices():	#pylint: disable=C0103
	""" Tests that OneOf class behaves properly when no string options given """
	assert (util_check.OneOf([1, 2, 3], case_sensitive=True).case_sensitive == None, util_check.OneOf([1, 2, 3], case_sensitive=False).case_sensitive == None) == (True, True)

def test_one_of_infinite_iterable_exception():	#pylint: disable=C0103
	""" Tests that OneOf class behaves properly when an improper iterable is given """
	with pytest.raises(TypeError) as excinfo:
		util_check.OneOf(itertools.count(start=0, step=1))
	assert excinfo.value.message == 'Parameter `choices` is of the wrong type'

def test_one_of_proper_no_errors():	#pylint: disable=C0103
	""" Tests that OneOf class behaves properly when all parameters are correctly specified """
	test_choices = ['a', 2, 3.0, 'a', util_check.Real()]
	obj = util_check.OneOf(test_choices, case_sensitive=True)
	assert (obj.types == [type(element) for element in test_choices], obj.choices == test_choices, obj.case_sensitive == True) == (True, True, True)

def test_one_of_proper_contains_behavior():	#pylint: disable=C0103
	""" Tests that OneOf class behaves properly extracting type information """
	obj1 = util_check.OneOf(['a', 'b', 3.0, 2], case_sensitive=True)
	obj2 = util_check.OneOf(['c', 'D', util_check.IncreasingRealNumpyVector()], case_sensitive=False)
	assert ('a' in obj1, 'b' in obj1, 3.0 in obj1, 2 in obj1, [1, 2] in obj1, 3.1 in obj1, 'A' in obj1, 'C' in obj2, 'd' in obj2, 'e' in obj2, 'E' in obj2, numpy.array([1, 2, 3]) in obj2, numpy.array([1.0, 0.0, -1.0]) in obj2) == \
		(True, True, True, True, False, False, False, True, True, False, False, True, False)

def test_one_of_includes():	#pylint: disable=C0103
	"""Test that the includes method of OneOf class behaves appropriately """
	ref_obj1 = util_check.OneOf(['a', 'b', 3.0, 2], case_sensitive=True)
	ref_obj2 = util_check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=False)
	assert (ref_obj1.includes('a'), ref_obj1.includes('b'), ref_obj1.includes(3.0), ref_obj1.includes(2), ref_obj1.includes(util_check.Number()), ref_obj1.includes('c'), ref_obj1.includes('A'),
		 ref_obj2.includes('none'), ref_obj2.includes('autos')) == (True, True, True, True, False, False, False, True, False)

def test_one_of_istype():	#pylint: disable=C0103
	"""Test that the istype method of OneOf class behaves appropriately """
	ref_obj1 = util_check.OneOf(['a', 'b', 3.0, 2], case_sensitive=True)
	ref_obj2 = util_check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=False)
	assert (ref_obj1.istype('a'), ref_obj1.istype('b'), ref_obj1.istype(3.0), ref_obj1.istype(2), ref_obj1.istype(util_check.Number()), ref_obj1.istype('c'), ref_obj1.istype('A'),
		 ref_obj2.istype('none'), ref_obj2.istype('autos'), ref_obj2.istype(set([1, 2]))) == (True, True, True, True, False, True, True, True, True, False)

###
# Test for NumberRange class
###
def test_number_range_minimum_not_a_number():	#pylint: disable=C0103
	""" Tests that NumberRange class behaves properly when minimum is not a number """
	with pytest.raises(TypeError) as excinfo:
		util_check.NumberRange(minimum=False, maximum=None)
	assert excinfo.value.message == 'Parameter `minimum` is of the wrong type'

def test_number_range_maximum_not_a_number():	#pylint: disable=C0103
	""" Tests that NumberRange class behaves properly when maximum is not a number """
	with pytest.raises(TypeError) as excinfo:
		util_check.NumberRange(minimum=None, maximum=True)
	assert excinfo.value.message == 'Parameter `maximum` is of the wrong type'

def test_number_range_minimum_and_maximum_not_specified():	#pylint: disable=C0103
	""" Tests that NumberRange class behaves properly when neither minimum nor maximum are specified """
	with pytest.raises(TypeError) as excinfo:
		util_check.NumberRange(minimum=None, maximum=None)
	assert excinfo.value.message == 'Either parameter `minimum` or parameter `maximum` needs to be specified'

def test_number_range_minimum_and_maximum_are_of_different_type():	#pylint: disable=C0103
	""" Tests that NumberRange class behaves properly when minimum is either integer or float and maximum is either float or integer """
	with pytest.raises(TypeError) as excinfo:
		util_check.NumberRange(minimum=1.5, maximum=3)
	assert excinfo.value.message == 'Parameters `minimum` and `maximum` have different types'

def test_number_range_minimum_greater_than_maximum():	#pylint: disable=C0103
	""" Tests that NumberRange class behaves properly when minimum is greater than maximum """
	with pytest.raises(ValueError) as excinfo:
		util_check.NumberRange(minimum=1.5, maximum=0.0)
	assert excinfo.value.message == 'Parameter `minimum` greater than parameter `maximum`'

def test_number_range_no_errors():	#pylint: disable=C0103
	""" Tests that NumberRange class behaves properly when all parameters are correctly specified """
	obj = util_check.NumberRange(minimum=10, maximum=20)
	assert (obj.minimum == 10, obj.maximum == 20) == (True, True)

def test_number_range_includes():	#pylint: disable=C0103
	""" Test that the includes method of NumberRange class behaves appropriately """
	ref_obj1 = util_check.NumberRange(10, 15)
	ref_obj2 = util_check.NumberRange(100.0, 200.0)
	assert (ref_obj1.includes(5), ref_obj1.includes(10), ref_obj1.includes(13), ref_obj1.includes(15), ref_obj1.includes(20), ref_obj1.includes(13.0),
		 ref_obj2.includes(75.1), ref_obj2.includes(100.0), ref_obj2.includes(150.0), ref_obj2.includes(200.0), ref_obj2.includes(200.1), ref_obj2.includes(200)) == \
		 (False, True, True, True, False, False, False, True, True, True, False, False)

def test_number_range_istype():	#pylint: disable=C0103
	""" Test that the istype method of NumberRange class behaves appropriately """
	ref_obj1 = util_check.NumberRange(10, 15)
	ref_obj2 = util_check.NumberRange(100.0, 200.0)
	assert (ref_obj1.istype(5), ref_obj1.istype(10), ref_obj1.istype(13), ref_obj1.istype(15), ref_obj1.istype(20), ref_obj1.istype(13.0),
		 ref_obj2.istype(75.1), ref_obj2.istype(100.0), ref_obj2.istype(150.0), ref_obj2.istype(200.0), ref_obj2.istype(200.1), ref_obj2.istype(200)) == \
		 (True, True, True, True, True, False, True, True, True, True, True, False)

###
# Test RealNumpyVector class
###
def test_real_numpy_vector_no_exception():	#pylint: disable=C0103
	""" Test that RealNumpyVector class behaves appropriately when all parameters are correctly specified """
	util_check.RealNumpyVector()

def test_real_numpy_vector_includes():	#pylint: disable=C0103
	""" Test that the includes method of RealNumpyVector class behaves appropriately """
	ref_obj = util_check.RealNumpyVector()
	assert (ref_obj.includes('a'), ref_obj.includes([1, 2, 3]), ref_obj.includes(numpy.array([])), ref_obj.includes(numpy.array([[1, 2, 3], [4, 5, 6]])), ref_obj.includes(numpy.array(['a', 'b'])),
		 ref_obj.includes(numpy.array([1, 2, 3])), ref_obj.includes(numpy.array([10.0, 8.0, 2.0]))) == (False, False, False, False, False, True, True)

def test_real_numpy_vector_istype():	#pylint: disable=C0103
	""" Test that the istype method of RealNumpyVector class behaves appropriately """
	ref_obj = util_check.RealNumpyVector()
	assert (ref_obj.istype('a'), ref_obj.istype([1, 2, 3]), ref_obj.istype(numpy.array([])), ref_obj.istype(numpy.array([[1, 2, 3], [4, 5, 6]])), ref_obj.istype(numpy.array(['a', 'b'])),
		 ref_obj.istype(numpy.array([1, 2, 3])), ref_obj.istype(numpy.array([10.0, 8.0, 2.0]))) == (False, False, False, False, False, True, True)

###
# Test IncreasingRealNumpyVector class
###
def test_increasing_real_numpy_vector_no_exception():	#pylint: disable=C0103
	""" Test that IncreasingRealNumpyVector class behaves appropriately when all parameters are correctly specified """
	util_check.IncreasingRealNumpyVector()

def test_increasing_real_numpy_vector_includes():	#pylint: disable=C0103
	""" Test that the includes method of IncreasingRealNumpyVector class behaves appropriately """
	ref_obj = util_check.IncreasingRealNumpyVector()
	assert (ref_obj.includes('a'), ref_obj.includes([1, 2, 3]), ref_obj.includes(numpy.array([])), ref_obj.includes(numpy.array([[1, 2, 3], [4, 5, 6]])), ref_obj.includes(numpy.array(['a', 'b'])),
		 ref_obj.includes(numpy.array([1, 0, -3])), ref_obj.includes(numpy.array([10.0, 8.0, 2.0])), ref_obj.includes(numpy.array([1, 2, 3])), ref_obj.includes(numpy.array([10.0, 12.1, 12.5]))) == \
		(False, False, False, False, False, False, False, True, True)

def test_increasing_real_numpy_vector_istype():	#pylint: disable=C0103
	""" Test that the istype method of IncreasingRealNumpyVector class behaves appropriately """
	ref_obj = util_check.IncreasingRealNumpyVector()
	assert (ref_obj.istype('a'), ref_obj.istype([1, 2, 3]), ref_obj.istype(numpy.array([])), ref_obj.istype(numpy.array([[1, 2, 3], [4, 5, 6]])), ref_obj.istype(numpy.array(['a', 'b'])),
		 ref_obj.istype(numpy.array([1, 0, -3])), ref_obj.istype(numpy.array([10.0, 8.0, 2.0])), ref_obj.istype(numpy.array([1, 2, 3])), ref_obj.istype(numpy.array([10.0, 12.1, 12.5]))) == \
		(False, False, False, False, False, False, False, True, True)

###
# Test PolymorphicType class
###
def test_type_match_polymorphic_type_wrong_type():	#pylint: disable=C0103
	""" Test if function behaves proprely when wrong type parameter is given """
	with pytest.raises(TypeError) as excinfo:
		util_check.PolymorphicType('a')
	assert excinfo.value.message == 'Parameter `types` is of the wrong type'

def test_type_match_polymorphic_type_subtype_wrong_type():	#pylint: disable=C0103
	""" Test if function behaves proprely when wrong sub-type parameter is given """
	with pytest.raises(TypeError) as excinfo:
		util_check.PolymorphicType([str, int, 'a'])
	assert excinfo.value.message == 'Parameter `types` element is of the wrong type'

def test_type_match_polymorphic_type_no_errors():	#pylint: disable=C0103
	""" Test if function behaves proprely when all parameters are correctly specified """
	test_instances = [str, int, None, util_check.ArbitraryLengthList, util_check.ArbitraryLengthTuple, util_check.ArbitraryLengthSet, util_check.IncreasingRealNumpyVector, util_check.RealNumpyVector, util_check.OneOf,
		  util_check.NumberRange, util_check.Number, util_check.Real]
	obj = util_check.PolymorphicType(test_instances)
	test_types = test_instances[:]
	test_types[2] = type(None)
	assert (obj.instances == test_instances, obj.types == test_types) == (True, True)

def test_polymorphic_type_includes():	#pylint: disable=C0103
	""" Test that the includes method of PolymorphicType class behaves appropriately """
	test_instances = [int, None, util_check.ArbitraryLengthList(int), util_check.ArbitraryLengthTuple(float), util_check.ArbitraryLengthSet(str), util_check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=True),
		  util_check.NumberRange(1, 3), util_check.Number(), util_check.Real(), util_check.RealNumpyVector()]
	ref_obj1 = util_check.PolymorphicType(test_instances)
	ref_obj2 = util_check.PolymorphicType([float, util_check.IncreasingRealNumpyVector()])
	assert (ref_obj1.includes(5), ref_obj1.includes(None), ref_obj1.includes([1, 2, 3]), ref_obj1.includes((2.0, 3.0)), ref_obj1.includes(set(['a', 'b', 'c'])), ref_obj1.includes('MANUAL'), ref_obj1.includes(2),
		 ref_obj1.includes(100.0), ref_obj1.includes(10+20j), ref_obj1.includes(numpy.array([10, 0.0, 30])), ref_obj1.includes('hello world'), ref_obj1.includes([1.0, 2.0, 3.0]), ref_obj1.includes('auto'),
		 ref_obj1.includes(numpy.array([])), ref_obj1.includes(numpy.array(['a', 'b', 'c'])), ref_obj2.includes(1), ref_obj2.includes(set([1, 2])), ref_obj2.includes(numpy.array([1, 0, -1])),
		 ref_obj2.includes(numpy.array([10.0, 20.0, 30.0])), ref_obj2.includes(5.0)) == (True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False, True, True)

def test_polymorphic_type_istype():	#pylint: disable=C0103
	""" Test that the istype method of PolymorphicType class behaves appropriately """
	test_instances = [int, None, util_check.ArbitraryLengthList(int), util_check.ArbitraryLengthTuple(float), util_check.ArbitraryLengthSet(str), util_check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=True),
		  util_check.NumberRange(1, 3), util_check.Number(), util_check.Real(), util_check.RealNumpyVector()]
	ref_obj1 = util_check.PolymorphicType(test_instances)
	ref_obj2 = util_check.PolymorphicType([float, util_check.IncreasingRealNumpyVector()])
	assert (ref_obj1.istype(5), ref_obj1.istype(None), ref_obj1.istype([1, 2, 3]), ref_obj1.istype((2.0, 3.0)), ref_obj1.istype(set(['a', 'b', 'c'])), ref_obj1.istype('MANUAL'), ref_obj1.istype(2),
		 ref_obj1.istype(100.0), ref_obj1.istype(10+20j), ref_obj1.istype(numpy.array([10, 0.0, 30])), ref_obj1.istype('hello world'), ref_obj1.istype([1.0, 2.0, 3.0]), ref_obj1.istype('auto'),
		 ref_obj1.istype(numpy.array([])), ref_obj1.istype(numpy.array(['a', 'b', 'c'])), ref_obj2.istype(1), ref_obj2.istype(set([1, 2])), ref_obj2.istype(numpy.array([1, 0, -1])),
		 ref_obj2.istype(numpy.array([10.0, 20.0, 30.0])), ref_obj2.istype(5.0)) == (True, True, True, True, True, True, True, True, True, True, True, False, True, False, False, False, False, False, True, True)

##
# Tests for get_function_args()
###
def test_get_function_args_all_positional_parameters():	#pylint: disable=C0103
	""" Test that function behaves properly when all parameters are positional parameters """
	def func(ppar1, ppar2, ppar3):	#pylint: disable=C0111,W0613
		pass
	assert util_check.get_function_args(func) == ('ppar1', 'ppar2', 'ppar3')

def test_get_function_args_all_keyword_parameters():	#pylint: disable=C0103,W0613
	""" Test that function behaves properly when all parameters are keywords parameters """
	def func(kpar1=1, kpar2=2, kpar3=3):	#pylint: disable=C0111,R0913,W0613
		pass
	assert util_check.get_function_args(func) == ('kpar1', 'kpar2', 'kpar3')

def test_get_function_args_positional_and_keyword_parameters():	#pylint: disable=C0103
	""" Test that function behaves properly when parameters are a mix of positional and keywords parameters """
	def func(ppar1, ppar2, ppar3, kpar1=1, kpar2=2, kpar3=3):	#pylint: disable=C0103,C0111,R0913,W0613
		pass
	assert util_check.get_function_args(func) == ('ppar1', 'ppar2', 'ppar3', 'kpar1', 'kpar2', 'kpar3')

def test_get_function_args_no_parameters():	#pylint: disable=C0103
	""" Test that function behaves properly when there are no parameters passed """
	def func():	#pylint: disable=C0111,R0913,W0613
		pass
	assert util_check.get_function_args(func) == ()

###
# Tests for create_parameter_dictionary()
###
def ret_func(par):
	""" Returns the passed parameter """
	return par

def decfunc(func):
	"""" Decorator function to test create_parameter_dictionary function """
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		"""
		Wrapper function that creates the parameter dictionary and returns a ret_func, which in turn just returns the parameter passed. This is for testing only, obviously
		in an actual environment the dedcorator would return the original (called) function with the passed parameters
		"""
		return ret_func(util_check.create_parameter_dictionary(func, *args, **kwargs))
	return wrapper

def test_create_parameter_dictionary_all_positional_parameters():	#pylint: disable=C0103
	""" Test that function behaves properly when all parameters are positional parameters """
	@decfunc
	def orig_func_all_positional_parameters(ppar1, ppar2, ppar3):	#pylint: disable=C0103,C0111,W0613
		pass
	assert orig_func_all_positional_parameters(1, 2, 3) == {'ppar1':1, 'ppar2':2, 'ppar3':3}

def test_create_parameter_dictionary_all_keyword_parameters():	#pylint: disable=C0103
	""" Test that function behaves properly when all parameters are keyword parameters """
	@decfunc
	def orig_func_all_keyword_parameters(kpar1, kpar2, kpar3):	#pylint: disable=C0103,C0111,W0613
		pass
	assert orig_func_all_keyword_parameters(kpar3=3, kpar2=2, kpar1=1) == {'kpar1':1, 'kpar2':2, 'kpar3':3}


def test_create_parameter_dictionary_positional_and_keyword_parameters():	#pylint: disable=C0103
	""" Test that function behaves properly when parameters are a mix of positional and keywords parameters """
	@decfunc
	def orig_func_positional_and_keyword_parameters(ppar1, ppar2, ppar3, kpar1=1, kpar2=2, kpar3=3):	#pylint: disable=C0103,C0111,R0913,W0613
		pass
	assert orig_func_positional_and_keyword_parameters(10, 20, 30, kpar2=1.5, kpar3='x', kpar1=[1, 2]) == {'ppar1':10, 'ppar2':20, 'ppar3':30, 'kpar1':[1, 2], 'kpar2':1.5, 'kpar3':'x'}

def test_create_parameter_dictionary_no_parameters():	#pylint: disable=C0103
	""" Test that function behaves properly when there are no parameters passed """
	@decfunc
	def orig_func_no_parameters():	#pylint: disable=C0103,C0111,R0913,W0613
		pass
	assert orig_func_no_parameters() == {}

def test_create_parameter_dictionary_more_positional_parameters_passed_than_defined():	#pylint: disable=C0103
	""" Test that function behaves properly when there are more parameters passed by position than in the function definition """
	@decfunc
	def orig_func(ppar1):	#pylint: disable=C0103,C0111,R0913,W0613
		pass
	assert orig_func(1, 2, 3) == {}	#pylint: disable=E1121

def test_create_parameter_dictionary_more_keyword_parameters_passed_than_defined():	#pylint: disable=C0103
	""" Test that function behaves properly when there are more parameters passed by keyword than in the function definition """
	@decfunc
	def orig_func(kpar1=0, kpar2=2):	#pylint: disable=C0103,C0111,R0913,W0613
		pass
	assert orig_func(kpar1=1, kpar2=2, kpar3=3) == {}	#pylint: disable=E1123

def test_create_parameter_dictionary_parameter_passed_by_position_and_keyword():	#pylint: disable=C0103
	""" Test that function behaves properly when there are parameters passed both by position and keyword """
	@decfunc
	def orig_func(ppar1, ppar2, kpar1=1, kpar2=2):	#pylint: disable=C0103,C0111,R0913,W0613
		pass
	assert orig_func(1, 2, ppar1=5) == {}	#pylint: disable=E1124

###
# Tests for type_match()
###
def test_type_match_str():
	""" Test if function behaves proprely for string type """
	assert (util_check.type_match('hello', str), util_check.type_match(135, str)) == (True, False)

def test_type_match_float():
	""" Test if function behaves proprely for float type """
	assert (util_check.type_match(1.5, float), util_check.type_match(135, float)) == (True, False)

def test_type_match_int():
	""" Test if function behaves proprely for integer type """
	assert (util_check.type_match(8, int), util_check.type_match(135.0, int)) == (True, False)

def test_type_match_number():
	""" Test if function behaves proprely for Number pseudo-type (integer, real or complex) """
	assert (util_check.type_match(1, util_check.Number()), util_check.type_match(135.0, util_check.Number()), util_check.type_match(1+1j, util_check.Number()), util_check.type_match('hello', util_check.Number())) == \
		(True, True, True, False)

def test_type_match_real():
	""" Test if function behaves proprely for Real pseudo-type (integer or real) """
	assert (util_check.type_match(1, util_check.Real()), util_check.type_match(135.0, util_check.Real()), util_check.type_match(1+1j, util_check.Real())) == (True, True, False)

def test_type_match_boolean():
	""" Test if function behaves proprely for boolean type """
	assert (util_check.type_match(True, bool), util_check.type_match(12.5, bool)) == (True, False)

def test_type_match_decimal():
	""" Test if function behaves proprely for Decimal type """
	assert (util_check.type_match(decimal.Decimal(1.25), decimal.Decimal), util_check.type_match(12.5, decimal.Decimal)) == (True, False)

def test_type_match_fraction():
	""" Test if function behaves proprely for Fraction type """
	assert (util_check.type_match(fractions.Fraction(4, 6), fractions.Fraction), util_check.type_match(12.5, fractions.Fraction)) == (True, False)

def test_type_match_arbitrary_length_list():	#pylint: disable=C0103
	""" Test if function behaves proprely for ArbitraryLengthList pseudo-type """
	assert (util_check.type_match([1, 2, 3], util_check.ArbitraryLengthList(int)), util_check.type_match('hello', util_check.ArbitraryLengthList(int))) == (True, False)

def test_type_match_arbitrary_length_tuple():	#pylint: disable=C0103
	""" Test if function behaves proprely for ArbitraryLengthTuple pseudo-type """
	assert (util_check.type_match((1, 2, 3), util_check.ArbitraryLengthTuple(int)), util_check.type_match((1, 2, 'a'), util_check.ArbitraryLengthTuple(int))) == (True, False)

def test_type_match_arbitrary_length_set():	#pylint: disable=C0103
	""" Test if function behaves proprely for ArbitraryLengthSet pseudo-type """
	assert (util_check.type_match(set([1, 2, 3]), util_check.ArbitraryLengthSet(int)), util_check.type_match(set([1, 2, 'a']), util_check.ArbitraryLengthSet(int))) == (True, False)

def test_type_match_fixed_length_list():	#pylint: disable=C0103
	""" Test if function behaves proprely for fixed-length list type """
	assert (util_check.type_match([1, 'a', 3.0], [int, str, float]), util_check.type_match([1, 'a', 3.0, 4.0], [int, str, float]), util_check.type_match([1, 'a', 3.0], [int, str, float, int]),
		 util_check.type_match([1, 2, 3.0], [int, str, float])) == (True, False, False, False)

def test_type_match_fixed_length_tuple():	#pylint: disable=C0103
	""" Test if function behaves proprely for fixed-length tuple type """
	assert (util_check.type_match((1, 'a', 3.0), (int, str, float)), util_check.type_match((1, 'a', 3.0, 4.0), (int, str, float)), util_check.type_match((1, 'a', 3.0), (int, str, float, int)),
		 util_check.type_match((1, 2, 3.0), (int, str, float))) == (True, False, False, False)

def test_type_match_fixed_length_set():	#pylint: disable=C0103
	""" Test if function behaves proprely for fixed-length set type """
	with pytest.raises(RuntimeError) as excinfo:
		util_check.type_match(set([1, 'a', 3.0]), set([int, str, float]))
	assert excinfo.value.message == 'Set is an un-ordered iterable, thus it cannot be type-checked against an ordered reference'

def test_type_match_one_of():	#pylint: disable=C0103
	""" Test if function behaves proprely for OneOf pseudo-type """
	assert (util_check.type_match('HELLO', util_check.OneOf(['HELLO', 45, 'WORLD'])), util_check.type_match(45, util_check.OneOf(['HELLO', 45, 'WORLD'])), util_check.type_match(1.0, util_check.OneOf(['HELLO', 45, 'WORLD']))) == \
		 (True, True, False)

def test_type_match_number_range():	#pylint: disable=C0103
	""" Test if function behaves proprely for NumberRange pseudo-type """
	assert (util_check.type_match(12, util_check.NumberRange(minimum=2, maximum=5)), util_check.type_match('a', util_check.NumberRange(minimum=2, maximum=5))) == (True, False)

def test_type_match_dict():
	""" Test if function behaves proprely for dictionary type """
	assert (util_check.type_match({'a':'hello', 'b':12.5, 'c':[1]}, {'a':str, 'b':float, 'c':[int]}),	# 'Regular' match
		 util_check.type_match({'a':'hello', 'c':[1]}, {'a':str, 'b':float, 'c':[int]}),	# One key-value pair missing in test object, useful where parameter is omitted to get default
		 util_check.type_match({'x':'hello', 'y':{'n':[1.5, 2.3]}, 'z':[1]}, {'x':str, 'y':{'n':util_check.ArbitraryLengthList(float), 'm':str}, 'z':[int]}), # Nested
		 util_check.type_match({'a':'hello', 'b':35, 'c':[1]}, {'a':str, 'b':float, 'c':[int]}),	# Value of one key in test object does not match
		 util_check.type_match({'a':'hello', 'd':12.5, 'c':[1]}, {'a':str, 'b':float, 'c':[int]})) == (True, True, True, False, False)	# One key in test object does not appear in reference object

def test_type_match_polymorphic_type():	#pylint: disable=C0103
	""" Test if function behaves proprely for PolymorphicType pseudo-type """
	assert (util_check.type_match('HELLO', util_check.PolymorphicType([str, int])), util_check.type_match(45, util_check.PolymorphicType([str, int])), util_check.type_match(1.5, util_check.PolymorphicType([str, int]))) \
		== (True, True, False)

def test_type_match_real_numpy_vector():	#pylint: disable=C0103
	""" Test if function behaves proprely for RealNumpyVector pseudo-type """
	assert (util_check.type_match(12, util_check.RealNumpyVector()), util_check.type_match(numpy.array([1, 2, 0]), util_check.RealNumpyVector()),
		 util_check.type_match(numpy.array([[1, 2, 0], [1, 1, 2]]), util_check.RealNumpyVector())) == (False, True, False)

def test_type_match_increasing_real_numpy_vector():	#pylint: disable=C0103
	""" Test if function behaves proprely for IncreasingRealNumpyVector pseudo-type """
	assert (util_check.type_match(12, util_check.IncreasingRealNumpyVector()), util_check.type_match(numpy.array([1, 2, 3]), util_check.IncreasingRealNumpyVector()),
		 util_check.type_match(numpy.array([True, False, True]), util_check.IncreasingRealNumpyVector()),
		 util_check.type_match(numpy.array([[1, 2, 3], [4, 5, 6]]), util_check.IncreasingRealNumpyVector())) == (False, True, False, False)

###
# Tests for check_type()
###
def test_check_type_simple_exception():	#pylint: disable=C0103
	""" Test that function behaves properly when a sigle (wrong) type is given (string, number, etc.) """
	@util_check.check_type('ppar1', int)
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(TypeError) as excinfo:
		func_check_type('Hello world')
	assert excinfo.value.message == 'Parameter ppar1 is of the wrong type'

def test_check_type_simple_no_exception():	#pylint: disable=C0103
	""" Test that function behaves properly when a sigle (right) type is given (string, number, etc.) """
	@util_check.check_type(param_name='ppar1', param_type=util_check.Number())
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	assert func_check_type(5.0) == 5.0

def test_check_type_parameter_not_specified():	#pylint: disable=C0103
	""" Test that function behaves properly when the parameter to be checked is not specified in the function call """
	@util_check.check_type(param_name='ppar2', param_type=util_check.Number())
	def func_check_type(ppar1, ppar2=None, ppar3=5):	#pylint: disable=C0111
		return ppar1, ppar2, ppar3
	assert func_check_type(3, ppar3=12) == (3, None, 12)

def test_check_type_parameter_specified_by_position_and_keyword():	#pylint: disable=C0103
	""" Test that function behaves properly when a parameter is specified both by position and keyword """
	@util_check.check_type(param_name='ppar2', param_type=util_check.Number())
	def func_check_type(ppar1, ppar2=None, ppar3=5):	#pylint: disable=C0111
		print ppar1, ppar2, ppar3
	with pytest.raises(TypeError) as excinfo:
		func_check_type(3, ppar3=12, ppar1=12)	#pylint: disable=E1124
	assert excinfo.value.message == "func_check_type() got multiple values for keyword argument 'ppar1'"

def test_check_type_parameter_repeated_keyword_arguments():	#pylint: disable=C0103
	""" Test that function behaves properly when a parameter is specified multiple times by keyword """
	@util_check.check_type(param_name='ppar2', param_type=util_check.Number())
	def func_check_type(ppar1, ppar2=None, ppar3=5):	#pylint: disable=C0111
		print ppar1, ppar2, ppar3
	with pytest.raises(TypeError) as excinfo:
		func_check_type(3, ppar3=12, **{'ppar3':12})	#pylint: disable=W0142
	assert excinfo.value.message == "func_check_type() got multiple values for keyword argument 'ppar3'"

###
# Tests for check_parameter()
###
def test_check_parameter_wrong_type():	#pylint: disable=C0103
	""" Test that function behaves properly when a sigle (wrong) type is given (string, number, etc.) """
	@util_check.check_parameter('ppar1', int)
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(TypeError) as excinfo:
		func_check_type('Hello world')
	assert excinfo.value.message == 'Parameter ppar1 is of the wrong type'

def test_check_parameter_one_of_error_case_insensitive():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is outside fixed number of string choices list with case sensitivity
	"""
	@util_check.check_parameter('ppar1', util_check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=False))
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(ValueError) as excinfo:
		func_check_type('Hello world')
	assert excinfo.value.message == "Parameter ppar1 is not one of ['NONE', 'MANUAL', 'AUTO'] (case insensitive)"

def test_check_parameter_one_of_error_case_sensitive():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is outside fixed number of string choices list with case insensitivity
	"""
	@util_check.check_parameter('ppar1', util_check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=True))
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(ValueError) as excinfo:
		func_check_type('none')
	assert excinfo.value.message == "Parameter ppar1 is not one of ['NONE', 'MANUAL', 'AUTO'] (case sensitive)"

def test_check_parameter_one_of_error_no_case_sensitivity():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is outside fixed number of choices list
	"""
	@util_check.check_parameter('ppar1', util_check.OneOf(range(3), case_sensitive=True))
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(ValueError) as excinfo:
		func_check_type(10)
	assert excinfo.value.message == 'Parameter ppar1 is not one of [0, 1, 2]'

def test_check_parameter_one_of_no_error():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is one of a fixed number of choices list
	"""
	@util_check.check_parameter('ppar1', util_check.OneOf(range(3), case_sensitive=True))
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	assert func_check_type(2) == 2

def test_check_parameter_range_no_maximum_out_of_range():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is out of range when no maximum is defined
	"""
	@util_check.check_parameter('ppar1', util_check.NumberRange(minimum=10))
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(ValueError) as excinfo:
		func_check_type(1)
	assert excinfo.value.message == 'Parameter ppar1 is not in the range [10, +inf]'

def test_check_parameter_range_no_maximum_in_range():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is in range when no maximum is defined
	"""
	@util_check.check_parameter('ppar1', util_check.NumberRange(minimum=10))
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	assert func_check_type(20) == 20

def test_check_parameter_range_no_minimum_out_of_range():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is out of range when no minimum is defined
	"""
	@util_check.check_parameter('ppar1', util_check.NumberRange(maximum=10))
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(ValueError) as excinfo:
		func_check_type(20)
	assert excinfo.value.message == 'Parameter ppar1 is not in the range [-inf, 10]'

def test_check_parameter_range_no_minimum_in_range():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is in range when no minimum is defined
	"""
	@util_check.check_parameter('ppar1', util_check.NumberRange(maximum=10))
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	assert func_check_type(5) == 5

def test_check_parameter_range_minimum_and_maximum_specified_out_of_range():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is out of range when no minimum is defined
	"""
	@util_check.check_parameter('ppar1', util_check.NumberRange(minimum=5.0, maximum=10.0))
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(ValueError) as excinfo:
		func_check_type(3.1)
	assert excinfo.value.message == 'Parameter ppar1 is not in the range [5.0, 10.0]'

def test_check_parameter_range_minimum_and_maximum_specified_in_range():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is in range when no minimum is defined
	"""
	@util_check.check_parameter('ppar1', util_check.NumberRange(minimum=100, maximum=200))
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	assert func_check_type(150) == 150

def test_check_parameter_polymorphic_type_error():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is not in the polymorphic types allowed
	"""
	@util_check.check_parameter('ppar1', util_check.PolymorphicType([None, float]))
	def func_check_type1(ppar1):	#pylint: disable=C0111
		print ppar1
	@util_check.check_parameter('ppar1', util_check.PolymorphicType([None, util_check.NumberRange(minimum=5, maximum=10), util_check.OneOf(['HELLO', 'WORLD'])]))
	def func_check_type2(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(TypeError) as excinfo1:	# Type not in the definition
		func_check_type1('a')
	eobj1 = excinfo1.value.message == 'Parameter ppar1 is of the wrong type'
	with pytest.raises(ValueError) as excinfo2:	# Type not in the definition
		func_check_type2(2)
	eobj2 = excinfo2.value.message == "Parameter ppar1 is not in the range [5, 10]\nParameter ppar1 is not one of ['HELLO', 'WORLD'] (case insensitive)"
	assert (eobj1, eobj2) == (True, True)

def test_check_parameter_polymorphic_type_no_error():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is in the polymorphic types allowed
	"""
	@util_check.check_parameter('ppar1', util_check.PolymorphicType([None, int, util_check.NumberRange(minimum=5.0, maximum=10.0), util_check.OneOf(['HELLO', 'WORLD'])]))
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	assert (func_check_type(None), func_check_type(3), func_check_type(7.0), func_check_type('WORLD')) == (None, 3, 7.0, 'WORLD')

def test_check_parameter_numpy_vector_wrong_type():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is not a Numpy vector
	"""
	@util_check.check_parameter('ppar1', util_check.RealNumpyVector())
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(TypeError) as excinfo:
		func_check_type(numpy.array([False]))
	assert excinfo.value.message == 'Parameter ppar1 is of the wrong type'

def test_check_parameter_numpy_vector_no_error():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is proper Numpy vector
	"""
	@util_check.check_parameter('ppar1', util_check.RealNumpyVector())
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	func_check_type(numpy.array([1.0, 2.0, 1.0-1e-10]))

def test_check_parameter_increasing_numpy_vector_wrong_type():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is not a Numpy vector
	"""
	@util_check.check_parameter('ppar1', util_check.IncreasingRealNumpyVector())
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(TypeError) as excinfo:
		func_check_type(numpy.array([False]))
	eobj1 = excinfo.value.message == 'Parameter ppar1 is of the wrong type'
	with pytest.raises(TypeError) as excinfo:
		func_check_type(numpy.array([1.0, 2.0, 1.0-1e-10]))
	eobj2 = excinfo.value.message == 'Parameter ppar1 is of the wrong type'
	assert (eobj1, eobj2) == (True, True)

def test_check_parameter_incresing_numpy_vector_no_error():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is properly incresing Numpy vector
	"""
	@util_check.check_parameter('ppar1', util_check.IncreasingRealNumpyVector())
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	func_check_type(numpy.array([1, 2, 3]))
