# test_ptypes.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111

import numpy

import putil.ptypes
import putil.test


###
# Functions
###
def test_engineering_notation_number():
	""" Test EngineeringNotationNumber pseudo-type """
	putil.test.assert_exception(
		putil.ptypes.engineering_notation_number,
		{'obj':'3.12b'},
		ValueError,
		('[START CONTRACT MSG: engineering_notation_number]'
		 'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.engineering_notation_number,
		{'obj':'f'},
		ValueError,
		('[START CONTRACT MSG: engineering_notation_number]'
		 'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.engineering_notation_number,
		{'obj':'a1b'},
		ValueError,
		('[START CONTRACT MSG: engineering_notation_number]'
		 'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.engineering_notation_number,
		{'obj':'   +  123.45f  '},
		ValueError,
		('[START CONTRACT MSG: engineering_notation_number]'
		 'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.ptypes.engineering_notation_number('   +123.45f  ')
	putil.ptypes.engineering_notation_number('   -0  ')


def test_engineering_notation_suffix():
	""" Test EngineeringNotationSuffix pseudo-type """
	putil.test.assert_exception(
		putil.ptypes.engineering_notation_suffix,
		{'obj':'b'},
		ValueError,
		('[START CONTRACT MSG: engineering_notation_suffix]'
		 'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.ptypes.engineering_notation_suffix('u')


def test_non_negative_integer():
	""" Test PosInteger pseudo-type """
	putil.test.assert_exception(
		putil.ptypes.non_negative_integer,
		{'obj':'b'},
		ValueError,
		('[START CONTRACT MSG: non_negative_integer]'
		 'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.non_negative_integer,
		{'obj':-3},
		ValueError,
		('[START CONTRACT MSG: non_negative_integer]'
		 'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.non_negative_integer,
		{'obj':5.2},
		ValueError,
		('[START CONTRACT MSG: non_negative_integer]'
		 'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.ptypes.non_negative_integer(0)
	putil.ptypes.non_negative_integer(2)


def test_real_num_contract():
	""" Tests for RealNumber pseudo-type """
	putil.test.assert_exception(
		putil.ptypes.real_num,
		{'obj':'a'},
		ValueError,
		('[START CONTRACT MSG: real_num]Argument `*[argument_name]*` '
		 'is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.real_num,
		{'obj':[1, 2, 3]},
		ValueError,
		('[START CONTRACT MSG: real_num]Argument `*[argument_name]*` '
		 'is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.real_num,
		{'obj':False},
		ValueError,
		('[START CONTRACT MSG: real_num]Argument `*[argument_name]*` '
		 'is not valid[STOP CONTRACT MSG]')
	)
	putil.ptypes.real_num(1)
	putil.ptypes.real_num(2.0)

def test_positive_real_num_contract():
	""" Tests for PositiveRealNumber pseudo-type """
	putil.test.assert_exception(
		putil.ptypes.positive_real_num,
		{'obj':'a'},
		ValueError,
		('[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*`'
		 ' is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.positive_real_num,
		{'obj':[1, 2, 3]},
		ValueError,
		('[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*`'
		 ' is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.positive_real_num,
		{'obj':False},
		ValueError,
		('[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*`'
		 ' is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.positive_real_num,
		{'obj':-1},
		ValueError,
		('[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*`'
		 ' is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.positive_real_num,
		{'obj':-2.0},
		ValueError,
		('[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*`'
		 ' is not valid[STOP CONTRACT MSG]')
	)
	putil.ptypes.positive_real_num(1)
	putil.ptypes.positive_real_num(2.0)

def test_offset_range_contract():
	""" Tests for PositiveRealNumber pseudo-type """
	putil.test.assert_exception(
		putil.ptypes.offset_range,
		{'obj':'a'},
		ValueError,
		('[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` '
		 'is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.offset_range,
		{'obj':[1, 2, 3]},
		ValueError,
		('[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` '
		 'is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.offset_range,
		{'obj':False},
		ValueError,
		('[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` '
		 'is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.offset_range,
		{'obj':-0.1},
		ValueError,
		('[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` '
		 'is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.offset_range,
		{'obj':-1.1},
		ValueError,
		('[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` '
		 'is not valid[STOP CONTRACT MSG]')
	)
	putil.ptypes.offset_range(0)
	putil.ptypes.offset_range(0.5)
	putil.ptypes.offset_range(1)

def test_function_contract():
	""" Tests for Function pseudo-type """
	def func1():
		pass
	putil.test.assert_exception(
		putil.ptypes.function,
		{'obj':'a'},
		ValueError,
		('[START CONTRACT MSG: function]Argument `*[argument_name]*` '
		 'is not valid[STOP CONTRACT MSG]')
	)
	putil.ptypes.function(func1)
	putil.ptypes.function(None)

def test_real_numpy_vector_contract():
	""" Tests for RealNumpyVector pseudo-type """
	putil.test.assert_exception(
		putil.ptypes.real_numpy_vector,
		{'obj':'a'},
		ValueError,
		('[START CONTRACT MSG: real_numpy_vector]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.real_numpy_vector,
		{'obj':[1, 2, 3]},
		ValueError,
		('[START CONTRACT MSG: real_numpy_vector]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.real_numpy_vector,
		{'obj':numpy.array([])},
		ValueError,
		('[START CONTRACT MSG: real_numpy_vector]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.real_numpy_vector,
		{'obj':numpy.array([[1, 2, 3], [4, 5, 6]])},
		ValueError,
		('[START CONTRACT MSG: real_numpy_vector]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.real_numpy_vector,
		{'obj':numpy.array(['a', 'b'])},
		ValueError,
		('[START CONTRACT MSG: real_numpy_vector]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.ptypes.real_numpy_vector(numpy.array([1, 2, 3]))
	putil.ptypes.real_numpy_vector(numpy.array([10.0, 8.0, 2.0]))
	putil.ptypes.real_numpy_vector(numpy.array([10.0]))

def test_increasing_real_numpy_vector_contract():
	""" Tests for IncreasingRealNumpyVector pseudo-type """
	putil.test.assert_exception(
		putil.ptypes.increasing_real_numpy_vector,
		{'obj':'a'},
		ValueError,
		('[START CONTRACT MSG: increasing_real_numpy_vector]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.increasing_real_numpy_vector,
		{'obj':[1, 2, 3]},
		ValueError,
		('[START CONTRACT MSG: increasing_real_numpy_vector]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.increasing_real_numpy_vector,
		{'obj':numpy.array([])},
		ValueError,
		('[START CONTRACT MSG: increasing_real_numpy_vector]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.increasing_real_numpy_vector,
		{'obj':numpy.array([[1, 2, 3], [4, 5, 6]])},
		ValueError,
		('[START CONTRACT MSG: increasing_real_numpy_vector]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.increasing_real_numpy_vector,
		{'obj':numpy.array(['a', 'b'])},
		ValueError,
		('[START CONTRACT MSG: increasing_real_numpy_vector]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.increasing_real_numpy_vector,
		{'obj':numpy.array([1, 0, -3])},
		ValueError,
		('[START CONTRACT MSG: increasing_real_numpy_vector]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.increasing_real_numpy_vector,
		{'obj':numpy.array([10.0, 8.0, 2.0])},
		ValueError,
		('[START CONTRACT MSG: increasing_real_numpy_vector]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.ptypes.increasing_real_numpy_vector(numpy.array([1, 2, 3]))
	putil.ptypes.increasing_real_numpy_vector(numpy.array([10.0, 12.1, 12.5]))
	putil.ptypes.increasing_real_numpy_vector(numpy.array([10.0]))

def test_interpolation_option_contract():
	""" Tests for InterpolationOption pseudo-type """
	putil.test.assert_exception(
		putil.ptypes.interpolation_option,
		{'obj':5},
		ValueError,
		('[START CONTRACT MSG: interpolation_option]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.interpolation_option,
		{'obj':'x'},
		ValueError,
		("[START CONTRACT MSG: interpolation_option]Argument "
		 "`*[argument_name]*` is not one of ['STRAIGHT', 'STEP', 'CUBIC', "
		 "'LINREG'] (case insensitive)[STOP CONTRACT MSG]")
	)
	putil.ptypes.interpolation_option(None)
	for item in ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']:
		putil.ptypes.interpolation_option(item)
		putil.ptypes.interpolation_option(item.lower())

def test_line_style_option_contract():
	""" Tests for LineStyleOption pseudo-type """
	putil.test.assert_exception(
		putil.ptypes.line_style_option,
		{'obj':5},
		ValueError,
		('[START CONTRACT MSG: line_style_option]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.line_style_option,
		{'obj':'x'},
		ValueError,
		("[START CONTRACT MSG: line_style_option]Argument "
		 "`*[argument_name]*` is not one of ['-', '--', '-.', "
		 "':'][STOP CONTRACT MSG]")
	)
	putil.ptypes.line_style_option(None)
	for item in ['-', '--', '-.', ':']:
		putil.ptypes.line_style_option(item)

def test_color_space_option_contract():
	""" Tests for LineStyleOption pseudo-type """
	putil.test.assert_exception(
		putil.ptypes.color_space_option,
		{'obj':5},
		ValueError,
		('[START CONTRACT MSG: color_space_option]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.color_space_option,
		{'obj':'x'},
		ValueError,
		("[START CONTRACT MSG: color_space_option]Argument "
		 "`*[argument_name]*` is not one of 'binary', 'Blues', 'BuGn', "
		 "'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', "
		 "'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', "
		 "'YlOrBr' or 'YlOrRd' (case insensitive)[STOP CONTRACT MSG]")
	)
	for item in [
			'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens',
			'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd',
			'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr',
			'YlOrRd']:
		putil.ptypes.color_space_option(item)


def test_csv_data_filter_contract():
	""" Test CsvDataFilter pseudo-type """
	putil.test.assert_exception(
		putil.ptypes.csv_data_filter,
		{'obj':'a'},
		ValueError,
		('[START CONTRACT MSG: csv_data_filter]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.csv_data_filter,
		{'obj':dict()},
		ValueError,
		('[START CONTRACT MSG: csv_data_filter]Argument '
		 '`*[argument_name]*` is empty[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.csv_data_filter,
		{'obj':{5:10}},
		ValueError,
		('[START CONTRACT MSG: csv_data_filter]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.csv_data_filter,
		{'obj':{'a':{'xx':2}}},
		ValueError,
		('[START CONTRACT MSG: csv_data_filter]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.csv_data_filter,
		{'obj':{'a':[3, {'xx':2}]}},
		ValueError,
		('[START CONTRACT MSG: csv_data_filter]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.test.assert_exception(
		putil.ptypes.csv_data_filter,
		{'obj':{'b':True}},
		ValueError,
		('[START CONTRACT MSG: csv_data_filter]Argument '
		 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	)
	putil.ptypes.csv_data_filter(None)
	putil.ptypes.csv_data_filter({'x':5})
