# functions.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0201,R0903,W0621

import pytest

import putil.plot


###
# Test for DataSource
###
class TestDataSource(object):
	""" Tests for abstract base class DataSource """
	# pylint: disable=R0912,W0223
	def test_compliance(self):
		class Test1(putil.plot.DataSource):
			pass
		class Test2(putil.plot.DataSource):
			def __str__(self):
				pass
		class Test3(putil.plot.DataSource):
			def __str__(self):
				pass
			def _set_dep_var(self, dep_var):
				pass
		class Test4(putil.plot.DataSource):
			def __str__(self):
				pass
			def _set_dep_var(self, dep_var):
				pass
			def _set_indep_var(self, indep_var):
				pass
		class Test5(putil.plot.DataSource):
			def __str__(self):
				pass
			def _set_dep_var(self, dep_var):
				pass
			def _set_indep_var(self, indep_var):
				pass
			dep_var = property(None, _set_dep_var)
		class Test6(putil.plot.DataSource):
			def __str__(self):
				pass
			def _set_dep_var(self, dep_var):
				pass
			def _set_indep_var(self, indep_var):
				pass
			dep_var = property(None, _set_dep_var)
			indep_var = property(None, _set_indep_var)
		with pytest.raises(TypeError) as excinfo:
			Test1()
		assert excinfo.value.message == (
			"Can't instantiate abstract class Test1 with abstract methods "
			"__str__, _set_dep_var, _set_indep_var, dep_var, indep_var"
		)
		with pytest.raises(TypeError) as excinfo:
			Test2()
		assert excinfo.value.message == (
			"Can't instantiate abstract class Test2 with abstract methods "
			"_set_dep_var, _set_indep_var, dep_var, indep_var"
		)
		with pytest.raises(TypeError) as excinfo:
			Test3()
		assert excinfo.value.message == (
			"Can't instantiate abstract class Test3 with abstract methods "
			"_set_indep_var, dep_var, indep_var"
		)
		with pytest.raises(TypeError) as excinfo:
			Test4()
		assert excinfo.value.message == (
			"Can't instantiate abstract class Test4 with abstract methods "
			"dep_var, indep_var"
		)
		with pytest.raises(TypeError) as excinfo:
			Test5()
		assert excinfo.value.message == (
			"Can't instantiate abstract class "
			"Test5 with abstract methods indep_var"
		)
		# This statement should raise no exception
		Test6()

###
# Tests for parameterized_color_space
###
class TestParameterizedColorSpace(object):
	""" Tests for function parameterized_color_space """
	# pylint: disable=W0232
	def test_param_list_wrong_type(self):
		""" Test for invalid series parameter """
		putil.test.assert_exception(
			putil.plot.parameterized_color_space,
			{'param_list':'a'},
			RuntimeError,
			'Argument `param_list` is not valid'
		)
		putil.test.assert_exception(
			putil.plot.parameterized_color_space,
			{'param_list':list()},
			TypeError,
			'Argument `param_list` is empty'
		)
		putil.test.assert_exception(
			putil.plot.parameterized_color_space,
			{'param_list':['a', None, False]},
			RuntimeError,
			'Argument `param_list` is not valid'
		)
		putil.plot.parameterized_color_space([0, 1, 2, 3.3])

	def test_offset_wrong_type(self):
		""" Test for invalid offset parameter """
		putil.test.assert_exception(
			putil.plot.parameterized_color_space,
			{'param_list':[1, 2], 'offset':'a'},
			RuntimeError,
			'Argument `offset` is not valid'
		)
		putil.test.assert_exception(
			putil.plot.parameterized_color_space,
			{'param_list':[1, 2], 'offset':-0.1},
			RuntimeError,
			'Argument `offset` is not valid'
		)
		putil.plot.parameterized_color_space([0, 1, 2, 3.3], 0.5)

	def test_color_space_wrong_type(self):
		""" Test for invalid offset parameter """
		putil.test.assert_exception(
			putil.plot.parameterized_color_space,
			{'param_list':[1, 2], 'color_space':3},
			RuntimeError,
			'Argument `color_space` is not valid'
		)
		msg = (
			"Argument `color_space` is not one of 'binary', 'Blues', 'BuGn', "
			"'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', "
			"'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', "
			"'YlOrBr' or 'YlOrRd' (case insensitive)"
		)
		putil.test.assert_exception(
			putil.plot.parameterized_color_space,
			{'param_list':[1, 2], 'color_space':'a'},
			ValueError,
			msg
		)
		# This should not raise an exception
		putil.plot.parameterized_color_space([0, 1, 2, 3.3], color_space='Blues')

	def test_function_works(self):
		""" Test for correct behavior of function """
		# pylint: disable=E1101
		import matplotlib.pyplot as plt
		color_space = plt.cm.Greys
		result = putil.plot.parameterized_color_space(
			[0, 2/3.0, 4/3.0, 2],
			0.25,
			'Greys'
		)
		assert result == [
			color_space(0.25),
			color_space(0.5),
			color_space(0.75),
			color_space(1.0)
		]
