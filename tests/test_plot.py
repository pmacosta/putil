# test_plot.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import mock, matplotlib, matplotlib.path, numpy, pytest, scipy
from scipy.misc import imread	#pylint: disable=E0611

import gen_ref_images, putil.misc, putil.plot, putil.test


###
# Helper functions
###
IMGTOL = 1e-3
def compare_images(image_file_name1, image_file_name2):
	""" Compare two images by calculating Manhattan and Zero norms """
	# Source: http://stackoverflow.com/questions/189943/how-can-i-quantify-difference-between-two-images
	img1 = imread(image_file_name1).astype(float)
	img2 = imread(image_file_name2).astype(float)
	if img1.size != img2.size:
		m_norm, z_norm = 2*[2*IMGTOL]
	else:
		diff = img1 - img2								# elementwise for scipy arrays
		m_norm = scipy.sum(numpy.abs(diff))				# Manhattan norm
		z_norm = scipy.linalg.norm(diff.ravel(), 0)		# Zero norm
	return (m_norm, z_norm)


###
# Contracts tests
###
def test_real_num_contract():	#pylint: disable=W0232
	""" Tests for RealNumber pseudo-type """
	putil.test.assert_exception(putil.plot.real_num, {'obj':'a'}, ValueError, '[START CONTRACT MSG: real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.real_num, {'obj':[1, 2, 3]}, ValueError, '[START CONTRACT MSG: real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.real_num, {'obj':False}, ValueError, '[START CONTRACT MSG: real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.plot.real_num(1)
	putil.plot.real_num(2.0)


def test_positive_real_num_contract():	#pylint: disable=W0232
	""" Tests for PositiveRealNumber pseudo-type """
	putil.test.assert_exception(putil.plot.positive_real_num, {'obj':'a'}, ValueError, '[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.positive_real_num, {'obj':[1, 2, 3]}, ValueError, '[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.positive_real_num, {'obj':False}, ValueError, '[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.positive_real_num, {'obj':-1}, ValueError, '[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.positive_real_num, {'obj':-2.0}, ValueError, '[START CONTRACT MSG: positive_real_num]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.plot.positive_real_num(1)
	putil.plot.positive_real_num(2.0)


def test_offset_range_contract():	#pylint: disable=W0232
	""" Tests for PositiveRealNumber pseudo-type """
	putil.test.assert_exception(putil.plot.offset_range, {'obj':'a'}, ValueError, '[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.offset_range, {'obj':[1, 2, 3]}, ValueError, '[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.offset_range, {'obj':False}, ValueError, '[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.offset_range, {'obj':-0.1}, ValueError, '[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.offset_range, {'obj':-1.1}, ValueError, '[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.plot.offset_range(0)
	putil.plot.offset_range(0.5)
	putil.plot.offset_range(1)


def test_function_contract():	#pylint: disable=W0232
	""" Tests for Function pseudo-type """
	putil.test.assert_exception(putil.plot.function, {'obj':'a'}, ValueError, '[START CONTRACT MSG: function]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.plot.function(test_real_num_contract)
	putil.plot.function(None)


def test_real_numpy_vector_contract():	#pylint: disable=W0232
	""" Tests for RealNumpyVector pseudo-type """
	putil.test.assert_exception(putil.plot.real_numpy_vector, {'obj':'a'}, ValueError, '[START CONTRACT MSG: real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.real_numpy_vector, {'obj':[1, 2, 3]}, ValueError, '[START CONTRACT MSG: real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.real_numpy_vector, {'obj':numpy.array([])}, ValueError, '[START CONTRACT MSG: real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.real_numpy_vector, {'obj':numpy.array([[1, 2, 3], [4, 5, 6]])}, ValueError, '[START CONTRACT MSG: real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.real_numpy_vector, {'obj':numpy.array(['a', 'b'])}, ValueError, '[START CONTRACT MSG: real_numpy_vector]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.plot.real_numpy_vector(numpy.array([1, 2, 3]))
	putil.plot.real_numpy_vector(numpy.array([10.0, 8.0, 2.0]))
	putil.plot.real_numpy_vector(numpy.array([10.0]))


def test_increasing_real_numpy_vector_contract():	#pylint: disable=W0232,C0103
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


def test_interpolation_option_contract():	#pylint: disable=W0232,C0103
	""" Tests for InterpolationOption pseudo-type """
	putil.test.assert_exception(putil.plot.interpolation_option, {'obj':5}, ValueError, '[START CONTRACT MSG: interpolation_option]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.interpolation_option, {'obj':'x'}, ValueError,\
							 "[START CONTRACT MSG: interpolation_option]Argument `*[argument_name]*` is not one of ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG'] (case insensitive)[STOP CONTRACT MSG]")
	putil.plot.interpolation_option(None)
	for item in ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']:
		putil.plot.interpolation_option(item)
		putil.plot.interpolation_option(item.lower())


def test_line_style_option_contract():	#pylint: disable=W0232
	""" Tests for LineStyleOption pseudo-type """
	putil.test.assert_exception(putil.plot.line_style_option, {'obj':5}, ValueError, '[START CONTRACT MSG: line_style_option]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.line_style_option, {'obj':'x'}, ValueError,\
							 "[START CONTRACT MSG: line_style_option]Argument `*[argument_name]*` is not one of ['-', '--', '-.', ':'][STOP CONTRACT MSG]")
	putil.plot.line_style_option(None)
	for item in ['-', '--', '-.', ':']:
		putil.plot.line_style_option(item)


def test_color_space_option_contract():	#pylint: disable=W0232,C0103
	""" Tests for LineStyleOption pseudo-type """
	putil.test.assert_exception(putil.plot.color_space_option, {'obj':5}, ValueError, '[START CONTRACT MSG: color_space_option]Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]')
	putil.test.assert_exception(putil.plot.color_space_option, {'obj':'x'}, ValueError,\
							 "[START CONTRACT MSG: color_space_option]Argument `*[argument_name]*` is not one of 'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', "+\
							 "'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr' or 'YlOrRd' (case insensitive)[STOP CONTRACT MSG]")
	for item in ['binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']:
		putil.plot.color_space_option(item)


def test_legend_position_validation():	#pylint: disable=W0232
	""" Tests for _legend_position_validation() pseudo-type """
	assert putil.plot._legend_position_validation(5) == True	#pylint: disable=W0212
	assert putil.plot._legend_position_validation('x') == True	#pylint: disable=W0212
	for item in [None, 'BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER']:
		assert putil.plot._legend_position_validation(item) == False	#pylint: disable=W0212


###
# Tests for BasicSource
###
class TestBasicSource(object):	#pylint: disable=W0232
	""" Tests for BasicSource """
	def test_indep_min_type(self):	#pylint: disable=C0103,R0201
		""" Tests indep_min type validation """
		# __init__ path
		# Wrong types
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':numpy.array([1, 2, 3]), 'dep_var':numpy.array([10, 20, 30]), 'indep_min':'a'}, RuntimeError, 'Argument `indep_min` is not valid')
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':numpy.array([1, 2, 3]), 'dep_var':numpy.array([10, 20, 30]), 'indep_min':False}, RuntimeError, 'Argument `indep_min` is not valid')
		# Valid values, these should not raise an exception
		for param_value in [1, 2.0]:
			putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_min=param_value)
		# Managed attribute path
		# Wrong types
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))	#pylint: disable=W0612
		for param_value in ['a', False]:
			with pytest.raises(RuntimeError) as excinfo:
				obj.indep_min = param_value
			assert excinfo.value.message == 'Argument `indep_min` is not valid'
		# Valid values, these should not raise an exception
		for param_value in [1, 2.0]:
			obj.indep_min = param_value
			assert obj.indep_min == param_value

	def test_indep_max_type(self):	#pylint: disable=C0103,R0201
		""" Tests indep_max type validation """
		# __init__ path
		# Wrong types
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':numpy.array([1, 2, 3]), 'dep_var':numpy.array([10, 20, 30]), 'indep_max':'a'}, RuntimeError, 'Argument `indep_max` is not valid')
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':numpy.array([1, 2, 3]), 'dep_var':numpy.array([10, 20, 30]), 'indep_max':False}, RuntimeError, 'Argument `indep_max` is not valid')
		# Valid values, these should not raise an exception
		for param_value in [1, 2.0]:
			putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_max=param_value)
		# Managed attribute path
		# Wrong types
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))	#pylint: disable=W0612
		for param_value in ['a', False]:
			with pytest.raises(RuntimeError) as excinfo:
				obj.indep_max = param_value
			assert excinfo.value.message == 'Argument `indep_max` is not valid'
		# Valid values, these should not raise an exception
		for param_value in [1, 2.0]:
			obj.indep_max = param_value
			assert obj.indep_max == param_value

	def test_indep_min_greater_than_indep_max(self):	#pylint: disable=C0103,R0201
		""" Test if object behaves correctly when indep_min and indep_max are incongrous """
		# Assign indep_min first
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_min=0.5)
		with pytest.raises(ValueError) as excinfo:
			obj.indep_max = 0
		assert excinfo.value.message == 'Argument `indep_min` is greater than argument `indep_max`'
		# Assign indep_max first
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))
		obj.indep_max = 40
		with pytest.raises(ValueError) as excinfo:
			obj.indep_min = 50
		assert excinfo.value.message == 'Argument `indep_min` is greater than argument `indep_max`'

	def test_indep_var_type(self):	#pylint: disable=C0103,R0201
		""" Tests indep_var type validation """
		# __init__ path
		# Wrong type
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':None, 'dep_var':numpy.array([10, 20, 30])}, RuntimeError, 'Argument `indep_var` is not valid')
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':'a', 'dep_var':numpy.array([10, 20, 30])}, RuntimeError, 'Argument `indep_var` is not valid')
		# Non monotonically increasing vector
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':numpy.array([1.0, 2.0, 0.0, 3.0]), 'dep_var':numpy.array([10, 20, 30])}, RuntimeError, 'Argument `indep_var` is not valid')
		# Empty vector
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':numpy.array([]), 'dep_var':numpy.array([10, 20, 30])}, RuntimeError, 'Argument `indep_var` is not valid')
		# Valid values, these should not raise any exception
		assert (putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30])).indep_var == numpy.array([1, 2, 3])).all()
		assert (putil.plot.BasicSource(indep_var=numpy.array([4.0, 5.0, 6.0]), dep_var=numpy.array([10, 20, 30])).indep_var == numpy.array([4.0, 5.0, 6.0])).all()
		# Invalid range bounding
		# Assign indep_min via attribute
		obj = putil.plot.BasicSource(numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))
		with pytest.raises(ValueError) as excinfo:
			obj.indep_min = 45
		assert excinfo.value.message == 'Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding'
		# Assign indep_max via attribute
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))
		with pytest.raises(ValueError) as excinfo:
			obj.indep_max = 0
		assert excinfo.value.message == 'Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding'
		# Assign both indep_min and indep_max via __init__ path
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':numpy.array([1, 2, 3]), 'dep_var':numpy.array([10, 20, 30]), 'indep_min':4, 'indep_max':10},\
							  ValueError, 'Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding')
		# Managed attribute path
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))
		# Wrong type
		assert (obj.indep_var == numpy.array([1, 2, 3])).all()
		with pytest.raises(RuntimeError) as excinfo:
			obj.indep_var = None
		assert excinfo.value.message == 'Argument `indep_var` is not valid'
		with pytest.raises(RuntimeError) as excinfo:
			obj.indep_var = 'a'
		assert excinfo.value.message == 'Argument `indep_var` is not valid'
		# Non monotonically increasing vector
		with pytest.raises(RuntimeError) as excinfo:
			obj.indep_var = numpy.array([1.0, 2.0, 0.0, 3.0])
		assert excinfo.value.message == 'Argument `indep_var` is not valid'
		# Valid values, these should not raise any exception
		obj.indep_var = numpy.array([4.0, 5.0, 6.0])
		assert (obj.indep_var == numpy.array([4.0, 5.0, 6.0])).all()

	def test_dep_var_type(self):	#pylint: disable=C0103,R0201
		""" Tests dep_var type validation """
		# __init__ path
		# Wrong type
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':numpy.array([1, 2, 3]), 'dep_var':None}, RuntimeError, 'Argument `dep_var` is not valid')
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':numpy.array([1, 2, 3]), 'dep_var':'a'}, RuntimeError, 'Argument `dep_var` is not valid')
		# Empty vector
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':numpy.array([1, 2, 3]), 'dep_var':[]}, RuntimeError, 'Argument `dep_var` is not valid')
		# Valid values, these should not raise any exception
		assert (putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([1, 2, 3])).dep_var == numpy.array([1, 2, 3])).all()
		assert (putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([4.0, 5.0, 6.0])).dep_var == numpy.array([4.0, 5.0, 6.0])).all()
		# Managed attribute path
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([1, 2, 3]))
		# Wrong type
		with pytest.raises(RuntimeError) as excinfo:
			obj.dep_var = 'a'
		assert excinfo.value.message == 'Argument `dep_var` is not valid'
		# Empty vector
		with pytest.raises(RuntimeError) as excinfo:
			obj.dep_var = numpy.array([])
		assert excinfo.value.message == 'Argument `dep_var` is not valid'
		# Valid values, these should not raise any exception
		obj.dep_var = numpy.array([1, 2, 3])
		assert (obj.dep_var == numpy.array([1, 2, 3])).all()
		obj.dep_var = numpy.array([4.0, 5.0, 6.0])
		assert (obj.dep_var == numpy.array([4.0, 5.0, 6.0])).all()

	def test_indep_var_and_dep_var_do_not_have_the_same_number_of_elements(self):	#pylint: disable=C0103,R0201
		""" Tests dep_var type validation """
		# Both set at object creation
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':numpy.array([10, 20, 30]), 'dep_var':numpy.array([1, 2, 3, 4, 5, 6]), 'indep_min':30, 'indep_max':50},\
			  ValueError, 'Arguments `indep_var` and `dep_var` must have the same number of elements')
		putil.test.assert_exception(putil.plot.BasicSource, {'indep_var':numpy.array([10, 20, 30]), 'dep_var':numpy.array([1, 2]), 'indep_min':30, 'indep_max':50},\
			  ValueError, 'Arguments `indep_var` and `dep_var` must have the same number of elements')
		# indep_var set first
		obj = putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30, 40, 50, 60]), dep_var=numpy.array([1, 2, 3, 4, 5, 6]), indep_min=30, indep_max=50)
		with pytest.raises(ValueError) as excinfo:
			obj.dep_var = numpy.array([100, 200, 300])
		assert excinfo.value.message == 'Arguments `indep_var` and `dep_var` must have the same number of elements'
		# dep_var set first
		obj = putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30]), dep_var=numpy.array([100, 200, 300]), indep_min=30, indep_max=50)
		with pytest.raises(ValueError) as excinfo:
			obj.indep_var = numpy.array([10, 20, 30, 40, 50, 60])
		assert excinfo.value.message == 'Arguments `indep_var` and `dep_var` must have the same number of elements'

	def test_complete(self):	#pylint: disable=C0103,R0201
		""" Test that _complete() method behaves correctly """
		obj = putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30]), dep_var=numpy.array([100, 200, 300]), indep_min=0, indep_max=50)
		obj._indep_var = None	#pylint: disable=W0212
		assert obj._complete() == False	#pylint: disable=W0212
		obj = putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30]), dep_var=numpy.array([100, 200, 300]), indep_min=0, indep_max=50)
		assert obj._complete() == True	#pylint: disable=W0212

	def test_str(self):	#pylint: disable=C0103,R0201
		""" Test that str behaves correctly """
		# Full set
		obj = str(putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_min=-10, indep_max=20.0))
		ref = 'Independent variable minimum: -10\nIndependent variable maximum: 20.0\nIndependent variable: [ 1, 2, 3 ]\nDependent variable: [ 10, 20, 30 ]'
		assert obj == ref
		# indep_min not set
		obj = str(putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_max=20.0))
		ref = 'Independent variable minimum: -inf\nIndependent variable maximum: 20.0\nIndependent variable: [ 1, 2, 3 ]\nDependent variable: [ 10, 20, 30 ]'
		assert obj == ref
		# indep_max not set
		obj = str(putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_min=-10))
		ref = 'Independent variable minimum: -10\nIndependent variable maximum: +inf\nIndependent variable: [ 1, 2, 3 ]\nDependent variable: [ 10, 20, 30 ]'
		assert obj == ref
		# indep_min and indep_max not set
		obj = str(putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30])))
		ref = 'Independent variable minimum: -inf\nIndependent variable maximum: +inf\nIndependent variable: [ 1, 2, 3 ]\nDependent variable: [ 10, 20, 30 ]'
		assert obj == ref

	def test_cannot_delete_attributes(self):	#pylint: disable=C0103,R0201
		""" Test that del method raises an exception on all class attributes """
		obj = putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30]), dep_var=numpy.array([100, 200, 300]))
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_min
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_max
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_var
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.dep_var
		assert excinfo.value.message == "can't delete attribute"


###
# Tests for CsvSource
###
def write_csv_file(file_handle):	#pylint: disable=C0111
	file_handle.write('Col1,Col2,Col3,Col4,Col5,Col6,Col7,Col8\n')
	file_handle.write('0,1,2,3,,5,1,7\n')
	file_handle.write('0,2,4,5,,4,2,6\n')
	file_handle.write('0,3,1,8,,3,3,5\n')
	file_handle.write('1,1,5,7,8,0,4,4\n')
	file_handle.write('1,2,3,7,9,7,5,3\n')


class TestCsvSource(object):	#pylint: disable=W0232,R0904
	""" Tests for CsvSource """
	def test_indep_min_type(self):	#pylint: disable=R0201
		""" Tests indep_min type validation """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# __init__ path
			# Wrong types
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col2', 'indep_min':'a'}, RuntimeError, 'Argument `indep_min` is not valid')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col2', 'indep_min':False}, RuntimeError, 'Argument `indep_min` is not valid')
			# Valid values, these should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_min=1)
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_min=2.0)
			# Managed attribute path
			# Wrong types
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_min=2.0)
			for param_value in ['a', False]:
				with pytest.raises(RuntimeError) as excinfo:
					obj.indep_min = param_value
				assert excinfo.value.message == 'Argument `indep_min` is not valid'
			# Valid values, these should not raise an exception
			for param_value in [1, 2.0]:
				obj.indep_min = param_value
				assert obj.indep_min == param_value

	def test_indep_max_type(self):	#pylint: disable=R0201
		""" Tests indep_max type validation """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# __init__ path
			# Wrong types
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col2', 'indep_max':'a'}, RuntimeError, 'Argument `indep_max` is not valid')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col2', 'indep_max':False}, RuntimeError, 'Argument `indep_max` is not valid')
			# Valid values, these should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_max=1)
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_max=2.0)
			# Managed attribute path
			# Wrong types
			obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))
			for param_value in ['a', False]:
				with pytest.raises(RuntimeError) as excinfo:
					obj.indep_max = param_value
				assert excinfo.value.message == 'Argument `indep_max` is not valid'
			# Valid values, these should not raise an exception
			for param_value in [1, 2.0]:
				obj.indep_max = param_value
				assert obj.indep_max == param_value

	def test_indep_min_greater_than_indep_max(self):	#pylint: disable=R0201,C0103
		""" Test if object behaves correctly when indep_min and indep_max are incongrous """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# Assign indep_min first
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_min=0.5)
			with pytest.raises(ValueError) as excinfo:
				obj.indep_max = 0
			assert excinfo.value.message == 'Argument `indep_min` is greater than argument `indep_max`'
			# Assign indep_max first
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_max=10)
			with pytest.raises(ValueError) as excinfo:
				obj.indep_min = 50
			assert excinfo.value.message == 'Argument `indep_min` is greater than argument `indep_max`'

	def test_file_name_wrong_type(self):	#pylint: disable=C0103,R0201
		""" Test if object behaves correctly when file_name is not valid """
		# This assignment should raise an exception
		putil.test.assert_exception(putil.plot.CsvSource, {'file_name':5, 'indep_col_label':'Col7', 'dep_col_label':'Col2'}, RuntimeError, 'Argument `file_name` is not valid')
		putil.test.assert_exception(putil.plot.CsvSource, {'file_name':None, 'indep_col_label':'Col7', 'dep_col_label':'Col2'}, RuntimeError, 'Argument `file_name` is not valid')

	def test_file_does_not_exist(self):	#pylint: disable=C0103,R0201
		""" Test if object behaves correctly when CSV file does not exist """
		file_name = 'nonexistent_file_name.csv'
		putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col2'}, IOError, 'File `{0}` could not be found'.format(file_name))

	def test_file_exists(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when CSV file exists """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2')

	def test_data_filter_wrong_type(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when dfilter is not valid """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# This assignment should raise an exception
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col2', 'dfilter':5}, RuntimeError, 'Argument `dfilter` is not valid')
			# This assignment should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', dfilter=None)

	def test_data_filter_operation(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when data filter and file name are given """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# This assignment should raise an exception
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col2', 'dfilter':{'Col99':500}},\
				ValueError, 'Column Col99 in data filter not found in comma-separated file {0} header'.format(file_name))
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', dfilter={'Col1':0})

	def test_indep_col_label_wrong_type(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when indep_col_label is not valid """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# These assignments should raise an exception
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':None, 'dep_col_label':'Col2'}, RuntimeError, 'Argument `indep_col_label` is not valid')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':5, 'dep_col_label':'Col2'}, RuntimeError, 'Argument `indep_col_label` is not valid')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col99', 'dep_col_label':'Col2'},\
				ValueError, 'Column Col99 (independent column label) could not be found in comma-separated file {0} header'.format(file_name))
			# These assignments should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', dfilter={'Col1':0})

	def test_dep_col_label_wrong_type(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when dep_col_label is not valid """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# This assignment should raise an exception
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':None}, RuntimeError, 'Argument `dep_col_label` is not valid')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':5}, RuntimeError, 'Argument `dep_col_label` is not valid')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col99'},\
				ValueError, 'Column Col99 (dependent column label) could not be found in comma-separated file {0} header'.format(file_name))
			# These assignments should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col3')

	def test_empty_indep_var_after_filter(self):	#pylint: disable=R0201,C0103
		""" Test if object behaves correctly when the independent variable is empty after data filter is applied """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':10}}, ValueError, 'Filtered independent variable is empty')

	def test_empty_dep_var_after_filter(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when the dependent variable is empty after data filter is applied """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col5', 'dfilter':{'Col1':0}}, ValueError, 'Filtered dependent variable is empty')

	def test_data_reversed(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when the independent dat is descending order """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col6', dep_col_label='Col3', dfilter={'Col1':0})
		assert (obj.indep_var == numpy.array([3, 4, 5])).all()
		assert (obj.dep_var == numpy.array([1, 4, 2])).all()

	def test_fproc_wrong_type(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when fproc is not valid """
		def fproc1():	#pylint: disable=C0111
			return numpy.array([1]), numpy.array([1])
		def fproc2(*args):	#pylint: disable=C0111,W0613
			return numpy.array([1]), numpy.array([1])
		def fproc3(*args, **kwargs):	#pylint: disable=C0111,W0613
			return numpy.array([1, 2, 3, 4, 5]), numpy.array([1, 2, 3, 1, 2])
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# These assignments should raise an exception
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col2', 'fproc':5}, RuntimeError, 'Argument `fproc` is not valid')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col2', 'fproc':fproc1},\
				ValueError, 'Argument `fproc` (function fproc1) does not have at least 2 arguments')
			# These assignments should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc=fproc2)
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc=fproc3)

	def test_fproc_wrong_return(self):	#pylint: disable=R0201,R0912,R0914
		""" Test if object behaves correctly when fproc returns the wrong type and/or number of arguments """
		def fproc1(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return True
		def fproc2(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 2])]
		def fproc3(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 2]), numpy.array([1, 2])]
		def fproc4(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [5, numpy.array([1, 2])]
		def fproc5(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [numpy.array([3, 2, 1]), numpy.array([1, 2, 3])]
		def fproc6(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 2]), 6]
		def fproc7(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 2]), numpy.array([3, 1])]
		def fproc8(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [numpy.array([]), numpy.array([3, 1])]
		def fproc9(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 3]), numpy.array([])]
		def fproc10(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [numpy.array([None, None]), numpy.array([3, 1])]
		def fproc11(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 3]), numpy.array([None, None])]
		def fproc12(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 3]), numpy.array([1, 2, 3])]
		def fproc13(indep_var, dep_var, par1):	#pylint: disable=C0111,W0613
			raise RuntimeError('Test exception message #1')
		def fproc14(indep_var, dep_var, par1=None):	#pylint: disable=C0111,W0613
			raise RuntimeError('Test exception message #2')
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# These assignments should raise an exception
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc1},\
				TypeError, 'Argument `fproc` (function fproc1) return value is not valid')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc2},\
				RuntimeError, 'Argument `fproc` (function fproc2) returned an illegal number of values')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc4}, TypeError, 'Processed independent variable is not valid')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc5}, TypeError, 'Processed independent variable is not valid')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc6}, TypeError, 'Processed dependent variable is not valid')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc8}, ValueError, 'Processed independent variable is empty')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc9}, ValueError, 'Processed dependent variable is empty')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc10}, ValueError, 'Processed independent variable is empty')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc11}, ValueError, 'Processed dependent variable is empty')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc12},\
				ValueError, 'Processed independent and dependent variables are of different length')
			msg = 'Processing function fproc13 raised an exception when called with the following arguments:\n'
			msg += 'indep_var: [ 1, 2, 3 ]\n'
			msg += 'dep_var: [ 1, 2, 3 ]\n'
			msg += 'fproc_eargs: \n'
			msg += '   par1: 13\n'
			msg += 'Exception error: Test exception message #1'
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc13, 'fproc_eargs':{'par1':13}}, RuntimeError, msg)
			#with pytest.raises(RuntimeError) as excinfo:
			#	putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc13, fproc_eargs={'par1':13})
			#msg = 'Processing function fproc13 raised an exception when called with the following arguments:\n'
			#msg += 'indep_var: [ 1, 2, 3 ]\n'
			#msg += 'dep_var: [ 1, 2, 3 ]\n'
			#msg += 'fproc_eargs: \n'
			#msg += '   par1: 13\n'
			#msg += 'Exception error: Test exception message #1'
			#assert excinfo.value.message == msg
			#with pytest.raises(RuntimeError) as excinfo:
			#	putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc14, fproc_eargs={})
			msg = 'Processing function fproc14 raised an exception when called with the following arguments:\n'
			msg += 'indep_var: [ 1, 2, 3 ]\n'
			msg += 'dep_var: [ 1, 2, 3 ]\n'
			msg += 'fproc_eargs: None\n'
			msg += 'Exception error: Test exception message #2'
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc14, 'fproc_eargs':{}}, RuntimeError, msg)
			#assert excinfo.value.message == msg
			#with pytest.raises(RuntimeError) as excinfo:
			#	putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc14)
			#assert excinfo.value.message == msg
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col2', 'dep_col_label':'Col3', 'dfilter':{'Col1':0}, 'fproc':fproc14}, RuntimeError, msg)
			# These assignments should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc3)
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc7)

	def test_fproc_eargs_wrong_type(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when fprog_eargs is not valid """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# This assignment should raise an exception
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col2', 'fproc_eargs':5},\
				RuntimeError, 'Argument `fproc_eargs` is not valid')
			# These assignments should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc_eargs=None)
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc_eargs={'arg1':23})

	def test_fproc_eargs_argument_name_validation(self):	#pylint: disable=R0201,C0103
		""" Test if object behaves correctly when checking if the arguments in the fprog_eargs dictionary exist """
		def fproc1(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 2]), numpy.array([1, 2])]
		def fproc2(indep_var, dep_var, par1, par2):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 2]), numpy.array([1, 2])]
		def fproc3(indep_var, dep_var, **kwargs):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 2]), numpy.array([1, 2])]
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# These assignments should raise an exception
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col2', 'fproc':fproc1, 'fproc_eargs':{'par1':5}},\
				ValueError, 'Extra argument `par1` not found in argument `fproc` (function fproc1) definition')
			putil.test.assert_exception(putil.plot.CsvSource, {'file_name':file_name, 'indep_col_label':'Col7', 'dep_col_label':'Col2', 'fproc':fproc2, 'fproc_eargs':{'par3':5}},\
				ValueError, 'Extra argument `par3` not found in argument `fproc` (function fproc2) definition')
			# These assignments should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc=fproc3, fproc_eargs={'par99':5})

	def test_fproc_works(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when executing function defined in fproc argument with extra arguments defined in fproc_eargs argument """
		def fproc1(indep_var, dep_var, indep_offset, dep_offset):	#pylint: disable=C0111,W0613
			return indep_var+indep_offset, dep_var+dep_offset
		with putil.misc.TmpFile(write_csv_file) as file_name:
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc1, fproc_eargs={'indep_offset':3, 'dep_offset':100})
		assert (obj.indep_var == numpy.array([4, 5, 6])).all()
		assert (obj.dep_var == numpy.array([102, 104, 101])).all()

	def test_str(self):	#pylint: disable=R0201
		""" Test that str behaves correctly """
		def fproc1(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return indep_var*1e-3, dep_var+1
		def fproc2(indep_var, dep_var, par1, par2):	#pylint: disable=C0111,W0613
			return indep_var+par1, dep_var-par2
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# dfilter
			obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3'))
			ref = 'File name: {0}\nData filter: \n   Col1: 0\nIndependent column label: Col2\nDependent column label: Col3\nProcessing function: None\nProcessing function extra arguments: None\n'.format(file_name)
			ref += 'Independent variable minimum: -inf\nIndependent variable maximum: +inf\nIndependent variable: [ 1, 2, 3 ]\nDependent variable: [ 2, 4, 1 ]'
			assert obj == ref
			# fproc
			obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3', indep_min=2e-3, indep_max=200, fproc=fproc1))
			ref = 'File name: {0}\nData filter: \n   Col1: 0\nIndependent column label: Col2\nDependent column label: Col3\nProcessing function: fproc1\nProcessing function extra arguments: None\n'.format(file_name)
			ref += 'Independent variable minimum: 0.002\nIndependent variable maximum: 200\nIndependent variable: [ 0.002, 0.003 ]\nDependent variable: [ 5, 2 ]'
			assert obj == ref
			# fproc_eargs
			obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3', indep_min=-2, indep_max=200, fproc=fproc2, fproc_eargs={'par1':3, 'par2':4}))
			ref = 'File name: {0}\nData filter: \n   Col1: 0\nIndependent column label: Col2\nDependent column label: Col3\nProcessing function: fproc2\nProcessing function extra arguments: \n   par1: 3\n   par2: 4\n'.format(file_name)
			ref += 'Independent variable minimum: -2\nIndependent variable maximum: 200\nIndependent variable: [ 4, 5, 6 ]\nDependent variable: [ -2, 0, -3 ]'
			assert obj == ref
			# indep_min set
			obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3', indep_min=-2, fproc=fproc2, fproc_eargs={'par1':3, 'par2':4}))
			ref = 'File name: {0}\nData filter: \n   Col1: 0\nIndependent column label: Col2\nDependent column label: Col3\nProcessing function: fproc2\nProcessing function extra arguments: \n   par1: 3\n   par2: 4\n'.format(file_name)
			ref += 'Independent variable minimum: -2\nIndependent variable maximum: +inf\nIndependent variable: [ 4, 5, 6 ]\nDependent variable: [ -2, 0, -3 ]'
			assert obj == ref
			# indep_max set
			obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3', indep_min=-2, indep_max=200, fproc=fproc2, fproc_eargs={'par1':3, 'par2':4}))
			ref = 'File name: {0}\nData filter: \n   Col1: 0\nIndependent column label: Col2\nDependent column label: Col3\nProcessing function: fproc2\nProcessing function extra arguments: \n   par1: 3\n   par2: 4\n'.format(file_name)
			ref += 'Independent variable minimum: -2\nIndependent variable maximum: 200\nIndependent variable: [ 4, 5, 6 ]\nDependent variable: [ -2, 0, -3 ]'
			assert obj == ref

	def test_complete(self):	#pylint: disable=R0201
		""" Test that _complete() method behaves correctly """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', )
			obj._indep_var = None	#pylint: disable=W0212
			assert obj._complete() == False	#pylint: disable=W0212
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', )
			assert obj._complete() == True	#pylint: disable=W0212

	def test_cannot_delete_attributes(self):	#pylint: disable=R0201
		""" Test that del method raises an exception on all class attributes """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2')
			with pytest.raises(AttributeError) as excinfo:
				del obj.file_name
			assert excinfo.value.message == "can't delete attribute"
			with pytest.raises(AttributeError) as excinfo:
				del obj.dfilter
			assert excinfo.value.message == "can't delete attribute"
			with pytest.raises(AttributeError) as excinfo:
				del obj.indep_col_label
			assert excinfo.value.message == "can't delete attribute"
			with pytest.raises(AttributeError) as excinfo:
				del obj.dep_col_label
			assert excinfo.value.message == "can't delete attribute"
			with pytest.raises(AttributeError) as excinfo:
				del obj.fproc
			assert excinfo.value.message == "can't delete attribute"
			with pytest.raises(AttributeError) as excinfo:
				del obj.fproc_eargs
			assert excinfo.value.message == "can't delete attribute"
			with pytest.raises(AttributeError) as excinfo:
				del obj.indep_min
			assert excinfo.value.message == "can't delete attribute"
			with pytest.raises(AttributeError) as excinfo:
				del obj.indep_max
			assert excinfo.value.message == "can't delete attribute"
			with pytest.raises(AttributeError) as excinfo:
				del obj.indep_var
			assert excinfo.value.message == "can't delete attribute"
			with pytest.raises(AttributeError) as excinfo:
				del obj.dep_var
			assert excinfo.value.message == "can't delete attribute"


###
# Tests for Series
###
@pytest.fixture
def default_source():
	""" Provides a default source to be used in teseting the putil.plot.Series() class """
	return putil.plot.BasicSource(indep_var=numpy.array([5, 6, 7, 8]), dep_var=numpy.array([0, -10, 5, 4]))


class TestSeries(object):	#pylint: disable=W0232
	""" Tests for Series """
	def test_data_source_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test if object behaves correctly when checking the data_source argument """
		class TestSource(object):	#pylint: disable=C0111,R0903,W0612
			def __init__(self):
				pass
		# These assignments should raise an exception
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3, 4]), dep_var=numpy.array([10, 20, 30, 40]))
		obj._indep_var = None	#pylint: disable=W0212
		putil.test.assert_exception(putil.plot.Series, {'data_source':obj, 'label':'test'}, RuntimeError, 'Argument `data_source` is not fully specified')
		putil.test.assert_exception(putil.plot.Series, {'data_source':5, 'label':'test'}, RuntimeError, 'Argument `data_source` does not have an `indep_var` attribute')
		obj = TestSource()
		obj.indep_var = numpy.array([5, 6, 7, 8])	#pylint: disable=W0201
		putil.test.assert_exception(putil.plot.Series, {'data_source':obj, 'label':'test'}, RuntimeError, 'Argument `data_source` does not have an `dep_var` attribute')
		# These assignments should not raise an exception
		obj.dep_var = numpy.array([0, -10, 5, 4])	#pylint: disable=W0201
		putil.plot.Series(data_source=None, label='test')
		putil.plot.Series(data_source=obj, label='test')
		obj = putil.plot.Series(data_source=default_source, label='test')
		assert (obj.indep_var == numpy.array([5, 6, 7, 8])).all()
		assert (obj.dep_var == numpy.array([0, -10, 5, 4])).all()

	def test_label_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test label data validation """
		# This assignments should raise an exception
		putil.test.assert_exception(putil.plot.Series, {'data_source':default_source, 'label':5}, RuntimeError, 'Argument `label` is not valid')
		putil.plot.Series(data_source=default_source, label=None)
		obj = putil.plot.Series(data_source=default_source, label='test')
		assert obj.label == 'test'

	def test_color_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test color data validation """
		# This assignments should raise an exception
		putil.test.assert_exception(putil.plot.Series, {'data_source':default_source, 'label':'test', 'color':default_source}, RuntimeError, 'Argument `color` is not valid')
		invalid_color_list = ['invalid_color_name', -0.01, 1.1, '#ABCDEX', (-1, 1, 1), [1, 2, 0.5], [1, 1, 2], (-1, 1, 1, 1), [1, 2, 0.5, 0.5], [1, 1, 2, 1], (1, 1, 1, -1)]
		valid_color_list = [None, 'moccasin', 0.5, '#ABCDEF', (0.5, 0.5, 0.5), [0.25, 0.25, 0.25, 0.25]]
		for color in invalid_color_list:
			putil.test.assert_exception(putil.plot.Series, {'data_source':default_source, 'label':'test', 'color':color}, TypeError, 'Invalid color specification')
		# These assignments should not raise an exception
		putil.plot.Series(data_source=default_source, label='test', color=None)
		for color in valid_color_list:
			obj = putil.plot.Series(data_source=default_source, label='test', color=color)
			assert obj.color == (color.lower() if isinstance(color, str) else color)

	def test_marker_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test marker data validation """
		# This assignments should raise an exception
		putil.test.assert_exception(putil.plot.Series, {'data_source':default_source, 'label':'test', 'marker':'hello'}, RuntimeError, 'Argument `marker` is not valid')
		# These assignments should not raise an exception
		obj = putil.plot.Series(data_source=default_source, label='test', marker=None)
		assert obj.marker == None
		obj = putil.plot.Series(data_source=default_source, label='test', marker='D')
		assert obj.marker == 'D'
		obj = putil.plot.Series(data_source=default_source, label='test')
		assert obj.marker == 'o'

	def test_interp_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test interp data validation """
		# These assignments should raise an exception
		putil.test.assert_exception(putil.plot.Series, {'data_source':default_source, 'label':'test', 'interp':5}, RuntimeError, 'Argument `interp` is not valid')
		putil.test.assert_exception(putil.plot.Series, {'data_source':default_source, 'label':'test', 'interp':'NOT_AN_OPTION'}, ValueError, "Argument `interp` is not one of ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG'] (case insensitive)")
		source_obj = putil.plot.BasicSource(indep_var=numpy.array([5]), dep_var=numpy.array([0]))
		putil.test.assert_exception(putil.plot.Series, {'data_source':source_obj, 'label':'test', 'interp':'CUBIC'}, ValueError, 'At least 4 data points are needed for CUBIC interpolation')
		# These assignments should not raise an exception
		putil.plot.Series(data_source=source_obj, label='test', interp='STRAIGHT')
		putil.plot.Series(data_source=source_obj, label='test', interp='STEP')
		putil.plot.Series(data_source=source_obj, label='test', interp='LINREG')
		putil.plot.Series(data_source=default_source, label='test', interp=None)
		obj = putil.plot.Series(data_source=default_source, label='test', interp='straight')
		assert obj.interp == 'STRAIGHT'
		obj = putil.plot.Series(data_source=default_source, label='test', interp='StEp')
		assert obj.interp == 'STEP'
		obj = putil.plot.Series(data_source=default_source, label='test', interp='CUBIC')
		assert obj.interp == 'CUBIC'
		obj = putil.plot.Series(data_source=default_source, label='test', interp='linreg')
		assert obj.interp == 'LINREG'
		obj = putil.plot.Series(data_source=default_source, label='test')
		assert obj.interp == 'CUBIC'

	def test_line_style_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test line_style data validation """
		# These assignments should raise an exception
		putil.test.assert_exception(putil.plot.Series, {'data_source':default_source, 'label':'test', 'line_style':5}, RuntimeError, 'Argument `line_style` is not valid')
		putil.test.assert_exception(putil.plot.Series, {'data_source':default_source, 'label':'test', 'line_style':'x'}, ValueError, "Argument `line_style` is not one of ['-', '--', '-.', ':']")
		# These assignments should not raise an exception
		putil.plot.Series(data_source=default_source, label='test', line_style=None)
		obj = putil.plot.Series(data_source=default_source, label='test', line_style='-')
		assert obj.line_style == '-'
		obj = putil.plot.Series(data_source=default_source, label='test', line_style='--')
		assert obj.line_style == '--'
		obj = putil.plot.Series(data_source=default_source, label='test', line_style='-.')
		assert obj.line_style == '-.'
		obj = putil.plot.Series(data_source=default_source, label='test', line_style=':')
		assert obj.line_style == ':'
		obj = putil.plot.Series(data_source=default_source, label='test')
		assert obj.line_style == '-'

	def test_secondary_axis_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test secondary_axis data validation """
		# This assignments should raise an exception
		putil.test.assert_exception(putil.plot.Series, {'data_source':default_source, 'label':'test', 'secondary_axis':5}, RuntimeError, 'Argument `secondary_axis` is not valid')
		# These assignments should not raise an exception
		putil.plot.Series(data_source=default_source, label='test', secondary_axis=None)
		obj = putil.plot.Series(data_source=default_source, label='test', secondary_axis=False)
		assert obj.secondary_axis == False
		obj = putil.plot.Series(data_source=default_source, label='test', secondary_axis=True)
		assert obj.secondary_axis == True
		obj = putil.plot.Series(data_source=default_source, label='test')
		assert obj.secondary_axis == False

	def test_calculate_curve(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test that interpolated curve is calculated when apropriate """
		obj = putil.plot.Series(data_source=default_source, label='test', interp=None)
		assert (obj.interp_indep_var, obj.interp_dep_var) == (None, None)
		obj = putil.plot.Series(data_source=default_source, label='test', interp='STRAIGHT')
		assert (obj.interp_indep_var, obj.interp_dep_var) == (None, None)
		obj = putil.plot.Series(data_source=default_source, label='test', interp='STEP')
		assert (obj.interp_indep_var, obj.interp_dep_var) == (None, None)
		obj = putil.plot.Series(data_source=default_source, label='test', interp='CUBIC')
		assert (obj.interp_indep_var, obj.interp_dep_var) != (None, None)
		obj = putil.plot.Series(data_source=default_source, label='test', interp='LINREG')
		assert (obj.interp_indep_var, obj.interp_dep_var) != (None, None)
		obj = putil.plot.Series(data_source=default_source, label='test')
		assert (obj.interp_indep_var, obj.interp_dep_var) != (None, None)

	def test_scale_indep_var(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test that independent variable scaling works """
		obj = putil.plot.Series(data_source=default_source, label='test', interp=None)
		assert obj.scaled_indep_var is not None
		assert obj.scaled_dep_var is not None
		assert obj.scaled_interp_indep_var is None
		assert obj.scaled_interp_dep_var is None
		obj._scale_indep_var(2)	#pylint: disable=W0212
		obj._scale_dep_var(4)	#pylint: disable=W0212
		assert (obj.scaled_indep_var == numpy.array([2.5, 3.0, 3.5, 4.0])).all()
		assert (obj.scaled_dep_var == numpy.array([0.0, -2.5, 1.25, 1.0])).all()
		assert obj.scaled_interp_indep_var is None
		assert obj.scaled_interp_dep_var is None
		obj.interp = 'CUBIC'
		assert (obj.scaled_indep_var == numpy.array([2.5, 3.0, 3.5, 4.0])).all()
		assert (obj.scaled_dep_var == numpy.array([0.0, -2.5, 1.25, 1.0])).all()
		assert obj.scaled_interp_indep_var is not None
		assert obj.scaled_interp_dep_var is not None

	def test_plottable(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test that object behaves properl when a series is not plottable """
		putil.test.assert_exception(putil.plot.Series, {'data_source':default_source, 'label':'test', 'marker':None, 'interp':None, 'line_style':None}, RuntimeError, 'Series options make it not plottable')
		obj = putil.plot.Series(data_source=default_source, label='test', marker='o', interp='CUBIC', line_style=None)
		with pytest.raises(RuntimeError) as excinfo:
			obj.marker = None
		assert excinfo.value.message == 'Series options make it not plottable'
		obj = putil.plot.Series(data_source=default_source, label='test', marker='None', interp='CUBIC', line_style='-')
		with pytest.raises(RuntimeError) as excinfo:
			obj.interp = None
		assert excinfo.value.message == 'Series options make it not plottable'
		obj = putil.plot.Series(data_source=default_source, label='test', marker=' ', interp='CUBIC', line_style='-')
		with pytest.raises(RuntimeError) as excinfo:
			obj.line_style = None
		assert excinfo.value.message == 'Series options make it not plottable'

	def test_str(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test that str behaves correctly """
		marker_list = [{'value':None, 'string':'None'}, {'value':'o', 'string':'o'}, {'value':matplotlib.path.Path([(0, 0), (1, 1)]), 'string':'matplotlib.path.Path object'}, {'value':[(0, 0), (1, 1)], 'string':'[(0, 0), (1, 1)]'},
				 {'value':r'$a_{b}$', 'string':r'$a_{b}$'}, {'value':matplotlib.markers.TICKLEFT, 'string':'matplotlib.markers.TICKLEFT'}]
		for marker_dict in marker_list:
			obj = putil.plot.Series(data_source=default_source, label='test', marker=marker_dict['value'])
			ret = ''
			ret += 'Data source: putil.plot.BasicSource class object\n'
			ret += 'Independent variable: [ 5, 6, 7, 8 ]\n'
			ret += 'Dependent variable: [ 0, -10, 5, 4 ]\n'
			ret += 'Label: test\n'
			ret += 'Color: k\n'
			ret += 'Marker: {0}\n'.format(marker_dict['string'])
			ret += 'Interpolation: CUBIC\n'
			ret += 'Line style: -\n'
			ret += 'Secondary axis: False'
			if str(obj) != ret:
				print 'Object:'
				print str(obj)
				print
				print 'Comparison:'
				print ret
			assert str(obj) == ret

	def test_cannot_delete_attributes(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		obj = putil.plot.Series(data_source=default_source, label='test')
		with pytest.raises(AttributeError) as excinfo:
			del obj.data_source
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.label
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.color
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.marker
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.interp
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.line_style
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.secondary_axis
		assert excinfo.value.message == "can't delete attribute"

	def test_images(self, tmpdir):	#pylint: disable=C0103,R0201,W0621
		""" Compare images to verify correct plotting of series """
		tmpdir.mkdir('test_images')
		images_dict_list = gen_ref_images.unittest_series_images(mode='test', test_dir=str(tmpdir))
		for images_dict in images_dict_list:
			ref_file_name = images_dict['ref_file_name']
			test_file_name = images_dict['test_file_name']
			metrics = compare_images(ref_file_name, test_file_name)
			result = (metrics[0] < IMGTOL) and (metrics[1] < IMGTOL)
			# print 'Comparison: {0} with {1} -> {2} {3}'.format(ref_file_name, test_file_name, result, metrics)
			assert result


###
# Tests for Panel
###
@pytest.fixture
def default_series(default_source):	#pylint: disable=W0621
	""" Provides a default series object to be used in teseting the putil.plot.Panel() class """
	return putil.plot.Series(data_source=default_source, label='test series')


class TestPanel(object):	#pylint: disable=W0232
	""" Tests for Series """
	def test_primary_axis_label_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test panel_primary_axis data validation """
		putil.test.assert_exception(putil.plot.Panel, {'series':default_series, 'primary_axis_label':5}, RuntimeError, 'Argument `primary_axis_label` is not valid')
		# This assignment should not raise an exception
		putil.plot.Panel(series=default_series, primary_axis_label=None)
		obj = putil.plot.Panel(series=default_series, primary_axis_label='test')
		assert obj.primary_axis_label == 'test'

	def test_primary_axis_units_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test panel_primary_axis data validation """
		putil.test.assert_exception(putil.plot.Panel, {'series':default_series, 'primary_axis_units':5}, RuntimeError, 'Argument `primary_axis_units` is not valid')
		# These assignments should not raise an exception
		putil.plot.Panel(series=default_series, primary_axis_units=None)
		obj = putil.plot.Panel(series=default_series, primary_axis_units='test')
		assert obj.primary_axis_units == 'test'

	def test_secondary_axis_label_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test panel_secondary_axis data validation """
		putil.test.assert_exception(putil.plot.Panel, {'series':default_series, 'secondary_axis_label':5}, RuntimeError, 'Argument `secondary_axis_label` is not valid')
		# These assignments should not raise an exception
		putil.plot.Panel(series=default_series, secondary_axis_label=None)
		obj = putil.plot.Panel(series=default_series, secondary_axis_label='test')
		assert obj.secondary_axis_label == 'test'

	def test_secondary_axis_units_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test panel_secondary_axis data validation """
		putil.test.assert_exception(putil.plot.Panel, {'series':default_series, 'secondary_axis_units':5}, RuntimeError, 'Argument `secondary_axis_units` is not valid')
		# These assignments should not raise an exception
		putil.plot.Panel(series=default_series, secondary_axis_units=None)
		obj = putil.plot.Panel(series=default_series, secondary_axis_units='test')
		assert obj.secondary_axis_units == 'test'

	def test_log_dep_axis_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test log_dep_axis data validation """
		putil.test.assert_exception(putil.plot.Panel, {'series':default_series, 'log_dep_axis':5}, RuntimeError, 'Argument `log_dep_axis` is not valid')
		putil.test.assert_exception(putil.plot.Panel, {'series':default_series, 'log_dep_axis':True}, ValueError, 'Series item 0 cannot be plotted in a logarithmic axis because it contains negative data points')
		# These assignments should not raise an exception
		non_negative_data_source = putil.plot.BasicSource(indep_var=numpy.array([5, 6, 7, 8]), dep_var=numpy.array([0.1, 10, 5, 4]))
		non_negative_series = putil.plot.Series(data_source=non_negative_data_source, label='non-negative data series')
		obj = putil.plot.Panel(series=default_series, log_dep_axis=False)
		assert obj.log_dep_axis == False
		obj = putil.plot.Panel(series=non_negative_series, log_dep_axis=True)
		assert obj.log_dep_axis == True
		obj = putil.plot.Panel(series=default_series)
		assert obj.log_dep_axis == False

	def test_show_indep_axis_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test show_indep_axis data validation """
		putil.test.assert_exception(putil.plot.Panel, {'series':default_series, 'show_indep_axis':5}, RuntimeError, 'Argument `show_indep_axis` is not valid')
		# These assignments should not raise an exception
		obj = putil.plot.Panel(series=default_series, show_indep_axis=False)
		assert obj.show_indep_axis == False
		obj = putil.plot.Panel(series=default_series, show_indep_axis=True)
		assert obj.show_indep_axis == True
		obj = putil.plot.Panel(series=default_series)
		assert obj.show_indep_axis == False

	def test_legend_props_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test legend_props data validation """
		putil.test.assert_exception(putil.plot.Panel, {'series':default_series, 'legend_props':5}, RuntimeError, 'Argument `legend_props` is not valid')
		putil.test.assert_exception(putil.plot.Panel, {'series':default_series, 'legend_props':{'not_a_valid_prop':5}}, ValueError, 'Illegal legend property `not_a_valid_prop`')
		msg = "Legend property `pos` is not one of ['BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER'] (case insensitive)"
		putil.test.assert_exception(putil.plot.Panel, {'series':default_series, 'legend_props':{'pos':5}}, TypeError, msg)
		putil.test.assert_exception(putil.plot.Panel, {'series':default_series, 'legend_props':{'cols':-1}}, RuntimeError, 'Legend property `cols` is not valid')
		# These assignments should not raise an exception
		obj = putil.plot.Panel(series=default_series, legend_props={'pos':'upper left'})
		assert obj.legend_props == {'pos':'UPPER LEFT', 'cols':1}
		obj = putil.plot.Panel(series=default_series, legend_props={'cols':3})
		assert obj.legend_props == {'pos':'BEST', 'cols':3}
		obj = putil.plot.Panel(series=default_series)
		assert obj.legend_props == {'pos':'BEST', 'cols':1}

	def test_intelligent_ticks(self):	#pylint: disable=C0103,R0201,W0621,R0915
		""" Test that intelligent_tick methods works for all scenarios """
		# 0
		# Tight = True
		# One sample
		vector = numpy.array([35e-6])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([31.5, 35, 38.5], ['31.5', '35.0', '38.5'], 31.5, 38.5, 1e-6, 'u')
		# print obj
		# 1
		# Scaling with more data samples after 1.0
		vector = numpy.array([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6], ['0.8', '0.9', '1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6'], 0.8, 1.6, 1, ' ')
		# print obj
		# 2
		# Regular, should not have any scaling
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([1, 2, 3, 4, 5, 6, 7], ['1', '2', '3', '4', '5', '6', '7'], 1, 7, 1, ' ')
		# print obj
		# 3
		# Regular, should not have any scaling
		vector = numpy.array([10, 20, 30, 40, 50, 60, 70])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([10, 20, 30, 40, 50, 60, 70], ['10', '20', '30', '40', '50', '60', '70'], 10, 70, 1, ' ')
		# print obj
		# 4
		# Scaling
		vector = numpy.array([1000, 2000, 3000, 4000, 5000, 6000, 7000])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([1, 2, 3, 4, 5, 6, 7], ['1', '2', '3', '4', '5', '6', '7'], 1, 7, 1e3, 'k')
		# print obj
		# 5
		# Scaling
		vector = numpy.array([200e6, 300e6, 400e6, 500e6, 600e6, 700e6, 800e6, 900e6, 1000e6])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([200, 300, 400, 500, 600, 700, 800, 900, 1000], ['200', '300', '400', '500', '600', '700', '800', '900', '1k'], 200, 1000, 1e6, 'M')
		# print obj
		# 6
		# No tick marks to place all data points on grid, space uniformely
		vector = numpy.array([105, 107.7, 215, 400.2, 600, 700, 800, 810, 820, 830, 840, 850, 900, 905])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([105.0, 193.8888888889, 282.7777777778, 371.6666666667, 460.5555555556, 549.4444444444, 638.3333333333, 727.2222222222, 816.1111111111, 905.0],
						   ['105', '194', '283', '372', '461', '549', '638', '727', '816', '905'], 105, 905, 1, ' ')
		# print obj
		# 7
		# Ticks marks where some data points can be on grid
		vector = numpy.array([10, 20, 30, 40, 41, 50, 60, 62, 70, 75.5, 80])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([10, 20, 30, 40, 50, 60, 70, 80], ['10', '20', '30', '40', '50', '60', '70', '80'], 10, 80, 1, ' ')
		# print obj
		# 8
		# Tight = False
		# One sample
		vector = numpy.array([1e-9])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=False)	#pylint: disable=W0212
		assert obj == ([0.9, 1, 1.1], ['0.9', '1.0', '1.1'], 0.9, 1.1, 1e-9, 'n')
		# print obj
		# 9
		# Scaling with more data samples after 1.0
		vector = numpy.array([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=False)	#pylint: disable=W0212
		assert obj == ([0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7], ['0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7'], 0.7, 1.7, 1, ' ')
		# print obj
		# 10
		# Scaling with more data samples before 1.0
		vector = numpy.array([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=False)	#pylint: disable=W0212
		assert obj == ([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2], ['0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2'], 0.2, 1.2, 1, ' ')
		# print obj
		# 11
		# Regular, with some overshoot
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot._intelligent_ticks(vector, min(vector), 7.5, tight=False)	#pylint: disable=W0212
		assert obj == ([0, 1, 2, 3, 4, 5, 6, 7, 8], ['0', '1', '2', '3', '4', '5', '6', '7', '8'], 0, 8, 1, ' ')
		# print obj
		# 12
		# Regular, with some undershoot
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot._intelligent_ticks(vector, 0.1, max(vector), tight=False)	#pylint: disable=W0212
		assert obj == ([0, 1, 2, 3, 4, 5, 6, 7, 8], ['0', '1', '2', '3', '4', '5', '6', '7', '8'], 0, 8, 1, ' ')
		# print obj
		# 13
		# Regular, with large overshoot
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot._intelligent_ticks(vector, min(vector), 20, tight=False)	#pylint: disable=W0212
		assert obj == ([0, 1, 2, 3, 4, 5, 6, 7, 8], ['0', '1', '2', '3', '4', '5', '6', '7', '8'], 0, 8, 1, ' ')
		# print obj
		# 14
		# Regular, with large undershoot
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot._intelligent_ticks(vector, -10, max(vector), tight=False)	#pylint: disable=W0212
		assert obj == ([0, 1, 2, 3, 4, 5, 6, 7, 8], ['0', '1', '2', '3', '4', '5', '6', '7', '8'], 0, 8, 1, ' ')
		# print obj
		# 15
		# Scaling, minimum as reference
		vector = 1e9+(numpy.array([10, 20, 30, 40, 50, 60, 70, 80])*1e3)
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([1.00001, 1.00002, 1.00003, 1.00004, 1.00005, 1.00006, 1.00007, 1.00008], ['1.00001', '1.00002', '1.00003', '1.00004', '1.00005', '1.00006', '1.00007', '1.00008'], 1.00001, 1.00008, 1e9, 'G')
		# print obj
		# 16
		# Scaling, delta as reference
		vector = numpy.array([10.1e6, 20e6, 30e6, 40e6, 50e6, 60e6, 70e6, 80e6, 90e6, 100e6, 20.22e9])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([10.1, 2255.6444444444, 4501.1888888889, 6746.7333333333, 8992.2777777778, 11237.8222222222, 13483.3666666667, 15728.9111111111, 17974.4555555556, 20220.0], \
						   ['10.1', '2.3k', '4.5k', '6.7k', '9.0k', '11.2k', '13.5k', '15.7k', '18.0k', '20.2k'], 10.1, 20220.0, 1e6, 'M')
		# print obj
		# 17
		# Scaling, maximum as reference
		vector = (numpy.array([0.7, 0.8, 0.9, 1.1, 1.2, 1.3, 1.4, 1.5])*1e12)
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5], ['0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3', '1.4', '1.5'], 0.7, 1.5, 1e12, 'T')
		# print obj
		# 18
		# Log axis
		# Tight False
		vector = (numpy.array([2e3, 3e4, 4e5, 5e6, 6e7]))
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True, log_axis=True)	#pylint: disable=W0212
		assert obj == ([1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1k', '10k', '100k'], 1, 100000, 1000, 'k')
		# 19
		# Tight True
		# Left side
		vector = (numpy.array([2e3, 3e4, 4e5, 5e6, 6e7]))
		obj = putil.plot._intelligent_ticks(vector, 500, max(vector), tight=False, log_axis=True)	#pylint: disable=W0212
		assert obj == ([1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1k', '10k', '100k'], 1, 100000, 1000, 'k')
		# print obj
		# 20
		# Right side
		vector = (numpy.array([2e3, 3e4, 4e5, 5e6, 6e7]))
		obj = putil.plot._intelligent_ticks(vector, min(vector), 1e9, tight=False, log_axis=True)	#pylint: disable=W0212
		assert obj == ([1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1k', '10k', '100k'], 1, 100000, 1000, 'k')
		# print obj
		# 21
		# Both
		# Right side
		vector = (numpy.array([2e3, 3e4, 4e5, 5e6, 6e7]))
		obj = putil.plot._intelligent_ticks(vector, 500, 1e9, tight=False, log_axis=True)	#pylint: disable=W0212
		assert obj == ([1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1k', '10k', '100k'], 1, 100000, 1000, 'k')
		# print obj

	def test_series(self):	#pylint: disable=C0103,R0201,W0621,R0914,R0915
		""" Test that the panel dependent axis are correctly set """
		ds1_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300, 400]), dep_var=numpy.array([1, 2, 3, 4]))
		ds2_obj = putil.plot.BasicSource(indep_var=numpy.array([300, 400, 500, 600, 700]), dep_var=numpy.array([3, 4, 5, 6, 7]))
		ds3_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300]), dep_var=numpy.array([20, 40, 50]))
		ds4_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300]), dep_var=numpy.array([10, 25, 35]))
		ds5_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300, 400]), dep_var=numpy.array([10, 20, 30, 40]))
		ds6_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300, 400]), dep_var=numpy.array([20, 30, 40, 100]))
		ds7_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300, 400]), dep_var=numpy.array([20, 30, 40, 50]))
		ds8_obj = putil.plot.BasicSource(indep_var=numpy.array([100]), dep_var=numpy.array([20]))
		series1_obj = putil.plot.Series(data_source=ds1_obj, label='series 1', interp=None)
		series2_obj = putil.plot.Series(data_source=ds2_obj, label='series 2', interp=None)
		series3_obj = putil.plot.Series(data_source=ds3_obj, label='series 3', interp=None, secondary_axis=True)
		series4_obj = putil.plot.Series(data_source=ds4_obj, label='series 4', interp=None, secondary_axis=True)
		series5_obj = putil.plot.Series(data_source=ds5_obj, label='series 5', interp=None, secondary_axis=True)
		series6_obj = putil.plot.Series(data_source=ds6_obj, label='series 6', interp=None, secondary_axis=True)
		series7_obj = putil.plot.Series(data_source=ds7_obj, label='series 7', interp=None)
		series8_obj = putil.plot.Series(data_source=ds8_obj, label='series 8', interp=None)
		# 0-8: Linear primary and secondary axis, with multiple series on both
		panel_obj = putil.plot.Panel(series=[series1_obj, series2_obj, series3_obj, series4_obj])
		assert (panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, True)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_locs == [0, 0.8, 1.6, 2.4, 3.2, 4.0, 4.8, 5.6, 6.4, 7.2, 8.0])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_labels == ['0.0', '0.8', '1.6', '2.4', '3.2', '4.0', '4.8', '5.6', '6.4', '7.2', '8.0'])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (0, 8)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' ')	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_locs == [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_labels == ['5', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55'])	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (5, 55)	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (1, ' ')	#pylint: disable=W0212
		# 9-17: Linear primary axis with multiple series	#pylint: disable=W0212
		panel_obj = putil.plot.Panel(series=[series1_obj, series2_obj])
		assert (panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, False)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_locs == [0, 1, 2, 3, 4, 5, 6, 7, 8])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_labels == ['0', '1', '2', '3', '4', '5', '6', '7', '8'])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (0, 8)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' ')	#pylint: disable=W0212
		assert panel_obj._secondary_dep_var_locs == None	#pylint: disable=W0212
		assert panel_obj._secondary_dep_var_labels == None	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (None, None)	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (None, None)	#pylint: disable=W0212
		# 18-26: Linear secondary axis with multiple series on both
		panel_obj = putil.plot.Panel(series=[series3_obj, series4_obj])
		assert (panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (False, True)	#pylint: disable=W0212
		assert panel_obj._primary_dep_var_locs == None	#pylint: disable=W0212
		assert panel_obj._primary_dep_var_labels == None	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (None, None)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (None, None)	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_locs == [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_labels == ['5', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55'])	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (5, 55)	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (1, ' ')	#pylint: disable=W0212
		# 27-35: Logarithmic primary and secondary axis, with multiple series on both
		panel_obj = putil.plot.Panel(series=[series1_obj, series5_obj], log_dep_axis=True)
		assert (panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, True)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_locs == [0.9, 1, 10, 100])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_labels == ['', '1', '10', '100'])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (0.9, 100)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' ')	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_locs == [0.9, 1, 10, 100])	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_labels == ['', '1', '10', '100'])	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (0.9, 100)	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (1, ' ')	#pylint: disable=W0212
		# 36-44: Logarithmic primary axis (bottom point at decade edge)
		panel_obj = putil.plot.Panel(series=[series1_obj], log_dep_axis=True)
		assert (panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, False)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_locs == [0.9, 1, 10])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_labels == ['', '1', '10'])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (0.9, 10)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' ')	#pylint: disable=W0212
		assert panel_obj._secondary_dep_var_locs == None	#pylint: disable=W0212
		assert panel_obj._secondary_dep_var_labels == None	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (None, None)	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (None, None)	#pylint: disable=W0212
		# 45-53: Logarithmic secondary axis (top point at decade edge)
		panel_obj = putil.plot.Panel(series=[series6_obj], log_dep_axis=True)
		assert (panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (False, True)	#pylint: disable=W0212
		assert panel_obj._primary_dep_var_locs == None	#pylint: disable=W0212
		assert panel_obj._primary_dep_var_labels == None	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (None, None)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (None, None)	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_locs == [10, 100, 110])	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_labels == ['10', '100', ''])	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (10, 110)	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (1, ' ')	#pylint: disable=W0212
		# 54-62: Logarithmic secondary axis (points not at decade edge)
		panel_obj = putil.plot.Panel(series=[series7_obj], log_dep_axis=True)
		assert (panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, False)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_locs == [10, 100])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_labels == ['10', '100'])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (10, 100)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' ')	#pylint: disable=W0212
		assert panel_obj._secondary_dep_var_locs == None	#pylint: disable=W0212
		assert panel_obj._secondary_dep_var_labels == None	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (None, None)	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (None, None)	#pylint: disable=W0212
		# 63-71: Logarithmic secondary axis (1 point)
		panel_obj = putil.plot.Panel(series=[series8_obj], log_dep_axis=True)
		assert (panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, False)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_locs == [18, 20, 22])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_labels == ['18', '20', '22'])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (18, 22)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' ')	#pylint: disable=W0212
		assert panel_obj._secondary_dep_var_locs == None	#pylint: disable=W0212
		assert panel_obj._secondary_dep_var_labels == None	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (None, None)	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (None, None)	#pylint: disable=W0212
		# 72-80: Linear secondary axis (1 point)
		panel_obj = putil.plot.Panel(series=[series8_obj], log_dep_axis=False)
		assert (panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, False)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_locs == [18, 20, 22])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_labels == ['18', '20', '22'])	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (18, 22)	#pylint: disable=W0212
		assert (panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' ')	#pylint: disable=W0212
		assert panel_obj._secondary_dep_var_locs == None	#pylint: disable=W0212
		assert panel_obj._secondary_dep_var_labels == None	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (None, None)	#pylint: disable=W0212
		assert (panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (None, None)	#pylint: disable=W0212

	def test_complete(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test that _complete() method behaves correctly """
		obj = putil.plot.Panel(series=None)
		assert obj._complete() == False	#pylint: disable=W0212
		obj.series = default_series
		assert obj._complete() == True	#pylint: disable=W0212

	def test_scale_series(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test that series scaling function behaves correctly """
		#return putil.plot.Series(data_source=default_source, label='test series')
		source_obj = putil.plot.BasicSource(indep_var=numpy.array([5, 6, 7, 8]), dep_var=numpy.array([4.2, 8, 10, 4]))
		series_obj = putil.plot.Series(data_source=source_obj, label='test', secondary_axis=True)
		panel1_obj = putil.plot.Panel(series=series_obj)
		panel2_obj = putil.plot.Panel(series=[default_series, series_obj])
		obj = putil.plot.Panel(series=default_series)
		obj._scale_dep_var(2, None)	#pylint: disable=W0212
		assert (abs(obj.series[0].scaled_dep_var-[0, -5, 2.5, 2]) < 1e-10).all() == True
		obj._scale_dep_var(2, 5)	#pylint: disable=W0212
		assert (abs(obj.series[0].scaled_dep_var-[0, -5, 2.5, 2]) < 1e-10).all() == True
		panel1_obj._scale_dep_var(None, 2)	#pylint: disable=W0212
		assert (abs(panel1_obj.series[0].scaled_dep_var-[2.1, 4, 5, 2]) < 1e-10).all() == True
		panel2_obj._scale_dep_var(4, 5)	#pylint: disable=W0212
		assert ((abs(panel2_obj.series[0].scaled_dep_var-[0, -2.5, 1.25, 1]) < 1e-10).all(), (abs(panel2_obj.series[1].scaled_dep_var-[0.84, 1.6, 2, 0.8]) < 1e-10).all()) == (True, True)

	def test_str(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test that str behaves correctly """
		obj = putil.plot.Panel(series=None)
		ret = 'Series: None\n'
		ret += 'Primary axis label: not specified\n'
		ret += 'Primary axis units: not specified\n'
		ret += 'Secondary axis label: not specified\n'
		ret += 'Secondary axis units: not specified\n'
		ret += 'Logarithmic dependent axis: False\n'
		ret += 'Show independent axis: False\n'
		ret += 'Legend properties:\n'
		ret += '   pos: BEST\n'
		ret += '   cols: 1'
		assert str(obj) == ret
		obj = putil.plot.Panel(series=default_series, primary_axis_label='Output', primary_axis_units='Volts', secondary_axis_label='Input', secondary_axis_units='Watts', show_indep_axis=True)
		ret = 'Series 0:\n'
		ret += '   Data source: putil.plot.BasicSource class object\n'
		ret += '   Independent variable: [ 5, 6, 7, 8 ]\n'
		ret += '   Dependent variable: [ 0, -10, 5, 4 ]\n'
		ret += '   Label: test series\n'
		ret += '   Color: k\n'
		ret += '   Marker: o\n'
		ret += '   Interpolation: CUBIC\n'
		ret += '   Line style: -\n'
		ret += '   Secondary axis: False\n'
		ret += 'Primary axis label: Output\n'
		ret += 'Primary axis units: Volts\n'
		ret += 'Secondary axis label: Input\n'
		ret += 'Secondary axis units: Watts\n'
		ret += 'Logarithmic dependent axis: False\n'
		ret += 'Show independent axis: True\n'
		ret += 'Legend properties:\n'
		ret += '   pos: BEST\n'
		ret += '   cols: 1'
		assert str(obj) == ret

	def test_cannot_delete_attributes(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		obj = putil.plot.Panel(series=default_series)
		with pytest.raises(AttributeError) as excinfo:
			del obj.series
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.primary_axis_label
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.secondary_axis_label
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.primary_axis_units
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.secondary_axis_units
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.log_dep_axis
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.legend_props
		assert excinfo.value.message == "can't delete attribute"

	def test_images(self, tmpdir):	#pylint: disable=C0103,R0201,W0621
		""" Compare images to verify correct plotting of panel """
		tmpdir.mkdir('test_images')
		images_dict_list = gen_ref_images.unittest_panel_images(mode='test', test_dir=str(tmpdir))
		for images_dict in images_dict_list:
			ref_file_name = images_dict['ref_file_name']
			test_file_name = images_dict['test_file_name']
			metrics = compare_images(ref_file_name, test_file_name)
			result = (metrics[0] < IMGTOL) and (metrics[1] < IMGTOL)
			# print 'Comparison: {0} with {1} -> {2} {3}'.format(ref_file_name, test_file_name, result, metrics)
			assert result


###
# Tests for Figure
###
@pytest.fixture
def default_panel(default_series):	#pylint: disable=W0621
	""" Provides a default panel object to be used in teseting the putil.plot.Figure() class """
	return putil.plot.Panel(series=default_series, primary_axis_label='Primary axis', primary_axis_units='A', secondary_axis_label='Secondary axis', secondary_axis_units='B')


class TestFigure(object):	#pylint: disable=W0232,R0903
	""" Tests for Figure """
	def test_indep_var_label_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test indep_var_label data validation """
		putil.test.assert_exception(putil.plot.Figure, {'panels':default_panel, 'indep_var_label':5}, RuntimeError, 'Argument `indep_var_label` is not valid')
		# These assignments should not raise an exception
		putil.plot.Figure(panels=default_panel, indep_var_label=None)
		putil.plot.Figure(panels=default_panel, indep_var_label='sec')
		obj = putil.plot.Figure(panels=default_panel, indep_var_label='test')
		assert obj.indep_var_label == 'test'

	def test_indep_var_units_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test indep_var_units data validation """
		putil.test.assert_exception(putil.plot.Figure, {'panels':default_panel, 'indep_var_units':5}, RuntimeError, 'Argument `indep_var_units` is not valid')
		# These assignments should not raise an exception
		putil.plot.Figure(panels=default_panel, indep_var_units=None)
		putil.plot.Figure(panels=default_panel, indep_var_units='sec')
		obj = putil.plot.Figure(panels=default_panel, indep_var_units='test')
		assert obj.indep_var_units == 'test'

	def test_title_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test title data validation """
		putil.test.assert_exception(putil.plot.Figure, {'panels':default_panel, 'title':5}, RuntimeError, 'Argument `title` is not valid')
		# These assignments should not raise an exception
		putil.plot.Figure(panels=default_panel, title=None)
		putil.plot.Figure(panels=default_panel, title='sec')
		obj = putil.plot.Figure(panels=default_panel, title='test')
		assert obj.title == 'test'

	def test_log_indep_axis_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test log_indep_axis data validation """
		putil.test.assert_exception(putil.plot.Figure, {'panels':default_panel, 'log_indep_axis':5}, RuntimeError, 'Argument `log_indep_axis` is not valid')
		negative_data_source = putil.plot.BasicSource(indep_var=numpy.array([-5, 6, 7, 8]), dep_var=numpy.array([0.1, 10, 5, 4]))
		negative_series = putil.plot.Series(data_source=negative_data_source, label='negative data series')
		negative_panel = putil.plot.Panel(series=negative_series)
		putil.test.assert_exception(putil.plot.Figure, {'panels':negative_panel, 'log_indep_axis':True}, ValueError, 'Figure cannot cannot be plotted with a logarithmic independent axis because panel 0, series 0 contains '+\
							  'negative independent data points')
		# These assignments should not raise an exception
		obj = putil.plot.Figure(panels=default_panel, log_indep_axis=False)
		assert obj.log_indep_axis == False
		obj = putil.plot.Figure(panels=default_panel, log_indep_axis=True)
		assert obj.log_indep_axis == True
		obj = putil.plot.Figure(panels=default_panel)
		assert obj.log_indep_axis == False

	def test_fig_width_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test figure width data validation """
		putil.test.assert_exception(putil.plot.Figure, {'panels':default_panel, 'fig_width':'a'}, RuntimeError, 'Argument `fig_width` is not valid')
		# These assignments should not raise an exception
		obj = putil.plot.Figure(panels=None)
		assert obj.fig_width == None
		obj = putil.plot.Figure(panels=default_panel)
		assert obj.fig_width-6.08 < 1e-10
		obj.fig_width = 5
		assert obj.fig_width == 5

	def test_fig_height_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test figure height data validation """
		putil.test.assert_exception(putil.plot.Figure, {'panels':default_panel, 'fig_height':'a'}, RuntimeError, 'Argument `fig_height` is not valid')
		# These assignments should not raise an exception
		obj = putil.plot.Figure(panels=None)
		assert obj.fig_height == None
		obj = putil.plot.Figure(panels=default_panel)
		assert obj.fig_height-4.31 < 1e-10
		obj.fig_height = 5
		assert obj.fig_height == 5

	def test_panels_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test panel data validation """
		putil.test.assert_exception(putil.plot.Figure, {'panels':5}, RuntimeError, 'Argument `panels` is not valid')
		putil.test.assert_exception(putil.plot.Figure, {'panels':[default_panel, putil.plot.Panel(series=None)]}, TypeError, 'Panel 1 is not fully specified')
		# These assignments should not raise an exception
		putil.plot.Figure(panels=None)
		putil.plot.Figure(panels=default_panel)

	def test_fig_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test fig attribute """
		obj = putil.plot.Figure(panels=None)
		assert obj.fig == None
		obj = putil.plot.Figure(panels=default_panel)
		assert isinstance(obj.fig, matplotlib.figure.Figure)

	def test_axes_list(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test axes_list attribute """
		obj = putil.plot.Figure(panels=None)
		assert obj.axes_list == list()
		obj = putil.plot.Figure(panels=default_panel)
		comp_list = list()
		for num, axis_dict in enumerate(obj.axes_list):
			if (axis_dict['number'] == num) and ((axis_dict['primary'] is None) or (isinstance(axis_dict['primary'], matplotlib.axes.Axes))) and \
					((axis_dict['secondary'] is None) or (isinstance(axis_dict['secondary'], matplotlib.axes.Axes))):
				comp_list.append(True)
		assert comp_list == len(obj.axes_list)*[True]

	def test_specified_figure_size_too_small(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test that method behaves correctly when requested figure size is too small """
		putil.test.assert_exception(putil.plot.Figure, {'panels':default_panel, 'indep_var_label':'Input', 'indep_var_units':'Amps', 'title':'My graph', 'fig_width':0.1, 'fig_height':200},\
							  RuntimeError, 'Figure size is too small: minimum width = 6.08, minimum height 4.99')
		putil.test.assert_exception(putil.plot.Figure, {'panels':default_panel, 'indep_var_label':'Input', 'indep_var_units':'Amps', 'title':'My graph', 'fig_width':200, 'fig_height':0.1},\
							  RuntimeError, 'Figure size is too small: minimum width = 6.08, minimum height 4.99')
		putil.test.assert_exception(putil.plot.Figure, {'panels':default_panel, 'indep_var_label':'Input', 'indep_var_units':'Amps', 'title':'My graph', 'fig_width':0.1, 'fig_height':0.1},\
							  RuntimeError, 'Figure size is too small: minimum width = 6.08, minimum height 4.99')

	def test_complete(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test that _complete() method behaves correctly """
		obj = putil.plot.Figure(panels=None)
		assert obj._complete() == False	#pylint: disable=W0212
		obj.panels = default_panel
		assert obj._complete() == True	#pylint: disable=W0212
		obj = putil.plot.Figure(panels=None)
		putil.test.assert_exception(obj.show, {}, RuntimeError, 'Figure object is not fully specified')

	def test_str(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test that str behaves correctly """
		obj = putil.plot.Figure(panels=None)
		ret = 'Panels: None\n'
		ret += 'Independent variable label: not specified\n'
		ret += 'Independent variable units: not specified\n'
		ret += 'Logarithmic independent axis: False\n'
		ret += 'Title: not specified\n'
		ret += 'Figure width: None\n'
		ret += 'Figure height: None\n'
		assert str(obj) == ret
		obj = putil.plot.Figure(panels=default_panel, indep_var_label='Input', indep_var_units='Amps', title='My graph')
		ret = 'Panel 0:\n'
		ret += '   Series 0:\n'
		ret += '      Data source: putil.plot.BasicSource class object\n'
		ret += '      Independent variable: [ 5, 6, 7, 8 ]\n'
		ret += '      Dependent variable: [ 0, -10, 5, 4 ]\n'
		ret += '      Label: test series\n'
		ret += '      Color: k\n'
		ret += '      Marker: o\n'
		ret += '      Interpolation: CUBIC\n'
		ret += '      Line style: -\n'
		ret += '      Secondary axis: False\n'
		ret += '   Primary axis label: Primary axis\n'
		ret += '   Primary axis units: A\n'
		ret += '   Secondary axis label: Secondary axis\n'
		ret += '   Secondary axis units: B\n'
		ret += '   Logarithmic dependent axis: False\n'
		ret += '   Show independent axis: False\n'
		ret += '   Legend properties:\n'
		ret += '      pos: BEST\n'
		ret += '      cols: 1\n'
		ret += 'Independent variable label: Input\n'
		ret += 'Independent variable units: Amps\n'
		ret += 'Logarithmic independent axis: False\n'
		ret += 'Title: My graph\n'
		ret += 'Figure width: 6.08\n'
		ret += 'Figure height: 4.99\n'
		assert str(obj) == ret

	def test_cannot_delete_attributes(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		obj = putil.plot.Figure(panels=default_panel)
		with pytest.raises(AttributeError) as excinfo:
			del obj.panels
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_var_label
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_var_units
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.title
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.log_indep_axis
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.fig_width
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.fig_height
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.fig
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.axes_list
		assert excinfo.value.message == "can't delete attribute"

	def test_show(self, default_panel, capsys):	#pylint: disable=C0103,R0201,W0621
		""" Test that show() method behaves correctly """
		def mock_show():	#pylint: disable=C0111
			print 'show called'
		obj = putil.plot.Figure(panels=default_panel)
		with mock.patch('putil.plot.plt.show', side_effect=mock_show):
			obj.show()
		out, _ = capsys.readouterr()
		assert out == 'show called\n'

	def test_images(self, tmpdir):	#pylint: disable=C0103,R0201,W0621
		""" Compare images to verify correct plotting of figure """
		tmpdir.mkdir('test_images')
		images_dict_list = gen_ref_images.unittest_figure_images(mode='test', test_dir=str(tmpdir))
		for images_dict in images_dict_list:
			ref_file_name = images_dict['ref_file_name']
			test_file_name = images_dict['test_file_name']
			metrics = compare_images(ref_file_name, test_file_name)
			result = (metrics[0] < IMGTOL) and (metrics[1] < IMGTOL)
			# print 'Comparison: {0} with {1} -> {2} {3}'.format(ref_file_name, test_file_name, result, metrics)
			assert result


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
