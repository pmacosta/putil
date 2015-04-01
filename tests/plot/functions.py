# functions.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import putil.plot


###
# Tests for parameterized_color_space
###
class TestParameterizedColorSpace(object):	#pylint: disable=W0232,R0903
	""" Tests for function parameterized_color_space """
	def test_param_list_wrong_type(self):	#pylint: disable=C0103,R0201,W0621
		""" Test for invalid series parameter """
		putil.test.assert_exception(putil.plot.parameterized_color_space, {'param_list':'a'}, RuntimeError, 'Argument `param_list` is not valid')
		putil.test.assert_exception(putil.plot.parameterized_color_space, {'param_list':list()}, TypeError, 'Argument `param_list` is empty')
		putil.test.assert_exception(putil.plot.parameterized_color_space, {'param_list':['a', None, False]}, RuntimeError, 'Argument `param_list` is not valid')
		putil.plot.parameterized_color_space([0, 1, 2, 3.3])

	def test_offset_wrong_type(self):	#pylint: disable=C0103,R0201,W0621
		""" Test for invalid offset parameter """
		putil.test.assert_exception(putil.plot.parameterized_color_space, {'param_list':[1, 2], 'offset':'a'}, RuntimeError, 'Argument `offset` is not valid')
		putil.test.assert_exception(putil.plot.parameterized_color_space, {'param_list':[1, 2], 'offset':-0.1}, RuntimeError, 'Argument `offset` is not valid')
		putil.plot.parameterized_color_space([0, 1, 2, 3.3], 0.5)

	def test_color_space_wrong_type(self):	#pylint: disable=C0103,R0201,W0621
		""" Test for invalid offset parameter """
		putil.test.assert_exception(putil.plot.parameterized_color_space, {'param_list':[1, 2], 'color_space':3}, RuntimeError, 'Argument `color_space` is not valid')
		msg = "Argument `color_space` is not one of 'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr' "+\
			"or 'YlOrRd' (case insensitive)"
		putil.test.assert_exception(putil.plot.parameterized_color_space, {'param_list':[1, 2], 'color_space':'a'}, ValueError, msg)
		# This should not raise an exception
		putil.plot.parameterized_color_space([0, 1, 2, 3.3], color_space='Blues')

	def test_function_works(self):	#pylint: disable=C0103,R0201,W0621
		""" Test for correct behavior of function """
		import matplotlib.pyplot as plt
		color_space = plt.cm.Greys	#pylint: disable=E1101
		result = putil.plot.parameterized_color_space([0, 2/3.0, 4/3.0, 2], 0.25, 'Greys')
		assert result == [color_space(0.25), color_space(0.5), color_space(0.75), color_space(1.0)]
