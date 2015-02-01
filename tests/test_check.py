# test_check.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

# TODO: Test evalaute_series_ and other test functions in this module and test module
#       Document test module and other test helper functions

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

###
# Test for Any class
###
class TestAny(object):	#pylint: disable=W0232
	""" Tests for Any pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201
		"""	Test that Any class behaves appropriately when all arguments are correctly specified """
		putil.check.Any()

	def test_includes(self):	#pylint: disable=R0201
		"""	Test that the includes method of Any class behaves appropriately """
		putil.test.evaluate_command_value_series([(1, True), (2.0, True), (1+2j, True), ('a', True), ([1, 2, 3], True)], putil.check.Any().includes)

	def test_istype(self):	#pylint: disable=R0201
		"""	Test that the istype method of Any class behaves appropriately """
		putil.test.evaluate_command_value_series([(1, True), (2.0, True), (1+2j, True), ('a', True), ([1, 2, 3], True)], putil.check.Any().istype)

	def test_exception_method(self):	#pylint: disable=R0201
		"""	Tests that Any class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_method((putil.check.Any, None, ''))

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.Any().__str__, (), 'putil.check.Any()'), (putil.check.Any().__repr__, (), 'putil.check.Any()')])

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
		putil.test.evaluate_command_value_series([(1, True), (2.0, True), (1+2j, True), ('a', False), ([1, 2, 3], False)], putil.check.Number().includes)

	def test_istype(self):	#pylint: disable=R0201
		"""	Test that the istype method of Number class behaves appropriately """
		putil.test.evaluate_command_value_series([(1, True), (2.0, True), (1+2j, True), ('a', False), ([1, 2, 3], False)], putil.check.Number().istype)

	def test_exception_method(self):	#pylint: disable=R0201
		"""	Tests that Number class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_method((putil.check.Number, ValueError, 'Argument `par1` is not a number'))


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
		putil.test.evaluate_command_value_series([(-1, False), (1, True), (2.0, False), (1+2j, False), ('a', False), ([1, 2, 3], False)], putil.check.PositiveInteger().includes)

	def test_istype(self):	#pylint: disable=R0201
		"""	Test that the istype method of PositiveInteger class behaves appropriately """
		putil.test.evaluate_command_value_series([(-1, False), (1, True), (2.0, False), (1+2j, False), ('a', False), ([1, 2, 3], False)], putil.check.PositiveInteger().istype)

	def test_exception_method(self):	#pylint: disable=C0103,R0201
		"""	Tests that PositiveInteger class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_method((putil.check.PositiveInteger, ValueError, 'Argument `par1` is not a positive integer'))

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.PositiveInteger().__str__, (), 'putil.check.PositiveInteger()'), (putil.check.PositiveInteger().__repr__, (), 'putil.check.PositiveInteger()')])

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
		putil.test.evaluate_command_value_series([(1, True), (2.0, True), (1+2j, False), ('a', False), ([1, 2, 3], False)], putil.check.Real().includes)

	def test_istype(self):	#pylint: disable=R0201
		"""	Test that the istype method of Real class behaves appropriately """
		putil.test.evaluate_command_value_series([(1, True), (2.0, True), (1+2j, False), ('a', False), ([1, 2, 3], False)], putil.check.Real().istype)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that Real class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_method((putil.check.Real, ValueError, 'Argument `par1` is not a real number'))

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.PositiveInteger().__str__, (), 'putil.check.PositiveInteger()'), (putil.check.PositiveInteger().__repr__, (), 'putil.check.PositiveInteger()')])


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
		putil.test.evaluate_command_value_series([(-1, False), (1, True), (2.0, True), (1+2j, False), ('a', False), ([1, 2, 3], False)], putil.check.PositiveReal().includes)

	def test_istype(self):	#pylint: disable=R0201
		"""	Test that the istype method of PositiveReal class behaves appropriately """
		putil.test.evaluate_command_value_series([(-1, False), (1, True), (2.0, True), (1+2j, False), ('a', False), ([1, 2, 3], False)], putil.check.PositiveReal().istype)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that PositiveReal class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_method((putil.check.PositiveReal, ValueError, 'Argument `par1` is not a positive real number'))

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.PositiveInteger().__str__, (), 'putil.check.PositiveInteger()'), (putil.check.PositiveInteger().__repr__, (), 'putil.check.PositiveInteger()')])


###
# Test for ArbitraryLength class
###
class TestArbitraryLength(object):	#pylint: disable=W0232
	""" Tests for ArbitraryLength pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLength class behaves appropriately when all arguments are correctly specified """
		obj = putil.check.ArbitraryLength(iter_type=list, element_type=str)
		putil.test.evaluate_command_value_series([('iter_type', list), ('element_type', str)], obj)

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
		cmd_pairs = [(cmd1, [1, 2], True), (cmd1, ((1, 2), ), False), (cmd1, set([1.0, 2.0]), False), (cmd1, 1+2j, False), (cmd1, 'a', False), (cmd2, [1, 2.0, 3], True), (cmd2, [1, 2.0, None], False),\
			         (cmd3, 5, False), (cmd3, [3], False), (cmd3, [{'a':'b', 'b':'b'}], False), (cmd3, [{'a':5, 'b':'b'}], True), (cmd3, [{'a':5, 'b':'b'}, {'a':True, 'b':'b'}], False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_istype(self):	#pylint: disable=R0201
		"""	Test that the istype method of ArbitraryLength class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLength(tuple, int).istype, putil.check.ArbitraryLength(list, putil.check.PositiveReal()).istype
		cmd_pairs = [(cmd1, [1, 2], False), (cmd1, ((1, 2), ), True), (cmd1, set([1.0, 2.0]), False), (cmd1, 1+2j, False), (cmd1, 'a', False), (cmd2, [1, 2], True), (cmd2, [1, -1], False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLength class behaves appropriately when inproper element in iterable is passed """
		putil.test.evaluate_exception_method((putil.check.ArbitraryLength, {'iter_type':set, 'element_type':int}, TypeError, 'Argument `par1` is of the wrong type'))

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.ArbitraryLength(list, int).__str__, (), 'putil.check.ArbitraryLength(iter_type=list, element_type=int, check_keys=True)'),
											      (putil.check.ArbitraryLength(set, float).__repr__, (), 'putil.check.ArbitraryLength(iter_type=set, element_type=float, check_keys=True)')])


###
# Test for ArbitraryLengthList class
###
class TestArbitraryLengthList(object):	#pylint: disable=W0232
	""" Tests for ArbitraryLengthList pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthList class behaves appropriately when all arguments are correctly specified """
		obj = putil.check.ArbitraryLengthList(int)
		putil.test.evaluate_command_value_series([('element_type', int), ('iter_type', list)], obj)

	def test_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthList class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_series((putil.check.ArbitraryLengthList, {'element_type':'a'}, TypeError, 'Argument `element_type` is of the wrong type'))

	def test_includes(self):	#pylint: disable=R0201,C0103
		"""	Test that the includes method of ArbitraryLengthList class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthList(int).includes, putil.check.ArbitraryLengthList(putil.check.NumberRange(0, 1)).includes
		cmd_pairs = [(cmd1, [1, 2], True), (cmd1, set([1, 2]), False), (cmd1, ((1, 2), ), False), (cmd1, 'a', False), (cmd2, [0.5], True), (cmd2, [-0.01], False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_istype(self):	#pylint: disable=R0201,C0103
		"""	Test that the istype method of ArbitraryLengthList class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthList(int).istype, putil.check.ArbitraryLengthList(putil.check.NumberRange(0, 1)).istype
		cmd_pairs = [(cmd1, [1, 2], True), (cmd1, set([1, 2]), False), (cmd1, ((1, 2), ), False), (cmd1, 'a', False), (cmd2, [0.5], True), (cmd2, [-0.01], True), (cmd2, 'a', False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthList class behaves appropriately when inproper element in list is passed """
		putil.test.evaluate_exception_method((putil.check.ArbitraryLengthList, {'element_type':int}, TypeError, 'Argument `par1` is of the wrong type'))

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.ArbitraryLengthList(putil.check.Any()).__str__, (), 'putil.check.ArbitraryLengthList(element_type=putil.check.Any())'),
											      (putil.check.ArbitraryLengthList(float).__repr__, (), 'putil.check.ArbitraryLengthList(element_type=float)')])


###
# Test for ArbitraryLengthTuple class
###
class TestArbitraryLengthTuple(object):	#pylint: disable=W0232
	""" Tests for ArbitraryLengthTuple pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthTuple class behaves appropriately when all arguments are correctly specified	"""
		obj = putil.check.ArbitraryLengthTuple(int)
		putil.test.evaluate_command_value_series([('element_type', int), ('iter_type', tuple)], obj)

	def test_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthTuple class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_series((putil.check.ArbitraryLengthTuple, {'element_type':'a'}, TypeError, 'Argument `element_type` is of the wrong type'))

	def test_includes(self):	#pylint: disable=R0201,C0103
		"""	Test that the includes method of ArbitraryLengthTuple class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthTuple(float).includes, putil.check.ArbitraryLengthTuple(putil.check.NumberRange(0, 1)).includes
		cmd_pairs = [(cmd1, ((1.0, 2.0), ), True), (cmd1, [1, 2], False), (cmd1, set([1, 2]), False), (cmd1, 'a', False), (cmd2, ((0.5, ), ), True), (cmd2, ((-0.01, ), ), False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_type(self):	#pylint: disable=R0201,C0103
		"""	Test that the istype method of ArbitraryLengthTuple class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthTuple(float).istype, putil.check.ArbitraryLengthTuple(putil.check.NumberRange(0, 1)).istype
		cmd_pairs = [(cmd1, ((1.0, 2.0), ), True), (cmd1, [1, 2], False), (cmd1, set([1, 2]), False), (cmd1, 'a', False), (cmd2, ((0.5, ), ), True), (cmd2, ((-0.01, ), ), True), (cmd2, 'a', False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthTuple class behaves appropriately when inproper element in tuple is passed """
		putil.test.evaluate_exception_method((putil.check.ArbitraryLengthTuple, {'element_type':str}, TypeError, 'Argument `par1` is of the wrong type'))

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.ArbitraryLengthTuple(putil.check.Real()).__str__, (), 'putil.check.ArbitraryLengthTuple(element_type=putil.check.Real())'),
											      (putil.check.ArbitraryLengthTuple(dict).__repr__, (), 'putil.check.ArbitraryLengthTuple(element_type=dict)')])


###
# Test for ArbitraryLengthSet class
###
class TestArbitraryLengthSet(object):	#pylint: disable=W0232
	""" Tests for ArbitraryLengthSet pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthSet class behaves appropriately when all arguments are correctly specified """
		obj = putil.check.ArbitraryLengthSet(int)
		putil.test.evaluate_command_value_series([('element_type', int), ('iter_type', set)], obj)

	def test_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthSet class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_series((putil.check.ArbitraryLengthSet, {'element_type':'a'}, TypeError, 'Argument `element_type` is of the wrong type'))

	def test_includes(self):	#pylint: disable=R0201,C0103
		""" Test that the includes method of ArbitraryLengthSet class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthSet(float).includes, putil.check.ArbitraryLengthSet(putil.check.NumberRange(0, 1)).includes
		cmd_pairs = [(cmd1, set([1.0, 2.0]), True), (cmd1, [1, 2], False), (cmd1, ((1, 2), ), False), (cmd1, 'a', False), (cmd2, set([0.5]), True), (cmd2, set([-0.01]), False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_istype(self):	#pylint: disable=R0201,C0103
		""" Test that the istype method of ArbitraryLengthSet class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthSet(float).istype, putil.check.ArbitraryLengthSet(putil.check.NumberRange(0, 1)).istype
		cmd_pairs = [(cmd1, set([1.0, 2.0]), True), (cmd1, [1, 2], False), (cmd1, ((1, 2), ), False), (cmd1, 'a', False), (cmd2, set([0.5]), True), (cmd2, set([-0.01]), True), (cmd2, set(['a']), False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthSet class behaves appropriately when inproper element in set is passed """
		putil.test.evaluate_exception_method((putil.check.ArbitraryLengthSet, {'element_type':float}, TypeError, 'Argument `par1` is of the wrong type'))

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.ArbitraryLengthSet(putil.check.PositiveReal()).__str__, (), 'putil.check.ArbitraryLengthSet(element_type=putil.check.PositiveReal())'),
											      (putil.check.ArbitraryLengthSet(str).__repr__, (), 'putil.check.ArbitraryLengthSet(element_type=str)')])

###
# Test for ArbitraryLengthDict class
###
class TestArbitraryLengthDict(object):	#pylint: disable=W0232
	""" Tests for ArbitraryLengthDict pseudo-type """

	def test_no_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthDict class behaves appropriately when all arguments are correctly specified """
		obj = putil.check.ArbitraryLengthDict(int)
		putil.test.evaluate_command_value_series([('iter_type', dict), ('element_type', int)], obj)

	def test_exception(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthDict class behaves appropriately when inproper argument type is passed """
		putil.test.evaluate_exception_series((putil.check.ArbitraryLengthDict, {'element_type':'a'}, TypeError, 'Argument `element_type` is of the wrong type'))

	def test_includes(self):	#pylint: disable=R0201,C0103
		"""	Test that the includes method of ArbitraryLengthDict class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthDict(int).includes, putil.check.ArbitraryLengthDict(putil.check.NumberRange(0, 1)).includes
		cmd_pairs = [(cmd1, {'a':1, 'b':2}, True), (cmd1, set([1, 2]), False), (cmd1, ((1, 2), ), False), (cmd1, {'a':'a'}, False), (cmd2, {'c':0.5}, True), (cmd2, {'d':-0.01}, False)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_istype(self):	#pylint: disable=R0201,C0103
		"""	Test that the istype method of ArbitraryLengthDict class behaves appropriately """
		cmd1, cmd2 = putil.check.ArbitraryLengthDict(int).istype, putil.check.ArbitraryLengthDict(putil.check.NumberRange(0, 1)).istype
		cmd_pairs = [(cmd1, {'a':1, 'b':2}, True), (cmd1, set([1, 2]), False), (cmd1, ((1, 2), ), False), (cmd1, {'a':'a'}, False), (cmd2, {'c':0.5}, True), (cmd2, {'d':-0.01}, True)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):	#pylint: disable=R0201,C0103
		"""	Tests that ArbitraryLengthDict class behaves appropriately when inproper element in list is passed """
		putil.test.evaluate_exception_method((putil.check.ArbitraryLengthDict, {'element_type':int}, TypeError, 'Argument `par1` is of the wrong type'))

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.ArbitraryLengthDict(putil.check.Number()).__str__, (), 'putil.check.ArbitraryLengthDict(element_type=putil.check.Number())'),
											      (putil.check.ArbitraryLengthDict(decimal.Decimal).__repr__, (), 'putil.check.ArbitraryLengthDict(element_type=decimal.Decimal)')])


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
		# case_sensitive is set to None if there is no string option
		putil.test.evaluate_command_value_series([(putil.check.OneOf([1, 2, 3], case_sensitive=True), 'case_sensitive', None), \
											      (putil.check.OneOf([1, 2, 4], case_sensitive=False), 'case_sensitive', None), \
											      (putil.check.OneOf(['a', 'b', 'c'], case_sensitive=False), 'case_sensitive', False)])

	def test_infinite_iterable_exception(self):	#pylint: disable=R0201,C0103
		""" Tests that OneOf class behaves properly when an improper iterable is given """
		putil.test.evaluate_exception_series((putil.check.OneOf, {'choices':itertools.count(start=0, step=1)}, TypeError, 'Argument `choices` is of the wrong type'))

	def test_proper_no_errors(self):	#pylint: disable=R0201,C0103
		""" Tests that OneOf class behaves properly when all arguments are correctly specified """
		test_choices = ['a', 2, 3.0, 'a', putil.check.Real()]
		obj = putil.check.OneOf(test_choices, case_sensitive=True)
		putil.test.evaluate_command_value_series([('types', [type(element) for element in test_choices]), ('choices', test_choices), ('case_sensitive', True)], obj)

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
		putil.test.evaluate_exception_method(exdesc, putil.check.OneOf)

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.OneOf(['a', 'b', 'c'], case_sensitive=True).__str__, (), 'putil.check.OneOf(choices=["a", "b", "c"], case_sensitive=True)'),
											      (putil.check.OneOf([1, 2, 3]).__repr__, (), 'putil.check.OneOf(choices=[1, 2, 3], case_sensitive=None)')])


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
		putil.test.evaluate_command_value_series([('minimum', 10.0), ('maximum', 20.0)], obj)

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
		putil.test.evaluate_exception_method(exdesc, putil.check.NumberRange)

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.NumberRange(maximum=2).__str__, (), 'putil.check.NumberRange(minimum=-infinity, maximum=2.0)'),
		                                          (putil.check.NumberRange(minimum=3).__str__, (), 'putil.check.NumberRange(minimum=3.0, maximum=+infinity)'),
										          (putil.check.NumberRange(minimum=4, maximum=5.1).__str__, (), 'putil.check.NumberRange(minimum=4.0, maximum=5.1)')])

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
		putil.test.evaluate_exception_method((putil.check.RealNumpyVector, ValueError, 'Argument `par1` is not a Numpy vector of real numbers'))

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.RealNumpyVector().__str__, (), 'putil.check.RealNumpyVector()'), (putil.check.RealNumpyVector().__repr__, (), 'putil.check.RealNumpyVector()')])


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
		putil.test.evaluate_exception_method((putil.check.IncreasingRealNumpyVector, ValueError, 'Argument `par1` is not a Numpy vector of increasing real numbers'))

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.IncreasingRealNumpyVector().__str__, (), 'putil.check.IncreasingRealNumpyVector()'),
											      (putil.check.IncreasingRealNumpyVector().__repr__, (), 'putil.check.IncreasingRealNumpyVector()')])


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
		putil.test.evaluate_command_value_series([(cmd1, '/some/file.txt', True), (cmd2, 'not a file', False), (cmd2, './test_check.py', True)])

	def test_istype(self):	#pylint: disable=R0201,C0103
		""" Test that the istype method of File class behaves appropriately """
		cmd1, cmd2 = putil.check.File().istype, putil.check.File(True).istype
		putil.test.evaluate_command_value_series([(cmd1, 3, False), (cmd2, 'not a file', True), (cmd2, './test_check.py', True)])

	def test_exception_method(self):    #pylint: disable=R0201
		""" Tests that exception method of File class behaves appropriately """
		putil.test.evaluate_exception_method((putil.check.File, IOError, 'File /some/path/file_name.ext could not be found'), ekwargs={'param':'/some/path/file_name.ext'})

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
		exdesc.append((set_file_name2, {'file_name':'test_check.py'}))
		putil.test.evaluate_exception_series(exdesc)

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.File().__str__, (), 'putil.check.File(check_existance=False)'),
											      (putil.check.File(True).__repr__, (), 'putil.check.File(check_existance=True)')])


###
# Test Function class
###
class TestFuntion(object):	#pylint: disable=W0232
	""" Tests for Funtion pseudo-type """

	def test_wrong_type(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely when wrong type argument is given """
		putil.test.evaluate_exception_series((putil.check.Function, {'num_pars':'a'}, TypeError, 'Argument `num_pars` is of the wrong type'))

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
		cmd1, cmd2, cmd3, cmd4 = putil.check.Function().includes, putil.check.Function(num_pars=3).includes, putil.check.Function(num_pars=2).includes, putil.check.Function(num_pars=5).includes
		cmd_pairs = [(cmd1, 3, False), (cmd1, foo1, True), (cmd2, foo1, False), (cmd3, foo1, True), (cmd1, foo2, True), (cmd4, foo2, True), (cmd3, foo2, True), (cmd1, foo3, True), (cmd4, foo3, True), (cmd3, foo3, True), \
			         (cmd1, foo4, True), (cmd4, foo4, True), (cmd3, foo4, True)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_istype(self):	#pylint: disable=R0201,C0103
		""" Test that the istype method of Function class behaves appropriately """
		def foo1(par1, par2):	#pylint: disable=C0111
			return par1, par2
		cmd1, cmd2, cmd3 = putil.check.Function().istype, putil.check.Function(num_pars=3).istype, putil.check.Function(num_pars=2).istype
		cmd_pairs = [(cmd1, 3, False), (cmd1, foo1, True), (cmd2, foo1, True), (cmd3, foo1, True)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception(self):    #pylint: disable=R0201
		""" Tests that exception method of Function class behaves appropriately """
		exdesc = list()
		exdesc.append(({'num_pars':1}, ValueError, 'Argument `par1` is not a function with 1 argument'))
		exdesc.append(({'num_pars':2}, ValueError, 'Argument `par1` is not a function with 2 arguments'))
		putil.test.evaluate_exception_method(exdesc, putil.check.Function, ekwargs={'param':'par1'})

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.Function().__str__, (), 'putil.check.Function(num_pars=None)'),
											      (putil.check.Function(4).__repr__, (), 'putil.check.Function(num_pars=4)')])


###
# Test PolymorphicType class
###
class TestPolymorphicType(object):	#pylint: disable=W0232
	""" Tests for PolymorphicType pseudo-type """

	def test_type_match_wrong_type(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely when wrong type argument is given """
		putil.test.evaluate_exception_series(({'types':'a'}, TypeError, 'Argument `types` is of the wrong type'), putil.check.PolymorphicType)

	def test_type_match_subtype_wrong_type(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely when wrong sub-type argument is given """
		putil.test.evaluate_exception_series(({'types':[str, int, 'a']}, TypeError, 'Argument `types` element is of the wrong type'), putil.check.PolymorphicType)

	def test_type_match_no_errors(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely when all arguments are correctly specified """
		test_instances = [str, int, None]+putil.check._get_pseudo_types()['type']	#pylint: disable=W0212
		obj = putil.check.PolymorphicType(test_instances)
		test_types = test_instances[0:2]+[type(None)]+test_instances[3:]
		assert all([obj.instances == test_instances, obj.types == test_types])

	def test_includes(self):	#pylint: disable=R0201,C0103
		""" Test that the includes method of PolymorphicType class behaves appropriately """
		test_instances = [int, None, putil.check.ArbitraryLengthList(int), putil.check.ArbitraryLengthTuple(float), putil.check.ArbitraryLengthSet(str), putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=True),
			              putil.check.NumberRange(1, 3), putil.check.Number(), putil.check.Real(), putil.check.RealNumpyVector()]
		cmd1, cmd2 = putil.check.PolymorphicType(test_instances).includes, putil.check.PolymorphicType([float, putil.check.IncreasingRealNumpyVector()]).includes
		cmd3, cmd4 = putil.check.PolymorphicType([putil.check.File(check_existance=False), putil.check.Function(num_pars=2)]).includes, putil.check.PolymorphicType([None, putil.check.PositiveInteger()]).includes
		cmd5, cmd6 = putil.check.PolymorphicType([None, putil.check.PositiveReal()]).includes, putil.check.PolymorphicType([None, putil.check.PositiveReal(), putil.check.Any()]).includes
		def foo1(par1, par2, par3):	#pylint: disable=C0111
			return par1, par2, par3
		def foo2(par1, par2):	#pylint: disable=C0111
			return par1, par2
		cmd_pairs = [(cmd1, 5, True), (cmd1, None, True), (cmd1, [1, 2, 3], True), (cmd1, ((2.0, 3.0), ), True), (cmd1, set(['a', 'b', 'c']), True), (cmd1, 'MANUAL', True), (cmd1, 2, True), \
                     (cmd1, 100.0, True), (cmd1, 10+20j, True), (cmd1, numpy.array([10, 0.0, 30]), True), (cmd1, 'hello world', False), (cmd1, [1.0, 2.0, 3.0], False), (cmd1, 'auto', False), \
                     (cmd1, numpy.array([]), False), (cmd1, numpy.array(['a', 'b', 'c']), False), (cmd2, 1, False), (cmd2, set([1, 2]), False), (cmd2, numpy.array([1, 0, -1]), False), \
                     (cmd2, numpy.array([10.0, 20.0, 30.0]), True), (cmd2, 5.0, True), (cmd3, 3, False), (cmd3, '/some/file', True), (cmd3, foo1, False), (cmd3, foo2, True), (cmd4, -1, False), \
                     (cmd4, 1, True), (cmd5, -0.001, False), (cmd5, 0.001, True), (cmd6, None, True), (cmd6, 2.0, True), (cmd6, 'a', True)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_istype(self):	#pylint: disable=R0201,C0103
		""" Test that the istype method of PolymorphicType class behaves appropriately """
		test_instances = [int, None, putil.check.ArbitraryLengthList(int), putil.check.ArbitraryLengthTuple(float), putil.check.ArbitraryLengthSet(str), putil.check.OneOf(['NONE', 'MANUAL', 'AUTO'], case_sensitive=True),
			              putil.check.NumberRange(1, 3), putil.check.Number(), putil.check.Real(), putil.check.RealNumpyVector()]
		cmd1, cmd2 = putil.check.PolymorphicType(test_instances).istype, putil.check.PolymorphicType([float, putil.check.IncreasingRealNumpyVector()]).istype
		cmd3, cmd4 = putil.check.PolymorphicType([putil.check.File(check_existance=False), putil.check.Function(num_pars=2)]).istype, putil.check.PolymorphicType([None, putil.check.PositiveInteger()]).istype
		cmd5, cmd6 = putil.check.PolymorphicType([None, putil.check.PositiveReal()]).istype, putil.check.PolymorphicType([None, putil.check.PositiveReal(), putil.check.Any()]).istype
		cmd7 = putil.check.PolymorphicType([None, {'a':int, 'b':str}]).istype
		def foo1(par1, par2, par3):	#pylint: disable=C0111
			return par1, par2, par3
		cmd_pairs = [(cmd1, 5, True), (cmd1, None, True), (cmd1, [1, 2, 3], True), (cmd1, ((2.0, 3.0), ), True), (cmd1, set(['a', 'b', 'c']), True), (cmd1, 'MANUAL', True), (cmd1, 2, True), \
                     (cmd1, 100.0, True), (cmd1, 10+20j, True), (cmd1, numpy.array([10, 0.0, 30]), True), (cmd1, 'hello world', True), (cmd1, [1.0, 2.0, 3.0], False), (cmd1, 'auto', True), \
                     (cmd1, numpy.array([]), False), (cmd1, numpy.array(['a', 'b', 'c']), False), (cmd2, 1, False), (cmd2, set([1, 2]), False), (cmd2, numpy.array([1, 0, -1]), False), \
                     (cmd2, numpy.array([10.0, 20.0, 30.0]), True), (cmd2, 5.0, True), (cmd3, 3, False), (cmd3, '/some/file', True), (cmd3, foo1, True), (cmd4, -1, False), (cmd4, 1, True), \
                     (cmd5, -0.001, False), (cmd5, 0.001, True), (cmd6, None, True), (cmd6, 2.0, True), (cmd6, 'a', True), (cmd7, None, True), (cmd7, {'c':5}, False), (cmd7, {'a':5}, False), \
                     (cmd7, {'a':5, 'b':'Hello'}, True)]
		putil.test.evaluate_command_value_series(cmd_pairs)

	def test_exception_method(self):    #pylint: disable=R0201
		""" Tests that exception method of PolymorphicType class behaves appropriately """
		exdesc = list()
		exdesc.append(({'types':[putil.check.OneOf(['NONE', 'MANUAL', 'AUTO']), putil.check.NumberRange(minimum=15, maximum=20)]}, ValueError, \
				        'Argument `par1` is not in the range [15.0, 20.0]', {'param_name':'par1', 'test_obj':5}))
		exdesc.append(({'types':[putil.check.OneOf(['NONE', 'MANUAL', 'AUTO']), putil.check.File(True)]}, RuntimeError, "(ValueError) Argument `par1` is not one of ['NONE', 'MANUAL', 'AUTO'] " \
				        "(case insensitive)\n(IOError) File _not_valid_ could not be found", {'param_name':'par1', 'param':'_not_valid_', 'test_obj':'not_a_file'}))
		exdesc.append(({'types':[putil.check.File(True), putil.check.Function(num_pars=2)]}, None, '', {'param_name':'par1', 'param':'_not_valid_', 'test_obj':32}))
		exdesc.append(({'types':[None, putil.check.PositiveInteger(), putil.check.NumberRange(minimum=15, maximum=20)]}, ValueError, \
				        'Argument `par1` is not in the range [15.0, 20.0]', {'param_name':'par1', 'test_obj':-1}))
		exdesc.append(({'types':[None, putil.check.PositiveReal(), putil.check.Any()]}, None, '', {'param_name':'par1', 'test_obj':-1}))
		putil.test.evaluate_exception_method(exdesc, putil.check.PolymorphicType)

	def test_str_and_repr(self):	#pylint: disable=R0201
		""" Test that both __str__() and __repr__() methods behave appropiately """
		putil.test.evaluate_command_value_series([(putil.check.PolymorphicType([int, putil.check.Number()]).__str__, (), 'putil.check.PolymorphicType(types=[int, putil.check.Number()])'),
											      (putil.check.PolymorphicType([putil.check.ArbitraryLengthList(dict), str]).__repr__, (), 'putil.check.PolymorphicType(types=[putil.check.ArbitraryLengthList(element_type=dict), str])')])


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
		cmd_pairs = [('a', False), (str, True), (5, False), (putil.check.PolymorphicType([str, int]), True), ([str, dict, list], False), (itertools.count(start=0, step=1), False), \
			         ({'a':str, 'b':int}, True), ({'a':str, 'b':[str, str]}, False), ({'a':str, 'b':{'c':putil.check.Number(), 'd':float}}, True)]
		putil.test.evaluate_command_value_series(cmd_pairs, putil.check.is_type_def)


###
# Tests for type_match()
###
class TestTypeMatch(object):	#pylint: disable=W0232
	""" Tests for type_match function """

	def test_str(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for string type """
		putil.test.evaluate_command_value_series([(('hello', str), True), ((135, str), False)], putil.check.type_match)

	def test_float(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for float type """
		putil.test.evaluate_command_value_series([((1.5, float), True), ((135, float), False)], putil.check.type_match)

	def test_int(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for integer type """
		putil.test.evaluate_command_value_series([((8, int), True), ((135.0, int), False)], putil.check.type_match)

	def test_number(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for Number pseudo-type (integer, real or complex) """
		obj = putil.check.Number()
		putil.test.evaluate_command_value_series([((1, obj), True), ((135.0, obj), True), ((1+1j, obj), True), (('hello', obj), False)], putil.check.type_match)

	def test_real(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for Real pseudo-type (integer or real) """
		putil.test.evaluate_command_value_series([((1, putil.check.Real()), True), ((135.0, putil.check.Real()), True), ((1+1j, putil.check.Real()), False)], putil.check.type_match)

	def test_boolean(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for boolean type """
		putil.test.evaluate_command_value_series([((True, bool), True), ((12.5, bool), False)], putil.check.type_match)

	def test_decimal(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for Decimal type """
		putil.test.evaluate_command_value_series([((decimal.Decimal(1.25), decimal.Decimal), True), ((12.5, decimal.Decimal), False)], putil.check.type_match)

	def test_fraction(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for Fraction type """
		putil.test.evaluate_command_value_series([((fractions.Fraction(4, 6), fractions.Fraction), True), ((12.5, fractions.Fraction), False)], putil.check.type_match)

	def test_arbitrary_length_list(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for ArbitraryLengthList pseudo-type """
		putil.test.evaluate_command_value_series([(([1, 2, 3], putil.check.ArbitraryLengthList(int)), True), (('hello', putil.check.ArbitraryLengthList(int)), False)], putil.check.type_match)

	def test_arbitrary_length_tuple(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for ArbitraryLengthTuple pseudo-type """
		putil.test.evaluate_command_value_series([(((1, 2, 3), putil.check.ArbitraryLengthTuple(int)), True), (((1, 2, 'a'), putil.check.ArbitraryLengthTuple(int)), False)], putil.check.type_match)

	def test_arbitrary_length_set(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for ArbitraryLengthSet pseudo-type """
		putil.test.evaluate_command_value_series([((set([1, 2, 3]), putil.check.ArbitraryLengthSet(int)), True), ((set([1, 2, 'a']), putil.check.ArbitraryLengthSet(int)), False)], putil.check.type_match)

	def test_fixed_length_list(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for fixed-length list type """
		putil.test.evaluate_command_value_series([(([1, 'a', 3.0], [int, str, float]), True), (([1, 'a', 3.0, 4.0], [int, str, float]), False), (([1, 'a', 3.0], [int, str, float, int]), False), \
											      (([1, 2, 3.0], [int, str, float]), False)], putil.check.type_match)

	def test_fixed_length_tuple(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for fixed-length tuple type """
		putil.test.evaluate_command_value_series([(((1, 'a', 3.0), (int, str, float)), True), (((1, 'a', 3.0, 4.0), (int, str, float)), False), (((1, 'a', 3.0), (int, str, float, int)), False), \
												  (((1, 2, 3.0), (int, str, float)), False)], putil.check.type_match)

	def test_fixed_length_set(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for fixed-length set type """
		exdesc = (putil.check.type_match, {'test_obj':set([1, 'a', 3.0]), 'ref_obj':set([int, str, float])}, RuntimeError, 'Set is an un-ordered iterable, thus it cannot be type-checked against an ordered reference')
		putil.test.evaluate_exception_series(exdesc)

	def test_one_of(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for OneOf pseudo-type """
		putil.test.evaluate_command_value_series([(('HELLO', putil.check.OneOf(['HELLO', 45, 'WORLD'])), True), ((45, putil.check.OneOf(['HELLO', 45, 'WORLD'])), True), \
											      ((1.0, putil.check.OneOf(['HELLO', 45, 'WORLD'])), False)], putil.check.type_match)

	def test_number_range(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for NumberRange pseudo-type """
		putil.test.evaluate_command_value_series([((12, putil.check.NumberRange(minimum=2, maximum=5)), True), (('a', putil.check.NumberRange(minimum=2, maximum=5)), False)], putil.check.type_match)
		#assert (putil.check.type_match(12, putil.check.NumberRange(minimum=2, maximum=5)), putil.check.type_match('a', putil.check.NumberRange(minimum=2, maximum=5))) == (True, False)

	def test_dict(self):	#pylint: disable=R0201
		""" Test if function behaves proprely for dictionary type """
		putil.test.evaluate_command_value_series([(({'a':'hello', 'b':12.5, 'c':[1]}, {'a':str, 'b':float, 'c':[int]}), True),	# 'Regular' match
											      (({'a':'hello', 'c':[1]}, {'a':str, 'b':float, 'c':[int]}), True),	# One key-value pair missing in test object, useful where argument is omitted to get default
											      (({'x':'hello', 'y':{'n':[1.5, 2.3]}, 'z':[1]}, {'x':str, 'y':{'n':putil.check.ArbitraryLengthList(float), 'm':str}, 'z':[int]}), True), # Nested
											      (({'a':'hello', 'b':35, 'c':[1]}, {'a':str, 'b':float, 'c':[int]}), False),	# Value of one key in test object does not match
											      (({'a':'hello', 'd':12.5, 'c':[1]}, {'a':str, 'b':float, 'c':[int]}), False)], putil.check.type_match)	# One key in test object does not appear in reference object

	def test_polymorphic_type(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for PolymorphicType pseudo-type """
		putil.test.evaluate_command_value_series([(('HELLO', putil.check.PolymorphicType([str, int])), True), ((45, putil.check.PolymorphicType([str, int])), True),
											      ((1.5, putil.check.PolymorphicType([str, int])), False)], putil.check.type_match)

	def test_real_numpy_vector(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for RealNumpyVector pseudo-type """
		putil.test.evaluate_command_value_series([((12, putil.check.RealNumpyVector()), False), ((numpy.array([1, 2, 0]), putil.check.RealNumpyVector()), True),
											      ((numpy.array([[1, 2, 0], [1, 1, 2]]), putil.check.RealNumpyVector()), False)], putil.check.type_match)

	def test_increasing_real_numpy_vector(self):	#pylint: disable=R0201,C0103
		""" Test if function behaves proprely for IncreasingRealNumpyVector pseudo-type """
		putil.test.evaluate_command_value_series([((12, putil.check.IncreasingRealNumpyVector()), False), ((numpy.array([1, 2, 3]), putil.check.IncreasingRealNumpyVector()), True),
											      ((numpy.array([True, False, True]), putil.check.IncreasingRealNumpyVector()), False),
											      ((numpy.array([[1, 2, 3], [4, 5, 6]]), putil.check.IncreasingRealNumpyVector()), False)], putil.check.type_match)


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
		putil.test.evaluate_command_value_series([(func_check_type1, None, None), (func_check_type1, 6, 6), (func_check_type1, 7.0, 7.0), (func_check_type1, 'WORLD', 'WORLD'),
											      (func_check_type2, None, None), (func_check_type2, 8, 8), (func_check_type2, {'a':'b'}, {'a':'b'}), (func_check_type3, True, True)])

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
		exdesc = list()
		exdesc.append(({'ppar1':{'x':'hello', 'b':45}}, TypeError, 'Argument `ppar1` is of the wrong type'))
		exdesc.append(({'ppar1':{'a':'hello', 'b':45, 'c':60}}, TypeError, 'Argument `ppar1` is of the wrong type'))
		exdesc.append(({'ppar1':{'a':'hello', 'b':True}}, TypeError, 'Argument `ppar1` is of the wrong type'))
		exdesc.append(({'ppar1':{'a':'hello'}}, TypeError, 'Argument `ppar1` is of the wrong type'))
		exdesc.append(({'ppar1':{'a':'hello', 'b':45}}, ))
		putil.test.evaluate_exception_series(exdesc, func_check_type)


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
		obj = DummyClass()
		exdesc = list()
		exdesc.append((func_check_type, {}, RuntimeError, 'Function func_check_type has no arguments'))
		exdesc.append((obj.class_func_check_type, {}, RuntimeError, 'Function class_func_check_type has no arguments after self'))
		putil.test.evaluate_exception_series(exdesc)

	def test_argument_not_declared(self): #pylint: disable=R0201
		""" Test that function behaves correctly when the function to check does not have an argument in the validation list """
		@putil.check.check_arguments({'par1':int})
		def func_check_type(par0, par2):	#pylint: disable=C0111,W0613
			pass
		putil.test.evaluate_exception_series((func_check_type, {'par0':1, 'par2':2}, RuntimeError, 'Argument par1 is not an argument of function func_check_type'))

	def test_wrong_type(self): #pylint: disable=R0201
		""" Test that function behaves correctly one of man parameters is of the wrong type """
		@putil.check.check_arguments({'par1':int, 'par2':str})
		def func_check_type1(par1, par2, par3):	#pylint: disable=C0111,W0613
			pass
		@putil.check.check_arguments({'par1':int, 'par2':str, 'par3':{'subpar1':float, 'subpar2':str}})
		def func_check_type2(par1, par2, par3):	#pylint: disable=C0111,W0613
			pass
		exdesc = list()
		exdesc.append((func_check_type1, {'par1':1, 'par2':2, 'par3':3}, TypeError, 'Argument `par2` is of the wrong type'))
		exdesc.append((func_check_type2, {'par1':1, 'par2':'hello', 'par3':{'subpar1':35.0, 'subpar2':1}}, TypeError, 'Argument `par3` is of the wrong type'))
		putil.test.evaluate_exception_series(exdesc)

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
		return {'type': ValueError, 'msg':'Argument `{0}` is not a valid node name'.format(param_name)}

	def __repr__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return self.__str__()

	def __str__(self):	#pylint: disable=R0201
		""" String with object description and parameters """
		return 'putil.test_check.NodeName()'
putil.check.register_new_type(NodeName, 'Hierarchical node name')


class BadType1(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def some_method(self):	#pylint: disable=C0111
		pass
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.BadType1()'


class BadType2(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj):	#pylint: disable=C0111,R0201,W0613
		return 5
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.BadType2()'


class BadType3(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj):	#pylint: disable=C0111,R0201,W0613
		return 5
	def includes(self, obj):	#pylint: disable=C0111,R0201,W0613
		return 5
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.BadType3()'


class BadType4(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self):	#pylint: disable=C0111,R0201,W0613
		return 5
	def includes(self):	#pylint: disable=C0111,R0201,W0613
		return 5
	def exception(self):	#pylint: disable=C0111,R0201,W0613
		return 5
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.BadType4()'


class BadType5(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj1, obj2, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, obj1, obj2, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, obj1, obj2, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.BadType5()'


class BadType6(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self):	#pylint: disable=C0111,R0201,W0613
		return 5
	def exception(self):	#pylint: disable=C0111,R0201,W0613
		return 5
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.BadType6()'


class BadType7(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, obj1, obj2, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, obj1, obj2, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.BadType7()'


class BadType8(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, obj):	#pylint: disable=C0111,R0201,W0613
		return 5
	def exception(self):	#pylint: disable=C0111,R0201,W0613
		return 5
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.BadType8()'


class BadType9(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, obj1, obj2, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.BadType9()'


class BadTypeA(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj):	#pylint: disable=C0111,R0201,W0613
		return 5
	def includes(self, obj):	#pylint: disable=C0111,R0201,W0613
		return 5
	def exception(self, param):	#pylint: disable=C0111,R0201,W0613
		return 5
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.BadTypeA()'


class BadTypeB(object):	#pylint: disable=R0903
	""" Bad pseudo-type implementation for testing purposes """
	def istype(self, obj):	#pylint: disable=C0111,R0201,W0613
		raise RuntimeError('Intentional exception')
	def includes(self, obj):	#pylint: disable=C0111,R0201,W0613
		raise RuntimeError('Intentional exception')
	def exception(self, param):	#pylint: disable=C0111,R0201,W0613
		raise RuntimeError('Intentional exception')
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.BadTypeB()'

class GoodType1(object):	#pylint: disable=R0903
	""" Good pseudo-type implementation for testing purposes """
	def istype(self, *pargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, *pargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, *pargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.GoodType1()'

class GoodType2(object):	#pylint: disable=R0903
	""" Good pseudo-type implementation for testing purposes """
	def istype(self, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.GoodType2()'

class GoodType3(object):	#pylint: disable=R0903
	""" Good pseudo-type implementation for testing purposes """
	def istype(self, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.GoodType3()'

class GoodType4(object):	#pylint: disable=R0903
	""" Good pseudo-type implementation for testing purposes """
	def istype(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.GoodType4()'

class GoodType5(object):	#pylint: disable=R0903
	""" Good pseudo-type implementation for testing purposes """
	def istype(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def includes(self, obj, *pargs, **kwargs):	#pylint: disable=C0111,R0201,W0613
		return True
	def exception(self, param):	#pylint: disable=C0111,R0201,W0613
		return {'type':None, 'msg':''}
	def __repr__(self):	#pylint: disable=C0111,R0201
		return self.__str__()
	def __str__(self):	#pylint: disable=C0111,R0201
		return 'putil.test_check.GoodType5()'


class TestCustomDataTypeAddition(object):	#pylint: disable=W0232,R0903
	""" Tests the creation of custom data types and its integration in the flow """

	def test_get_istype(self):	#pylint: disable=R0201,C0103
		""" Test that get_istype method behaves as expected """
		exdesc = list()
		exdesc.append(({'ptype':BadTypeA(), 'obj':5}, TypeError, 'Pseudo type test_check.BadTypeA.istype() method needs to return a boolean value'))
		exdesc.append(({'ptype':BadTypeB(), 'obj':5}, RuntimeError, 'Error trying to obtain pseudo type test_check.BadTypeB.istype() result'))
		exdesc.append(({'ptype':NodeName(), 'obj':'a.b.c'}, ))
		putil.test.evaluate_exception_series(exdesc, putil.check.get_istype)

	def test_get_includes(self):	#pylint: disable=R0201,C0103
		""" Test that get_includes method behaves as expected """
		exdesc = list()
		exdesc.append(({'ptype':BadTypeA(), 'obj':5}, TypeError, 'Pseudo type test_check.BadTypeA.includes() method needs to return a boolean value'))
		exdesc.append(({'ptype':BadTypeB(), 'obj':5}, RuntimeError, 'Error trying to obtain pseudo type test_check.BadTypeB.includes() result'))
		exdesc.append(({'ptype':NodeName(), 'obj':'a.b.c'}, ))
		putil.test.evaluate_exception_series(exdesc, putil.check.get_includes)

	def test_get_exception(self):	#pylint: disable=R0201,C0103
		""" Test that get_exception method behaves as expected """
		exdesc = list()
		exdesc.append(({'ptype':BadTypeA(), 'param':5}, TypeError, 'Pseudo type test_check.BadTypeA.exception() method needs to return a dictionary with keys "type" and "msg", '
				                                                   'with the exception type object and exception message respectively'))
		exdesc.append(({'ptype':BadTypeB(), 'param':5}, RuntimeError, 'Error trying to obtain pseudo type test_check.BadTypeB.exception() result'))
		exdesc.append(({'ptype':GoodType5(), 'param':'a.b.c'}, ))
		exdesc.append(({'ptype':NodeName(), 'param_name':'a.b.c'}, ))
		putil.test.evaluate_exception_series(exdesc, putil.check.get_exception)

	def test_custom_data_type_errors(self):	#pylint: disable=R0201,C0103
		""" Test that custom pseudo-type validation behaves as expected """
		exdesc = list()
		exdesc.append(({'cls':5, 'desc':'Bad type'}, TypeError, 'Pseudo type has to be a class'))
		exdesc.append(({'cls':BadType1, 'desc':'Bad type'}, TypeError, 'Pseudo type test_check.BadType1 must have an istype() method'))
		exdesc.append(({'cls':BadType2, 'desc':'Bad type'}, TypeError, 'Pseudo type test_check.BadType2 must have an includes() method'))
		exdesc.append(({'cls':BadType3, 'desc':'Bad type'}, TypeError, 'Pseudo type test_check.BadType3 must have an exception() method'))
		exdesc.append(({'cls':BadType4, 'desc':'Bad type'}, RuntimeError, 'Method test_check.BadType4.istype() must have only one argument'))
		exdesc.append(({'cls':BadType5, 'desc':'Bad type'}, RuntimeError, 'Method test_check.BadType5.istype() must have only one argument'))
		exdesc.append(({'cls':BadType6, 'desc':'Bad type'}, RuntimeError, 'Method test_check.BadType6.includes() must have only one argument'))
		exdesc.append(({'cls':BadType7, 'desc':'Bad type'}, RuntimeError, 'Method test_check.BadType7.includes() must have only one argument'))
		exdesc.append(({'cls':BadType8, 'desc':'Bad type'}, RuntimeError, 'Method test_check.BadType8.exception() must have only `param` and/or `param_name` arguments'))
		exdesc.append(({'cls':BadType9, 'desc':'Bad type'}, RuntimeError, 'Method test_check.BadType9.exception() must have only `param` and/or `param_name` arguments'))
		exdesc.append(({'cls':GoodType1, 'desc':'Good type'}, ))
		exdesc.append(({'cls':GoodType2, 'desc':'Good type'}, ))
		exdesc.append(({'cls':GoodType3, 'desc':'Good type'}, ))
		exdesc.append(({'cls':GoodType4, 'desc':'Good type'}, ))
		putil.test.evaluate_exception_series(exdesc, putil.check.register_new_type)

	def test_custom_data_type_addition_works(self): #pylint: disable=R0201,C0103
		""" Test that adding a custom data type to check module framework works """
		@putil.check.check_argument(putil.check.PolymorphicType([None, putil.check.NumberRange(minimum=5.0, maximum=10.0), putil.check.OneOf(['HELLO', 'WORLD']), NodeName()]))
		def func_check(par1):	#pylint: disable=C0111
			return par1
		exdesc = list()
		exdesc.append(({'par1':'node1.node2   . node3'}, ValueError, "Argument `par1` is not one of ['HELLO', 'WORLD'] (case insensitive)\nArgument `par1` is not a valid node name"))
		exdesc.append(({'par1':' node1.node2.node3'}, ValueError, "Argument `par1` is not one of ['HELLO', 'WORLD'] (case insensitive)\nArgument `par1` is not a valid node name"))
		exdesc.append(({'par1':'node1.node2.node3 '}, ValueError, "Argument `par1` is not one of ['HELLO', 'WORLD'] (case insensitive)\nArgument `par1` is not a valid node name"))
		exdesc.append(({'par1':1}, ValueError, 'Argument `par1` is not in the range [5.0, 10.0]'))
		exdesc.append(({'par1':[1, 2]}, TypeError, 'Argument `par1` is of the wrong type'))
		exdesc.append(({'par1':None}, ))
		exdesc.append(({'par1':7.5}, ))
		exdesc.append(({'par1':'node1.node2.node3'}, ))
		putil.test.evaluate_exception_series(exdesc, func_check)
