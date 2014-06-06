# check_test.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Decorators for API parameter checking unit tests
"""

import numpy
import pytest
import decimal
import fractions
import functools
import itertools

import putil.check


###
# Test for Number class
###
def test_number_no_exception():
	"""	Test that Number class behaves appropriately when all parameters are correctly specified """
	putil.check.Number()

def test_number_includes():
	"""	Test that the includes method of Number class behaves appropriately	"""
	ref_obj = putil.check.Number()
	assert (ref_obj.includes(1), ref_obj.includes(2.0), ref_obj.includes(1+2j), ref_obj.includes('a'), ref_obj.includes([1, 2, 3])) == (True, True, True, False, False)

def test_number_istype():
	"""	Test that the istype method of Number class behaves appropriately """
	ref_obj = putil.check.Number()
	assert (ref_obj.istype(1), ref_obj.istype(2.0), ref_obj.istype(1+2j), ref_obj.istype('a'), ref_obj.istype([1, 2, 3])) == (True, True, True, False, False)

###
# Test for Real class
###
def test_real_no_exception():
	"""	Test that Real class behaves appropriately when all parameters are correctly specified	"""
	putil.check.Real()

def test_real_includes():
	"""	Test that the includes method of Real class behaves appropriately """
	ref_obj = putil.check.Real()
	assert (ref_obj.includes(1), ref_obj.includes(2.0), ref_obj.includes(1+2j), ref_obj.includes('a'), ref_obj.includes([1, 2, 3])) == (True, True, False, False, False)

def test_real_istype():
	"""	Test that the istype method of Real class behaves appropriately """
	ref_obj = putil.check.Real()
	assert (ref_obj.istype(1), ref_obj.istype(2.0), ref_obj.istype(1+2j), ref_obj.istype('a'), ref_obj.istype([1, 2, 3])) == (True, True, False, False, False)

###
# Test for ArbitraryLength class
###
def test_arbitrary_length_no_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLength class behaves appropriately when all parameters are correctly specified """
	obj_type = str
	obj = putil.check.ArbitraryLength(obj_type)
	assert obj.element_type == obj_type

def test_arbitrary_length_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLength class behaves appropriately when inproper parameter type is passed """
	with pytest.raises(TypeError) as excinfo:
		putil.check.ArbitraryLength('a')
	assert excinfo.value.message == 'Parameter `element_type` is of the wrong type'

def test_arbitrary_length_includes():
	"""	Test that the includes method of ArbitraryLength class behaves appropriately """
	ref_obj = putil.check.ArbitraryLength(int)
	assert (ref_obj.includes([1, 2]), ref_obj.includes((1, 2)), ref_obj.includes(set([1.0, 2.0])), ref_obj.includes(1+2j), ref_obj.includes('a')) == (True, True, False, False, False)

def test_arbitrary_length_istype():
	"""	Test that the istype method of ArbitraryLength class behaves appropriately """
	ref_obj = putil.check.ArbitraryLength(int)
	assert (ref_obj.istype([1, 2]), ref_obj.istype((1, 2)), ref_obj.istype(set([1.0, 2.0])), ref_obj.istype(1+2j), ref_obj.istype('a')) == (True, True, False, False, False)

###
# Test for ArbitraryLengthList class
###
def test_arbitrary_length_list_no_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLengthList class behaves appropriately when all parameters are correctly specified """
	obj_type = int
	obj = putil.check.ArbitraryLengthList(obj_type)
	assert (obj.element_type == obj_type, obj.iter_type == list) == (True, True)

def test_arbitrary_length_list_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLengthList class behaves appropriately when inproper parameter type is passed """
	with pytest.raises(TypeError) as excinfo:
		putil.check.ArbitraryLengthList('a')
	assert excinfo.value.message == 'Parameter `element_type` is of the wrong type'

def test_arbitrary_length_list_includes():	#pylint: disable=C0103
	"""	Test that the includes method of ArbitraryLengthList class behaves appropriately """
	ref_obj = putil.check.ArbitraryLengthList(int)
	assert (ref_obj.includes([1, 2]), ref_obj.includes(set([1, 2])), ref_obj.includes((1, 2)), ref_obj.includes('a')) == (True, False, False, False)

def test_arbitrary_length_list_istype():	#pylint: disable=C0103
	"""	Test that the istype method of ArbitraryLengthList class behaves appropriately """
	ref_obj = putil.check.ArbitraryLengthList(int)
	assert (ref_obj.istype([1, 2]), ref_obj.istype(set([1, 2])), ref_obj.istype((1, 2)), ref_obj.istype('a')) == (True, False, False, False)

###
# Test for ArbitraryLengthTuple class
###
def test_arbitrary_length_tuple_no_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLengthTuple class behaves appropriately when all parameters are correctly specified	"""
	obj_type = int
	obj = putil.check.ArbitraryLengthTuple(obj_type)
	assert (obj.element_type == obj_type, obj.iter_type == tuple) == (True, True)

def test_arbitrary_length_tuple_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLengthTuple class behaves appropriately when inproper parameter type is passed """
	with pytest.raises(TypeError) as excinfo:
		putil.check.ArbitraryLengthTuple('a')
	assert excinfo.value.message == 'Parameter `element_type` is of the wrong type'

def test_arbitrary_length_tuple_includes():	#pylint: disable=C0103
	"""	Test that the includes method of ArbitraryLengthTuple class behaves appropriately """
	ref_obj = putil.check.ArbitraryLengthTuple(float)
	assert (ref_obj.includes((1.0, 2.0)), ref_obj.includes([1, 2]), ref_obj.includes(set([1, 2])), ref_obj.includes('a')) == (True, False, False, False)

def test_arbitrary_length_tuple_type():	#pylint: disable=C0103
	"""	Test that the istype method of ArbitraryLengthTuple class behaves appropriately """
	ref_obj = putil.check.ArbitraryLengthTuple(float)
	assert (ref_obj.istype((1.0, 2.0)), ref_obj.istype([1, 2]), ref_obj.istype(set([1, 2])), ref_obj.istype('a')) == (True, False, False, False)

###
# Test for ArbitraryLengthSet class
###
def test_arbitrary_length_set_no_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLengthSet class behaves appropriately when all parameters are correctly specified """
	obj_type = int
	obj = putil.check.ArbitraryLengthSet(obj_type)
	assert (obj.element_type == obj_type, obj.iter_type == set) == (True, True)

def test_arbitrary_length_set_exception():	#pylint: disable=C0103
	"""	Tests that ArbitraryLengthSet class behaves appropriately when inproper parameter type is passed """
	with pytest.raises(TypeError) as excinfo:
		putil.check.ArbitraryLengthSet('a')
	assert excinfo.value.message == 'Parameter `element_type` is of the wrong type'

def test_arbitrary_length_set_includes():	#pylint: disable=C0103
	""" Test that the includes method of ArbitraryLengthSet class behaves appropriately """
	ref_obj = putil.check.ArbitraryLengthSet(float)
	assert (ref_obj.includes(set([1.0, 2.0])), ref_obj.includes([1, 2]), ref_obj.includes((1, 2)), ref_obj.includes('a')) == (True, False, False, False)

def test_arbitrary_length_set_istype():	#pylint: disable=C0103
	""" Test that the istype method of ArbitraryLengthSet class behaves appropriately """
	ref_obj = putil.check.ArbitraryLengthSet(float)
	assert (ref_obj.istype(set([1.0, 2.0])), ref_obj.istype([1, 2]), ref_obj.istype((1, 2)), ref_obj.istype('a')) == (True, False, False, False)

###
# Test for OneOf class
###
def test_one_of_case_insensitive_exception():	#pylint: disable=C0103
	""" Tests that OneOf class behaves properly when an improper case_insensitive type is given """
	with pytest.raises(TypeError) as excinfo:
		putil.check.OneOf(['a', 'b', 'c'], case_sensitive=3)
	assert excinfo.value.message == 'Parameter `case_sensitive` is of the wrong type'

def test_one_of_case_insensitive_none_if_no_strings_in_choices():	#pylint: disable=C0103
	""" Tests that OneOf class behaves properly when no string options given """
	assert (putil.check.OneOf([1, 2, 3], case_sensitive=True).case_sensitive == None, putil.check.OneOf([1, 2, 3], case_sensitive=False).case_sensitive == None) == (True, True)

def test_one_of_infinite_iterable_exception():	#pylint: disable=C0103
	""" Tests that OneOf class behaves properly when an improper iterable is given """
	with pytest.raises(TypeError) as excinfo:
		putil.check.OneOf(itertools.count(start=0, step=1))
	assert excinfo.value.message == 'Parameter `choices` is of the wrong type'

def test_one_of_proper_no_errors():	#pylint: disable=C0103
	""" Tests that OneOf class behaves properly when all parameters are correctly specified """
	test_choices = ['a', 2, 3.0, 'a', putil.check.Real()]
	obj = putil.check.OneOf(test_choices, case_sensitive=True)
	assert (obj.types == [type(element) for element in test_choices], obj.choices == test_choices, obj.case_sensitive == True) == (True, True, True)

def test_one_of_proper_contains_behavior():	#pylint: disable=C0103
	""" Tests that OneOf class behaves properly extracting type information """
	obj1 = putil.check.OneOf(['a', 'b', 3.0, 2], case_sensitive=True)
	obj2 = putil.check.OneOf(['c', 'D', putil.check.IncreasingRealNumpyVector()], case_sensitive=False)
	assert ('a' in obj1, 'b' in obj1, 3.0 in obj1, 2 in obj1, [1, 2] in obj1, 3.1 in obj1, 'A' in obj1, 'C' in obj2, 'd' in obj2, 'e' in obj2, 'E' in obj2, numpy.array([1, 2, 3]) in obj2, numpy.array([1.0, 0.0, -1.0]) in obj2) == \
		(True, True, True, True, False, False, False, True, True, False, False, True, False)

def test_one_of_includes():	#pylint: disable=C0103
	"""Test that the includes method of OneOf class behaves appropriately """
	ref_obj1 = putil.check.OneOf(['a', 'b', 3.0, 2], case_sensitive=True)
	ref_obj2 = putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=False)
	assert (ref_obj1.includes('a'), ref_obj1.includes('b'), ref_obj1.includes(3.0), ref_obj1.includes(2), ref_obj1.includes(putil.check.Number()), ref_obj1.includes('c'), ref_obj1.includes('A'),
		 ref_obj2.includes('none'), ref_obj2.includes('autos')) == (True, True, True, True, False, False, False, True, False)

def test_one_of_istype():	#pylint: disable=C0103
	"""Test that the istype method of OneOf class behaves appropriately """
	ref_obj1 = putil.check.OneOf(['a', 'b', 3.0, 2], case_sensitive=True)
	ref_obj2 = putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=False)
	assert (ref_obj1.istype('a'), ref_obj1.istype('b'), ref_obj1.istype(3.0), ref_obj1.istype(2), ref_obj1.istype(putil.check.Number()), ref_obj1.istype('c'), ref_obj1.istype('A'),
		 ref_obj2.istype('none'), ref_obj2.istype('autos'), ref_obj2.istype(set([1, 2]))) == (True, True, True, True, False, True, True, True, True, False)

def test_one_of_exception():
	""" Tests that exception method of OneOf class behaves appropriately """
	test1 = putil.check.OneOf(['a', 'b', 3.0, 2], case_sensitive=False).exception('par1') == {'type':ValueError, 'msg':"Parameter `par1` is not one of ['a', 'b', 3.0, 2] (case insensitive)"}
	test2 = putil.check.OneOf(['a', 'b', 3.0, 2], case_sensitive=True).exception('par1') == {'type':ValueError, 'msg':"Parameter `par1` is not one of ['a', 'b', 3.0, 2] (case sensitive)"}
	test3 = putil.check.OneOf([3.0, 2], case_sensitive=True).exception('par1') == {'type':ValueError, 'msg':"Parameter `par1` is not one of [3.0, 2]"}
	assert (test1, test2, test3) == (True, True, True)

###
# Test for NumberRange class
###
def test_number_range_minimum_not_a_number():	#pylint: disable=C0103
	""" Tests that NumberRange class behaves properly when minimum is not a number """
	with pytest.raises(TypeError) as excinfo:
		putil.check.NumberRange(minimum=False, maximum=None)
	assert excinfo.value.message == 'Parameter `minimum` is of the wrong type'

def test_number_range_maximum_not_a_number():	#pylint: disable=C0103
	""" Tests that NumberRange class behaves properly when maximum is not a number """
	with pytest.raises(TypeError) as excinfo:
		putil.check.NumberRange(minimum=None, maximum=True)
	assert excinfo.value.message == 'Parameter `maximum` is of the wrong type'

def test_number_range_minimum_and_maximum_not_specified():	#pylint: disable=C0103
	""" Tests that NumberRange class behaves properly when neither minimum nor maximum are specified """
	with pytest.raises(TypeError) as excinfo:
		putil.check.NumberRange(minimum=None, maximum=None)
	assert excinfo.value.message == 'Either parameter `minimum` or parameter `maximum` needs to be specified'

def test_number_range_minimum_and_maximum_are_of_different_type():	#pylint: disable=C0103
	""" Tests that NumberRange class behaves properly when minimum is either integer or float and maximum is either float or integer """
	with pytest.raises(TypeError) as excinfo:
		putil.check.NumberRange(minimum=1.5, maximum=3)
	assert excinfo.value.message == 'Parameters `minimum` and `maximum` have different types'

def test_number_range_minimum_greater_than_maximum():	#pylint: disable=C0103
	""" Tests that NumberRange class behaves properly when minimum is greater than maximum """
	with pytest.raises(ValueError) as excinfo:
		putil.check.NumberRange(minimum=1.5, maximum=0.0)
	assert excinfo.value.message == 'Parameter `minimum` greater than parameter `maximum`'

def test_number_range_no_errors():	#pylint: disable=C0103
	""" Tests that NumberRange class behaves properly when all parameters are correctly specified """
	obj = putil.check.NumberRange(minimum=10, maximum=20)
	assert (obj.minimum == 10, obj.maximum == 20) == (True, True)

def test_number_range_includes():	#pylint: disable=C0103
	""" Test that the includes method of NumberRange class behaves appropriately """
	ref_obj1 = putil.check.NumberRange(10, 15)
	ref_obj2 = putil.check.NumberRange(100.0, 200.0)
	assert (ref_obj1.includes(5), ref_obj1.includes(10), ref_obj1.includes(13), ref_obj1.includes(15), ref_obj1.includes(20), ref_obj1.includes(13.0),
		 ref_obj2.includes(75.1), ref_obj2.includes(100.0), ref_obj2.includes(150.0), ref_obj2.includes(200.0), ref_obj2.includes(200.1), ref_obj2.includes(200)) == \
		 (False, True, True, True, False, False, False, True, True, True, False, False)

def test_number_range_istype():	#pylint: disable=C0103
	""" Test that the istype method of NumberRange class behaves appropriately """
	ref_obj1 = putil.check.NumberRange(10, 15)
	ref_obj2 = putil.check.NumberRange(100.0, 200.0)
	assert (ref_obj1.istype(5), ref_obj1.istype(10), ref_obj1.istype(13), ref_obj1.istype(15), ref_obj1.istype(20), ref_obj1.istype(13.0),
		 ref_obj2.istype(75.1), ref_obj2.istype(100.0), ref_obj2.istype(150.0), ref_obj2.istype(200.0), ref_obj2.istype(200.1), ref_obj2.istype(200)) == \
		 (True, True, True, True, True, False, True, True, True, True, True, False)

def test_number_range_exception():
	""" Tests that exception method of NumberRange class behaves appropriately """
	test1 = putil.check.NumberRange(maximum=15).exception('par1') == {'type':ValueError, 'msg':'Parameter `par1` is not in the range [-inf, 15]'}
	test2 = putil.check.NumberRange(minimum=20.0).exception('par1') == {'type':ValueError, 'msg':'Parameter `par1` is not in the range [20.0, +inf]'}
	test3 = putil.check.NumberRange(minimum=3.5, maximum=4.75).exception('par1') == {'type':ValueError, 'msg':'Parameter `par1` is not in the range [3.5, 4.75]'}
	assert (test1, test2, test3) == (True, True, True)

###
# Test RealNumpyVector class
###
def test_real_numpy_vector_no_exception():	#pylint: disable=C0103
	""" Test that RealNumpyVector class behaves appropriately when all parameters are correctly specified """
	putil.check.RealNumpyVector()

def test_real_numpy_vector_includes():	#pylint: disable=C0103
	""" Test that the includes method of RealNumpyVector class behaves appropriately """
	ref_obj = putil.check.RealNumpyVector()
	assert (ref_obj.includes('a'), ref_obj.includes([1, 2, 3]), ref_obj.includes(numpy.array([])), ref_obj.includes(numpy.array([[1, 2, 3], [4, 5, 6]])), ref_obj.includes(numpy.array(['a', 'b'])),
		 ref_obj.includes(numpy.array([1, 2, 3])), ref_obj.includes(numpy.array([10.0, 8.0, 2.0])), ref_obj.includes(numpy.array([10.0]))) == (False, False, False, False, False, True, True, True)

def test_real_numpy_vector_istype():	#pylint: disable=C0103
	""" Test that the istype method of RealNumpyVector class behaves appropriately """
	ref_obj = putil.check.RealNumpyVector()
	assert (ref_obj.istype('a'), ref_obj.istype([1, 2, 3]), ref_obj.istype(numpy.array([])), ref_obj.istype(numpy.array([[1, 2, 3], [4, 5, 6]])), ref_obj.istype(numpy.array(['a', 'b'])),
		 ref_obj.istype(numpy.array([1, 2, 3])), ref_obj.istype(numpy.array([10.0, 8.0, 2.0])), ref_obj.istype(numpy.array([10.0]))) == (False, False, False, False, False, True, True, True)

###
# Test IncreasingRealNumpyVector class
###
def test_increasing_real_numpy_vector_no_exception():	#pylint: disable=C0103
	""" Test that IncreasingRealNumpyVector class behaves appropriately when all parameters are correctly specified """
	putil.check.IncreasingRealNumpyVector()

def test_increasing_real_numpy_vector_includes():	#pylint: disable=C0103
	""" Test that the includes method of IncreasingRealNumpyVector class behaves appropriately """
	ref_obj = putil.check.IncreasingRealNumpyVector()
	assert (ref_obj.includes('a'), ref_obj.includes([1, 2, 3]), ref_obj.includes(numpy.array([])), ref_obj.includes(numpy.array([[1, 2, 3], [4, 5, 6]])), ref_obj.includes(numpy.array(['a', 'b'])),
		 ref_obj.includes(numpy.array([1, 0, -3])), ref_obj.includes(numpy.array([10.0, 8.0, 2.0])), ref_obj.includes(numpy.array([1, 2, 3])), ref_obj.includes(numpy.array([10.0, 12.1, 12.5])),
		 ref_obj.includes(numpy.array([10.0]))) == (False, False, False, False, False, False, False, True, True, True)

def test_increasing_real_numpy_vector_istype():	#pylint: disable=C0103
	""" Test that the istype method of IncreasingRealNumpyVector class behaves appropriately """
	ref_obj = putil.check.IncreasingRealNumpyVector()
	assert (ref_obj.istype('a'), ref_obj.istype([1, 2, 3]), ref_obj.istype(numpy.array([])), ref_obj.istype(numpy.array([[1, 2, 3], [4, 5, 6]])), ref_obj.istype(numpy.array(['a', 'b'])),
		 ref_obj.istype(numpy.array([1, 0, -3])), ref_obj.istype(numpy.array([10.0, 8.0, 2.0])), ref_obj.istype(numpy.array([1, 2, 3])), ref_obj.istype(numpy.array([10.0, 12.1, 12.5])), ref_obj.istype(numpy.array([10.0]))) == \
		(False, False, False, False, False, False, False, True, True, True)

###
# Test File class
###
def test_file_parameter_wrong_type():	#pylint: disable=C0103
	""" Test if function behaves proprely when wrong type parameter is given """
	with pytest.raises(TypeError) as excinfo:
		putil.check.File('a')
	assert excinfo.value.message == 'Parameter `check_existance` is of the wrong type'

def test_file_includes():	#pylint: disable=C0103
	""" Test that the includes method of File class behaves appropriately """
	assert (putil.check.File().includes('/some/file.txt'), putil.check.File(True).includes('not a file'), putil.check.File(True).includes('./check_test.py')) == (True, False, True)

def test_file_istype():	#pylint: disable=C0103
	""" Test that the istype method of File class behaves appropriately """
	assert (putil.check.File().istype(3), putil.check.File(True).istype('not a file'), putil.check.File(True).istype('./putil.check_test.py')) == (False, True, True)

def test_file_exception():
	""" Tests that exception method of File class behaves appropriately """
	assert putil.check.File().exception('/some/path/file_name.ext') == {'type':IOError, 'msg':'File /some/path/file_name.ext could not be found'}

###
# Test Function class
###
def test_function_wrong_type():	#pylint: disable=C0103
	""" Test if function behaves proprely when wrong type parameter is given """
	with pytest.raises(TypeError) as excinfo:
		putil.check.Function('a')
	assert excinfo.value.message == 'Parameter `num_pars` is of the wrong type'

def test_function_includes():	#pylint: disable=C0103
	""" Test that the includes method of Function class behaves appropriately """
	def foo1(par1, par2):	#pylint: disable=C0111
		return par1, par2
	def foo2(par1, *args):	#pylint: disable=C0111
		return par1, args
	def foo3(par1, *kwargs):	#pylint: disable=C0111
		return par1, kwargs
	def foo4(par1, *args, **kwargs):	#pylint: disable=C0111
		return par1, args, kwargs
	assert (putil.check.Function().includes(3), putil.check.Function().includes(foo1), putil.check.Function(num_pars=3).includes(foo1), putil.check.Function(num_pars=2).includes(foo1),
		putil.check.Function().includes(foo2), putil.check.Function(num_pars=5).includes(foo2), putil.check.Function(num_pars=2).includes(foo2),
		putil.check.Function().includes(foo3), putil.check.Function(num_pars=5).includes(foo3), putil.check.Function(num_pars=2).includes(foo3),
		putil.check.Function().includes(foo4), putil.check.Function(num_pars=5).includes(foo4), putil.check.Function(num_pars=2).includes(foo4)) == (False, True, False, True, True, True, True, True, True, True, True, True, True)

def test_function_istype():	#pylint: disable=C0103
	""" Test that the istype method of Function class behaves appropriately """
	def foo1(par1, par2):	#pylint: disable=C0111
		return par1, par2
	assert (putil.check.Function().istype(3), putil.check.Function().istype(foo1), putil.check.Function(num_pars=3).istype(foo1), putil.check.Function(num_pars=2).istype(foo1)) == (False, True, True, True)

def test_function_exception():
	""" Tests that exception method of Function class behaves appropriately """
	assert (putil.check.Function(num_pars=1).exception('par1') == {'type':ValueError, 'msg':'Parameter `par1` is not a function with 1 parameter'},
		putil.check.Function(num_pars=2).exception('par1') == {'type':ValueError, 'msg':'Parameter `par1` is not a function with 2 parameters'}) == (True, True)

###
# Test PolymorphicType class
###
def test_type_match_polymorphic_type_wrong_type():	#pylint: disable=C0103
	""" Test if function behaves proprely when wrong type parameter is given """
	with pytest.raises(TypeError) as excinfo:
		putil.check.PolymorphicType('a')
	assert excinfo.value.message == 'Parameter `types` is of the wrong type'

def test_type_match_polymorphic_type_subtype_wrong_type():	#pylint: disable=C0103
	""" Test if function behaves proprely when wrong sub-type parameter is given """
	with pytest.raises(TypeError) as excinfo:
		putil.check.PolymorphicType([str, int, 'a'])
	assert excinfo.value.message == 'Parameter `types` element is of the wrong type'

def test_type_match_polymorphic_type_no_errors():	#pylint: disable=C0103
	""" Test if function behaves proprely when all parameters are correctly specified """
	test_instances = [str, int, None, putil.check.ArbitraryLengthList, putil.check.ArbitraryLengthTuple, putil.check.ArbitraryLengthSet, putil.check.IncreasingRealNumpyVector, putil.check.RealNumpyVector, putil.check.OneOf,
		  putil.check.NumberRange, putil.check.Number, putil.check.Real, putil.check.File, putil.check.Function]
	obj = putil.check.PolymorphicType(test_instances)
	test_types = test_instances[:]
	test_types[2] = type(None)
	assert (obj.instances == test_instances, obj.types == test_types) == (True, True)

def test_polymorphic_type_includes():	#pylint: disable=C0103
	""" Test that the includes method of PolymorphicType class behaves appropriately """
	test_instances = [int, None, putil.check.ArbitraryLengthList(int), putil.check.ArbitraryLengthTuple(float), putil.check.ArbitraryLengthSet(str), putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=True),
		  putil.check.NumberRange(1, 3), putil.check.Number(), putil.check.Real(), putil.check.RealNumpyVector()]
	ref_obj1 = putil.check.PolymorphicType(test_instances)
	ref_obj2 = putil.check.PolymorphicType([float, putil.check.IncreasingRealNumpyVector()])
	ref_obj3 = putil.check.PolymorphicType([putil.check.File(check_existance=False), putil.check.Function(num_pars=2)])
	def foo1(par1, par2, par3):	#pylint: disable=C0111
		return par1, par2, par3
	def foo2(par1, par2):	#pylint: disable=C0111
		return par1, par2
	assert (ref_obj1.includes(5), ref_obj1.includes(None), ref_obj1.includes([1, 2, 3]), ref_obj1.includes((2.0, 3.0)), ref_obj1.includes(set(['a', 'b', 'c'])), ref_obj1.includes('MANUAL'), ref_obj1.includes(2),
		 ref_obj1.includes(100.0), ref_obj1.includes(10+20j), ref_obj1.includes(numpy.array([10, 0.0, 30])), ref_obj1.includes('hello world'), ref_obj1.includes([1.0, 2.0, 3.0]), ref_obj1.includes('auto'),
		 ref_obj1.includes(numpy.array([])), ref_obj1.includes(numpy.array(['a', 'b', 'c'])), ref_obj2.includes(1), ref_obj2.includes(set([1, 2])), ref_obj2.includes(numpy.array([1, 0, -1])),
		 ref_obj2.includes(numpy.array([10.0, 20.0, 30.0])), ref_obj2.includes(5.0), ref_obj3.includes(3), ref_obj3.includes('/some/file'), ref_obj3.includes(foo1), ref_obj3.includes(foo2)) == \
		 (True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False, True, True, False, True, False, True)

def test_polymorphic_type_istype():	#pylint: disable=C0103
	""" Test that the istype method of PolymorphicType class behaves appropriately """
	test_instances = [int, None, putil.check.ArbitraryLengthList(int), putil.check.ArbitraryLengthTuple(float), putil.check.ArbitraryLengthSet(str), putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=True),
		  putil.check.NumberRange(1, 3), putil.check.Number(), putil.check.Real(), putil.check.RealNumpyVector()]
	ref_obj1 = putil.check.PolymorphicType(test_instances)
	ref_obj2 = putil.check.PolymorphicType([float, putil.check.IncreasingRealNumpyVector()])
	ref_obj3 = putil.check.PolymorphicType([putil.check.File(check_existance=False), putil.check.Function(num_pars=2)])
	def foo1(par1, par2, par3):	#pylint: disable=C0111
		return par1, par2, par3
	assert (ref_obj1.istype(5), ref_obj1.istype(None), ref_obj1.istype([1, 2, 3]), ref_obj1.istype((2.0, 3.0)), ref_obj1.istype(set(['a', 'b', 'c'])), ref_obj1.istype('MANUAL'), ref_obj1.istype(2),
		 ref_obj1.istype(100.0), ref_obj1.istype(10+20j), ref_obj1.istype(numpy.array([10, 0.0, 30])), ref_obj1.istype('hello world'), ref_obj1.istype([1.0, 2.0, 3.0]), ref_obj1.istype('auto'),
		 ref_obj1.istype(numpy.array([])), ref_obj1.istype(numpy.array(['a', 'b', 'c'])), ref_obj2.istype(1), ref_obj2.istype(set([1, 2])), ref_obj2.istype(numpy.array([1, 0, -1])),
		 ref_obj2.istype(numpy.array([10.0, 20.0, 30.0])), ref_obj2.istype(5.0), ref_obj3.istype(3), ref_obj3.istype('/some/file'), ref_obj3.istype(foo1)) == \
		 (True, True, True, True, True, True, True, True, True, True, True, False, True, False, False, False, False, False, True, True, False, True, True)

def test_polymorphic_exception():
	""" Tests that exception method of PolymorphicType class behaves appropriately """
	obj1 = putil.check.PolymorphicType([putil.check.OneOf(['NONE', 'MANUAL', 'AUTO']), putil.check.NumberRange(minimum=15, maximum=20)])
	obj2 = putil.check.PolymorphicType([putil.check.OneOf(['NONE', 'MANUAL', 'AUTO']), putil.check.File(True)])
	obj3 = putil.check.PolymorphicType([putil.check.File(True), putil.check.Function(num_pars=2)])
	test1 = obj1.exception('par1', 5) == {'type':ValueError, 'msg':"Parameter `par1` is not one of ['NONE', 'MANUAL', 'AUTO'] (case insensitive)\nParameter `par1` is not in the range [15, 20]"}
	test2 = obj2.exception('par1', '_not_valid_') == {'type':RuntimeError, 'msg':"(ValueError) Parameter `par1` is not one of ['NONE', 'MANUAL', 'AUTO'] (case insensitive)\n(IOError) File _not_valid_ could not be found"}
	test3 = obj3.exception('par1', '_not_valid_') == {'type':RuntimeError, 'msg':'(IOError) File _not_valid_ could not be found\n(ValueError) Parameter `par1` is not a function with 2 parameters'}
	assert (test1, test2, test3) == (True, True, True)

##
# Tests for get_function_args()
###
def test_get_function_args_all_positional_parameters():	#pylint: disable=C0103
	""" Test that function behaves properly when all parameters are positional parameters """
	def func(ppar1, ppar2, ppar3):	#pylint: disable=C0111,W0613
		pass
	assert putil.check.get_function_args(func) == ('ppar1', 'ppar2', 'ppar3')

def test_get_function_args_all_keyword_parameters():	#pylint: disable=C0103,W0613
	""" Test that function behaves properly when all parameters are keywords parameters """
	def func(kpar1=1, kpar2=2, kpar3=3):	#pylint: disable=C0111,R0913,W0613
		pass
	assert putil.check.get_function_args(func) == ('kpar1', 'kpar2', 'kpar3')

def test_get_function_args_positional_and_keyword_parameters():	#pylint: disable=C0103
	""" Test that function behaves properly when parameters are a mix of positional and keywords parameters """
	def func(ppar1, ppar2, ppar3, kpar1=1, kpar2=2, kpar3=3):	#pylint: disable=C0103,C0111,R0913,W0613
		pass
	assert putil.check.get_function_args(func) == ('ppar1', 'ppar2', 'ppar3', 'kpar1', 'kpar2', 'kpar3')

def test_get_function_args_no_parameters():	#pylint: disable=C0103
	""" Test that function behaves properly when there are no parameters passed """
	def func():	#pylint: disable=C0111,R0913,W0613
		pass
	assert putil.check.get_function_args(func) == ()

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
		return ret_func(putil.check.create_parameter_dictionary(func, *args, **kwargs))
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
	assert (putil.check.type_match('hello', str), putil.check.type_match(135, str)) == (True, False)

def test_type_match_float():
	""" Test if function behaves proprely for float type """
	assert (putil.check.type_match(1.5, float), putil.check.type_match(135, float)) == (True, False)

def test_type_match_int():
	""" Test if function behaves proprely for integer type """
	assert (putil.check.type_match(8, int), putil.check.type_match(135.0, int)) == (True, False)

def test_type_match_number():
	""" Test if function behaves proprely for Number pseudo-type (integer, real or complex) """
	assert (putil.check.type_match(1, putil.check.Number()), putil.check.type_match(135.0, putil.check.Number()), putil.check.type_match(1+1j, putil.check.Number()), putil.check.type_match('hello', putil.check.Number())) == \
		(True, True, True, False)

def test_type_match_real():
	""" Test if function behaves proprely for Real pseudo-type (integer or real) """
	assert (putil.check.type_match(1, putil.check.Real()), putil.check.type_match(135.0, putil.check.Real()), putil.check.type_match(1+1j, putil.check.Real())) == (True, True, False)

def test_type_match_boolean():
	""" Test if function behaves proprely for boolean type """
	assert (putil.check.type_match(True, bool), putil.check.type_match(12.5, bool)) == (True, False)

def test_type_match_decimal():
	""" Test if function behaves proprely for Decimal type """
	assert (putil.check.type_match(decimal.Decimal(1.25), decimal.Decimal), putil.check.type_match(12.5, decimal.Decimal)) == (True, False)

def test_type_match_fraction():
	""" Test if function behaves proprely for Fraction type """
	assert (putil.check.type_match(fractions.Fraction(4, 6), fractions.Fraction), putil.check.type_match(12.5, fractions.Fraction)) == (True, False)

def test_type_match_arbitrary_length_list():	#pylint: disable=C0103
	""" Test if function behaves proprely for ArbitraryLengthList pseudo-type """
	assert (putil.check.type_match([1, 2, 3], putil.check.ArbitraryLengthList(int)), putil.check.type_match('hello', putil.check.ArbitraryLengthList(int))) == (True, False)

def test_type_match_arbitrary_length_tuple():	#pylint: disable=C0103
	""" Test if function behaves proprely for ArbitraryLengthTuple pseudo-type """
	assert (putil.check.type_match((1, 2, 3), putil.check.ArbitraryLengthTuple(int)), putil.check.type_match((1, 2, 'a'), putil.check.ArbitraryLengthTuple(int))) == (True, False)

def test_type_match_arbitrary_length_set():	#pylint: disable=C0103
	""" Test if function behaves proprely for ArbitraryLengthSet pseudo-type """
	assert (putil.check.type_match(set([1, 2, 3]), putil.check.ArbitraryLengthSet(int)), putil.check.type_match(set([1, 2, 'a']), putil.check.ArbitraryLengthSet(int))) == (True, False)

def test_type_match_fixed_length_list():	#pylint: disable=C0103
	""" Test if function behaves proprely for fixed-length list type """
	assert (putil.check.type_match([1, 'a', 3.0], [int, str, float]), putil.check.type_match([1, 'a', 3.0, 4.0], [int, str, float]), putil.check.type_match([1, 'a', 3.0], [int, str, float, int]),
		 putil.check.type_match([1, 2, 3.0], [int, str, float])) == (True, False, False, False)

def test_type_match_fixed_length_tuple():	#pylint: disable=C0103
	""" Test if function behaves proprely for fixed-length tuple type """
	assert (putil.check.type_match((1, 'a', 3.0), (int, str, float)), putil.check.type_match((1, 'a', 3.0, 4.0), (int, str, float)), putil.check.type_match((1, 'a', 3.0), (int, str, float, int)),
		 putil.check.type_match((1, 2, 3.0), (int, str, float))) == (True, False, False, False)

def test_type_match_fixed_length_set():	#pylint: disable=C0103
	""" Test if function behaves proprely for fixed-length set type """
	with pytest.raises(RuntimeError) as excinfo:
		putil.check.type_match(set([1, 'a', 3.0]), set([int, str, float]))
	assert excinfo.value.message == 'Set is an un-ordered iterable, thus it cannot be type-checked against an ordered reference'

def test_type_match_one_of():	#pylint: disable=C0103
	""" Test if function behaves proprely for OneOf pseudo-type """
	assert (putil.check.type_match('HELLO', putil.check.OneOf(['HELLO', 45, 'WORLD'])), putil.check.type_match(45, putil.check.OneOf(['HELLO', 45, 'WORLD'])),
		 putil.check.type_match(1.0, putil.check.OneOf(['HELLO', 45, 'WORLD']))) == (True, True, False)

def test_type_match_number_range():	#pylint: disable=C0103
	""" Test if function behaves proprely for NumberRange pseudo-type """
	assert (putil.check.type_match(12, putil.check.NumberRange(minimum=2, maximum=5)), putil.check.type_match('a', putil.check.NumberRange(minimum=2, maximum=5))) == (True, False)

def test_type_match_dict():
	""" Test if function behaves proprely for dictionary type """
	assert (putil.check.type_match({'a':'hello', 'b':12.5, 'c':[1]}, {'a':str, 'b':float, 'c':[int]}),	# 'Regular' match
		 putil.check.type_match({'a':'hello', 'c':[1]}, {'a':str, 'b':float, 'c':[int]}),	# One key-value pair missing in test object, useful where parameter is omitted to get default
		 putil.check.type_match({'x':'hello', 'y':{'n':[1.5, 2.3]}, 'z':[1]}, {'x':str, 'y':{'n':putil.check.ArbitraryLengthList(float), 'm':str}, 'z':[int]}), # Nested
		 putil.check.type_match({'a':'hello', 'b':35, 'c':[1]}, {'a':str, 'b':float, 'c':[int]}),	# Value of one key in test object does not match
		 putil.check.type_match({'a':'hello', 'd':12.5, 'c':[1]}, {'a':str, 'b':float, 'c':[int]})) == (True, True, True, False, False)	# One key in test object does not appear in reference object

def test_type_match_polymorphic_type():	#pylint: disable=C0103
	""" Test if function behaves proprely for PolymorphicType pseudo-type """
	assert (putil.check.type_match('HELLO', putil.check.PolymorphicType([str, int])), putil.check.type_match(45, putil.check.PolymorphicType([str, int])), putil.check.type_match(1.5, putil.check.PolymorphicType([str, int]))) \
		== (True, True, False)

def test_type_match_real_numpy_vector():	#pylint: disable=C0103
	""" Test if function behaves proprely for RealNumpyVector pseudo-type """
	assert (putil.check.type_match(12, putil.check.RealNumpyVector()), putil.check.type_match(numpy.array([1, 2, 0]), putil.check.RealNumpyVector()),
		 putil.check.type_match(numpy.array([[1, 2, 0], [1, 1, 2]]), putil.check.RealNumpyVector())) == (False, True, False)

def test_type_match_increasing_real_numpy_vector():	#pylint: disable=C0103
	""" Test if function behaves proprely for IncreasingRealNumpyVector pseudo-type """
	assert (putil.check.type_match(12, putil.check.IncreasingRealNumpyVector()), putil.check.type_match(numpy.array([1, 2, 3]), putil.check.IncreasingRealNumpyVector()),
		 putil.check.type_match(numpy.array([True, False, True]), putil.check.IncreasingRealNumpyVector()),
		 putil.check.type_match(numpy.array([[1, 2, 3], [4, 5, 6]]), putil.check.IncreasingRealNumpyVector())) == (False, True, False, False)

###
# Tests for check_type()
###
def test_check_type_simple_exception():	#pylint: disable=C0103
	""" Test that function behaves properly when a sigle (wrong) type is given (string, number, etc.) """
	@putil.check.check_parameter_type('ppar1', int)
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(TypeError) as excinfo:
		func_check_type('Hello world')
	assert excinfo.value.message == 'Parameter `ppar1` is of the wrong type'

def test_check_type_simple_no_exception():	#pylint: disable=C0103
	""" Test that function behaves properly when a sigle (right) type is given (string, number, etc.) """
	@putil.check.check_parameter_type(param_name='ppar1', param_type=putil.check.Number())
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	assert func_check_type(5.0) == 5.0

def test_check_type_parameter_not_specified():	#pylint: disable=C0103
	""" Test that function behaves properly when the parameter to be checked is not specified in the function call """
	@putil.check.check_parameter_type(param_name='ppar2', param_type=putil.check.Number())
	def func_check_type(ppar1, ppar2=None, ppar3=5):	#pylint: disable=C0111
		return ppar1, ppar2, ppar3
	assert func_check_type(3, ppar3=12) == (3, None, 12)

def test_check_type_parameter_specified_by_position_and_keyword():	#pylint: disable=C0103
	""" Test that function behaves properly when a parameter is specified both by position and keyword """
	@putil.check.check_parameter_type(param_name='ppar2', param_type=putil.check.Number())
	def func_check_type(ppar1, ppar2=None, ppar3=5):	#pylint: disable=C0111
		print ppar1, ppar2, ppar3
	with pytest.raises(TypeError) as excinfo:
		func_check_type(3, ppar3=12, ppar1=12)	#pylint: disable=E1124
	assert excinfo.value.message == "func_check_type() got multiple values for keyword argument 'ppar1'"

def test_check_type_parameter_repeated_keyword_arguments():	#pylint: disable=C0103
	""" Test that function behaves properly when a parameter is specified multiple times by keyword """
	@putil.check.check_parameter_type(param_name='ppar2', param_type=putil.check.Number())
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
	@putil.check.check_parameter('ppar1', int)
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(TypeError) as excinfo:
		func_check_type('Hello world')
	assert excinfo.value.message == 'Parameter `ppar1` is of the wrong type'

def test_check_parameter_one_of_error_case_insensitive():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is outside fixed number of string choices list with case sensitivity
	"""
	@putil.check.check_parameter('ppar1', putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=False))
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(ValueError) as excinfo:
		func_check_type('Hello world')
	assert excinfo.value.message == "Parameter `ppar1` is not one of ['NONE', 'MANUAL', 'AUTO'] (case insensitive)"

def test_check_parameter_one_of_error_case_sensitive():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is outside fixed number of string choices list with case insensitivity
	"""
	@putil.check.check_parameter('ppar1', putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=True))
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(ValueError) as excinfo:
		func_check_type('none')
	assert excinfo.value.message == "Parameter `ppar1` is not one of ['NONE', 'MANUAL', 'AUTO'] (case sensitive)"

def test_check_parameter_one_of_error_no_case_sensitivity():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is outside fixed number of choices list
	"""
	@putil.check.check_parameter('ppar1', putil.check.OneOf(range(3), case_sensitive=True))
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(ValueError) as excinfo:
		func_check_type(10)
	assert excinfo.value.message == 'Parameter `ppar1` is not one of [0, 1, 2]'

def test_check_parameter_one_of_no_error():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is one of a fixed number of choices list
	"""
	@putil.check.check_parameter('ppar1', putil.check.OneOf(range(3), case_sensitive=True))
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	assert func_check_type(2) == 2

def test_check_parameter_range_no_maximum_out_of_range():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is out of range when no maximum is defined
	"""
	@putil.check.check_parameter('ppar1', putil.check.NumberRange(minimum=10))
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(ValueError) as excinfo:
		func_check_type(1)
	assert excinfo.value.message == 'Parameter `ppar1` is not in the range [10, +inf]'

def test_check_parameter_range_no_maximum_in_range():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is in range when no maximum is defined
	"""
	@putil.check.check_parameter('ppar1', putil.check.NumberRange(minimum=10))
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	assert func_check_type(20) == 20

def test_check_parameter_range_no_minimum_out_of_range():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is out of range when no minimum is defined
	"""
	@putil.check.check_parameter('ppar1', putil.check.NumberRange(maximum=10))
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(ValueError) as excinfo:
		func_check_type(20)
	assert excinfo.value.message == 'Parameter `ppar1` is not in the range [-inf, 10]'

def test_check_parameter_range_no_minimum_in_range():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is in range when no minimum is defined
	"""
	@putil.check.check_parameter('ppar1', putil.check.NumberRange(maximum=10))
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	assert func_check_type(5) == 5

def test_check_parameter_range_minimum_and_maximum_specified_out_of_range():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is out of range when no minimum is defined
	"""
	@putil.check.check_parameter('ppar1', putil.check.NumberRange(minimum=5.0, maximum=10.0))
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(ValueError) as excinfo:
		func_check_type(3.1)
	assert excinfo.value.message == 'Parameter `ppar1` is not in the range [5.0, 10.0]'

def test_check_parameter_range_minimum_and_maximum_specified_in_range():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is in range when no minimum is defined
	"""
	@putil.check.check_parameter('ppar1', putil.check.NumberRange(minimum=100, maximum=200))
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	assert func_check_type(150) == 150

def test_check_parameter_polymorphic_type_error():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is not in the polymorphic types allowed
	"""
	@putil.check.check_parameter('ppar1', putil.check.PolymorphicType([None, float]))
	def func_check_type1(ppar1):	#pylint: disable=C0111
		print ppar1
	@putil.check.check_parameter('ppar1', putil.check.PolymorphicType([None, putil.check.NumberRange(minimum=5, maximum=10), putil.check.OneOf(['HELLO', 'WORLD'])]))
	def func_check_type2(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(TypeError) as excinfo1:	# Type not in the definition
		func_check_type1('a')
	eobj1 = excinfo1.value.message == 'Parameter `ppar1` is of the wrong type'
	with pytest.raises(ValueError) as excinfo2:	# Type not in the definition
		func_check_type2(2)
	eobj2 = excinfo2.value.message == "Parameter `ppar1` is not in the range [5, 10]\nParameter `ppar1` is not one of ['HELLO', 'WORLD'] (case insensitive)"
	assert (eobj1, eobj2) == (True, True)

def test_check_parameter_polymorphic_type_no_error():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is in the polymorphic types allowed
	"""
	@putil.check.check_parameter('ppar1', putil.check.PolymorphicType([None, int, putil.check.NumberRange(minimum=5.0, maximum=10.0), putil.check.OneOf(['HELLO', 'WORLD'])]))
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	assert (func_check_type(None), func_check_type(3), func_check_type(7.0), func_check_type('WORLD')) == (None, 3, 7.0, 'WORLD')

def test_check_parameter_numpy_vector_wrong_type():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is not a Numpy vector
	"""
	@putil.check.check_parameter('ppar1', putil.check.RealNumpyVector())
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(TypeError) as excinfo:
		func_check_type(numpy.array([False]))
	assert excinfo.value.message == 'Parameter `ppar1` is of the wrong type'

def test_check_parameter_numpy_vector_no_error():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is proper Numpy vector
	"""
	@putil.check.check_parameter('ppar1', putil.check.RealNumpyVector())
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	func_check_type(numpy.array([1.0, 2.0, 1.0-1e-10]))

def test_check_parameter_increasing_numpy_vector_wrong_type():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is not a Numpy vector
	"""
	@putil.check.check_parameter('ppar1', putil.check.IncreasingRealNumpyVector())
	def func_check_type(ppar1):	#pylint: disable=C0111
		print ppar1
	with pytest.raises(TypeError) as excinfo:
		func_check_type(numpy.array([False]))
	eobj1 = excinfo.value.message == 'Parameter `ppar1` is of the wrong type'
	with pytest.raises(TypeError) as excinfo:
		func_check_type(numpy.array([1.0, 2.0, 1.0-1e-10]))
	eobj2 = excinfo.value.message == 'Parameter `ppar1` is of the wrong type'
	assert (eobj1, eobj2) == (True, True)

def test_check_parameter_incresing_numpy_vector_no_error():	#pylint: disable=C0103
	"""
	Test that function behaves properly when a parameter is properly incresing Numpy vector
	"""
	@putil.check.check_parameter('ppar1', putil.check.IncreasingRealNumpyVector())
	def func_check_type(ppar1):	#pylint: disable=C0111
		return ppar1
	func_check_type(numpy.array([1, 2, 3]))
