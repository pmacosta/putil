# contracts.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0201

import numpy

import putil.plot, putil.test


###
# Contracts tests
###
class TestContracts(object):	#pylint: disable=W0232
	def test_real_num_contract(self):	#pylint: disable=W0232
		""" Tests for RealNumber pseudo-type """
		putil.test.assert_exception(putil.plot.real_num, {'obj':'a'}, ValueError, '[START CONTRACT MSG: real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.real_num, {'obj':[1, 2, 3]}, ValueError, '[START CONTRACT MSG: real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.real_num, {'obj':False}, ValueError, '[START CONTRACT MSG: real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.plot.real_num(1)
		putil.plot.real_num(2.0)

	def test_positive_real_num_contract(self):	#pylint: disable=W0232
		""" Tests for PositiveRealNumber pseudo-type """
		putil.test.assert_exception(putil.plot.positive_real_num, {'obj':'a'}, ValueError, '[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.positive_real_num, {'obj':[1, 2, 3]}, ValueError, '[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.positive_real_num, {'obj':False}, ValueError, '[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.positive_real_num, {'obj':-1}, ValueError, '[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.positive_real_num, {'obj':-2.0}, ValueError, '[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.plot.positive_real_num(1)
		putil.plot.positive_real_num(2.0)

	def test_offset_range_contract(self):	#pylint: disable=W0232
		""" Tests for PositiveRealNumber pseudo-type """
		putil.test.assert_exception(putil.plot.offset_range, {'obj':'a'}, ValueError, '[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.offset_range, {'obj':[1, 2, 3]}, ValueError, '[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.offset_range, {'obj':False}, ValueError, '[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.offset_range, {'obj':-0.1}, ValueError, '[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.offset_range, {'obj':-1.1}, ValueError, '[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.plot.offset_range(0)
		putil.plot.offset_range(0.5)
		putil.plot.offset_range(1)

	def test_function_contract(self):	#pylint: disable=W0232
		""" Tests for Function pseudo-type """
		def func1():	#pylint: disable=W0232
			pass
		putil.test.assert_exception(putil.plot.function, {'obj':'a'}, ValueError, '[START CONTRACT MSG: function]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.plot.function(func1)
		putil.plot.function(None)

	def test_real_numpy_vector_contract(self):	#pylint: disable=W0232
		""" Tests for RealNumpyVector pseudo-type """
		putil.test.assert_exception(putil.plot.real_numpy_vector, {'obj':'a'}, ValueError, '[START CONTRACT MSG: real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.real_numpy_vector, {'obj':[1, 2, 3]}, ValueError, '[START CONTRACT MSG: real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.real_numpy_vector, {'obj':numpy.array([])}, ValueError, '[START CONTRACT MSG: real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.real_numpy_vector, {'obj':numpy.array([[1, 2, 3], [4, 5, 6]])}, ValueError, '[START CONTRACT MSG: real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.real_numpy_vector, {'obj':numpy.array(['a', 'b'])}, ValueError, '[START CONTRACT MSG: real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.plot.real_numpy_vector(numpy.array([1, 2, 3]))
		putil.plot.real_numpy_vector(numpy.array([10.0, 8.0, 2.0]))
		putil.plot.real_numpy_vector(numpy.array([10.0]))

	def test_increasing_real_numpy_vector_contract(self):	#pylint: disable=W0232,C0103
		""" Tests for IncreasingRealNumpyVector pseudo-type """
		putil.test.assert_exception(putil.plot.increasing_real_numpy_vector, {'obj':'a'}, ValueError, '[START CONTRACT MSG: increasing_real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.increasing_real_numpy_vector, {'obj':[1, 2, 3]}, ValueError, '[START CONTRACT MSG: increasing_real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.increasing_real_numpy_vector, {'obj':numpy.array([])}, ValueError, '[START CONTRACT MSG: increasing_real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.increasing_real_numpy_vector, {'obj':numpy.array([[1, 2, 3], [4, 5, 6]])},\
			 ValueError, '[START CONTRACT MSG: increasing_real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.increasing_real_numpy_vector, {'obj':numpy.array(['a', 'b'])},\
			 ValueError, '[START CONTRACT MSG: increasing_real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.increasing_real_numpy_vector, {'obj':numpy.array([1, 0, -3])},\
			 ValueError, '[START CONTRACT MSG: increasing_real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.increasing_real_numpy_vector, {'obj':numpy.array([10.0, 8.0, 2.0])},\
			 ValueError, '[START CONTRACT MSG: increasing_real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.plot.increasing_real_numpy_vector(numpy.array([1, 2, 3]))
		putil.plot.increasing_real_numpy_vector(numpy.array([10.0, 12.1, 12.5]))
		putil.plot.increasing_real_numpy_vector(numpy.array([10.0]))

	def test_interpolation_option_contract(self):	#pylint: disable=W0232,C0103
		""" Tests for InterpolationOption pseudo-type """
		putil.test.assert_exception(putil.plot.interpolation_option, {'obj':5}, ValueError, '[START CONTRACT MSG: interpolation_option]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.interpolation_option, {'obj':'x'}, ValueError,\
								 "[START CONTRACT MSG: interpolation_option]Argument `*[argument_name]*` is not one of ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG'] (case insensitive)[STOP CONTRACT MSG]")
		putil.plot.interpolation_option(None)
		for item in ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']:
			putil.plot.interpolation_option(item)
			putil.plot.interpolation_option(item.lower())

	def test_line_style_option_contract(self):	#pylint: disable=W0232
		""" Tests for LineStyleOption pseudo-type """
		putil.test.assert_exception(putil.plot.line_style_option, {'obj':5}, ValueError, '[START CONTRACT MSG: line_style_option]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.line_style_option, {'obj':'x'}, ValueError,\
								 "[START CONTRACT MSG: line_style_option]Argument `*[argument_name]*` is not one of ['-', '--', '-.', ':'][STOP CONTRACT MSG]")
		putil.plot.line_style_option(None)
		for item in ['-', '--', '-.', ':']:
			putil.plot.line_style_option(item)

	def test_color_space_option_contract(self):	#pylint: disable=W0232,C0103
		""" Tests for LineStyleOption pseudo-type """
		putil.test.assert_exception(putil.plot.color_space_option, {'obj':5}, ValueError, '[START CONTRACT MSG: color_space_option]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
		putil.test.assert_exception(putil.plot.color_space_option, {'obj':'x'}, ValueError,\
								 "[START CONTRACT MSG: color_space_option]Argument `*[argument_name]*` is not one of 'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', "+\
								 "'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr' or 'YlOrRd' (case insensitive)[STOP CONTRACT MSG]")
		for item in ['binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']:
			putil.plot.color_space_option(item)

	def test_legend_position_validation(self):	#pylint: disable=W0232
		""" Tests for _legend_position_validation() pseudo-type """
		assert putil.plot.panel._legend_position_validation(5) == True	#pylint: disable=W0212
		assert putil.plot.panel._legend_position_validation('x') == True	#pylint: disable=W0212
		for item in [None, 'BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER']:
			assert putil.plot.panel._legend_position_validation(item) == False	#pylint: disable=W0212
