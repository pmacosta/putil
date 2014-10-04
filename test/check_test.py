# check_test.py		pylint: disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Decorators for API argument checking unit tests
"""

import numpy
import pytest
import decimal
import fractions
import functools
import itertools

import putil.test
import putil.misc
import putil.check

def evaluate_exception_method(emspec_list, cobj=None, offset=0, par='par1'):	#pylint: disable=R0914
	""" Test exception method """
	# Convert to list if a single tuples is given (if necessary)
	emspec_list = emspec_list if isinstance(emspec_list, list) else [emspec_list]
	# Add object to list of tuples (if necessary)
	emspec_list = [(cobj, )+emspec_item for emspec_item in emspec_list] if cobj else emspec_list
	# Add None as argument list (if necessary)
	new_emspec_list = list()
	for emspec_item in emspec_list:
		if len(emspec_item) == 3:
			emspec_item = list(emspec_item)
			emspec_item.insert(1, None)
			emspec_item = tuple(emspec_item)
		new_emspec_list.append(emspec_item)
	emspec_list = new_emspec_list
	# Evaluate exception method list and produce readable test list
	comp_text = '[{0}] {1}.exception({2}) -> {3} ({4})'
	expected_list = list()
	actual_list = list()
	for num, (cobj, kwargs, etype, emsg) in enumerate(emspec_list):
		# Test exception method
		actual_dict = (cobj(**kwargs) if kwargs else cobj()).exception(par)
		amsg = actual_dict['msg'] if 'edata' not in actual_dict else putil.check.format_msg(actual_dict['msg'], actual_dict['edata'])
		# Produce expected and actual pretty printed results
		expected_list.append(comp_text.format(num+offset, cobj, putil.misc.quote_str(par), etype, emsg))
		actual_list.append(comp_text.format(num+offset, cobj, putil.misc.quote_str(par), actual_dict['type'], amsg))
	# Produce final actual vs. expected pretty printed list
	expected_msg, actual_msg = '\n'.join(expected_list), '\n'.join(actual_list)
	# Evaluate results
	assert expected_msg == actual_msg

###
# Test for Any class
###
class TestAny(object):	#pylint: disable=W0232
	""" Tests for Any pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201
		"""	Test that Any class behaves appropriately when all arguments are correctly specified """
		putil.check.Any()

	def test_includes(self):	#pylint: disable=R0201
		"""	Test that the includes method of Any class behaves appropriately	"""
		cmd = putil.check.Any().includes
		pairs = [(1, True), (2.0, True), (1+2j, True), ('a', True), ([1, 2, 3], True)]
		putil.test.evaluate_value_series(cmd, pairs)

	def test_istype(self):	#pylint: disable=R0201
		"""	Test that the istype method of Any class behaves appropriately """
		cmd = putil.check.Any().istype
		pairs = [(1, True), (2.0, True), (1+2j, True), ('a', True), ([1, 2, 3], True)]
		putil.test.evaluate_value_series(cmd, pairs)

	def test_exception_method(self):	#pylint: disable=R0201
		"""	Tests that Any class behaves appropriately when inproper argument type is passed """
		evaluate_exception_method((putil.check.Any, None, ''))

###
# Test for Number class
###
class TestNumber(object):	#pylint: disable=W0232
	""" Tests for Number pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201
		"""	Test that Number class behaves appropriately when all arguments are correctly specified """
		putil.check.Number()

	def test_includes(self):	#pylint: disable=R0201
		"""	Test that the includes method of Number class behaves appropriately	"""
		cmd = putil.check.Number().includes
		pairs = [(1, True), (2.0, True), (1+2j, True), ('a', False), ([1, 2, 3], False)]
		putil.test.evaluate_value_series(cmd, pairs)

	def test_istype(self):	#pylint: disable=R0201
		"""	Test that the istype method of Number class behaves appropriately """
		cmd = putil.check.Number().istype
		pairs = [(1, True), (2.0, True), (1+2j, True), ('a', False), ([1, 2, 3], False)]
		putil.test.evaluate_value_series(cmd, pairs)

	def test_exception_method(self):	#pylint: disable=R0201
		"""	Tests that Number class behaves appropriately when inproper argument type is passed """
		evaluate_exception_method((putil.check.Number, ValueError, 'Argument `par1` is not a number'))


###
# Test for PositiveInteger class
###
class TestPositiveInteger(object):	#pylint: disable=W0232
	""" Tests for PositiveInteger pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		"""	Test that PositiveInteger class behaves appropriately when all arguments are correctly specified """
		putil.check.PositiveInteger()

	def test_includes(self):	#pylint: disable=R0201
		"""	Test that the includes method of PositiveInteger class behaves appropriately """
		cmd = putil.check.PositiveInteger().includes
		pairs = [(-1, False), (1, True), (2.0, False), (1+2j, False), ('a', False), ([1, 2, 3], False)]
		putil.test.evaluate_value_series(cmd, pairs)

	def test_istype(self):	#pylint: disable=R0201
		"""	Test that the istype method of PositiveInteger class behaves appropriately """
		cmd = putil.check.PositiveInteger().istype
		pairs = [(-1, False), (1, True), (2.0, False), (1+2j, False), ('a', False), ([1, 2, 3], False)]
		putil.test.evaluate_value_series(cmd, pairs)

	def test_exception_method(self):	#pylint: disable=C0103,R0201
		"""	Tests that PositiveInteger class behaves appropriately when inproper argument type is passed """
		evaluate_exception_method((putil.check.PositiveInteger, ValueError, 'Argument `par1` is not a positive integer'))


###
# Test for Real class
###
class TestReal(object):	#pylint: disable=W0232
	""" Tests for Real pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201
		"""	Test that Real class behaves appropriately when all arguments are correctly specified """
		putil.check.Real()

	def test_includes(self):	#pylint: disable=R0201
		"""	Test that the includes method of Real class behaves appropriately """
		cmd = putil.check.Real().includes
		pairs = [(1, True), (2.0, True), (1+2j, False), ('a', False), ([1, 2, 3], False)]
		putil.test.evaluate_value_series(cmd, pairs)

	def test_istype(self):	#pylint: disable=R0201
		"""	Test that the istype method of Real class behaves appropriately """
		cmd = putil.check.Real().istype
		pairs = [(1, True), (2.0, True), (1+2j, False), ('a', False), ([1, 2, 3], False)]
		putil.test.evaluate_value_series(cmd, pairs)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that Real class behaves appropriately when inproper argument type is passed """
		evaluate_exception_method((putil.check.Real, ValueError, 'Argument `par1` is not a real number'))


###
# Test for PositiveReal class
###
class TestPositiveReal(object):	#pylint: disable=W0232
	""" Tests for PositiveReal pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		"""	Test that PositiveReal class behaves appropriately when all arguments are correctly specified """
		putil.check.PositiveReal()

	def test_includes(self):	#pylint: disable=R0201
		"""	Test that the includes method of PositiveReal class behaves appropriately """
		cmd = putil.check.PositiveReal().includes
		pairs = [(-1, False), (1, True), (2.0, True), (1+2j, False), ('a', False), ([1, 2, 3], False)]
		putil.test.evaluate_value_series(cmd, pairs)

	def test_istype(self):	#pylint: disable=R0201
		"""	Test that the istype method of PositiveReal class behaves appropriately """
		cmd = putil.check.PositiveReal().istype
		pairs = [(-1, False), (1, True), (2.0, True), (1+2j, False), ('a', False), ([1, 2, 3], False)]
		putil.test.evaluate_value_series(cmd, pairs)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that PositiveReal class behaves appropriately when inproper argument type is passed """
		evaluate_exception_method((putil.check.PositiveReal, ValueError, 'Argument `par1` is not a positive real number'))


###
# Test for ArbitraryLength class
###
class TestArbitraryLength(object):	#pylint: disable=W0232
	""" Tests for ArbitraryLength pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLength class behaves appropriately when all arguments are correctly specified """
		obj = putil.check.ArbitraryLength(iter_type=list, element_type=str)
		assert (obj.iter_type == list, obj.element_type == str) == (True, True)

	def test_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLength class behaves appropriately when inproper argument type is passed """
		exdesc = list()
		exdesc.append(({'iter_type':'a', 'element_type':str}, TypeError, 'Argument `iter_type` is of the wrong type'))
		exdesc.append(({'iter_type':list, 'element_type':'a'}, TypeError, 'Argument `element_type` is of the wrong type'))
		exdesc.append(({'iter_type':list, 'element_type':int}, ))
		exdesc.append(({'iter_type':set, 'element_type':int}, ))
		exdesc.append(({'iter_type':tuple, 'element_type':int}, ))
		exdesc.append(({'iter_type':list, 'element_type':putil.check.Number()}, ))
		putil.test.evaluate_exception_series(exdesc, putil.check.ArbitraryLength)

	def test_includes(self):	#pylint: disable=R0201
		"""	Test that the includes method of ArbitraryLength class behaves appropriately """
		cmd1, cmd2, cmd3 = putil.check.ArbitraryLength(list, int).includes, putil.check.ArbitraryLength(list, putil.check.Number()).includes, putil.check.ArbitraryLength(list, {'a':putil.check.Number(), 'b':str}).includes
		cmd_pairs = [(cmd1, [1, 2], True), (cmd1, (1, 2), False), (cmd1, set([1.0, 2.0]), False), (cmd1, 1+2j, False), (cmd1, 'a', False), (cmd2, [1, 2.0, 3], True), (cmd2, [1, 2.0, None], False),\
			         (cmd3, 5, False), (cmd3, [3], False), (cmd3, [{'a':'b', 'b':'b'}], False), (cmd3, [{'a':5, 'b':'b'}], True), (cmd3, [{'a':5, 'b':'b'}, {'a':True, 'b':'b'}], False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_istype(self):	#pylint: disable=R0201
		"""	Test that the istype method of ArbitraryLength class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLength(tuple, int).istype, putil.check.ArbitraryLength(list, putil.check.PositiveReal()).istype
		cmd_pairs = [(cmd1, [1, 2], False), (cmd1, (1, 2), True), (cmd1, set([1.0, 2.0]), False), (cmd1, 1+2j, False), (cmd1, 'a', False), (cmd2, [1, 2], True), (cmd2, [1, -1], False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLength class behaves appropriately when inproper element in iterable is passed """
		evaluate_exception_method((putil.check.ArbitraryLength, {'iter_type':set, 'element_type':int}, TypeError, 'Argument `par1` is of the wrong type'))


###
# Test for ArbitraryLengthList class
###
class TestArbitraryLengthList(object):	#pylint: disable=W0232
	""" Tests for ArbitraryLengthList pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthList class behaves appropriately when all arguments are correctly specified """
		obj = putil.check.ArbitraryLengthList(int)
		assert (obj.element_type == int, obj.iter_type == list) == (True, True)

	def test_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthList class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_series((putil.check.ArbitraryLengthList, {'element_type':'a'}, TypeError, 'Argument `element_type` is of the wrong type'))

	def test_includes(self):	#pylint: disable=R0201,C0103
		"""	Test that the includes method of ArbitraryLengthList class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthList(int).includes, putil.check.ArbitraryLengthList(putil.check.NumberRange(0, 1)).includes
		cmd_pairs = [(cmd1, [1, 2], True), (cmd1, set([1, 2]), False), (cmd1, (1, 2), False), (cmd1, 'a', False), (cmd2, [0.5], True), (cmd2, [-0.01], False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_istype(self):	#pylint: disable=R0201,C0103
		"""	Test that the istype method of ArbitraryLengthList class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthList(int).istype, putil.check.ArbitraryLengthList(putil.check.NumberRange(0, 1)).istype
		cmd_pairs = [(cmd1, [1, 2], True), (cmd1, set([1, 2]), False), (cmd1, (1, 2), False), (cmd1, 'a', False), (cmd2, [0.5], True), (cmd2, [-0.01], True), (cmd2, 'a', False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthList class behaves appropriately when inproper element in list is passed """
		evaluate_exception_method((putil.check.ArbitraryLengthList, {'element_type':int}, TypeError, 'Argument `par1` is of the wrong type'))


###
# Test for ArbitraryLengthTuple class
###
class TestArbitraryLengthTuple(object):	#pylint: disable=W0232
	""" Tests for ArbitraryLengthTuple pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthTuple class behaves appropriately when all arguments are correctly specified	"""
		obj = putil.check.ArbitraryLengthTuple(int)
		assert (obj.element_type == int, obj.iter_type == tuple) == (True, True)

	def test_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthTuple class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_series((putil.check.ArbitraryLengthTuple, {'element_type':'a'}, TypeError, 'Argument `element_type` is of the wrong type'))

	def test_includes(self):	#pylint: disable=R0201,C0103
		"""	Test that the includes method of ArbitraryLengthTuple class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthTuple(float).includes, putil.check.ArbitraryLengthTuple(putil.check.NumberRange(0, 1)).includes
		cmd_pairs = [(cmd1, (1.0, 2.0), True), (cmd1, [1, 2], False), (cmd1, set([1, 2]), False), (cmd1, 'a', False), (cmd2, (0.5,), True), (cmd2, (-0.01,), False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_type(self):	#pylint: disable=R0201,C0103
		"""	Test that the istype method of ArbitraryLengthTuple class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthTuple(float).istype, putil.check.ArbitraryLengthTuple(putil.check.NumberRange(0, 1)).istype
		cmd_pairs = [(cmd1, (1.0, 2.0), True), (cmd1, [1, 2], False), (cmd1, set([1, 2]), False), (cmd1, 'a', False), (cmd2, (0.5,), True), (cmd2, (-0.01,), True), (cmd2, 'a', False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthTuple class behaves appropriately when inproper element in tuple is passed """
		evaluate_exception_method((putil.check.ArbitraryLengthTuple, {'element_type':str}, TypeError, 'Argument `par1` is of the wrong type'))


###
# Test for ArbitraryLengthSet class
###
class TestArbitraryLengthSet(object):	#pylint: disable=W0232
	""" Tests for ArbitraryLengthSet pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthSet class behaves appropriately when all arguments are correctly specified """
		obj = putil.check.ArbitraryLengthSet(int)
		assert (obj.element_type == int, obj.iter_type == set) == (True, True)

	def test_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthSet class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_series((putil.check.ArbitraryLengthSet, {'element_type':'a'}, TypeError, 'Argument `element_type` is of the wrong type'))

	def test_includes(self):	#pylint: disable=R0201,C0103
		""" Test that the includes method of ArbitraryLengthSet class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthSet(float).includes, putil.check.ArbitraryLengthSet(putil.check.NumberRange(0, 1)).includes
		cmd_pairs = [(cmd1, set([1.0, 2.0]), True), (cmd1, [1, 2], False), (cmd1, (1, 2), False), (cmd1, 'a', False), (cmd2, set([0.5]), True), (cmd2, set([-0.01]), False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_istype(self):	#pylint: disable=R0201,C0103
		""" Test that the istype method of ArbitraryLengthSet class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthSet(float).istype, putil.check.ArbitraryLengthSet(putil.check.NumberRange(0, 1)).istype
		cmd_pairs = [(cmd1, set([1.0, 2.0]), True), (cmd1, [1, 2], False), (cmd1, (1, 2), False), (cmd1, 'a', False), (cmd2, set([0.5]), True), (cmd2, set([-0.01]), True), (cmd2, set(['a']), False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthSet class behaves appropriately when inproper element in set is passed """
		evaluate_exception_method((putil.check.ArbitraryLengthSet, {'element_type':float}, TypeError, 'Argument `par1` is of the wrong type'))

###
# Test for ArbitraryLengthDict class
###
class TestArbitraryLengthDict(object):	#pylint: disable=W0232
	""" Tests for ArbitraryLengthDict pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthDict class behaves appropriately when all arguments are correctly specified """
		obj = putil.check.ArbitraryLengthDict(int)
		assert (obj.element_type == int, obj.iter_type == dict) == (True, True)

	def test_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthDict class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_series((putil.check.ArbitraryLengthDict, {'element_type':'a'}, TypeError, 'Argument `element_type` is of the wrong type'))

	def test_includes(self):	#pylint: disable=R0201,C0103
		"""	Test that the includes method of ArbitraryLengthDict class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthDict(int).includes, putil.check.ArbitraryLengthDict(putil.check.NumberRange(0, 1)).includes
		cmd_pairs = [(cmd1, {'a':1, 'b':2}, True), (cmd1, set([1, 2]), False), (cmd1, (1, 2), False), (cmd1, {'a':'a'}, False), (cmd2, {'c':0.5}, True), (cmd2, {'d':-0.01}, False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_istype(self):	#pylint: disable=R0201,C0103
		"""	Test that the istype method of ArbitraryLengthDict class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthDict(int).istype, putil.check.ArbitraryLengthDict(putil.check.NumberRange(0, 1)).istype
		cmd_pairs = [(cmd1, {'a':1, 'b':2}, True), (cmd1, set([1, 2]), False), (cmd1, (1, 2), False), (cmd1, {'a':'a'}, False), (cmd2, {'c':0.5}, True), (cmd2, {'d':-0.01}, True)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthDict class behaves appropriately when inproper element in list is passed """
		evaluate_exception_method((putil.check.ArbitraryLengthDict, {'element_type':int}, TypeError, 'Argument `par1` is of the wrong type'))


###
# Test for OneOf class
###
class TestOneOf(object):	#pylint: disable=W0232
	""" Tests for OneOf pseudo-type """

	def test_case_insensitive_exception(self):	#pylint: disable=R0201,C0103
		""" Tests that OneOf class behaves properly when an improper case_insensitive type is given """
		putil.test.evaluate_exception_series((putil.check.OneOf, {'choices':['a', 'b', 'c'], 'case_sensitive':3}, TypeError, 'Argument `case_sensitive` is of the wrong type'))

	def test_case_insensitive_none_if_no_strings_in_choices(self):	#pylint: disable=R0201,C0103
		""" Tests that OneOf class behaves properly when no string options given """
		assert (putil.check.OneOf([1, 2, 3], case_sensitive=True).case_sensitive == None, putil.check.OneOf([1, 2, 3], case_sensitive=False).case_sensitive == None) == (True, True)

	def test_infinite_iterable_exception(self):	#pylint: disable=R0201,C0103
		""" Tests that OneOf class behaves properly when an improper iterable is given """
		putil.test.evaluate_exception_series((putil.check.OneOf, {'choices':itertools.count(start=0, step=1)}, TypeError, 'Argument `choices` is of the wrong type'))

	def test_proper_no_errors(self):	#pylint: disable=R0201,C0103
		""" Tests that OneOf class behaves properly when all arguments are correctly specified """
		test_choices = ['a', 2, 3.0, 'a', putil.check.Real()]
		obj = putil.check.OneOf(test_choices, case_sensitive=True)
		assert (obj.types == [type(element) for element in test_choices], obj.choices == test_choices, obj.case_sensitive == True) == (True, True, True)

	def test_proper_contains_behavior(self):	#pylint: disable=R0201,C0103
		""" Tests that OneOf class behaves properly extracting type information """
		obj1, obj2 = putil.check.OneOf(['a', 'b', 3.0, 2], case_sensitive=True), putil.check.OneOf(['c', 'D', putil.check.IncreasingRealNumpyVector()], case_sensitive=False)
		obj3, obj4 = putil.check.OneOf(['e', 'F', putil.check.PositiveInteger()], case_sensitive=False), putil.check.OneOf(['g', 'H', putil.check.PositiveReal()], case_sensitive=False)
		putil.test.evaluate_contains_series([(obj1, 'a', True), (obj1, 'b', True), (obj1, 3.0, True), (obj1, 2, True), (obj1, [1, 2], False), (obj1, 3.1, False), (obj1, 'A', False), \
									         (obj2, 'C', True), (obj2, 'd', True), (obj2, 'e', False), (obj2, 'E', False), (obj2, numpy.array([1, 2, 3]), True), (obj2, numpy.array([1.0, 0.0, -1.0]), False), \
									         (obj3, -2, False), (obj3, 3, True), (obj4, -2.0, False), (obj4, 0.001, True)])

	def test_includes(self):	#pylint: disable=R0201,C0103
		""" Test that the includes method of OneOf class behaves appropriately """
		cmd1, cmd2 = putil.check.OneOf(['a', 'b', 3.0, 2], case_sensitive=True).includes, putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=False).includes
		cmd3, cmd4 = putil.check.OneOf(['e', 'F', putil.check.PositiveInteger()], case_sensitive=False).includes, putil.check.OneOf(['g', 'H', putil.check.PositiveReal()], case_sensitive=False).includes
		cmd_pairs = [(cmd1, 'a', True), (cmd1, 'b', True), (cmd1, 3.0, True), (cmd1, 2, True), (cmd1, putil.check.Number(), False), (cmd1, 'c', False), (cmd1, 'A', False), (cmd2, 'none', True), (cmd2, 'autos', False), \
			         (cmd3, -1, False), (cmd3, 1, True), (cmd4, -0.001, False), (cmd4, 0.001, True)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_istype(self):	#pylint: disable=R0201,C0103
		""" Test that the istype method of OneOf class behaves appropriately """
		cmd1 = putil.check.OneOf(['a', 'b', 3.0, 2], case_sensitive=True).istype
		cmd2 = putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=False).istype
		cmd3 = putil.check.OneOf(['e', 'F', putil.check.PositiveInteger()], case_sensitive=False).istype
		cmd4 = putil.check.OneOf(['g', 'H', putil.check.PositiveReal()], case_sensitive=False).istype
		cmd_pairs = [(cmd1, 'a', True), (cmd1, 'b', True), (cmd1, 3.0, True), (cmd1, 2, True), (cmd1, putil.check.Number(), False), (cmd1, 'c', True), (cmd1, 'A', True), (cmd2, 'none', True), (cmd2, 'autos', True), \
					 (cmd2, set([1, 2]), False), (cmd3, -1, False), (cmd3, 1, True), (cmd4, -0.001, False), (cmd4, 0.001, True)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):	#pylint: disable=R0201
		""" Tests that exception method of OneOf class behaves appropriately """
		exdesc = list()
		exdesc.append(({'choices':['a', 'b', 3.0, 2], 'case_sensitive':False}, ValueError, "Argument `par1` is not one of ['a', 'b', 3.0, 2] (case insensitive)"))
		exdesc.append(({'choices':['a', 'b', 3.0, 2], 'case_sensitive':True}, ValueError, "Argument `par1` is not one of ['a', 'b', 3.0, 2] (case sensitive)"))
		exdesc.append(({'choices':[3.0, 2], 'case_sensitive':True}, ValueError, "Argument `par1` is not one of [3.0, 2]"))
		exdesc.append(({'choices':['g', 'H', putil.check.PositiveReal()], 'case_sensitive':False}, ValueError, "Argument `par1` is not one of ['g', 'H', positive real number] (case insensitive)"))
		evaluate_exception_method(exdesc, putil.check.OneOf)


###
# Test for NumberRange class
###
class TestNumberRange(object):	#pylint: disable=W0232
	""" Tests for NumberRange pseudo-type """

	def test_minimum_not_a_number(self):	#pylint: disable=R0201,C0103
		""" Tests that NumberRange class behaves properly when minimum is not a number """
		putil.test.evaluate_exception_series((putil.check.NumberRange, {'minimum':False, 'maximum':None}, TypeError, 'Argument `minimum` is of the wrong type'))

	def test_maximum_not_a_number(self):	#pylint: disable=R0201,C0103
		""" Tests that NumberRange class behaves properly when maximum is not a number """
		putil.test.evaluate_exception_series((putil.check.NumberRange, {'minimum':None, 'maximum':True}, TypeError, 'Argument `maximum` is of the wrong type'))

	def test_minimum_and_maximum_not_specified(self):	#pylint: disable=R0201,C0103
		""" Tests that NumberRange class behaves properly when neither minimum nor maximum are specified """
		putil.test.evaluate_exception_series((putil.check.NumberRange, {'minimum':None, 'maximum':None}, TypeError, 'Either argument `minimum` or argument `maximum` needs to be specified'))

	def test_minimum_greater_than_maximum(self):	#pylint: disable=R0201,C0103
		""" Tests that NumberRange class behaves properly when minimum is greater than maximum """
		putil.test.evaluate_exception_series((putil.check.NumberRange, {'minimum':1.5, 'maximum':0.0}, ValueError, 'Argument `minimum` greater than argument `maximum`'))

	def test_no_errors(self):	#pylint: disable=R0201,C0103
		""" Tests that NumberRange class behaves properly when all arguments are correctly specified """
		obj = putil.check.NumberRange(minimum=10, maximum=20)
		assert (obj.minimum == 10, obj.maximum == 20) == (True, True)

	def test_includes(self):	#pylint: disable=R0201,C0103
		""" Test that the includes method of NumberRange class behaves appropriately """
		cmd1, cmd2, cmd3, cmd4 = putil.check.NumberRange(10, 15).includes, putil.check.NumberRange(100.0, 200.0).includes, putil.check.NumberRange(minimum=10).includes, putil.check.NumberRange(maximum=20).includes
		cmd_pairs = [(cmd1, 5, False), (cmd1, 10, True), (cmd1, 13, True), (cmd1, 15, True), (cmd1, 20, False), (cmd1, 13.0, True), (cmd2, 75.1, False), (cmd2, 100.0, True), (cmd2, 150.0, True), (cmd2, 200.0, True), \
			         (cmd2, 200.1, False), (cmd2, 200, True), (cmd3, 20, True), (cmd3, 5, False), (cmd4, 25, False), (cmd4, 5, True)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_istype(self):	#pylint: disable=R0201,C0103
		""" Test that the istype method of NumberRange class behaves appropriately """
		cmd1, cmd2 = putil.check.NumberRange(10, 15).istype, putil.check.NumberRange(100.0, 200.0).istype
		cmd_pairs = [(cmd1, 5, True), (cmd1, 10, True), (cmd1, 13, True), (cmd1, 15, True), (cmd1, 20, True), (cmd1, 13.0, True), (cmd2, 75.1, True), (cmd2, 100.0, True), (cmd2, 150.0, True), (cmd2, 200.0, True), \
			         (cmd2, 200.1, True), (cmd2, 200, True), (cmd2, 'a', False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):	#pylint: disable=R0201
		""" Tests that exception method of NumberRange class behaves appropriately """
		exdesc = list()
		exdesc.append(({'maximum':15}, ValueError, 'Argument `par1` is not in the range [-inf, 15.0]'))
		exdesc.append(({'minimum':20}, ValueError, 'Argument `par1` is not in the range [20.0, +inf]'))
		exdesc.append(({'minimum':3.5, 'maximum':4.75}, ValueError, 'Argument `par1` is not in the range [3.5, 4.75]'))
		evaluate_exception_method(exdesc, putil.check.NumberRange)

###
# Test RealNumpyVector class
###
class TestRealNumpyVector(object):	#pylint: disable=W0232
	""" Tests for RealNumpyVector pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		""" Test that RealNumpyVector class behaves appropriately when all arguments are correctly specified """
		putil.check.RealNumpyVector()

	def test_includes(self):	#pylint: disable=R0201,C0103
		""" Test that the includes method of RealNumpyVector class behaves appropriately """
		cmd_pairs = [('a', False), ([1, 2, 3], False), (numpy.array([]), False), (numpy.array([[1, 2, 3], [4, 5, 6]]), False), (numpy.array(['a', 'b']), False), (numpy.array([1, 2, 3]), True), \
			         (numpy.array([10.0, 8.0, 2.0]), True), (numpy.array([10.0]), True)]
		putil.test.evaluate_command_value_series(cmd_pairs, putil.check.RealNumpyVector().includes)

	def test_istype(self):	#pylint: disable=R0201,C0103
		""" Test that the istype method of RealNumpyVector class behaves appropriately """
		cmd_pairs = [('a', False), ([1, 2, 3], False), (numpy.array([]), False), (numpy.array([[1, 2, 3], [4, 5, 6]]), False), (numpy.array(['a', 'b']), False), (numpy.array([1, 2, 3]), True), \
			         (numpy.array([10.0, 8.0, 2.0]), True), (numpy.array([10.0]), True)]
		putil.test.evaluate_command_value_series(cmd_pairs, putil.check.RealNumpyVector().istype)

	def test_exception_method(self):    #pylint: disable=R0201,C0103
		""" Tests that exception method of RealNumpyVector class behaves appropriately """
		evaluate_exception_method((putil.check.RealNumpyVector, ValueError, 'Argument `par1` is not a Numpy vector of real numbers'))


###
# Test IncreasingRealNumpyVector class
###
class TestIncreasingRealNumpyVector(object):	#pylint: disable=W0232
	""" Tests for IncreasingRealNumpyVector pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		""" Test that IncreasingRealNumpyVector class behaves appropriately when all arguments are correctly specified """
		putil.check.IncreasingRealNumpyVector()

	def test_includes(self):	#pylint: disable=R0201,C0103
		""" Test that the includes method of IncreasingRealNumpyVector class behaves appropriately """
		cmd_pairs = [('a', False), ([1, 2, 3], False), (numpy.array([]), False), (numpy.array([[1, 2, 3], [4, 5, 6]]), False), (numpy.array(['a', 'b']), False), (numpy.array([1, 0, -3]), False), \
                     (numpy.array([10.0, 8.0, 2.0]), False), (numpy.array([1, 2, 3]), True), (numpy.array([10.0, 12.1, 12.5]), True), (numpy.array([10.0]), True)]
		putil.test.evaluate_command_value_series(cmd_pairs, putil.check.IncreasingRealNumpyVector().includes)

	def test_istype(self):	#pylint: disable=R0201,C0103
		""" Test that the istype method of IncreasingRealNumpyVector class behaves appropriately """
		cmd_pairs = [('a', False), ([1, 2, 3], False), (numpy.array([]), False), (numpy.array([[1, 2, 3], [4, 5, 6]]), False), (numpy.array(['a', 'b']), False), (numpy.array([1, 0, -3]), False), \
                     (numpy.array([10.0, 8.0, 2.0]), False), (numpy.array([1, 2, 3]), True), (numpy.array([10.0, 12.1, 12.5]), True), (numpy.array([10.0]), True)]
		putil.test.evaluate_command_value_series(cmd_pairs, putil.check.IncreasingRealNumpyVector().istype)

	def test_exception_method(self):    #pylint: disable=R0201,C0103
		""" Tests that exception method of RealNumpyVector class behaves appropriately """
		evaluate_exception_method((putil.check.IncreasingRealNumpyVector, ValueError, 'Argument `par1` is not a Numpy vector of increasing real numbers'))


###
# Test File class
###
class TestFile(object):	#pylint: disable=W0232
	""" Tests for File pseudo-type """

	def test_argument_wrong_type(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely when wrong type argument is given """
		putil.test.evaluate_exception_series((putil.check.File, {'check_existance':'a'}, TypeError, 'Argument `check_existance` is of the wrong type'))

	def test_includes(self):	#pylint: disable=R0201,C0103
		""" Test that the includes method of File class behaves appropriately """
		cmd1, cmd2 = putil.check.File().includes, putil.check.File(True).includes
		putil.test.evaluate_command_value_series([(cmd1, '/some/file.txt', True), (cmd2, 'not a file', False), (cmd2, './check_test.py', True)])

	def test_istype(self):	#pylint: disable=R0201,C0103
		""" Test that the istype method of File class behaves appropriately """
		cmd1, cmd2 = putil.check.File().istype, putil.check.File(True).istype
		putil.test.evaluate_command_value_series([(cmd1, 3, False), (cmd2, 'not a file', True), (cmd2, './check_test.py', True)])

	def test_exception_method(self):    #pylint: disable=R0201
		""" Tests that exception method of File class behaves appropriately """
		evaluate_exception_method((putil.check.File, IOError, 'File /some/path/file_name.ext could not be found'), par='/some/path/file_name.ext')

	def test_in_code(self):    #pylint: disable=R0201
		""" Test type checking in a real code scenario """
		@putil.check.check_argument(putil.check.File(check_existance=False))
		def set_file_name1(file_name):	#pylint: disable=C0111
			print file_name
		@putil.check.check_argument(putil.check.File(check_existance=True))
		def set_file_name2(file_name):	#pylint: disable=C0111
			print file_name
		exdesc = list()
		exdesc.append((set_file_name1, {'file_name':5}, TypeError, 'Argument `file_name` is of the wrong type'))
		exdesc.append((set_file_name2, {'file_name':5}, TypeError, 'Argument `file_name` is of the wrong type'))
		exdesc.append((set_file_name2, {'file_name':'file.csv'}, IOError, 'File file.csv could not be found'))
		exdesc.append((set_file_name1, {'file_name':'file.csv'}))
		exdesc.append((set_file_name2, {'file_name':'check_test.py'}))
		putil.test.evaluate_exception_series(exdesc)

###
# Test Function class
###
class TestFuntion(object):	#pylint: disable=W0232
	""" Tests for Funtion pseudo-type """

	def test_wrong_type(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely when wrong type argument is given """
		with pytest.raises(TypeError) as excinfo:
			putil.check.Function('a')
		assert excinfo.value.message == 'Argument `num_pars` is of the wrong type'

	def test_includes(self):	#pylint: disable=R0201,C0103
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

	def test_istype(self):	#pylint: disable=R0201,C0103
		""" Test that the istype method of Function class behaves appropriately """
		def foo1(par1, par2):	#pylint: disable=C0111
			return par1, par2
		assert (putil.check.Function().istype(3), putil.check.Function().istype(foo1), putil.check.Function(num_pars=3).istype(foo1), putil.check.Function(num_pars=2).istype(foo1)) == (False, True, True, True)

	def test_exception(self):    #pylint: disable=R0201
		""" Tests that exception method of Function class behaves appropriately """
		assert (putil.check.Function(num_pars=1).exception('par1') == {'type':ValueError, 'msg':'Argument `par1` is not a function with 1 argument'},
			putil.check.Function(num_pars=2).exception('par1') == {'type':ValueError, 'msg':'Argument `par1` is not a function with 2 arguments'}) == (True, True)


###
# Test PolymorphicType class
###
class TestPolymorphicType(object):	#pylint: disable=W0232
	""" Tests for PolymorphicType pseudo-type """

	def test_type_match_wrong_type(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely when wrong type argument is given """
		with pytest.raises(TypeError) as excinfo:
			putil.check.PolymorphicType('a')
		assert excinfo.value.message == 'Argument `types` is of the wrong type'

	def test_type_match_subtype_wrong_type(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely when wrong sub-type argument is given """
		with pytest.raises(TypeError) as excinfo:
			putil.check.PolymorphicType([str, int, 'a'])
		assert excinfo.value.message == 'Argument `types` element is of the wrong type'

	def test_type_match_no_errors(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely when all arguments are correctly specified """
		test_instances = [str, int, None, putil.check.ArbitraryLengthList, putil.check.ArbitraryLengthTuple, putil.check.ArbitraryLengthSet, putil.check.IncreasingRealNumpyVector, putil.check.RealNumpyVector, putil.check.OneOf,
			  putil.check.NumberRange, putil.check.Number, putil.check.Real, putil.check.File, putil.check.Function, putil.check.Any]
		obj = putil.check.PolymorphicType(test_instances)
		test_types = test_instances[:]
		test_types[2] = type(None)
		assert (obj.instances == test_instances, obj.types == test_types) == (True, True)

	def test_includes(self):	#pylint: disable=R0201,C0103
		""" Test that the includes method of PolymorphicType class behaves appropriately """
		test_instances = [int, None, putil.check.ArbitraryLengthList(int), putil.check.ArbitraryLengthTuple(float), putil.check.ArbitraryLengthSet(str), putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=True),
			  putil.check.NumberRange(1, 3), putil.check.Number(), putil.check.Real(), putil.check.RealNumpyVector()]
		ref_obj1 = putil.check.PolymorphicType(test_instances)
		ref_obj2 = putil.check.PolymorphicType([float, putil.check.IncreasingRealNumpyVector()])
		ref_obj3 = putil.check.PolymorphicType([putil.check.File(check_existance=False), putil.check.Function(num_pars=2)])
		ref_obj4 = putil.check.PolymorphicType([None, putil.check.PositiveInteger()])
		ref_obj5 = putil.check.PolymorphicType([None, putil.check.PositiveReal()])
		ref_obj6 = putil.check.PolymorphicType([None, putil.check.PositiveReal(), putil.check.Any()])
		def foo1(par1, par2, par3):	#pylint: disable=C0111
			return par1, par2, par3
		def foo2(par1, par2):	#pylint: disable=C0111
			return par1, par2
		assert (ref_obj1.includes(5), ref_obj1.includes(None), ref_obj1.includes([1, 2, 3]), ref_obj1.includes((2.0, 3.0)), ref_obj1.includes(set(['a', 'b', 'c'])), ref_obj1.includes('MANUAL'), ref_obj1.includes(2),
			 ref_obj1.includes(100.0), ref_obj1.includes(10+20j), ref_obj1.includes(numpy.array([10, 0.0, 30])), ref_obj1.includes('hello world'), ref_obj1.includes([1.0, 2.0, 3.0]), ref_obj1.includes('auto'),
			 ref_obj1.includes(numpy.array([])), ref_obj1.includes(numpy.array(['a', 'b', 'c'])), ref_obj2.includes(1), ref_obj2.includes(set([1, 2])), ref_obj2.includes(numpy.array([1, 0, -1])),
			 ref_obj2.includes(numpy.array([10.0, 20.0, 30.0])), ref_obj2.includes(5.0), ref_obj3.includes(3), ref_obj3.includes('/some/file'), ref_obj3.includes(foo1), ref_obj3.includes(foo2), ref_obj4.includes(-1),
			 ref_obj4.includes(1), ref_obj5.includes(-0.001), ref_obj5.includes(0.001), ref_obj6.includes(None), ref_obj6.includes(2.0), ref_obj6.includes('a')) == \
			 (True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False, True, True, False, True, False, True, False, True, False, True, True, True, True)

	def test_istype(self):	#pylint: disable=R0201,C0103
		""" Test that the istype method of PolymorphicType class behaves appropriately """
		test_instances = [int, None, putil.check.ArbitraryLengthList(int), putil.check.ArbitraryLengthTuple(float), putil.check.ArbitraryLengthSet(str), putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=True),
			  putil.check.NumberRange(1, 3), putil.check.Number(), putil.check.Real(), putil.check.RealNumpyVector()]
		ref_obj1 = putil.check.PolymorphicType(test_instances)
		ref_obj2 = putil.check.PolymorphicType([float, putil.check.IncreasingRealNumpyVector()])
		ref_obj3 = putil.check.PolymorphicType([putil.check.File(check_existance=False), putil.check.Function(num_pars=2)])
		ref_obj4 = putil.check.PolymorphicType([None, putil.check.PositiveInteger()])
		ref_obj5 = putil.check.PolymorphicType([None, putil.check.PositiveReal()])
		ref_obj6 = putil.check.PolymorphicType([None, putil.check.PositiveReal(), putil.check.Any()])
		ref_obj7 = putil.check.PolymorphicType([None, {'a':int, 'b':str}])
		def foo1(par1, par2, par3):	#pylint: disable=C0111
			return par1, par2, par3
		assert (ref_obj1.istype(5), ref_obj1.istype(None), ref_obj1.istype([1, 2, 3]), ref_obj1.istype((2.0, 3.0)), ref_obj1.istype(set(['a', 'b', 'c'])), ref_obj1.istype('MANUAL'), ref_obj1.istype(2),
			 ref_obj1.istype(100.0), ref_obj1.istype(10+20j), ref_obj1.istype(numpy.array([10, 0.0, 30])), ref_obj1.istype('hello world'), ref_obj1.istype([1.0, 2.0, 3.0]), ref_obj1.istype('auto'),
			 ref_obj1.istype(numpy.array([])), ref_obj1.istype(numpy.array(['a', 'b', 'c'])), ref_obj2.istype(1), ref_obj2.istype(set([1, 2])), ref_obj2.istype(numpy.array([1, 0, -1])),
			 ref_obj2.istype(numpy.array([10.0, 20.0, 30.0])), ref_obj2.istype(5.0), ref_obj3.istype(3), ref_obj3.istype('/some/file'), ref_obj3.istype(foo1), ref_obj4.istype(-1),
			 ref_obj4.istype(1), ref_obj5.istype(-0.001), ref_obj5.istype(0.001), ref_obj6.istype(None), ref_obj6.istype(2.0), ref_obj6.istype('a'),
			 ref_obj7.istype(None), ref_obj7.istype({'c':5}), ref_obj7.istype({'a':5}), ref_obj7.istype({'a':5, 'b':'Hello'})) == \
			 (True, True, True, True, True, True, True, True, True, True, True, False, True, False, False, False, False, False, True, True, False, True, True, False, True, False, True, True, True, True, True, False, False, True)

	def test_exception_method(self):    #pylint: disable=R0201
		""" Tests that exception method of PolymorphicType class behaves appropriately """
		test_list = list()
		obj1 = putil.check.PolymorphicType([putil.check.OneOf(['NONE', 'MANUAL', 'AUTO']), putil.check.NumberRange(minimum=15, maximum=20)])
		obj2 = putil.check.PolymorphicType([putil.check.OneOf(['NONE', 'MANUAL', 'AUTO']), putil.check.File(True)])
		obj3 = putil.check.PolymorphicType([putil.check.File(True), putil.check.Function(num_pars=2)])
		obj4 = putil.check.PolymorphicType([None, putil.check.PositiveInteger(), putil.check.NumberRange(minimum=15, maximum=20)])
		obj5 = putil.check.PolymorphicType([None, putil.check.PositiveReal(), putil.check.Any()])
		test_list.append(obj1.exception(param_name='par1', test_obj=5) == {'type':ValueError, 'msg':'Argument `par1` is not in the range [15.0, 20.0]'})
		test_list.append(obj2.exception(param_name='par1', param='_not_valid_', test_obj='not_a_file') == \
					{'type':RuntimeError, 'msg':"(ValueError) Argument `par1` is not one of ['NONE', 'MANUAL', 'AUTO'] (case insensitive)\n(IOError) File *[file_name]* could not be found", \
					'edata': {'field': 'file_name', 'value': '_not_valid_'}})
		test_list.append(obj3.exception(param_name='par1', param='_not_valid_', test_obj=32) == {'type':None, 'msg':''})
		test_list.append(obj4.exception(param_name='par1', test_obj=-1) == {'type':ValueError, 'msg':'Argument `par1` is not in the range [15.0, 20.0]'})
		test_list.append(obj5.exception(param_name='par1', test_obj=-1) == {'type':None, 'msg':''})
		assert test_list == len(test_list)*[True]


##
# Tests for get_function_args()
###
class TestGetFunctionArgs(object):	#pylint: disable=W0232
	""" Tests for get_function_args function """

	def test_all_positional_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when all arguments are positional arguments """
		def func(ppar1, ppar2, ppar3):	#pylint: disable=C0111,W0613
			pass
		assert putil.check.get_function_args(func) == ('ppar1', 'ppar2', 'ppar3')

	def test_all_keyword_arguments(self):	#pylint: disable=R0201,C0103,W0613
		""" Test that function behaves properly when all arguments are keywords arguments """
		def func(kpar1=1, kpar2=2, kpar3=3):	#pylint: disable=C0111,R0913,W0613
			pass
		assert putil.check.get_function_args(func) == ('kpar1', 'kpar2', 'kpar3')

	def test_positional_and_keyword_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when arguments are a mix of positional and keywords arguments """
		def func(ppar1, ppar2, ppar3, kpar1=1, kpar2=2, kpar3=3):	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert putil.check.get_function_args(func) == ('ppar1', 'ppar2', 'ppar3', 'kpar1', 'kpar2', 'kpar3')

	def test_no_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when there are no arguments passed """
		def func():	#pylint: disable=C0111,R0913,W0613
			pass
		assert putil.check.get_function_args(func) == ()


###
# Tests for create_argument_dictionary()
###
def ret_func(par):
	""" Returns the passed argument """
	return par

def decfunc(func):
	"""" Decorator function to test create_argument_dictionary function """
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		"""
		Wrapper function that creates the argument dictionary and returns a ret_func, which in turn just returns the argument passed. This is for testing only, obviously
		in an actual environment the dedcorator would return the original (called) function with the passed arguments
		"""
		return ret_func(putil.check.create_argument_dictionary(func, *args, **kwargs))
	return wrapper

class TestCreateArgumentDictionary(object):	#pylint: disable=W0232
	""" Tests for create_argument_dictionary function """

	def test_all_positional_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when all arguments are positional arguments """
		@decfunc
		def orig_func_all_positional_arguments(ppar1, ppar2, ppar3):	#pylint: disable=C0103,C0111,W0613
			pass
		assert orig_func_all_positional_arguments(1, 2, 3) == {'ppar1':1, 'ppar2':2, 'ppar3':3}

	def test_all_keyword_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when all arguments are keyword arguments """
		@decfunc
		def orig_func_all_keyword_arguments(kpar1, kpar2, kpar3):	#pylint: disable=C0103,C0111,W0613
			pass
		assert orig_func_all_keyword_arguments(kpar3=3, kpar2=2, kpar1=1) == {'kpar1':1, 'kpar2':2, 'kpar3':3}

	def test_positional_and_keyword_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when arguments are a mix of positional and keywords arguments """
		@decfunc
		def orig_func_positional_and_keyword_arguments(ppar1, ppar2, ppar3, kpar1=1, kpar2=2, kpar3=3):	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert orig_func_positional_and_keyword_arguments(10, 20, 30, kpar2=1.5, kpar3='x', kpar1=[1, 2]) == {'ppar1':10, 'ppar2':20, 'ppar3':30, 'kpar1':[1, 2], 'kpar2':1.5, 'kpar3':'x'}

	def test_no_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when there are no arguments passed """
		@decfunc
		def orig_func_no_arguments():	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert orig_func_no_arguments() == {}

	def test_more_positional_arguments_passed_than_defined(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when there are more arguments passed by position than in the function definition """
		@decfunc
		def orig_func(ppar1):	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert orig_func(1, 2, 3) == {}	#pylint: disable=E1121

	def test_more_keyword_arguments_passed_than_defined(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when there are more arguments passed by keyword than in the function definition """
		@decfunc
		def orig_func(kpar1=0, kpar2=2):	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert orig_func(kpar1=1, kpar2=2, kpar3=3) == {}	#pylint: disable=E1123

	def test_argument_passed_by_position_and_keyword(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when there are arguments passed both by position and keyword """
		@decfunc
		def orig_func(ppar1, ppar2, kpar1=1, kpar2=2):	#pylint: disable=C0103,C0111,R0913,W0613
			pass
		assert orig_func(1, 2, ppar1=5) == {}	#pylint: disable=E1124


###
# Tests for is_type_def()
###
class TestIsTypeDef(object):	#pylint: disable=W0232,R0903
	""" Tests for is_type_def function """
	def test_is_type_def_works(self):	#pylint: disable=R0201
		""" Test that is_type_def works as expected """
		test_list = list()
		test_list.append(putil.check.is_type_def('a') == False)
		test_list.append(putil.check.is_type_def(str) == True)
		test_list.append(putil.check.is_type_def(5) == False)
		test_list.append(putil.check.is_type_def(putil.check.PolymorphicType([str, int])) == True)
		test_list.append(putil.check.is_type_def([str, dict, list]) == False)
		test_list.append(putil.check.is_type_def(itertools.count(start=0, step=1)) == False)
		test_list.append(putil.check.is_type_def({'a':str, 'b':int}) == True)
		test_list.append(putil.check.is_type_def({'a':str, 'b':[str, str]}) == False)
		test_list.append(putil.check.is_type_def({'a':str, 'b':{'c':putil.check.Number(), 'd':float}}) == True)
		assert test_list == len(test_list)*[True]

###
# Tests for type_match()
###
class TestTypeMatch(object):	#pylint: disable=W0232
	""" Tests for type_match function """

	def test_str(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for string type """
		assert (putil.check.type_match('hello', str), putil.check.type_match(135, str)) == (True, False)

	def test_float(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for float type """
		assert (putil.check.type_match(1.5, float), putil.check.type_match(135, float)) == (True, False)

	def test_int(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for integer type """
		assert (putil.check.type_match(8, int), putil.check.type_match(135.0, int)) == (True, False)

	def test_number(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for Number pseudo-type (integer, real or complex) """
		assert (putil.check.type_match(1, putil.check.Number()), putil.check.type_match(135.0, putil.check.Number()), putil.check.type_match(1+1j, putil.check.Number()), putil.check.type_match('hello', putil.check.Number())) == \
			(True, True, True, False)

	def test_real(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for Real pseudo-type (integer or real) """
		assert (putil.check.type_match(1, putil.check.Real()), putil.check.type_match(135.0, putil.check.Real()), putil.check.type_match(1+1j, putil.check.Real())) == (True, True, False)

	def test_boolean(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for boolean type """
		assert (putil.check.type_match(True, bool), putil.check.type_match(12.5, bool)) == (True, False)

	def test_decimal(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for Decimal type """
		assert (putil.check.type_match(decimal.Decimal(1.25), decimal.Decimal), putil.check.type_match(12.5, decimal.Decimal)) == (True, False)

	def test_fraction(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for Fraction type """
		assert (putil.check.type_match(fractions.Fraction(4, 6), fractions.Fraction), putil.check.type_match(12.5, fractions.Fraction)) == (True, False)

	def test_arbitrary_length_list(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for ArbitraryLengthList pseudo-type """
		assert (putil.check.type_match([1, 2, 3], putil.check.ArbitraryLengthList(int)), putil.check.type_match('hello', putil.check.ArbitraryLengthList(int))) == (True, False)

	def test_arbitrary_length_tuple(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for ArbitraryLengthTuple pseudo-type """
		assert (putil.check.type_match((1, 2, 3), putil.check.ArbitraryLengthTuple(int)), putil.check.type_match((1, 2, 'a'), putil.check.ArbitraryLengthTuple(int))) == (True, False)

	def test_arbitrary_length_set(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for ArbitraryLengthSet pseudo-type """
		assert (putil.check.type_match(set([1, 2, 3]), putil.check.ArbitraryLengthSet(int)), putil.check.type_match(set([1, 2, 'a']), putil.check.ArbitraryLengthSet(int))) == (True, False)

	def test_fixed_length_list(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for fixed-length list type """
		assert (putil.check.type_match([1, 'a', 3.0], [int, str, float]), putil.check.type_match([1, 'a', 3.0, 4.0], [int, str, float]), putil.check.type_match([1, 'a', 3.0], [int, str, float, int]),
			 putil.check.type_match([1, 2, 3.0], [int, str, float])) == (True, False, False, False)

	def test_fixed_length_tuple(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for fixed-length tuple type """
		assert (putil.check.type_match((1, 'a', 3.0), (int, str, float)), putil.check.type_match((1, 'a', 3.0, 4.0), (int, str, float)), putil.check.type_match((1, 'a', 3.0), (int, str, float, int)),
			 putil.check.type_match((1, 2, 3.0), (int, str, float))) == (True, False, False, False)

	def test_fixed_length_set(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for fixed-length set type """
		with pytest.raises(RuntimeError) as excinfo:
			putil.check.type_match(set([1, 'a', 3.0]), set([int, str, float]))
		assert excinfo.value.message == 'Set is an un-ordered iterable, thus it cannot be type-checked against an ordered reference'

	def test_one_of(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for OneOf pseudo-type """
		assert (putil.check.type_match('HELLO', putil.check.OneOf(['HELLO', 45, 'WORLD'])), putil.check.type_match(45, putil.check.OneOf(['HELLO', 45, 'WORLD'])),
			 putil.check.type_match(1.0, putil.check.OneOf(['HELLO', 45, 'WORLD']))) == (True, True, False)

	def test_number_range(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for NumberRange pseudo-type """
		assert (putil.check.type_match(12, putil.check.NumberRange(minimum=2, maximum=5)), putil.check.type_match('a', putil.check.NumberRange(minimum=2, maximum=5))) == (True, False)

	def test_dict(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for dictionary type """
		assert (putil.check.type_match({'a':'hello', 'b':12.5, 'c':[1]}, {'a':str, 'b':float, 'c':[int]}),	# 'Regular' match
			 putil.check.type_match({'a':'hello', 'c':[1]}, {'a':str, 'b':float, 'c':[int]}),	# One key-value pair missing in test object, useful where argument is omitted to get default
			 putil.check.type_match({'x':'hello', 'y':{'n':[1.5, 2.3]}, 'z':[1]}, {'x':str, 'y':{'n':putil.check.ArbitraryLengthList(float), 'm':str}, 'z':[int]}), # Nested
			 putil.check.type_match({'a':'hello', 'b':35, 'c':[1]}, {'a':str, 'b':float, 'c':[int]}),	# Value of one key in test object does not match
			 putil.check.type_match({'a':'hello', 'd':12.5, 'c':[1]}, {'a':str, 'b':float, 'c':[int]})) == (True, True, True, False, False)	# One key in test object does not appear in reference object

	def test_polymorphic_type(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for PolymorphicType pseudo-type """
		assert (putil.check.type_match('HELLO', putil.check.PolymorphicType([str, int])), putil.check.type_match(45, putil.check.PolymorphicType([str, int])), putil.check.type_match(1.5, putil.check.PolymorphicType([str, int]))) \
			== (True, True, False)

	def test_real_numpy_vector(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for RealNumpyVector pseudo-type """
		assert (putil.check.type_match(12, putil.check.RealNumpyVector()), putil.check.type_match(numpy.array([1, 2, 0]), putil.check.RealNumpyVector()),
			 putil.check.type_match(numpy.array([[1, 2, 0], [1, 1, 2]]), putil.check.RealNumpyVector())) == (False, True, False)

	def test_increasing_real_numpy_vector(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for IncreasingRealNumpyVector pseudo-type """
		assert (putil.check.type_match(12, putil.check.IncreasingRealNumpyVector()), putil.check.type_match(numpy.array([1, 2, 3]), putil.check.IncreasingRealNumpyVector()),
			 putil.check.type_match(numpy.array([True, False, True]), putil.check.IncreasingRealNumpyVector()),
			 putil.check.type_match(numpy.array([[1, 2, 3], [4, 5, 6]]), putil.check.IncreasingRealNumpyVector())) == (False, True, False, False)


###
# Tests for check_type()
###
class TestCheckType(object):	#pylint: disable=W0232
	""" Tests for check_type function """

	def test_simple_exception(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a sigle (wrong) type is given (string, number, etc.) """
		@putil.check.check_argument_type('ppar1', int)
		def func_check_type(ppar1):	#pylint: disable=C0111
			print ppar1
		putil.test.evaluate_exception_series((func_check_type, {'ppar1':'Hello world'}, TypeError, 'Argument `ppar1` is of the wrong type'))

	def test_simple_no_exception(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a sigle (right) type is given (string, number, etc.) """
		@putil.check.check_argument_type(param_name='ppar1', param_type=putil.check.Number())
		def func_check_type(ppar1):	#pylint: disable=C0111
			return ppar1
		assert func_check_type(5.0) == 5.0

	def test_argument_not_specified(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when the argument to be checked is not specified in the function call """
		@putil.check.check_argument_type(param_name='ppar2', param_type=putil.check.Number())
		def func_check_type(ppar1, ppar2=35, ppar3=5):	#pylint: disable=C0111
			return ppar1, ppar2, ppar3
		assert func_check_type(3, ppar3=12) == (3, 35, 12)

	def test_argument_specified_by_position_and_keyword(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is specified both by position and keyword """
		@putil.check.check_argument_type(param_name='ppar2', param_type=putil.check.Number())
		def func_check_type(ppar1, ppar2=35, ppar3=5):	#pylint: disable=C0111
			print ppar1, ppar2, ppar3
		with pytest.raises(TypeError) as excinfo:
			func_check_type(3, ppar3=12, ppar1=12)	#pylint: disable=E1124
		assert excinfo.value.message == "func_check_type() got multiple values for keyword argument 'ppar1'"

	def test_argument_repeated_keyword_arguments(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is specified multiple times by keyword """
		@putil.check.check_argument_type(param_name='ppar2', param_type=putil.check.Number())
		def func_check_type(ppar1, ppar2=None, ppar3=5):	#pylint: disable=C0111
			print ppar1, ppar2, ppar3
		with pytest.raises(TypeError) as excinfo:
			func_check_type(3, ppar3=12, **{'ppar3':12})	#pylint: disable=W0142
		assert excinfo.value.message == "func_check_type() got multiple values for keyword argument 'ppar3'"


###
# Tests for check_argument()
###
class TestCheckArgument(object):	#pylint: disable=W0232
	""" Tests for check_argument function """

	def test_function_with_no_argument(self): #pylint: disable=R0201,C0103
		""" Test that function behaves properly when a function has no arguments """
		@putil.check.check_argument(int)
		def func_check_type():	#pylint: disable=C0111
			pass
		class DummyClass(object): #pylint: disable=C0111,R0903
			def __init__(self):
				pass
			@putil.check.check_argument(str)
			def class_func_check_type(self):	#pylint: disable=C0111
				pass
		obj = DummyClass()
		exdesc = list()
		exdesc.append((func_check_type, None, RuntimeError, 'Function func_check_type has no arguments'))
		exdesc.append((obj.class_func_check_type, None, RuntimeError, 'Function class_func_check_type has no arguments after self'))
		putil.test.evaluate_exception_series(exdesc)

	def test_wrong_type(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a sigle (wrong) type is given (string, number, etc.) """
		@putil.check.check_argument(int)
		def func_check_type(ppar1):	#pylint: disable=C0111
			print ppar1
		putil.test.evaluate_exception_series((func_check_type, {'ppar1':'Hello world'}, TypeError, 'Argument `ppar1` is of the wrong type'))

	def test_one_of_error_case_insensitive(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is outside fixed number of string choices list with case sensitivity """
		@putil.check.check_argument(putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=False))
		def func_check_type(ppar1):	#pylint: disable=C0111
			print ppar1
		putil.test.evaluate_exception_series((func_check_type, {'ppar1':'Hello world'}, ValueError, "Argument `ppar1` is not one of ['NONE', 'MANUAL', 'AUTO'] (case insensitive)"))

	def test_one_of_error_case_sensitive(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is outside fixed number of string choices list with case insensitivity """
		@putil.check.check_argument(putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=True))
		def func_check_type(ppar1):	#pylint: disable=C0111
			print ppar1
		putil.test.evaluate_exception_series((func_check_type, {'ppar1':'none'}, ValueError, "Argument `ppar1` is not one of ['NONE', 'MANUAL', 'AUTO'] (case sensitive)"))

	def test_one_of_error_no_case_sensitivity(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is outside fixed number of choices list """
		@putil.check.check_argument(putil.check.OneOf(range(3), case_sensitive=True))
		def func_check_type(ppar1):	#pylint: disable=C0111
			print ppar1
		putil.test.evaluate_exception_series((func_check_type, {'ppar1':10}, ValueError, 'Argument `ppar1` is not one of [0, 1, 2]'))

	def test_one_of_no_error(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is one of a fixed number of choices list """
		@putil.check.check_argument(putil.check.OneOf(range(3), case_sensitive=True))
		def func_check_type(ppar1):	#pylint: disable=C0111
			return ppar1
		assert func_check_type(2) == 2

	def test_range_no_maximum_out_of_range(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is out of range when no maximum is defined """
		@putil.check.check_argument(putil.check.NumberRange(minimum=10))
		def func_check_type(ppar1):	#pylint: disable=C0111
			print ppar1
		putil.test.evaluate_exception_series((func_check_type, {'ppar1':1}, ValueError, 'Argument `ppar1` is not in the range [10.0, +inf]'))

	def test_range_no_maximum_in_range(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is in range when no maximum is defined """
		@putil.check.check_argument(putil.check.NumberRange(minimum=10))
		def func_check_type(ppar1):	#pylint: disable=C0111
			return ppar1
		assert func_check_type(20) == 20

	def test_range_no_minimum_out_of_range(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is out of range when no minimum is defined """
		@putil.check.check_argument(putil.check.NumberRange(maximum=10))
		def func_check_type(ppar1):	#pylint: disable=C0111
			print ppar1
		putil.test.evaluate_exception_series((func_check_type, {'ppar1':20}, ValueError, 'Argument `ppar1` is not in the range [-inf, 10.0]'))

	def test_range_no_minimum_in_range(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is in range when no minimum is defined """
		@putil.check.check_argument(putil.check.NumberRange(maximum=10))
		def func_check_type(ppar1):	#pylint: disable=C0111
			return ppar1
		assert func_check_type(5) == 5

	def test_range_minimum_and_maximum_specified_out_of_range(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is out of range when no minimum is defined """
		@putil.check.check_argument(putil.check.NumberRange(minimum=5.0, maximum=10.0))
		def func_check_type(ppar1):	#pylint: disable=C0111
			print ppar1
		putil.test.evaluate_exception_series((func_check_type, {'ppar1':3.1}, ValueError, 'Argument `ppar1` is not in the range [5.0, 10.0]'))

	def test_range_minimum_and_maximum_specified_in_range(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is in range when no minimum is defined """
		@putil.check.check_argument(putil.check.NumberRange(minimum=100, maximum=200))
		def func_check_type(ppar1):	#pylint: disable=C0111
			return ppar1
		assert func_check_type(150) == 150

	def test_polymorphic_type_error(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is not in the polymorphic types allowed """
		@putil.check.check_argument(putil.check.PolymorphicType([None, float]))
		def func_check_type1(ppar1):	#pylint: disable=C0111
			print ppar1
		@putil.check.check_argument(putil.check.PolymorphicType([None, putil.check.NumberRange(minimum=5, maximum=10), putil.check.OneOf(['HELLO', 'WORLD'])]))
		def func_check_type2(ppar1):	#pylint: disable=C0111
			print ppar1
		@putil.check.check_argument(putil.check.PolymorphicType([None, putil.check.NumberRange(minimum=5, maximum=10), putil.check.NumberRange(minimum=20, maximum=30)]))
		def func_check_type3(ppar1):	#pylint: disable=C0111
			print ppar1
		exdesc = list()
		exdesc.append((func_check_type1, {'ppar1':'a'}, TypeError, 'Argument `ppar1` is of the wrong type'))
		exdesc.append((func_check_type2, {'ppar1':2}, ValueError, 'Argument `ppar1` is not in the range [5.0, 10.0]'))
		exdesc.append((func_check_type2, {'ppar1':'teto'}, ValueError, "Argument `ppar1` is not one of ['HELLO', 'WORLD'] (case insensitive)"))
		exdesc.append((func_check_type3, {'ppar1':2}, ValueError, 'Argument `ppar1` is not in the range [5.0, 10.0]\nArgument `ppar1` is not in the range [20.0, 30.0]'))
		putil.test.evaluate_exception_series(exdesc)

	def test_polymorphic_type_no_error(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is in the polymorphic types allowed """
		@putil.check.check_argument(putil.check.PolymorphicType([None, int, putil.check.NumberRange(minimum=5.0, maximum=10.0), putil.check.OneOf(['HELLO', 'WORLD'])]))
		def func_check_type1(ppar1):	#pylint: disable=C0111
			return ppar1
		# Test definitions consisting entireley of buil-in (i.e. non-pseudo-type) types
		@putil.check.check_argument(putil.check.PolymorphicType([None, int, dict]))
		def func_check_type2(ppar1):	#pylint: disable=C0111
			return ppar1
		@putil.check.check_argument(putil.check.PolymorphicType([None, putil.check.NumberRange(minimum=5, maximum=10), putil.check.OneOf(['HELLO', 'WORLD']), putil.check.Any()]))
		def func_check_type3(ppar1):	#pylint: disable=C0111
			return ppar1
		assert (func_check_type1(None), func_check_type1(6), func_check_type1(7.0), func_check_type1('WORLD'), func_check_type2(None), func_check_type2(8), func_check_type2({'a':'b'}), func_check_type3(True)) == \
			(None, 6, 7.0, 'WORLD', None, 8, {'a':'b'}, True)

	def test_numpy_vector_wrong_type(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is not a Numpy vector """
		@putil.check.check_argument(putil.check.RealNumpyVector())
		def func_check_type(ppar1):	#pylint: disable=C0111
			print ppar1
		putil.test.evaluate_exception_series((func_check_type, {'ppar1':numpy.array([False])}, TypeError, 'Argument `ppar1` is of the wrong type'))

	def test_numpy_vector_no_error(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is proper Numpy vector """
		@putil.check.check_argument(putil.check.RealNumpyVector())
		def func_check_type(ppar1):	#pylint: disable=C0111
			return ppar1
		func_check_type(numpy.array([1.0, 2.0, 1.0-1e-10]))

	def test_increasing_numpy_vector_wrong_type(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is not a Numpy vector """
		@putil.check.check_argument(putil.check.IncreasingRealNumpyVector())
		def func_check_type(ppar1):	#pylint: disable=C0111
			print ppar1
		exdesc = list()
		exdesc.append(({'ppar1':numpy.array([False])}, TypeError, 'Argument `ppar1` is of the wrong type'))
		exdesc.append(({'ppar1':numpy.array([1.0, 2.0, 1.0-1e-10])}, TypeError, 'Argument `ppar1` is of the wrong type'))
		putil.test.evaluate_exception_series(exdesc, func_check_type)

	def test_incresing_numpy_vector_no_error(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is properly incresing Numpy vector """
		@putil.check.check_argument(putil.check.IncreasingRealNumpyVector())
		def func_check_type(ppar1):	#pylint: disable=C0111
			return ppar1
		func_check_type(numpy.array([1, 2, 3]))

	def test_dict(self):	#pylint: disable=R0201,C0103
		""" Test that function behaves properly when a argument is a dictionary """
		@putil.check.check_argument({'a':str, 'b':putil.check.Number()})
		def func_check_type(ppar1):	#pylint: disable=C0111
			return ppar1
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			func_check_type({'x':'hello', 'b':45})
		test_list.append(excinfo.value.message == 'Argument `ppar1` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			func_check_type({'a':'hello', 'b':45, 'c':60})
		test_list.append(excinfo.value.message == 'Argument `ppar1` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			func_check_type({'a':'hello', 'b':True})
		test_list.append(excinfo.value.message == 'Argument `ppar1` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			func_check_type({'a':'hello'})
		test_list.append(excinfo.value.message == 'Argument `ppar1` is of the wrong type')
		# This statement should not raise any exception
		func_check_type({'a':'hello', 'b':45})
		assert test_list == len(test_list)*[True]


###
# Tests for check_arguments()
###
class TestCheckArguments(object):	#pylint: disable=W0232,R0903
	""" Tests for check_arguments function """

	def test_function_with_no_argument(self): #pylint: disable=R0201,C0103
		""" Test that function behaves properly when a function has no arguments """
		@putil.check.check_arguments({'par1':int})
		def func_check_type():	#pylint: disable=C0111
			pass
		class DummyClass(object): #pylint: disable=C0111,R0903
			def __init__(self):
				pass
			@putil.check.check_arguments({'par1':str})
			def class_func_check_type(self):	#pylint: disable=C0111
				pass
		test_list = list()
		with pytest.raises(RuntimeError) as excinfo:
			func_check_type()
		test_list.append(excinfo.value.message == 'Function func_check_type has no arguments')
		obj = DummyClass()
		with pytest.raises(RuntimeError) as excinfo:
			obj.class_func_check_type()
		test_list.append(excinfo.value.message == 'Function class_func_check_type has no arguments after self')
		assert test_list == 2*[True]

	def test_argument_not_declared(self): #pylint: disable=R0201
		""" Test that function behaves correctly when the function to check does not have an argument in the validation list """
		@putil.check.check_arguments({'par1':int})
		def func_check_type(par0, par2):	#pylint: disable=C0111,W0613
			pass
		with pytest.raises(RuntimeError) as excinfo:
			func_check_type(1, 2)
		assert excinfo.value.message == 'Argument par1 is not an argument of function func_check_type'

	def test_wrong_type(self): #pylint: disable=R0201
		""" Test that function behaves correctly one of man parameters is of the wrong type """
		@putil.check.check_arguments({'par1':int, 'par2':str})
		def func_check_type1(par1, par2, par3):	#pylint: disable=C0111,W0613
			pass
		@putil.check.check_arguments({'par1':int, 'par2':str, 'par3':{'subpar1':float, 'subpar2':str}})
		def func_check_type2(par1, par2, par3):	#pylint: disable=C0111,W0613
			pass
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			func_check_type1(1, 2, 3)
		test_list.append(excinfo.value.message == 'Argument `par2` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			func_check_type2(1, 'hello', {'subpar1':35.0, 'subpar2':1})
		test_list.append(excinfo.value.message == 'Argument `par3` is of the wrong type')
		func_check_type1(1, 'hello', None)
		func_check_type2(1, 'hello', {'subpar1':35.0, 'subpar2':'no'})
		assert test_list == 2*[True]

###
# Custom data type addition
###
class NodeName(object):	#pylint: disable=R0903
	""" Hierarchical node name data type class """
	def includes(self, test_obj):	#pylint: disable=R0201,W0613
		"""	Test that an object belongs to the pseudo-type """
		return False if (not isinstance(test_obj, str)) or (isinstance(test_obj, str) and (' ' in test_obj)) else all([element.strip() != '' for element in test_obj.strip().split('.')])

	def istype(self, test_obj):	#pylint: disable=R0201
		"""	Checks to see if object is of the same class type """
		return isinstance(test_obj, str)

	def exception(self, param_name):	#pylint: disable=R0201,W0613
		"""	Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = ValueError
		exp_dict['msg'] = 'Argument `{0}` is not a valid node name'.format(param_name)
		return exp_dict
putil.check.register_new_type(NodeName, 'Hierarchical node name')


class BadType1(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def some_method(self):	#pylint: disable=C0111
		pass


class BadType2(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj):	#pylint: disable=C0111,R0201,W0613
		return 5


class BadType3(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj):	#pylint: disable=C0111,R0201,W0613
		return 5
	def includes(self, obj):	#pylint: disable=C0111,R0201,W0613
		return 5


class BadType4(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self):	#pylint: disable=C0111,R0201,W0613
		return 5
	def includes(self):	#pylint: disable=C0111,R0201,W0613
		return 5
	def exception(self):	#pylint: disable=C0111,R0201,W0613
		return 5


class BadType5(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj1, obj2, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, obj1, obj2, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, obj1, obj2, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True


class BadType6(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self):	#pylint: disable=C0111,R0201,W0613
		return 5
	def exception(self):	#pylint: disable=C0111,R0201,W0613
		return 5


class BadType7(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, obj1, obj2, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, obj1, obj2, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True


class BadType8(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, obj):	#pylint: disable=C0111,R0201,W0613
		return 5
	def exception(self):	#pylint: disable=C0111,R0201,W0613
		return 5


class BadType9(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, obj1, obj2, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True


class BadTypeA(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj):	#pylint: disable=C0111,R0201,W0613
		return 5
	def includes(self, obj):	#pylint: disable=C0111,R0201,W0613
		return 5
	def exception(self, param):	#pylint: disable=C0111,R0201,W0613
		return 5


class BadTypeB(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj):	#pylint: disable=C0111,R0201,W0613
		raise RuntimeError('Intentional exception')
	def includes(self, obj):	#pylint: disable=C0111,R0201,W0613
		raise RuntimeError('Intentional exception')
	def exception(self, param):	#pylint: disable=C0111,R0201,W0613
		raise RuntimeError('Intentional exception')


class GoodType1(object):	#pylint: disable=R0903
	""" Good pseudo-type implementation for testing purposes """
	def istype(self, *pargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, *pargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, *pargs):	#pylint: disable=C0111,R0201,W0613
		return True

class GoodType2(object):	#pylint: disable=R0903
	""" Good pseudo-type implementation for testing purposes """
	def istype(self, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True

class GoodType3(object):	#pylint: disable=R0903
	""" Good pseudo-type implementation for testing purposes """
	def istype(self, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True

class GoodType4(object):	#pylint: disable=R0903
	""" Good pseudo-type implementation for testing purposes """
	def istype(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True

class GoodType5(object):	#pylint: disable=R0903
	""" Good pseudo-type implementation for testing purposes """
	def istype(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, param):	#pylint: disable=C0111,R0201,W0613
		return {'type':None, 'msg':''}


class TestCustomDataTypeAddition(object):	#pylint: disable=W0232,R0903
	""" Tests the creation of custom data types and its integration in the flow """

	def test_get_istype(self):	#pylint: disable=R0201,C0103
		""" Test that get_istype method behaves as expected """
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.check.get_istype(BadTypeA(), 5)
		test_list.append(excinfo.value.message == 'Pseudo type check_test.BadTypeA.istype() method needs to return a boolean value')
		with pytest.raises(RuntimeError) as excinfo:
			putil.check.get_istype(BadTypeB(), 5)
		test_list.append(excinfo.value.message == 'Error trying to obtain pseudo type check_test.BadTypeB.istype() result')
		# This statement should not raise any exception
		putil.check.get_istype(NodeName(), 'a.b.c')
		assert test_list == len(test_list)*[True]


	def test_get_includes(self):	#pylint: disable=R0201,C0103
		""" Test that get_includes method behaves as expected """
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.check.get_includes(BadTypeA(), 5)
		test_list.append(excinfo.value.message == 'Pseudo type check_test.BadTypeA.includes() method needs to return a boolean value')
		with pytest.raises(RuntimeError) as excinfo:
			putil.check.get_includes(BadTypeB(), 5)
		test_list.append(excinfo.value.message == 'Error trying to obtain pseudo type check_test.BadTypeB.includes() result')
		# This statement should not raise any exception
		putil.check.get_includes(NodeName(), 'a.b.c')
		assert test_list == len(test_list)*[True]


	def test_get_exception(self):	#pylint: disable=R0201,C0103
		""" Test that get_exception method behaves as expected """
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.check.get_exception(BadTypeA(), param=5)
		test_list.append(excinfo.value.message == 'Pseudo type check_test.BadTypeA.exception() method needs to return a dictionary with keys "type" and "msg", with the exception type object and exception message respectively')
		with pytest.raises(RuntimeError) as excinfo:
			putil.check.get_exception(BadTypeB(), param=5)
		test_list.append(excinfo.value.message == 'Error trying to obtain pseudo type check_test.BadTypeB.exception() result')
		# This statement should not raise any exception
		putil.check.get_exception(GoodType5(), param='a.b.c')
		putil.check.get_exception(NodeName(), param_name='a.b.c')
		assert test_list == len(test_list)*[True]


	def test_custom_data_type_errors(self):	#pylint: disable=R0201,C0103
		""" Test that custom pseudo-type validation behaves as expected """
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.check.register_new_type(5, 'Bad type')
		test_list.append(excinfo.value.message == 'Pseudo type has to be a class')
		with pytest.raises(TypeError) as excinfo:
			putil.check.register_new_type(BadType1, 'Bad type')
		test_list.append(excinfo.value.message == 'Pseudo type check_test.BadType1 must have an istype() method')
		with pytest.raises(TypeError) as excinfo:
			putil.check.register_new_type(BadType2, 'Bad type')
		test_list.append(excinfo.value.message == 'Pseudo type check_test.BadType2 must have an includes() method')
		with pytest.raises(TypeError) as excinfo:
			putil.check.register_new_type(BadType3, 'Bad type')
		test_list.append(excinfo.value.message == 'Pseudo type check_test.BadType3 must have an exception() method')
		with pytest.raises(RuntimeError) as excinfo:
			putil.check.register_new_type(BadType4, 'Bad type')
		test_list.append(excinfo.value.message == 'Method check_test.BadType4.istype() must have only one argument')
		with pytest.raises(RuntimeError) as excinfo:
			putil.check.register_new_type(BadType5, 'Bad type')
		test_list.append(excinfo.value.message == 'Method check_test.BadType5.istype() must have only one argument')
		with pytest.raises(RuntimeError) as excinfo:
			putil.check.register_new_type(BadType6, 'Bad type')
		test_list.append(excinfo.value.message == 'Method check_test.BadType6.includes() must have only one argument')
		with pytest.raises(RuntimeError) as excinfo:
			putil.check.register_new_type(BadType7, 'Bad type')
		test_list.append(excinfo.value.message == 'Method check_test.BadType7.includes() must have only one argument')
		with pytest.raises(RuntimeError) as excinfo:
			putil.check.register_new_type(BadType8, 'Bad type')
		test_list.append(excinfo.value.message == 'Method check_test.BadType8.exception() must have only `param` and/or `param_name` arguments')
		print excinfo.value.message
		with pytest.raises(RuntimeError) as excinfo:
			putil.check.register_new_type(BadType9, 'Bad type')
		test_list.append(excinfo.value.message == 'Method check_test.BadType9.exception() must have only `param` and/or `param_name` arguments')
		# These statements should not raise any exception
		putil.check.register_new_type(GoodType1, 'Good type')
		putil.check.register_new_type(GoodType2, 'Good type')
		putil.check.register_new_type(GoodType3, 'Good type')
		putil.check.register_new_type(GoodType4, 'Good type')
		assert test_list == len(test_list)*[True]

	def test_custom_data_type_addition_works(self): #pylint: disable=R0201,C0103
		""" Test that adding a custom data type to check module framework works """
		@putil.check.check_argument(putil.check.PolymorphicType([None, putil.check.NumberRange(minimum=5.0, maximum=10.0), putil.check.OneOf(['HELLO', 'WORLD']), NodeName()]))
		def func_check(par1):	#pylint: disable=C0111
			return par1
		test_list = list()
		with pytest.raises(ValueError) as excinfo:
			func_check('node1.node2   . node3')
		test_list.append(excinfo.value.message == "Argument `par1` is not one of ['HELLO', 'WORLD'] (case insensitive)\nArgument `par1` is not a valid node name")
		with pytest.raises(ValueError) as excinfo:
			func_check(' node1.node2.node3')
		test_list.append(excinfo.value.message == "Argument `par1` is not one of ['HELLO', 'WORLD'] (case insensitive)\nArgument `par1` is not a valid node name")
		with pytest.raises(ValueError) as excinfo:
			func_check('node1.node2.node3 ')
		test_list.append(excinfo.value.message == "Argument `par1` is not one of ['HELLO', 'WORLD'] (case insensitive)\nArgument `par1` is not a valid node name")
		with pytest.raises(ValueError) as excinfo:
			func_check(1)
		test_list.append(excinfo.value.message == 'Argument `par1` is not in the range [5.0, 10.0]')
		with pytest.raises(TypeError) as excinfo:
			func_check([1, 2])
		test_list.append(excinfo.value.message == 'Argument `par1` is of the wrong type')
		# These statements should not raise any exception
		func_check(None)
		func_check(7.5)
		func_check('node1.node2.node3')
		assert test_list == len(test_list)*[True]
