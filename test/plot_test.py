# plot_test.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.plot unit tests
"""

import scipy
import numpy
import pytest
import matplotlib
import matplotlib.path
from scipy.misc import imread	#pylint: disable=E0611

import putil.plot
import putil.misc
import gen_ref_images

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
# Reusable tests
###
def indep_min_max_type(func, param):
	""" Tests indep_min and indep_max type validation """
	comp = list()
	# __init__ path
	# Wrong types
	for param_value in ['a', False]:
		with pytest.raises(TypeError) as excinfo:
			func(**{param:param_value})	#pylint: disable=W0142
		comp.append(excinfo.value.message == 'Argument `{0}` is of the wrong type'.format(param))
	# Valid values, these should not raise an exception
	for param_value in [None, 1, 2.0]:
		kwarg = {param:param_value}	#pylint: disable=W0612
		exec('comp.append(func(**kwarg).{0} == {1})'.format(param, param_value))	#pylint: disable=W0142,W0122
	# Managed attribute path
	# Wrong types
	obj = func()	#pylint: disable=W0612
	for param_value in ['a', False]:
		with pytest.raises(TypeError) as excinfo:
			exec("obj.{0} = {1}".format(param, "'{0}'".format(param_value) if isinstance(param_value, str) else param_value))	#pylint: disable=W0122
		comp.append(excinfo.value.message == 'Argument `{0}` is of the wrong type'.format(param))
	# Valid values, these should not raise an exception
	for param_value in [None, 1, 2.0]:
		exec('obj.{0} = {1}'.format(param, param_value))	#pylint: disable=W0122
		exec('comp.append(obj.{0} == {1})'.format(param, param_value))	#pylint: disable=W0122
	assert comp == 10*[True]

def indep_min_greater_than_indep_max(func):	#pylint: disable=C0103
	""" Test if object behaves correctly when indep_min and indep_max are incongrous """
	comp = list()
	# Assign indep_min first
	obj = func(indep_min=45)
	with pytest.raises(ValueError) as excinfo:
		obj.indep_max = 0
	comp.append(excinfo.value.message == 'Argument `indep_min` is greater than argument `indep_max`')
	# Assign indep_max first
	obj = func()
	obj.indep_max = 40
	with pytest.raises(ValueError) as excinfo:
		obj.indep_min = 50
	comp.append(excinfo.value.message == 'Argument `indep_min` is greater than argument `indep_max`')
	assert comp == 2*[True]

###
# Tests for BasicSource
###
class TestBasicSource(object):	#pylint: disable=W0232
	""" Tests for BasicSource """
	def test_indep_min_type(self):	#pylint: disable=C0103,R0201
		""" Tests indep_min type validation """
		test_list = list()
		# __init__ path
		# Wrong types
		for param_value in ['a', False]:
			with pytest.raises(TypeError) as excinfo:
				putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_min=param_value)
			test_list.append(excinfo.value.message == 'Argument `indep_min` is of the wrong type')
		# Valid values, these should not raise an exception
		for param_value in [1, 2.0]:
			putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_min=param_value)
		# Managed attribute path
		# Wrong types
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))	#pylint: disable=W0612
		for param_value in ['a', False]:
			with pytest.raises(TypeError) as excinfo:
				obj.indep_min = param_value
			test_list.append(excinfo.value.message == 'Argument `indep_min` is of the wrong type')
		# Valid values, these should not raise an exception
		for param_value in [1, 2.0]:
			obj.indep_min = param_value
			test_list.append(obj.indep_min == param_value)
		assert test_list == 6*[True]

	def test_indep_max_type(self):	#pylint: disable=C0103,R0201
		""" Tests indep_max type validation """
		test_list = list()
		# __init__ path
		# Wrong types
		for param_value in ['a', False]:
			with pytest.raises(TypeError) as excinfo:
				putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_max=param_value)
			test_list.append(excinfo.value.message == 'Argument `indep_max` is of the wrong type')
		# Valid values, these should not raise an exception
		for param_value in [1, 2.0]:
			putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_max=param_value)
		# Managed attribute path
		# Wrong types
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))	#pylint: disable=W0612
		for param_value in ['a', False]:
			with pytest.raises(TypeError) as excinfo:
				obj.indep_max = param_value
			test_list.append(excinfo.value.message == 'Argument `indep_max` is of the wrong type')
		# Valid values, these should not raise an exception
		for param_value in [1, 2.0]:
			obj.indep_max = param_value
			test_list.append(obj.indep_max == param_value)
		assert test_list == 6*[True]

	def test_indep_min_greater_than_indep_max(self):	#pylint: disable=C0103,R0201
		""" Test if object behaves correctly when indep_min and indep_max are incongrous """
		test_list = list()
		# Assign indep_min first
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_min=0.5)
		with pytest.raises(ValueError) as excinfo:
			obj.indep_max = 0
		test_list.append(excinfo.value.message == 'Argument `indep_min` is greater than argument `indep_max`')
		# Assign indep_max first
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))
		obj.indep_max = 40
		with pytest.raises(ValueError) as excinfo:
			obj.indep_min = 50
		test_list.append(excinfo.value.message == 'Argument `indep_min` is greater than argument `indep_max`')
		assert test_list == 2*[True]

	def test_indep_var_type(self):	#pylint: disable=C0103,R0201
		""" Tests indep_var type validation """
		test_list = list()
		# __init__ path
		# Wrong type
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(indep_var=None, dep_var=numpy.array([10, 20, 30]))
		test_list.append(excinfo.value.message == 'Argument `indep_var` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(indep_var='a', dep_var=numpy.array([10, 20, 30]))
		test_list.append(excinfo.value.message == 'Argument `indep_var` is of the wrong type')
		# Non monotonically increasing vector
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(indep_var=numpy.array([1.0, 2.0, 0.0, 3.0]), dep_var=numpy.array([10, 20, 30]))
		test_list.append(excinfo.value.message == 'Argument `indep_var` is of the wrong type')
		# Empty vector
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(indep_var=numpy.array([]), dep_var=numpy.array([10, 20, 30]))
		test_list.append(excinfo.value.message == 'Argument `indep_var` is of the wrong type')
		# Valid values, these should not raise any exception
		test_list.append((putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30])).indep_var == numpy.array([1, 2, 3])).all())
		test_list.append((putil.plot.BasicSource(indep_var=numpy.array([4.0, 5.0, 6.0]), dep_var=numpy.array([10, 20, 30])).indep_var == numpy.array([4.0, 5.0, 6.0])).all())
		# Invalid range bounding
		# Assign indep_min via attribute
		obj = putil.plot.BasicSource(numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))
		with pytest.raises(ValueError) as excinfo:
			obj.indep_min = 45
		test_list.append(excinfo.value.message == 'Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding')
		# Assign indep_max via attribute
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))
		with pytest.raises(ValueError) as excinfo:
			obj.indep_max = 0
		test_list.append(excinfo.value.message == 'Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding')
		# Assign both indep_min and indep_max via __init__ path
		with pytest.raises(ValueError) as excinfo:
			putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_min=4, indep_max=10)
		test_list.append(excinfo.value.message == 'Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding')
		# Managed attribute path
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))
		# Wrong type
		test_list.append((obj.indep_var == numpy.array([1, 2, 3])).all())
		with pytest.raises(TypeError) as excinfo:
			obj.indep_var = None
		test_list.append(excinfo.value.message == 'Argument `indep_var` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.indep_var = 'a'
		test_list.append(excinfo.value.message == 'Argument `indep_var` is of the wrong type')
		# Non monotonically increasing vector
		with pytest.raises(TypeError) as excinfo:
			obj.indep_var = numpy.array([1.0, 2.0, 0.0, 3.0])
		test_list.append(excinfo.value.message == 'Argument `indep_var` is of the wrong type')
		# Valid values, these should not raise any exception
		obj.indep_var = numpy.array([4.0, 5.0, 6.0])
		test_list.append((obj.indep_var == numpy.array([4.0, 5.0, 6.0])).all())
		assert test_list == 14*[True]

	def test_dep_var_type(self):	#pylint: disable=C0103,R0201
		""" Tests dep_var type validation """
		test_list = list()
		# __init__ path
		# Wrong type
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=None)
		test_list.append(excinfo.value.message == 'Argument `dep_var` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var='a')
		test_list.append(excinfo.value.message == 'Argument `dep_var` is of the wrong type')
		# Empty vector
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([]))
		test_list.append(excinfo.value.message == 'Argument `dep_var` is of the wrong type')
		# Valid values, these should not raise any exception
		test_list.append((putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([1, 2, 3])).dep_var == numpy.array([1, 2, 3])).all())
		test_list.append((putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([4.0, 5.0, 6.0])).dep_var == numpy.array([4.0, 5.0, 6.0])).all())
		# Managed attribute path
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([1, 2, 3]))
		# Wrong type
		with pytest.raises(TypeError) as excinfo:
			obj.dep_var = 'a'
		test_list.append(excinfo.value.message == 'Argument `dep_var` is of the wrong type')
		# Empty vector
		with pytest.raises(TypeError) as excinfo:
			obj.dep_var = numpy.array([])
		test_list.append(excinfo.value.message == 'Argument `dep_var` is of the wrong type')
		# Valid values, these should not raise any exception
		obj.dep_var = numpy.array([1, 2, 3])
		test_list.append((obj.dep_var == numpy.array([1, 2, 3])).all())
		obj.dep_var = numpy.array([4.0, 5.0, 6.0])
		test_list.append((obj.dep_var == numpy.array([4.0, 5.0, 6.0])).all())
		assert test_list == 9*[True]

	def test_indep_var_and_dep_var_do_not_have_the_same_number_of_elements(self):	#pylint: disable=C0103,R0201
		""" Tests dep_var type validation """
		test_list = list()
		# Both set at object creation
		with pytest.raises(ValueError) as excinfo:
			putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30]), dep_var=numpy.array([1, 2, 3, 4, 5, 6]), indep_min=30, indep_max=50)
		test_list.append(excinfo.value.message == 'Arguments `indep_var` and `dep_var` must have the same number of elements')
		with pytest.raises(ValueError) as excinfo:
			putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30]), dep_var=numpy.array([1, 2]), indep_min=30, indep_max=50)
		test_list.append(excinfo.value.message == 'Arguments `indep_var` and `dep_var` must have the same number of elements')
		# indep_var set first
		obj = putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30, 40, 50, 60]), dep_var=numpy.array([1, 2, 3, 4, 5, 6]), indep_min=30, indep_max=50)
		with pytest.raises(ValueError) as excinfo:
			obj.dep_var = numpy.array([100, 200, 300])
		test_list.append(excinfo.value.message == 'Arguments `indep_var` and `dep_var` must have the same number of elements')
		# dep_var set first
		obj = putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30]), dep_var=numpy.array([100, 200, 300]), indep_min=30, indep_max=50)
		with pytest.raises(ValueError) as excinfo:
			obj.indep_var = numpy.array([10, 20, 30, 40, 50, 60])
		test_list.append(excinfo.value.message == 'Arguments `indep_var` and `dep_var` must have the same number of elements')
		assert test_list == 4*[True]

	def test_complete(self):	#pylint: disable=C0103,R0201
		""" Test that _complete() method behaves correctly """
		test_list = list()
		obj = putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30]), dep_var=numpy.array([100, 200, 300]), indep_min=0, indep_max=50)
		obj._indep_var = None	#pylint: disable=W0212
		test_list.append(obj._complete() == False)	#pylint: disable=W0212
		obj = putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30]), dep_var=numpy.array([100, 200, 300]), indep_min=0, indep_max=50)
		test_list.append(obj._complete() == True)	#pylint: disable=W0212
		assert test_list == 2*[True]

	def test_str(self):	#pylint: disable=C0103,R0201
		""" Test that str behaves correctly """
		test_list = list()
		# Full set
		obj = str(putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_min=-10, indep_max=20.0))
		ref = 'Independent variable minimum: -10\nIndependent variable maximum: 20.0\nIndependent variable: [ 1.0, 2.0, 3.0 ]\nDependent variable: [ 10.0, 20.0, 30.0 ]'
		test_list.append(obj == ref)
		# indep_min not set
		obj = str(putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_max=20.0))
		ref = 'Independent variable minimum: -inf\nIndependent variable maximum: 20.0\nIndependent variable: [ 1.0, 2.0, 3.0 ]\nDependent variable: [ 10.0, 20.0, 30.0 ]'
		test_list.append(obj == ref)
		# indep_max not set
		obj = str(putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_min=-10))
		ref = 'Independent variable minimum: -10\nIndependent variable maximum: +inf\nIndependent variable: [ 1.0, 2.0, 3.0 ]\nDependent variable: [ 10.0, 20.0, 30.0 ]'
		test_list.append(obj == ref)
		# indep_min and indep_max not set
		obj = str(putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30])))
		ref = 'Independent variable minimum: -inf\nIndependent variable maximum: +inf\nIndependent variable: [ 1.0, 2.0, 3.0 ]\nDependent variable: [ 10.0, 20.0, 30.0 ]'
		test_list.append(obj == ref)
		assert test_list == 4*[True]

	def test_cannot_delete_attributes(self):	#pylint: disable=C0103,R0201
		""" Test that del method raises an exception on all class attributes """
		obj = putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30]), dep_var=numpy.array([100, 200, 300]))
		test_list = list()
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_min
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_max
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_var
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.dep_var
		test_list.append(excinfo.value.message == "can't delete attribute")
		assert test_list == 4*[True]

###
# Tests for CsvSource
###
def write_csv_file(file_handle):	#pylint: disable=C0111
	file_handle.write('Col1,Col2,Col3,Col4,Col5,Col6,Col7\n')
	file_handle.write('0,1,2,3,,5,1\n')
	file_handle.write('0,2,4,5,,4,2\n')
	file_handle.write('0,3,1,8,,3,3\n')
	file_handle.write('1,1,5,7,8,0,4\n')
	file_handle.write('1,2,3,7,9,7,5\n')


class TestCsvSource(object):	#pylint: disable=W0232,R0904
	""" Tests for CsvSource """
	def test_indep_min_type(self):	#pylint: disable=R0201
		""" Tests indep_min type validation """
		test_list = list()
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# __init__ path
			# Wrong types
			for param_value in ['a', False]:
				with pytest.raises(TypeError) as excinfo:
					putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_min=param_value)
				test_list.append(excinfo.value.message == 'Argument `indep_min` is of the wrong type')
			# Valid values, these should not raise an exception
			for param_value in [1, 2.0]:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_min=param_value)
			# Managed attribute path
			# Wrong types
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_min=param_value)
			for param_value in ['a', False]:
				with pytest.raises(TypeError) as excinfo:
					obj.indep_min = param_value
				test_list.append(excinfo.value.message == 'Argument `indep_min` is of the wrong type')
			# Valid values, these should not raise an exception
			for param_value in [1, 2.0]:
				obj.indep_min = param_value
				test_list.append(obj.indep_min == param_value)
		assert test_list == 6*[True]

	def test_indep_max_type(self):	#pylint: disable=R0201
		""" Tests indep_max type validation """
		test_list = list()
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# __init__ path
			# Wrong types
			for param_value in ['a', False]:
				with pytest.raises(TypeError) as excinfo:
					putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_max=param_value)
				test_list.append(excinfo.value.message == 'Argument `indep_max` is of the wrong type')
			# Valid values, these should not raise an exception
			for param_value in [1, 2.0]:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_max=param_value)
			# Managed attribute path
			# Wrong types
			obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]))
			for param_value in ['a', False]:
				with pytest.raises(TypeError) as excinfo:
					obj.indep_max = param_value
				test_list.append(excinfo.value.message == 'Argument `indep_max` is of the wrong type')
			# Valid values, these should not raise an exception
			for param_value in [1, 2.0]:
				obj.indep_max = param_value
				test_list.append(obj.indep_max == param_value)
		assert test_list == 6*[True]

	def test_indep_min_greater_than_indep_max(self):	#pylint: disable=R0201,C0103
		""" Test if object behaves correctly when indep_min and indep_max are incongrous """
		test_list = list()
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# Assign indep_min first
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_min=0.5)
			with pytest.raises(ValueError) as excinfo:
				obj.indep_max = 0
			test_list.append(excinfo.value.message == 'Argument `indep_min` is greater than argument `indep_max`')
			# Assign indep_max first
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', indep_max=10)
			with pytest.raises(ValueError) as excinfo:
				obj.indep_min = 50
			test_list.append(excinfo.value.message == 'Argument `indep_min` is greater than argument `indep_max`')
		assert test_list == 2*[True]

	def test_file_name_wrong_type(self):	#pylint: disable=C0103,R0201
		""" Test if object behaves correctly when file_name is of the wrong type """
		# This assignment should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.CsvSource(file_name=5, indep_col_label='Col7', dep_col_label='Col2')
		test_list.append(excinfo.value.message == 'Argument `file_name` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.plot.CsvSource(file_name=None, indep_col_label='Col7', dep_col_label='Col2')
		test_list.append(excinfo.value.message == 'Argument `file_name` is of the wrong type')

	def test_file_does_not_exist(self):	#pylint: disable=C0103,R0201
		""" Test if object behaves correctly when CSV file does not exist """
		file_name = 'nonexistent_file_name.csv'
		with pytest.raises(IOError) as excinfo:
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2')
		assert excinfo.value.message == 'File {0} could not be found'.format(file_name)

	def test_file_exists(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when CSV file exists """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2')

	def test_data_filter_wrong_type(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when dfilter is of the wrong type """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# This assignment should raise an exception
			with pytest.raises(TypeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', dfilter=5)
			test = excinfo.value.message == 'Argument `dfilter` is of the wrong type'
			# This assignment should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', dfilter=None)
		assert test == True

	def test_data_filter_operation(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when data filter and file name are given """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# This assignment should raise an exception
			with pytest.raises(ValueError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', dfilter={'Col99':500})
			test = excinfo.value.message == 'Column Col99 in data filter not found in comma-separated file {0} header'.format(file_name)
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', dfilter={'Col1':0})
		assert test == True

	def test_indep_col_label_wrong_type(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when indep_col_label is of the wrong type """
		test_list = list()
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# These assignments should raise an exception
			with pytest.raises(TypeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label=None, dep_col_label='Col2')
			test_list.append(excinfo.value.message == 'Argument `indep_col_label` is of the wrong type')
			with pytest.raises(TypeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label=5, dep_col_label='Col2')
			test_list.append(excinfo.value.message == 'Argument `indep_col_label` is of the wrong type')
			with pytest.raises(ValueError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col99', dep_col_label='Col2')
			test_list.append(excinfo.value.message == 'Column Col99 (independent column label) could not be found in comma-separated file {0} header'.format(file_name))
			# These assignments should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', dfilter={'Col1':0})
		assert test_list == 3*[True]

	def test_dep_col_label_wrong_type(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when dep_col_label is of the wrong type """
		test_list = list()
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# This assignment should raise an exception
			with pytest.raises(TypeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label=None)
			test_list.append(excinfo.value.message == 'Argument `dep_col_label` is of the wrong type')
			with pytest.raises(TypeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label=5)
			test_list.append(excinfo.value.message == 'Argument `dep_col_label` is of the wrong type')
			with pytest.raises(ValueError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col99')
			test_list.append(excinfo.value.message == 'Column Col99 (dependent column label) could not be found in comma-separated file {0} header'.format(file_name))	# Thess assignments should not raise an exception
			# These assignments should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col3')
		assert test_list == 3*[True]

	def test_empty_indep_var_after_filter(self):	#pylint: disable=R0201,C0103
		""" Test if object behaves correctly when the independent variable is empty after data filter is applied """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			with pytest.raises(ValueError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':10})
		assert excinfo.value.message == 'Filtered independent variable is empty'

	def test_empty_dep_var_after_filter(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when the dependent variable is empty after data filter is applied """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			with pytest.raises(ValueError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col5', dfilter={'Col1':0})
		assert excinfo.value.message == 'Filtered dependent variable is empty'

	def test_data_reversed(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when the independent dat is descending order """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col6', dep_col_label='Col3', dfilter={'Col1':0})
		assert ((obj.indep_var == numpy.array([3, 4, 5])).all(), (obj.dep_var == numpy.array([1, 4, 2])).all()) == (True, True)

	def test_fproc_wrong_type(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when fproc is of the wrong type """
		def fproc1():	#pylint: disable=C0111
			return numpy.array([1]), numpy.array([1])
		def fproc2(*args):	#pylint: disable=C0111,W0613
			return numpy.array([1]), numpy.array([1])
		def fproc3(*args, **kwargs):	#pylint: disable=C0111,W0613
			return numpy.array([1, 2, 3, 4, 5]), numpy.array([1, 2, 3, 1, 2])
		test_list = list()
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# These assignments should raise an exception
			with pytest.raises(TypeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc=5)
			test_list.append(excinfo.value.message == 'Argument `fproc` is of the wrong type')
			with pytest.raises(ValueError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc=fproc1)
			test_list.append(excinfo.value.message == 'Argument `fproc` (function fproc1) does not have at least 2 arguments')
			# These assignments should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc=fproc2)
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc=fproc3)
		assert test_list == 2*[True]

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
			raise RuntimeError('Test exception message')
		test_list = list()
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# These assignments should raise an exception
			with pytest.raises(TypeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc1)
			test_list.append(excinfo.value.message == 'Argument `fproc` (function fproc1) return value is of the wrong type')
			with pytest.raises(RuntimeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc2)
			test_list.append(excinfo.value.message == 'Argument `fproc` (function fproc2) returned an illegal number of values')
			with pytest.raises(TypeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc4)
			test_list.append(excinfo.value.message == 'Processed independent variable is of the wrong type')
			with pytest.raises(TypeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc5)
			test_list.append(excinfo.value.message == 'Processed independent variable is of the wrong type')
			with pytest.raises(TypeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc6)
			test_list.append(excinfo.value.message == 'Processed dependent variable is of the wrong type')
			with pytest.raises(ValueError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc8)
			test_list.append(excinfo.value.message == 'Processed independent variable is empty')
			with pytest.raises(ValueError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc9)
			test_list.append(excinfo.value.message == 'Processed dependent variable is empty')
			with pytest.raises(ValueError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc10)
			test_list.append(excinfo.value.message == 'Processed independent variable is empty')
			with pytest.raises(ValueError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc11)
			test_list.append(excinfo.value.message == 'Processed dependent variable is empty')
			with pytest.raises(ValueError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc12)
			test_list.append(excinfo.value.message == 'Processed independent and dependent variables are of different length')
			with pytest.raises(RuntimeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc13, fproc_eargs={'par1':13})
			msg = 'Processing function fproc13 raised an exception when called with the following arguments:\n'
			msg += 'indep_var: [ 1.0, 2.0, 3.0 ]\n'
			msg += 'dep_var: [ 1.0, 2.0, 3.0 ]\n'
			msg += 'par1: 13\n'
			msg += 'Exception error: Test exception message'
			test_list.append(excinfo.value.message == msg)
			# These assignments should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc3)
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc7)
		assert test_list == [True]*11

	def test_fproc_eargs_wrong_type(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when fprog_eargs is of the wrong type """
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# This assignment should raise an exception
			with pytest.raises(TypeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc_eargs=5)
			test = excinfo.value.message == 'Argument `fproc_eargs` is of the wrong type'
			# These assignments should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc_eargs=None)
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc_eargs={'arg1':23})
		assert test == True

	def test_fproc_eargs_argument_name_validation(self):	#pylint: disable=R0201,C0103
		""" Test if object behaves correctly when checking if the arguments in the fprog_eargs dictionary exist """
		def fproc1(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 2]), numpy.array([1, 2])]
		def fproc2(indep_var, dep_var, par1, par2):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 2]), numpy.array([1, 2])]
		def fproc3(indep_var, dep_var, **kwargs):	#pylint: disable=C0111,W0613
			return [numpy.array([1, 2]), numpy.array([1, 2])]
		test_list = list()
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# These assignments should raise an exception
			with pytest.raises(RuntimeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc=fproc1, fproc_eargs={'par1':5})
			test_list.append(excinfo.value.message == 'Extra argument `par1` not found in argument `fproc` (function fproc1) definition')
			with pytest.raises(RuntimeError) as excinfo:
				putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc=fproc2, fproc_eargs={'par3':5})
			test_list.append(excinfo.value.message == 'Extra argument `par3` not found in argument `fproc` (function fproc2) definition')
			# These assignments should not raise an exception
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', fproc=fproc3, fproc_eargs={'par99':5})
		assert test_list == 2*[True]

	def test_fproc_works(self):	#pylint: disable=R0201
		""" Test if object behaves correctly when executing function defined in fproc argument with extra arguments defined in fproc_eargs argument """
		def fproc1(indep_var, dep_var, indep_offset, dep_offset):	#pylint: disable=C0111,W0613
			return indep_var+indep_offset, dep_var+dep_offset
		with putil.misc.TmpFile(write_csv_file) as file_name:
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc1, fproc_eargs={'indep_offset':3, 'dep_offset':100})
		assert [(obj.indep_var == numpy.array([4, 5, 6])).all(), (obj.dep_var == numpy.array([102, 104, 101])).all()] == [True]*2

	def test_str(self):	#pylint: disable=R0201
		""" Test that str behaves correctly """
		def fproc1(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return indep_var*1e-3, dep_var+1
		def fproc2(indep_var, dep_var, par1, par2):	#pylint: disable=C0111,W0613
			return indep_var+par1, dep_var-par2
		test_list = list()
		with putil.misc.TmpFile(write_csv_file) as file_name:
			# dfilter
			obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3'))
			ref = 'File name: {0}\nData filter: \n   Col1: 0\nIndependent column label: Col2\nDependent column label: Col3\nProcessing function: None\nProcessing function extra arguments: None\n'.format(file_name)
			ref += 'Independent variable minimum: -inf\nIndependent variable maximum: +inf\nIndependent variable: [ 1.0, 2.0, 3.0 ]\nDependent variable: [ 2.0, 4.0, 1.0 ]'
			test_list.append(obj == ref)
			# fproc
			obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3', indep_min=2e-3, indep_max=200, fproc=fproc1))
			ref = 'File name: {0}\nData filter: \n   Col1: 0\nIndependent column label: Col2\nDependent column label: Col3\nProcessing function: fproc1\nProcessing function extra arguments: None\n'.format(file_name)
			ref += 'Independent variable minimum: 0.002\nIndependent variable maximum: 200\nIndependent variable: [ 0.002, 0.003 ]\nDependent variable: [ 5.0, 2.0 ]'
			test_list.append(obj == ref)
			# fproc_eargs
			obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3', indep_min=-2, indep_max=200, fproc=fproc2, fproc_eargs={'par1':3, 'par2':4}))
			ref = 'File name: {0}\nData filter: \n   Col1: 0\nIndependent column label: Col2\nDependent column label: Col3\nProcessing function: fproc2\nProcessing function extra arguments: \n   par1: 3\n   par2: 4\n'.format(file_name)
			ref += 'Independent variable minimum: -2\nIndependent variable maximum: 200\nIndependent variable: [ 4.0, 5.0, 6.0 ]\nDependent variable: [ -2.0, 0.0, -3.0 ]'
			test_list.append(obj == ref)
			# indep_min set
			obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3', indep_min=-2, fproc=fproc2, fproc_eargs={'par1':3, 'par2':4}))
			ref = 'File name: {0}\nData filter: \n   Col1: 0\nIndependent column label: Col2\nDependent column label: Col3\nProcessing function: fproc2\nProcessing function extra arguments: \n   par1: 3\n   par2: 4\n'.format(file_name)
			ref += 'Independent variable minimum: -2\nIndependent variable maximum: +inf\nIndependent variable: [ 4.0, 5.0, 6.0 ]\nDependent variable: [ -2.0, 0.0, -3.0 ]'
			test_list.append(obj == ref)
			# indep_max set
			obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3', indep_min=-2, indep_max=200, fproc=fproc2, fproc_eargs={'par1':3, 'par2':4}))
			ref = 'File name: {0}\nData filter: \n   Col1: 0\nIndependent column label: Col2\nDependent column label: Col3\nProcessing function: fproc2\nProcessing function extra arguments: \n   par1: 3\n   par2: 4\n'.format(file_name)
			ref += 'Independent variable minimum: -2\nIndependent variable maximum: 200\nIndependent variable: [ 4.0, 5.0, 6.0 ]\nDependent variable: [ -2.0, 0.0, -3.0 ]'
			test_list.append(obj == ref)
		assert test_list == 5*[True]

	def test_complete(self):	#pylint: disable=R0201
		""" Test that _complete() method behaves correctly """
		test_list = list()
		with putil.misc.TmpFile(write_csv_file) as file_name:
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', )
			obj._indep_var = None	#pylint: disable=W0212
			test_list.append(obj._complete() == False)	#pylint: disable=W0212
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2', )
			test_list.append(obj._complete() == True)	#pylint: disable=W0212
		assert test_list == 2*[True]

	def test_cannot_delete_attributes(self):	#pylint: disable=R0201
		""" Test that del method raises an exception on all class attributes """
		test_list = list()
		with putil.misc.TmpFile(write_csv_file) as file_name:
			obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col7', dep_col_label='Col2')
			with pytest.raises(AttributeError) as excinfo:
				del obj.file_name
			test_list.append(excinfo.value.message == "can't delete attribute")
			with pytest.raises(AttributeError) as excinfo:
				del obj.dfilter
			test_list.append(excinfo.value.message == "can't delete attribute")
			with pytest.raises(AttributeError) as excinfo:
				del obj.indep_col_label
			test_list.append(excinfo.value.message == "can't delete attribute")
			with pytest.raises(AttributeError) as excinfo:
				del obj.dep_col_label
			test_list.append(excinfo.value.message == "can't delete attribute")
			with pytest.raises(AttributeError) as excinfo:
				del obj.fproc
			test_list.append(excinfo.value.message == "can't delete attribute")
			with pytest.raises(AttributeError) as excinfo:
				del obj.fproc_eargs
			test_list.append(excinfo.value.message == "can't delete attribute")
			with pytest.raises(AttributeError) as excinfo:
				del obj.indep_min
			test_list.append(excinfo.value.message == "can't delete attribute")
			with pytest.raises(AttributeError) as excinfo:
				del obj.indep_max
			test_list.append(excinfo.value.message == "can't delete attribute")
			with pytest.raises(AttributeError) as excinfo:
				del obj.indep_var
			test_list.append(excinfo.value.message == "can't delete attribute")
			with pytest.raises(AttributeError) as excinfo:
				del obj.dep_var
			test_list.append(excinfo.value.message == "can't delete attribute")
		assert test_list == 10*[True]

###
# Tests for Series
###
@pytest.fixture
def default_source():
	""" Provides a default source to be used in teseting the putil.Series() class """
	return putil.plot.BasicSource(indep_var=numpy.array([5, 6, 7, 8]), dep_var=numpy.array([0, -10, 5, 4]))

class TestSeries(object):	#pylint: disable=W0232
	""" Tests for Series """
	def test_data_source_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test if object behaves correctly when checking the data_source argument """
		class TestSource(object):	#pylint: disable=C0111,R0903,W0612
			def __init__(self):
				pass
		test_list = list()
		# These assignments should raise an exception
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3, 4]), dep_var=numpy.array([10, 20, 30, 40]))
		obj._indep_var = None	#pylint: disable=W0212
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.Series(data_source=obj, label='test')
		test_list.append(excinfo.value.message == 'Argument `data_source` is not fully specified')
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.Series(data_source=5, label='test')
		test_list.append(excinfo.value.message == 'Argument `data_source` does not have `indep_var` attribute')
		obj = TestSource()
		obj.indep_var = numpy.array([5, 6, 7, 8])	#pylint: disable=W0201
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.Series(data_source=obj, label='test')
		test_list.append(excinfo.value.message == 'Argument `data_source` does not have `dep_var` attribute')
		obj.dep_var = numpy.array([0, -10, 5, 4])	#pylint: disable=W0201
		# These assignments should not raise an exception
		putil.plot.Series(data_source=None, label='test')
		putil.plot.Series(data_source=obj, label='test')
		obj = putil.plot.Series(data_source=default_source, label='test')
		test_list.append(((obj.indep_var == numpy.array([5, 6, 7, 8])).all(), (obj.dep_var == numpy.array([0, -10, 5, 4])).all()) == (True, True))
		assert test_list == [True]*4

	def test_label_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test label data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Series(data_source=default_source, label=5)
		test_list.append(excinfo.value.message == 'Argument `label` is of the wrong type')
		# These assignments should not raise an exception
		putil.plot.Series(data_source=default_source, label=None)
		obj = putil.plot.Series(data_source=default_source, label='test')
		test_list.append(obj.label == 'test')
		assert test_list == [True]*2

	def test_color_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test color data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Series(data_source=default_source, label='test', color=default_source)
		test_list.append(excinfo.value.message == 'Argument `color` is of the wrong type')
		invalid_color_list = ['invalid_color_name', -0.01, 1.1, '#ABCDEX', (-1, 1, 1), [1, 2, 0.5], [1, 1, 2], (-1, 1, 1, 1), [1, 2, 0.5, 0.5], [1, 1, 2, 1], (1, 1, 1, -1)]
		valid_color_list = [None, 'moccasin', 0.5, '#ABCDEF', (0.5, 0.5, 0.5), [0.25, 0.25, 0.25, 0.25]]
		for color in invalid_color_list:
			with pytest.raises(TypeError) as excinfo:
				print color
				putil.plot.Series(data_source=default_source, label='test', color=color)
			print excinfo.value.message
			test_list.append(excinfo.value.message == 'Invalid color specification')
		# These assignments should not raise an exception
		putil.plot.Series(data_source=default_source, label='test', color=None)
		for color in valid_color_list:
			obj = putil.plot.Series(data_source=default_source, label='test', color=color)
			test_list.append(obj.color == (color.lower() if isinstance(color, str) else color))
		print test_list
		assert test_list == [True]*(len(invalid_color_list)+len(valid_color_list)+1)

	def test_marker_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test marker data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Series(data_source=default_source, label='test', marker='hello')
		test_list.append(excinfo.value.message == 'Argument `marker` is of the wrong type')
		# These assignments should not raise an exception
		obj = putil.plot.Series(data_source=default_source, label='test', marker=None)
		test_list.append(obj.marker == None)
		obj = putil.plot.Series(data_source=default_source, label='test', marker='D')
		test_list.append(obj.marker == 'D')
		obj = putil.plot.Series(data_source=default_source, label='test')
		test_list.append(obj.marker == 'o')
		assert test_list == [True]*4

	def test_interp_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test interp data validation """
		# These assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Series(data_source=default_source, label='test', interp=5)
		test_list.append(excinfo.value.message == 'Argument `interp` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.plot.Series(data_source=default_source, label='test', interp='NOT_AN_OPTION')
		test_list.append(excinfo.value.message == "Argument `interp` is not one of ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG'] (case insensitive)")
		source_obj = putil.plot.BasicSource(indep_var=numpy.array([5]), dep_var=numpy.array([0]))
		with pytest.raises(ValueError) as excinfo:
			putil.plot.Series(data_source=source_obj, label='test', interp='CUBIC')
		test_list.append(excinfo.value.message == 'At least 4 data points are needed for CUBIC interpolation')
		# These assignments should not raise an exception
		putil.plot.Series(data_source=source_obj, label='test', interp='STRAIGHT')
		putil.plot.Series(data_source=source_obj, label='test', interp='STEP')
		putil.plot.Series(data_source=source_obj, label='test', interp='LINREG')
		putil.plot.Series(data_source=default_source, label='test', interp=None)
		obj = putil.plot.Series(data_source=default_source, label='test', interp='straight')
		test_list.append(obj.interp == 'STRAIGHT')
		obj = putil.plot.Series(data_source=default_source, label='test', interp='StEp')
		test_list.append(obj.interp == 'STEP')
		obj = putil.plot.Series(data_source=default_source, label='test', interp='CUBIC')
		test_list.append(obj.interp == 'CUBIC')
		obj = putil.plot.Series(data_source=default_source, label='test', interp='linreg')
		test_list.append(obj.interp == 'LINREG')
		obj = putil.plot.Series(data_source=default_source, label='test')
		test_list.append(obj.interp == 'CUBIC')
		assert test_list == [True]*8

	def test_line_style_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test line_style data validation """
		# These assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Series(data_source=default_source, label='test', line_style=5)
		test_list.append(excinfo.value.message == 'Argument `line_style` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.plot.Series(data_source=default_source, label='test', line_style='x')
		test_list.append(excinfo.value.message == "Argument `line_style` is not one of ['-', '--', '-.', ':'] (case insensitive)")
		# These assignments should not raise an exception
		putil.plot.Series(data_source=default_source, label='test', line_style=None)
		obj = putil.plot.Series(data_source=default_source, label='test', line_style='-')
		test_list.append(obj.line_style == '-')
		obj = putil.plot.Series(data_source=default_source, label='test', line_style='--')
		test_list.append(obj.line_style == '--')
		obj = putil.plot.Series(data_source=default_source, label='test', line_style='-.')
		test_list.append(obj.line_style == '-.')
		obj = putil.plot.Series(data_source=default_source, label='test', line_style=':')
		test_list.append(obj.line_style == ':')
		obj = putil.plot.Series(data_source=default_source, label='test')
		test_list.append(obj.line_style == '-')
		assert test_list == [True]*7

	def test_secondary_axis_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test secondary_axis data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Series(data_source=default_source, label='test', secondary_axis=5)
		test_list.append(excinfo.value.message == 'Argument `secondary_axis` is of the wrong type')
		# These assignments should not raise an exception
		putil.plot.Series(data_source=default_source, label='test', secondary_axis=None)
		obj = putil.plot.Series(data_source=default_source, label='test', secondary_axis=False)
		test_list.append(obj.secondary_axis == False)
		obj = putil.plot.Series(data_source=default_source, label='test', secondary_axis=True)
		test_list.append(obj.secondary_axis == True)
		obj = putil.plot.Series(data_source=default_source, label='test')
		test_list.append(obj.secondary_axis == False)
		assert test_list == [True]*4

	def test_calculate_curve(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test that interpolated curve is calculated when apropriate """
		test_list = list()
		obj = putil.plot.Series(data_source=default_source, label='test', interp=None)
		test_list.append((obj.interp_indep_var, obj.interp_dep_var) == (None, None))
		obj = putil.plot.Series(data_source=default_source, label='test', interp='STRAIGHT')
		test_list.append((obj.interp_indep_var, obj.interp_dep_var) == (None, None))
		obj = putil.plot.Series(data_source=default_source, label='test', interp='STEP')
		test_list.append((obj.interp_indep_var, obj.interp_dep_var) == (None, None))
		obj = putil.plot.Series(data_source=default_source, label='test', interp='CUBIC')
		test_list.append((obj.interp_indep_var, obj.interp_dep_var) != (None, None))
		obj = putil.plot.Series(data_source=default_source, label='test', interp='LINREG')
		test_list.append((obj.interp_indep_var, obj.interp_dep_var) != (None, None))
		obj = putil.plot.Series(data_source=default_source, label='test')
		test_list.append((obj.interp_indep_var, obj.interp_dep_var) != (None, None))
		assert test_list == [True]*6

	def test_scale_indep_var(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test that independent variable scaling works """
		test_list = list()
		obj = putil.plot.Series(data_source=default_source, label='test', interp=None)
		test_list.append((obj.scaled_indep_var is not None, obj.scaled_dep_var is not None, obj.scaled_interp_indep_var is None, obj.scaled_interp_dep_var is None) == (True, True, True, True))
		obj._scale_indep_var(2)	#pylint: disable=W0212
		obj._scale_dep_var(4)	#pylint: disable=W0212
		test_list.append(((obj.scaled_indep_var == numpy.array([2.5, 3.0, 3.5, 4.0])).all(), (obj.scaled_dep_var == numpy.array([0.0, -2.5, 1.25, 1.0])).all(), \
					   obj.scaled_interp_indep_var is None, obj.scaled_interp_dep_var is None) == (True, True, True, True))
		obj.interp = 'CUBIC'
		test_list.append(((obj.scaled_indep_var == numpy.array([2.5, 3.0, 3.5, 4.0])).all(), (obj.scaled_dep_var == numpy.array([0.0, -2.5, 1.25, 1.0])).all(), \
					   obj.scaled_interp_indep_var is not None, obj.scaled_interp_dep_var is not None) == (True, True, True, True))
		assert test_list == [True]*3

	def test_plottable(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test that object behaves properl when a series is not plottable """
		test_list = list()
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.Series(data_source=default_source, label='test', marker=None, interp=None, line_style=None)
		test_list.append(excinfo.value.message == 'Series options make it not plottable')
		obj = putil.plot.Series(data_source=default_source, label='test', marker='o', interp='CUBIC', line_style=None)
		with pytest.raises(RuntimeError) as excinfo:
			obj.marker = None
		test_list.append(excinfo.value.message == 'Series options make it not plottable')
		obj = putil.plot.Series(data_source=default_source, label='test', marker='None', interp='CUBIC', line_style='-')
		with pytest.raises(RuntimeError) as excinfo:
			obj.interp = None
		test_list.append(excinfo.value.message == 'Series options make it not plottable')
		obj = putil.plot.Series(data_source=default_source, label='test', marker=' ', interp='CUBIC', line_style='-')
		with pytest.raises(RuntimeError) as excinfo:
			obj.line_style = None
		test_list.append(excinfo.value.message == 'Series options make it not plottable')
		assert test_list == [True]*4

	def test_str(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test that str behaves correctly """
		test_list = list()
		marker_list = [{'value':None, 'string':'None'}, {'value':'o', 'string':'o'}, {'value':matplotlib.path.Path([(0, 0), (1, 1)]), 'string':'matplotlib.path.Path object'}, {'value':[(0, 0), (1, 1)], 'string':'[(0, 0), (1, 1)]'},
				 {'value':r'$a_{b}$', 'string':r'$a_{b}$'}]
		for marker_dict in marker_list:
			obj = putil.plot.Series(data_source=default_source, label='test', marker=marker_dict['value'])
			ret = ''
			ret += 'Data source: putil.plot.BasicSource class object\n'
			ret += 'Independent variable: [ 5.0, 6.0, 7.0, 8.0 ]\n'
			ret += 'Dependent variable: [ 0.0, -10.0, 5.0, 4.0 ]\n'
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
			test_list.append(str(obj) == ret)
		assert test_list == 5*[True]

	def test_cannot_delete_attributes(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		obj = putil.plot.Series(data_source=default_source, label='test')
		test_list = list()
		with pytest.raises(AttributeError) as excinfo:
			del obj.data_source
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.label
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.color
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.marker
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.interp
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.line_style
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.secondary_axis
		test_list.append(excinfo.value.message == "can't delete attribute")
		assert test_list == 7*[True]

	def test_images(self, tmpdir):	#pylint: disable=C0103,R0201,W0621
		""" Compare images to verify correct plotting of series """
		tmpdir.mkdir('test_images')
		test_list = list()
		images_dict_list = gen_ref_images.unittest_series_images(mode='test', test_dir=str(tmpdir))
		for images_dict in images_dict_list:
			ref_file_name = images_dict['ref_file_name']
			test_file_name = images_dict['test_file_name']
			metrics = compare_images(ref_file_name, test_file_name)
			result = (metrics[0] < IMGTOL) and (metrics[1] < IMGTOL)
			print 'Comparison: {0} with {1} -> {2} {3}'.format(ref_file_name, test_file_name, result, metrics)
			test_list.append(result)
		assert test_list == [True]*len(images_dict_list)

###
# Tests for Panel
###
@pytest.fixture
def default_series(default_source):	#pylint: disable=W0621
	""" Provides a default series object to be used in teseting the putil.Panel() class """
	return putil.plot.Series(data_source=default_source, label='test series')

class TestPanel(object):	#pylint: disable=W0232
	""" Tests for Series """
	def test_primary_axis_label_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test panel_primary_axis data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Panel(series=default_series, primary_axis_label=5)
		test_list.append(excinfo.value.message == 'Argument `primary_axis_label` is of the wrong type')
		# These assignments should not raise an exception
		putil.plot.Panel(series=default_series, primary_axis_label=None)
		obj = putil.plot.Panel(series=default_series, primary_axis_label='test')
		test_list.append(obj.primary_axis_label == 'test')
		assert test_list == [True]*2

	def test_primary_axis_units_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test panel_primary_axis data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Panel(series=default_series, primary_axis_units=5)
		test_list.append(excinfo.value.message == 'Argument `primary_axis_units` is of the wrong type')
		# These assignments should not raise an exception
		putil.plot.Panel(series=default_series, primary_axis_units=None)
		obj = putil.plot.Panel(series=default_series, primary_axis_units='test')
		test_list.append(obj.primary_axis_units == 'test')
		assert test_list == [True]*2

	def test_secondary_axis_label_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test panel_secondary_axis data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Panel(series=default_series, secondary_axis_label=5)
		test_list.append(excinfo.value.message == 'Argument `secondary_axis_label` is of the wrong type')
		# These assignments should not raise an exception
		putil.plot.Panel(series=default_series, secondary_axis_label=None)
		obj = putil.plot.Panel(series=default_series, secondary_axis_label='test')
		test_list.append(obj.secondary_axis_label == 'test')
		assert test_list == [True]*2

	def test_secondary_axis_units_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test panel_secondary_axis data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Panel(series=default_series, secondary_axis_units=5)
		test_list.append(excinfo.value.message == 'Argument `secondary_axis_units` is of the wrong type')
		# These assignments should not raise an exception
		putil.plot.Panel(series=default_series, secondary_axis_units=None)
		obj = putil.plot.Panel(series=default_series, secondary_axis_units='test')
		test_list.append(obj.secondary_axis_units == 'test')
		assert test_list == [True]*2

	def test_log_dep_axis_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test log_dep_axis data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Panel(series=default_series, log_dep_axis=5)
		test_list.append(excinfo.value.message == 'Argument `log_dep_axis` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.plot.Panel(series=default_series, log_dep_axis=True)
		test_list.append(excinfo.value.message == 'Series element 0 cannot be plotted in a logarithmic axis because it contains negative data points')
		# These assignments should not raise an exception
		non_negative_data_source = putil.plot.BasicSource(indep_var=numpy.array([5, 6, 7, 8]), dep_var=numpy.array([0.1, 10, 5, 4]))
		non_negative_series = putil.plot.Series(data_source=non_negative_data_source, label='non-negative data series')
		obj = putil.plot.Panel(series=default_series, log_dep_axis=False)
		test_list.append(obj.log_dep_axis == False)
		obj = putil.plot.Panel(series=non_negative_series, log_dep_axis=True)
		test_list.append(obj.log_dep_axis == True)
		obj = putil.plot.Panel(series=default_series)
		test_list.append(obj.log_dep_axis == False)
		assert test_list == [True]*5

	def test_show_indep_axis_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test show_indep_axis data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Panel(series=default_series, show_indep_axis=5)
		test_list.append(excinfo.value.message == 'Argument `show_indep_axis` is of the wrong type')
		# These assignments should not raise an exception
		obj = putil.plot.Panel(series=default_series, show_indep_axis=False)
		test_list.append(obj.show_indep_axis == False)
		obj = putil.plot.Panel(series=default_series, show_indep_axis=True)
		test_list.append(obj.show_indep_axis == True)
		obj = putil.plot.Panel(series=default_series)
		test_list.append(obj.show_indep_axis == False)
		assert test_list == [True]*4

	def test_legend_props_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test legend_props data validation """
		# These assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Panel(series=default_series, legend_props=5)
		test_list.append(excinfo.value.message == 'Argument `legend_props` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.plot.Panel(series=default_series, legend_props={'not_a_valid_prop':5})
		test_list.append(excinfo.value.message == 'Illegal legend property `not_a_valid_prop`')
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Panel(series=default_series, legend_props={'pos':5})
		msg = "Legend property `pos` is not one of ['BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER'] (case insensitive)"
		test_list.append(excinfo.value.message == msg)
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Panel(series=default_series, legend_props={'cols':-1})
		test_list.append(excinfo.value.message == 'Legend property `cols` is of the wrong type')
		# These assignments should not raise an exception
		obj = putil.plot.Panel(series=default_series, legend_props={'pos':'upper left'})
		test_list.append(obj.legend_props == {'pos':'UPPER LEFT', 'cols':1})
		obj = putil.plot.Panel(series=default_series, legend_props={'cols':3})
		test_list.append(obj.legend_props == {'pos':'BEST', 'cols':3})
		obj = putil.plot.Panel(series=default_series)
		test_list.append(obj.legend_props == {'pos':'BEST', 'cols':1})
		print obj.legend_props
		assert test_list == [True]*7

	def test_intelligent_ticks(self):	#pylint: disable=C0103,R0201,W0621,R0915
		""" Test that intelligent_tick methods works for all scenarios """
		test_list = list()
		# 0
		# Tight = True
		# One sample
		vector = numpy.array([35e-6])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		test_list.append(obj == ([31.5, 35, 38.5], ['31.5', '35.0', '38.5'], 31.5, 38.5, 1e-6, 'u'))
		print obj
		# 1
		# Scaling with more data samples after 1.0
		vector = numpy.array([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		test_list.append(obj == ([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6], ['0.8', '0.9', '1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6'], 0.8, 1.6, 1, ' '))
		print obj
		# 2
		# Regular, should not have any scaling
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		test_list.append(obj == ([1, 2, 3, 4, 5, 6, 7], ['1', '2', '3', '4', '5', '6', '7'], 1, 7, 1, ' '))
		print obj
		# 3
		# Regular, should not have any scaling
		vector = numpy.array([10, 20, 30, 40, 50, 60, 70])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		test_list.append(obj == ([10, 20, 30, 40, 50, 60, 70], ['10', '20', '30', '40', '50', '60', '70'], 10, 70, 1, ' '))
		print obj
		# 4
		# Scaling
		vector = numpy.array([1000, 2000, 3000, 4000, 5000, 6000, 7000])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		test_list.append(obj == ([1, 2, 3, 4, 5, 6, 7], ['1', '2', '3', '4', '5', '6', '7'], 1, 7, 1e3, 'k'))
		print obj
		# 5
		# Scaling
		vector = numpy.array([200e6, 300e6, 400e6, 500e6, 600e6, 700e6, 800e6, 900e6, 1000e6])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		test_list.append(obj == ([200, 300, 400, 500, 600, 700, 800, 900, 1000], ['200', '300', '400', '500', '600', '700', '800', '900', '1k'], 200, 1000, 1e6, 'M'))
		print obj
		# 6
		# No tick marks to place all data points on grid, space uniformely
		vector = numpy.array([105, 107.7, 215, 400.2, 600, 700, 800, 810, 820, 830, 840, 850, 900, 905])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		test_list.append(obj == ([105.0, 193.88888889, 282.77777778, 371.66666667, 460.55555556, 549.44444444, 638.33333333, 727.22222222, 816.11111111, 905.0],
						   ['105', '194', '283', '372', '461', '549', '638', '727', '816', '905'], 105, 905, 1, ' '))
		print obj
		# 7
		# Ticks marks where some data points can be on grid
		vector = numpy.array([10, 20, 30, 40, 41, 50, 60, 62, 70, 75.5, 80])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		test_list.append(obj == ([10, 20, 30, 40, 50, 60, 70, 80], ['10', '20', '30', '40', '50', '60', '70', '80'], 10, 80, 1, ' '))
		print obj
		# 8
		# Tight = False
		# One sample
		vector = numpy.array([1e-9])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=False)	#pylint: disable=W0212
		test_list.append(obj == ([0.9, 1, 1.1], ['0.9', '1.0', '1.1'], 0.9, 1.1, 1e-9, 'n'))
		print obj
		# 9
		# Scaling with more data samples after 1.0
		vector = numpy.array([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=False)	#pylint: disable=W0212
		test_list.append(obj == ([0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7], ['0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7'], 0.7, 1.7, 1, ' '))
		print obj
		# 10
		# Scaling with more data samples before 1.0
		vector = numpy.array([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=False)	#pylint: disable=W0212
		test_list.append(obj == ([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2], ['0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2'], 0.2, 1.2, 1, ' '))
		print obj
		# 11
		# Regular, with some overshoot
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot._intelligent_ticks(vector, min(vector), 7.5, tight=False)	#pylint: disable=W0212
		test_list.append(obj == ([0, 1, 2, 3, 4, 5, 6, 7, 8], ['0', '1', '2', '3', '4', '5', '6', '7', '8'], 0, 8, 1, ' '))
		print obj
		# 12
		# Regular, with some undershoot
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot._intelligent_ticks(vector, 0.1, max(vector), tight=False)	#pylint: disable=W0212
		test_list.append(obj == ([0, 1, 2, 3, 4, 5, 6, 7, 8], ['0', '1', '2', '3', '4', '5', '6', '7', '8'], 0, 8, 1, ' '))
		print obj
		# 13
		# Regular, with large overshoot
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot._intelligent_ticks(vector, min(vector), 20, tight=False)	#pylint: disable=W0212
		test_list.append(obj == ([0, 1, 2, 3, 4, 5, 6, 7, 8], ['0', '1', '2', '3', '4', '5', '6', '7', '8'], 0, 8, 1, ' '))
		print obj
		# 14
		# Regular, with large undershoot
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot._intelligent_ticks(vector, -10, max(vector), tight=False)	#pylint: disable=W0212
		test_list.append(obj == ([0, 1, 2, 3, 4, 5, 6, 7, 8], ['0', '1', '2', '3', '4', '5', '6', '7', '8'], 0, 8, 1, ' '))
		print obj
		# 15
		# Scaling, minimum as reference
		vector = 1e9+(numpy.array([10, 20, 30, 40, 50, 60, 70, 80])*1e3)
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		test_list.append(obj == ([1.00001, 1.00002, 1.00003, 1.00004, 1.00005, 1.00006, 1.00007, 1.00008], ['1.00001', '1.00002', '1.00003', '1.00004', '1.00005', '1.00006', '1.00007', '1.00008'], 1.00001, 1.00008, 1e9, 'G'))
		print obj
		# 16
		# Scaling, delta as reference
		vector = numpy.array([10.1e6, 20e6, 30e6, 40e6, 50e6, 60e6, 70e6, 80e6, 90e6, 100e6, 20.22e9])
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		test_list.append(obj == ([10.1, 2255.6444444, 4501.1888889, 6746.7333333, 8992.2777778, 11237.822222, 13483.366667, 15728.911111, 17974.455556, 20220.0], \
						   ['10.1', '2.3k', '4.5k', '6.7k', '9.0k', '11.2k', '13.5k', '15.7k', '18.0k', '20.2k'], 10.1, 20220.0, 1e6, 'M'))
		print obj
		# 17
		# Scaling, maximum as reference
		vector = (numpy.array([0.7, 0.8, 0.9, 1.1, 1.2, 1.3, 1.4, 1.5])*1e12)
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		test_list.append(obj == ([0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5], ['0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3', '1.4', '1.5'], 0.7, 1.5, 1e12, 'T'))
		print obj
		# 18
		# Log axis
		# Tight False
		vector = (numpy.array([2e3, 3e4, 4e5, 5e6, 6e7]))
		obj = putil.plot._intelligent_ticks(vector, min(vector), max(vector), tight=True, log_axis=True)	#pylint: disable=W0212
		test_list.append(obj == ([1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1k', '10k', '100k'], 1, 100000, 1000, 'k'))
		# 19
		# Tight True
		# Left side
		vector = (numpy.array([2e3, 3e4, 4e5, 5e6, 6e7]))
		obj = putil.plot._intelligent_ticks(vector, 500, max(vector), tight=False, log_axis=True)	#pylint: disable=W0212
		test_list.append(obj == ([1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1k', '10k', '100k'], 1, 100000, 1000, 'k'))
		print obj
		# 20
		# Right side
		vector = (numpy.array([2e3, 3e4, 4e5, 5e6, 6e7]))
		obj = putil.plot._intelligent_ticks(vector, min(vector), 1e9, tight=False, log_axis=True)	#pylint: disable=W0212
		test_list.append(obj == ([1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1k', '10k', '100k'], 1, 100000, 1000, 'k'))
		print obj
		# 21
		# Both
		# Right side
		vector = (numpy.array([2e3, 3e4, 4e5, 5e6, 6e7]))
		obj = putil.plot._intelligent_ticks(vector, 500, 1e9, tight=False, log_axis=True)	#pylint: disable=W0212
		test_list.append(obj == ([1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1k', '10k', '100k'], 1, 100000, 1000, 'k'))
		print obj
		#
		assert test_list == [True]*22

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
		test_list = list()
		# 0-8: Linear primary and secondary axis, with multiple series on both
		panel_obj = putil.plot.Panel(series=[series1_obj, series2_obj, series3_obj, series4_obj])
		test_list.append((panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, True))	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_locs == [0, 0.8, 1.6, 2.4, 3.2, 4.0, 4.8, 5.6, 6.4, 7.2, 8.0])	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_labels == ['0.0', '0.8', '1.6', '2.4', '3.2', '4.0', '4.8', '5.6', '6.4', '7.2', '8.0'])	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (0, 8))	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' '))	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_locs == [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_labels == ['5', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55'])	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (5, 55))	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (1, ' '))	#pylint: disable=W0212
		# 9-17: Linear primary axis with multiple series	#pylint: disable=W0212
		panel_obj = putil.plot.Panel(series=[series1_obj, series2_obj])
		test_list.append((panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, False))	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_locs == [0, 1, 2, 3, 4, 5, 6, 7, 8])	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_labels == ['0', '1', '2', '3', '4', '5', '6', '7', '8'])	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (0, 8))	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' '))	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_locs == None)	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_labels == None)	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (None, None))	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (None, None))	#pylint: disable=W0212
		# 18-26: Linear secondary axis with multiple series on both
		panel_obj = putil.plot.Panel(series=[series3_obj, series4_obj])
		test_list.append((panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (False, True))	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_locs == None)	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_labels == None)	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (None, None))	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (None, None))	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_locs == [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_labels == ['5', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55'])	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (5, 55))	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (1, ' '))	#pylint: disable=W0212
		# 27-35: Logarithmic primary and secondary axis, with multiple series on both
		panel_obj = putil.plot.Panel(series=[series1_obj, series5_obj], log_dep_axis=True)
		test_list.append((panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, True))	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_locs == [0.9, 1, 10, 100])	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_labels == ['', '1', '10', '100'])	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (0.9, 100))	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' '))	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_locs == [0.9, 1, 10, 100])	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_labels == ['', '1', '10', '100'])	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (0.9, 100))	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (1, ' '))	#pylint: disable=W0212
		# 36-44: Logarithmic primary axis (bottom point at decade edge)
		panel_obj = putil.plot.Panel(series=[series1_obj], log_dep_axis=True)
		test_list.append((panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, False))	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_locs == [0.9, 1, 10])	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_labels == ['', '1', '10'])	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (0.9, 10))	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' '))	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_locs == None)	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_labels == None)	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (None, None))	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (None, None))	#pylint: disable=W0212
		# 45-53: Logarithmic secondary axis (top point at decade edge)
		panel_obj = putil.plot.Panel(series=[series6_obj], log_dep_axis=True)
		test_list.append((panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (False, True))	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_locs == None)	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_labels == None)	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (None, None))	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (None, None))	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_locs == [10, 100, 110])	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_labels == ['10', '100', ''])	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (10, 110))	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (1, ' '))	#pylint: disable=W0212
		# 54-62: Logarithmic secondary axis (points not at decade edge)
		panel_obj = putil.plot.Panel(series=[series7_obj], log_dep_axis=True)
		test_list.append((panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, False))	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_locs == [10, 100])	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_labels == ['10', '100'])	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (10, 100))	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' '))	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_locs == None)	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_labels == None)	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (None, None))	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (None, None))	#pylint: disable=W0212
		# 63-71: Logarithmic secondary axis (1 point)
		panel_obj = putil.plot.Panel(series=[series8_obj], log_dep_axis=True)
		test_list.append((panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, False))	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_locs == [18, 20, 22])	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_labels == ['18', '20', '22'])	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (18, 22))	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' '))	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_locs == None)	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_labels == None)	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (None, None))	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (None, None))	#pylint: disable=W0212
		# 72-80: Linear secondary axis (1 point)
		panel_obj = putil.plot.Panel(series=[series8_obj], log_dep_axis=False)
		test_list.append((panel_obj._panel_has_primary_axis, panel_obj._panel_has_secondary_axis) == (True, False))	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_locs == [18, 20, 22])	#pylint: disable=W0212
		test_list.append(panel_obj._primary_dep_var_labels == ['18', '20', '22'])	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (18, 22))	#pylint: disable=W0212
		test_list.append((panel_obj._primary_dep_var_div, panel_obj._primary_dep_var_unit_scale) == (1, ' '))	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_locs == None)	#pylint: disable=W0212
		test_list.append(panel_obj._secondary_dep_var_labels == None)	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (None, None))	#pylint: disable=W0212
		test_list.append((panel_obj._secondary_dep_var_div, panel_obj._secondary_dep_var_unit_scale) == (None, None))	#pylint: disable=W0212
		#
		assert test_list == [True]*81

	def test_complete(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test that _complete() method behaves correctly """
		test_list = list()
		obj = putil.plot.Panel(series=None)
		test_list.append(obj._complete() == False)	#pylint: disable=W0212
		obj.series = default_series
		test_list.append(obj._complete() == True)	#pylint: disable=W0212
		assert test_list == 2*[True]

	def test_scale_series(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test that series scaling function behaves correctly """
		#return putil.plot.Series(data_source=default_source, label='test series')
		source_obj = putil.plot.BasicSource(indep_var=numpy.array([5, 6, 7, 8]), dep_var=numpy.array([4.2, 8, 10, 4]))
		series_obj = putil.plot.Series(data_source=source_obj, label='test', secondary_axis=True)
		panel1_obj = putil.plot.Panel(series=series_obj)
		panel2_obj = putil.plot.Panel(series=[default_series, series_obj])
		test_list = list()
		obj = putil.plot.Panel(series=default_series)
		obj._scale_dep_var(2, None)	#pylint: disable=W0212
		test_list.append((abs(obj.series[0].scaled_dep_var-[0, -5, 2.5, 2]) < 1e-10).all() == True)
		obj._scale_dep_var(2, 5)	#pylint: disable=W0212
		test_list.append((abs(obj.series[0].scaled_dep_var-[0, -5, 2.5, 2]) < 1e-10).all() == True)
		panel1_obj._scale_dep_var(None, 2)	#pylint: disable=W0212
		test_list.append((abs(panel1_obj.series[0].scaled_dep_var-[2.1, 4, 5, 2]) < 1e-10).all() == True)
		panel2_obj._scale_dep_var(4, 5)	#pylint: disable=W0212
		test_list.append(((abs(panel2_obj.series[0].scaled_dep_var-[0, -2.5, 1.25, 1]) < 1e-10).all(), (abs(panel2_obj.series[1].scaled_dep_var-[0.84, 1.6, 2, 0.8]) < 1e-10).all()) == (True, True))
		assert test_list == 4*[True]

	def test_str(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test that str behaves correctly """
		test_list = list()
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
		test_list.append(str(obj) == ret)
		obj = putil.plot.Panel(series=default_series, primary_axis_label='Output', primary_axis_units='Volts', secondary_axis_label='Input', secondary_axis_units='Watts', show_indep_axis=True)
		ret = 'Series 0:\n'
		ret += '   Data source: putil.plot.BasicSource class object\n'
		ret += '   Independent variable: [ 5.0, 6.0, 7.0, 8.0 ]\n'
		ret += '   Dependent variable: [ 0.0, -10.0, 5.0, 4.0 ]\n'
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
		test_list.append(str(obj) == ret)
		assert test_list == 2*[True]

	def test_cannot_delete_attributes(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		obj = putil.plot.Panel(series=default_series)
		test_list = list()
		with pytest.raises(AttributeError) as excinfo:
			del obj.series
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.primary_axis_label
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.secondary_axis_label
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.primary_axis_units
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.secondary_axis_units
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.log_dep_axis
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.legend_props
		test_list.append(excinfo.value.message == "can't delete attribute")
		assert test_list == 7*[True]

	def test_images(self, tmpdir):	#pylint: disable=C0103,R0201,W0621
		""" Compare images to verify correct plotting of panel """
		tmpdir.mkdir('test_images')
		test_list = list()
		images_dict_list = gen_ref_images.unittest_panel_images(mode='test', test_dir=str(tmpdir))
		for images_dict in images_dict_list:
			ref_file_name = images_dict['ref_file_name']
			test_file_name = images_dict['test_file_name']
			metrics = compare_images(ref_file_name, test_file_name)
			result = (metrics[0] < IMGTOL) and (metrics[1] < IMGTOL)
			print 'Comparison: {0} with {1} -> {2} {3}'.format(ref_file_name, test_file_name, result, metrics)
			test_list.append(result)
		assert test_list == [True]*len(images_dict_list)

###
# Tests for Figure
###
@pytest.fixture
def default_panel(default_series):	#pylint: disable=W0621
	""" Provides a default panel object to be used in teseting the putil.Figure() class """
	return putil.plot.Panel(series=default_series, primary_axis_label='Primary axis', primary_axis_units='A', secondary_axis_label='Secondary axis', secondary_axis_units='B')

class TestFigure(object):	#pylint: disable=W0232,R0903
	""" Tests for Figure """
	def test_indep_var_label_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test indep_var_label data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Figure(panels=default_panel, indep_var_label=5)
		test_list.append(excinfo.value.message == 'Argument `indep_var_label` is of the wrong type')
		# These assignments should not raise an exception
		putil.plot.Figure(panels=default_panel, indep_var_label=None)
		putil.plot.Figure(panels=default_panel, indep_var_label='sec')
		obj = putil.plot.Figure(panels=default_panel, indep_var_label='test')
		test_list.append(obj.indep_var_label == 'test')
		assert test_list == [True]*2

	def test_indep_var_units_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test indep_var_units data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Figure(panels=default_panel, indep_var_units=5)
		test_list.append(excinfo.value.message == 'Argument `indep_var_units` is of the wrong type')
		# These assignments should not raise an exception
		putil.plot.Figure(panels=default_panel, indep_var_units=None)
		putil.plot.Figure(panels=default_panel, indep_var_units='sec')
		obj = putil.plot.Figure(panels=default_panel, indep_var_units='test')
		test_list.append(obj.indep_var_units == 'test')
		assert test_list == [True]*2

	def test_title_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test title data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Figure(panels=default_panel, title=5)
		test_list.append(excinfo.value.message == 'Argument `title` is of the wrong type')
		# These assignments should not raise an exception
		putil.plot.Figure(panels=default_panel, title=None)
		putil.plot.Figure(panels=default_panel, title='sec')
		obj = putil.plot.Figure(panels=default_panel, title='test')
		test_list.append(obj.title == 'test')
		assert test_list == [True]*2

	def test_log_indep_axis_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test log_indep_axis data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Figure(panels=default_panel, log_indep_axis=5)
		test_list.append(excinfo.value.message == 'Argument `log_indep_axis` is of the wrong type')
		negative_data_source = putil.plot.BasicSource(indep_var=numpy.array([-5, 6, 7, 8]), dep_var=numpy.array([0.1, 10, 5, 4]))
		negative_series = putil.plot.Series(data_source=negative_data_source, label='negative data series')
		negative_panel = putil.plot.Panel(series=negative_series)
		with pytest.raises(ValueError) as excinfo:
			putil.plot.Figure(panels=negative_panel, log_indep_axis=True)
		test_list.append(excinfo.value.message == 'Figure cannot cannot be plotted with a logarithmic independent axis because panel 0, series 0 contains negative independent data points')
		# These assignments should not raise an exception
		obj = putil.plot.Figure(panels=default_panel, log_indep_axis=False)
		test_list.append(obj.log_indep_axis == False)
		obj = putil.plot.Figure(panels=default_panel, log_indep_axis=True)
		test_list.append(obj.log_indep_axis == True)
		obj = putil.plot.Figure(panels=default_panel)
		test_list.append(obj.log_indep_axis == False)
		assert test_list == [True]*5

	def test_fig_width_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test figure width data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Figure(panels=default_panel, fig_width='a')
		test_list.append(excinfo.value.message == 'Argument `fig_width` is of the wrong type')
		# These assignments should not raise an exception
		obj = putil.plot.Figure(panels=None)
		test_list.append(obj.fig_width == None)
		obj = putil.plot.Figure(panels=default_panel)
		test_list.append(obj.fig_width-6.08 < 1e-10)
		obj.fig_width = 5
		test_list.append(obj.fig_width == 5)
		assert test_list == 4*[True]

	def test_fig_height_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test figure height data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Figure(panels=default_panel, fig_height='a')
		test_list.append(excinfo.value.message == 'Argument `fig_height` is of the wrong type')
		# These assignments should not raise an exception
		obj = putil.plot.Figure(panels=None)
		test_list.append(obj.fig_height == None)
		obj = putil.plot.Figure(panels=default_panel)
		test_list.append(obj.fig_height-4.31 < 1e-10)
		obj.fig_height = 5
		test_list.append(obj.fig_height == 5)
		assert test_list == 4*[True]

	def test_panels_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test panel data validation """
		# This assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Figure(panels=5)
		test_list.append(excinfo.value.message == 'Argument `panels` is of the wrong type')
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.Figure(panels=[default_panel, putil.plot.Panel(series=None)])
		test_list.append(excinfo.value.message == 'Panel 1 is not fully specified')
		# These assignments should not raise an exception
		putil.plot.Figure(panels=None)
		putil.plot.Figure(panels=default_panel)
		assert test_list == 2*[True]

	def test_fig_wrong_type(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test fig attribute """
		test_list = list()
		obj = putil.plot.Figure(panels=None)
		test_list.append(obj.fig == None)
		obj = putil.plot.Figure(panels=default_panel)
		test_list.append(isinstance(obj.fig, matplotlib.figure.Figure))
		assert test_list == 2*[True]

	def test_axes_list(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test axes_list attribute """
		test_list = list()
		obj = putil.plot.Figure(panels=None)
		test_list.append(obj.axes_list == list())
		obj = putil.plot.Figure(panels=default_panel)
		comp_list = list()
		for num, axis_dict in enumerate(obj.axes_list):
			if (axis_dict['number'] == num) and ((axis_dict['primary'] is None) or (isinstance(axis_dict['primary'], matplotlib.axes.Axes))) and \
					((axis_dict['secondary'] is None) or (isinstance(axis_dict['secondary'], matplotlib.axes.Axes))):
				comp_list.append(True)
		test_list.append(comp_list == len(obj.axes_list)*[True])
		assert test_list == 2*[True]

	def test_specified_figure_size_too_small(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test that method behaves correctly when requested figure size is too small """
		test_list = list()
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.Figure(panels=default_panel, indep_var_label='Input', indep_var_units='Amps', title='My graph', fig_width=0.1, fig_height=200)
		test_list.append(excinfo.value.message == 'Figure size is too small: minimum width = 6.08, minimum height 4.99')
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.Figure(panels=default_panel, indep_var_label='Input', indep_var_units='Amps', title='My graph', fig_width=200, fig_height=0.1)
		test_list.append(excinfo.value.message == 'Figure size is too small: minimum width = 6.08, minimum height 4.99')
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.Figure(panels=default_panel, indep_var_label='Input', indep_var_units='Amps', title='My graph', fig_width=0.1, fig_height=0.1)
		test_list.append(excinfo.value.message == 'Figure size is too small: minimum width = 6.08, minimum height 4.99')
		assert test_list == 3*[True]

	def test_complete(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test that _complete() method behaves correctly """
		test_list = list()
		obj = putil.plot.Figure(panels=None)
		test_list.append(obj._complete() == False)	#pylint: disable=W0212
		obj.panels = default_panel
		test_list.append(obj._complete() == True)	#pylint: disable=W0212
		assert test_list == 2*[True]

	def test_str(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test that str behaves correctly """
		test_list = list()
		obj = putil.plot.Figure(panels=None)
		ret = 'Panels: None\n'
		ret += 'Independent variable label: not specified\n'
		ret += 'Independent variable units: not specified\n'
		ret += 'Logarithmic independent axis: False\n'
		ret += 'Title: not specified\n'
		ret += 'Figure width: None\n'
		ret += 'Figure height: None\n'
		test_list.append(str(obj) == ret)
		obj = putil.plot.Figure(panels=default_panel, indep_var_label='Input', indep_var_units='Amps', title='My graph')
		ret = 'Panel 0:\n'
		ret += '   Series 0:\n'
		ret += '      Data source: putil.plot.BasicSource class object\n'
		ret += '      Independent variable: [ 5.0, 6.0, 7.0, 8.0 ]\n'
		ret += '      Dependent variable: [ 0.0, -10.0, 5.0, 4.0 ]\n'
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
		test_list.append(str(obj) == ret)
		assert test_list == 2*[True]

	def test_cannot_delete_attributes(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		obj = putil.plot.Figure(panels=default_panel)
		test_list = list()
		with pytest.raises(AttributeError) as excinfo:
			del obj.panels
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_var_label
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_var_units
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.title
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.log_indep_axis
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.fig_width
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.fig_height
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.fig
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.axes_list
		test_list.append(excinfo.value.message == "can't delete attribute")
		assert test_list == 9*[True]

	def test_images(self, tmpdir):	#pylint: disable=C0103,R0201,W0621
		""" Compare images to verify correct plotting of figure """
		tmpdir.mkdir('test_images')
		test_list = list()
		images_dict_list = gen_ref_images.unittest_figure_images(mode='test', test_dir=str(tmpdir))
		for images_dict in images_dict_list:
			ref_file_name = images_dict['ref_file_name']
			test_file_name = images_dict['test_file_name']
			metrics = compare_images(ref_file_name, test_file_name)
			result = (metrics[0] < IMGTOL) and (metrics[1] < IMGTOL)
			print 'Comparison: {0} with {1} -> {2} {3}'.format(ref_file_name, test_file_name, result, metrics)
			test_list.append(result)
		assert test_list == [True]*len(images_dict_list)

###
# Tests for parameterized_color_space
###
class TestParameterizedColorSpace(object):	#pylint: disable=W0232,R0903
	""" Tests for function parameterized_color_space """
	def test_param_list_wrong_type(self):	#pylint: disable=C0103,R0201,W0621
		""" Test for invalid series parameter """
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.parameterized_color_space('a')
		test_list.append(excinfo.value.message == 'Argument `param_list` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.plot.parameterized_color_space(list())
		test_list.append(excinfo.value.message == 'Argument `param_list` is empty')
		with pytest.raises(TypeError) as excinfo:
			putil.plot.parameterized_color_space(['a', None, False])
		test_list.append(excinfo.value.message == 'Argument `param_list` is of the wrong type')
		# This should not raise an exception
		putil.plot.parameterized_color_space([0, 1, 2, 3.3])
		assert test_list == 3*[True]

	def test_offset_wrong_type(self):	#pylint: disable=C0103,R0201,W0621
		""" Test for invalid offset parameter """
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.parameterized_color_space([1, 2], 'a')
		test_list.append(excinfo.value.message == 'Argument `offset` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.plot.parameterized_color_space([1, 2], -0.1)
		test_list.append(excinfo.value.message == 'Argument `offset` is not in the range [0.0, 1.0]')
		# This should not raise an exception
		putil.plot.parameterized_color_space([0, 1, 2, 3.3], 0.5)
		assert test_list == 2*[True]

	def test_color_space_wrong_type(self):	#pylint: disable=C0103,R0201,W0621
		""" Test for invalid offset parameter """
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.parameterized_color_space([1, 2], color_space=3)
		test_list.append(excinfo.value.message == 'Argument `color_space` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.plot.parameterized_color_space([1, 2], color_space='a')
		test_list.append(excinfo.value.message == "Argument `color_space` is not one of ['binary', 'Blues', 'BuGn', 'BuPu', 'gist_yarg', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd'] (case insensitive)")	#pylint: disable=C0301
		# This should not raise an exception
		putil.plot.parameterized_color_space([0, 1, 2, 3.3], color_space='Blues')
		assert test_list == 2*[True]

	def test_function_works(self):	#pylint: disable=C0103,R0201,W0621
		""" Test for correct behavior of function """
		import matplotlib.pyplot as plt
		color_space = plt.cm.Greys	#pylint: disable=E1101
		result = putil.plot.parameterized_color_space([0, 2/3.0, 4/3.0, 2], 0.25, 'Greys')
		assert result == [color_space(0.25), color_space(0.5), color_space(0.75), color_space(1.0)]
