# plot_test.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.plot unit tests
"""

import scipy
import numpy
import pytest
from scipy.misc import imread	#pylint: disable=E0611

import putil.plot
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
		comp.append(excinfo.value.message == 'Parameter `{0}` is of the wrong type'.format(param))
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
		comp.append(excinfo.value.message == 'Parameter `{0}` is of the wrong type'.format(param))
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
	comp.append(excinfo.value.message == 'Parameter `indep_min` is greater than parameter `indep_max`')
	# Assign indep_max first
	obj = func()
	obj.indep_max = 40
	with pytest.raises(ValueError) as excinfo:
		obj.indep_min = 50
	comp.append(excinfo.value.message == 'Parameter `indep_min` is greater than parameter `indep_max`')
	assert comp == 2*[True]

###
# Tests for BasicSource
###
class TestBasicSource(object):	#pylint: disable=W0232
	""" Tests for BasicSource """
	def test_indep_min_type(self):	#pylint: disable=C0103,R0201
		""" Tests indep_min type validation """
		indep_min_max_type(putil.plot.BasicSource, 'indep_min')

	def test_indep_max_type(self):	#pylint: disable=C0103,R0201
		""" Tests indep_max type validation """
		indep_min_max_type(putil.plot.BasicSource, 'indep_max')

	def test_indep_min_greater_than_indep_max(self):	#pylint: disable=C0103,R0201
		""" Test if object behaves correctly when indep_min and indep_max are incongrous """
		indep_min_greater_than_indep_max(putil.plot.BasicSource)

	def test_indep_var_type(self):	#pylint: disable=C0103,R0201
		""" Tests indep_var type validation """
		comp = list()
		# __init__ path
		# Wrong type
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(indep_var='a')
		comp.append(excinfo.value.message == 'Parameter `indep_var` is of the wrong type')
		# Non monotonically increasing vector
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(indep_var=numpy.array([1.0, 2.0, 0.0, 3.0]))
		comp.append(excinfo.value.message == 'Parameter `indep_var` is of the wrong type')
		# Empty vector
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(indep_var=numpy.array([]))
		comp.append(excinfo.value.message == 'Parameter `indep_var` is of the wrong type')
		# Valid values, these should not raise any exception
		comp.append(putil.plot.BasicSource(indep_var=None).indep_var == None)
		comp.append((putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3])).indep_var == numpy.array([1, 2, 3])).all())
		comp.append((putil.plot.BasicSource(indep_var=numpy.array([4.0, 5.0, 6.0])).indep_var == numpy.array([4.0, 5.0, 6.0])).all())
		# Invalid range bounding
		# Assign indep_min via __init__ path
		obj = putil.plot.BasicSource(indep_min=45)
		with pytest.raises(ValueError) as excinfo:
			obj.indep_var = numpy.array([1, 2, 3])
		comp.append(excinfo.value.message == 'Parameter `indep_var` is empty after `indep_min`/`indep_max` range bounding')
		# Assign indep_min via attribute
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]))
		with pytest.raises(ValueError) as excinfo:
			obj.indep_min = 10
		comp.append(excinfo.value.message == 'Parameter `indep_var` is empty after `indep_min`/`indep_max` range bounding')
		# Assign indep_max via attribute
		obj = putil.plot.BasicSource(indep_max=0)
		with pytest.raises(ValueError) as excinfo:
			obj.indep_var = numpy.array([1, 2, 3])
		comp.append(excinfo.value.message == 'Parameter `indep_var` is empty after `indep_min`/`indep_max` range bounding')
		# Assign indep_max via attribute
		obj = putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]))
		with pytest.raises(ValueError) as excinfo:
			obj.indep_max = 0
		comp.append(excinfo.value.message == 'Parameter `indep_var` is empty after `indep_min`/`indep_max` range bounding')
		# Assign both indep_min and indep_max via __init__ path
		with pytest.raises(ValueError) as excinfo:
			putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), indep_min=4, indep_max=10)
		comp.append(excinfo.value.message == 'Parameter `indep_var` is empty after `indep_min`/`indep_max` range bounding')
		# Managed attribute path
		obj = putil.plot.BasicSource()
		# Wrong type
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(indep_var='a')
		comp.append(excinfo.value.message == 'Parameter `indep_var` is of the wrong type')
		# Non monotonically increasing vector
		with pytest.raises(TypeError) as excinfo:
			obj.indep_var = numpy.array([1.0, 2.0, 0.0, 3.0])
		comp.append(excinfo.value.message == 'Parameter `indep_var` is of the wrong type')
		# Empty vector
		with pytest.raises(TypeError) as excinfo:
			obj.indep_var = numpy.array([])
		comp.append(excinfo.value.message == 'Parameter `indep_var` is of the wrong type')
		obj.indep_var = None
		comp.append(obj.indep_var == None)
		obj.indep_var = numpy.array([1, 2, 3])
		comp.append((obj.indep_var == numpy.array([1, 2, 3])).all())
		obj.indep_var = numpy.array([4.0, 5.0, 6.0])
		comp.append((obj.indep_var == numpy.array([4.0, 5.0, 6.0])).all())
		assert comp == 17*[True]

	def test_dep_var_type(self):	#pylint: disable=C0103,R0201
		""" Tests dep_var type validation """
		comp = list()
		# __init__ path
		# Wrong type
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(dep_var='a')
		comp.append(excinfo.value.message == 'Parameter `dep_var` is of the wrong type')
		# Empty vector
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(dep_var=numpy.array([]))
		comp.append(excinfo.value.message == 'Parameter `dep_var` is of the wrong type')
		# Valid values, these should not raise any exception
		comp.append(putil.plot.BasicSource(dep_var=None).dep_var == None)
		comp.append((putil.plot.BasicSource(dep_var=numpy.array([1, 2, 3])).dep_var == numpy.array([1, 2, 3])).all())
		comp.append((putil.plot.BasicSource(dep_var=numpy.array([4.0, 5.0, 6.0])).dep_var == numpy.array([4.0, 5.0, 6.0])).all())
		# Managed attribute path
		obj = putil.plot.BasicSource()
		# Wrong type
		with pytest.raises(TypeError) as excinfo:
			putil.plot.BasicSource(dep_var='a')
		comp.append(excinfo.value.message == 'Parameter `dep_var` is of the wrong type')
		# Empty vector
		with pytest.raises(TypeError) as excinfo:
			obj.dep_var = numpy.array([])
		comp.append(excinfo.value.message == 'Parameter `dep_var` is of the wrong type')
		obj.dep_var = None
		comp.append(obj.dep_var == None)
		obj.dep_var = numpy.array([1, 2, 3])
		comp.append((obj.dep_var == numpy.array([1, 2, 3])).all())
		obj.dep_var = numpy.array([4.0, 5.0, 6.0])
		comp.append((obj.dep_var == numpy.array([4.0, 5.0, 6.0])).all())
		assert comp == 10*[True]

	def test_indep_var_and_dep_var_do_not_have_the_same_number_of_elements(self):	#pylint: disable=C0103,R0201
		""" Tests dep_var type validation """
		comp = list()
		# indep_var set first
		obj = putil.plot.BasicSource(indep_var=numpy.array([10, 20, 30, 40, 50, 60]), indep_min=30, indep_max=50)
		with pytest.raises(ValueError) as excinfo:
			obj.dep_var = numpy.array([100, 200, 300])
		comp.append(excinfo.value.message == 'Parameters `indep_var` and `dep_var` must have the same number of elements')
		# dep_var set first
		obj = putil.plot.BasicSource(dep_var=numpy.array([100, 200, 300]), indep_min=30, indep_max=50)
		with pytest.raises(ValueError) as excinfo:
			obj.indep_var = numpy.array([10, 20, 30, 40, 50, 60])
		comp.append(excinfo.value.message == 'Parameters `indep_var` and `dep_var` must have the same number of elements')
		assert comp == 2*[True]

	def test_complete(self):	#pylint: disable=C0103,R0201
		""" Test that _complete() method behaves correctly """
		comp = list()
		obj = putil.plot.BasicSource(indep_min=0, indep_max=50)
		comp.append(obj._complete() == False)	#pylint: disable=W0212
		obj.indep_var = numpy.array([1, 2, 3])
		comp.append(obj._complete() == False)	#pylint: disable=W0212
		obj.dep_var = numpy.array([10, 20, 30])
		comp.append(obj._complete() == True)	#pylint: disable=W0212
		assert comp == 3*[True]

	def test_str(self):	#pylint: disable=C0103,R0201
		""" Test that str behaves correctly """
		comp = list()
		# Null object
		obj = str(putil.plot.BasicSource())
		ref = 'Independent variable minimum: -inf\nIndependent variable maximum: +inf\nIndependent variable: None\nDependent variable: None'
		comp.append(obj == ref)
		# indep_min set
		obj = str(putil.plot.BasicSource(indep_min=10))
		ref = 'Independent variable minimum: 10\nIndependent variable maximum: +inf\nIndependent variable: None\nDependent variable: None'
		comp.append(obj == ref)
		# indep_max set
		obj = str(putil.plot.BasicSource(indep_min=10, indep_max=20))
		ref = 'Independent variable minimum: 10\nIndependent variable maximum: 20\nIndependent variable: None\nDependent variable: None'
		comp.append(obj == ref)
		# indep_var set
		obj = str(putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), indep_min=-10, indep_max=20.0))
		ref = 'Independent variable minimum: -10\nIndependent variable maximum: 20.0\nIndependent variable: [ 1.0, 2.0, 3.0 ]\nDependent variable: None'
		comp.append(obj == ref)
		# dep_var set
		obj = str(putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3]), dep_var=numpy.array([10, 20, 30]), indep_min=-10, indep_max=20.0))
		ref = 'Independent variable minimum: -10\nIndependent variable maximum: 20.0\nIndependent variable: [ 1.0, 2.0, 3.0 ]\nDependent variable: [ 10.0, 20.0, 30.0 ]'
		comp.append(obj == ref)
		assert comp == 5*[True]

	def test_cannot_delete_attributes(self):	#pylint: disable=C0103,R0201
		""" Test that del method raises an exception on all class attributes """
		obj = putil.plot.BasicSource()
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
@pytest.fixture
def tmp_csv_file(tmpdir):
	""" Fixture to create temporary CSV file for testing purposes """
	file_handle = tmpdir.mkdir('sub').join('tmp.csv')
	file_handle.write('Col1,Col2,Col3,Col4,Col5,Col6\n', mode='w')
	file_handle.write('0,1,2,3,,5\n', mode='a')
	file_handle.write('0,2,4,5,,4\n', mode='a')
	file_handle.write('0,3,1,8,,3\n', mode='a')
	file_handle.write('1,1,5,7,8,0\n', mode='a')
	file_handle.write('1,2,3,7,9,7\n', mode='a')
	return True

class TestCsvSource(object):	#pylint: disable=W0232,R0904
	""" Tests for CsvSource """
	def test_indep_min_type(self):	#pylint: disable=C0103,R0201
		""" Tests indep_min type validation """
		indep_min_max_type(putil.plot.CsvSource, 'indep_min')

	def test_indep_max_type(self):	#pylint: disable=C0103,R0201
		""" Tests indep_max type validation """
		indep_min_max_type(putil.plot.CsvSource, 'indep_max')

	def test_indep_min_greater_than_indep_max(self):	#pylint: disable=C0103,R0201
		""" Test if object behaves correctly when indep_min and indep_max are incongrous """
		indep_min_greater_than_indep_max(putil.plot.CsvSource)

	def test_file_name_wrong_type(self):	#pylint: disable=C0103,R0201
		""" Test if object behaves correctly when file_name is of the wrong type """
		# This assignment should raise an exception
		with pytest.raises(TypeError) as excinfo:
			putil.plot.CsvSource(file_name=5)
		comp = excinfo.value.message == 'Parameter `file_name` is of the wrong type'
		# This assignment should not raise an exception
		putil.plot.CsvSource(file_name=None)
		assert comp == True

	def test_file_does_not_exist(self):	#pylint: disable=C0103,R0201
		""" Test if object behaves correctly when CSV file does not exist """
		file_name = 'nonexistent_file_name.csv'
		with pytest.raises(IOError) as excinfo:
			putil.plot.CsvSource(file_name=file_name)
		assert excinfo.value.message == 'File {0} could not be found'.format(file_name)

	def test_file_exist(self, tmpdir, tmp_csv_file):	#pylint: disable=W0621,W0613,C0103,R0201
		""" Test if object behaves correctly when CSV file exists """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		putil.plot.CsvSource(file_name=file_name)

	def test_data_filter_wrong_type(self):	#pylint: disable=C0103,R0201
		""" Test if object behaves correctly when dfilter is of the wrong type """
		# This assignment should raise an exception
		with pytest.raises(TypeError) as excinfo:
			putil.plot.CsvSource(dfilter=5)
		comp = excinfo.value.message == 'Parameter `dfilter` is of the wrong type'
		# This assignment should not raise an exception
		putil.plot.CsvSource(dfilter=None)
		assert comp == True

	def test_data_filter_operation(self, tmpdir, tmp_csv_file):	#pylint: disable=W0621,W0613,C0103,R0201
		""" Test if object behaves correctly when data filter and file name are given """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		# This assignment should raise an exception
		with pytest.raises(ValueError) as excinfo:
			putil.plot.CsvSource(file_name=file_name, dfilter={'Col99':500})
		comp = excinfo.value.message == 'Column COL99 in data filter not found in comma-separated file {0} header'.format(file_name)
		putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0})
		assert comp == True

	def test_indep_col_label_wrong_type(self, tmpdir, tmp_csv_file):	#pylint: disable=W0621,W0613,C0103,R0201
		""" Test if object behaves correctly when indep_col_label is of the wrong type """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		test_list = list()
		# These assignments should raise an exception
		with pytest.raises(TypeError) as excinfo:
			putil.plot.CsvSource(indep_col_label=5)
		test_list.append(excinfo.value.message == 'Parameter `indep_col_label` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col99')
		test_list.append(excinfo.value.message == 'Column COL99 (independent column label) could not be found in comma-separated file {0} header'.format(file_name))
		# These assignments should not raise an exception
		putil.plot.CsvSource(indep_col_label=None)
		putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2')
		assert test_list == [True, True]

	def test_dep_col_label_wrong_type(self, tmpdir, tmp_csv_file):	#pylint: disable=W0621,W0613,C0103,R0201
		""" Test if object behaves correctly when dep_col_label is of the wrong type """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		test_list = list()
		# This assignment should raise an exception
		with pytest.raises(TypeError) as excinfo:
			putil.plot.CsvSource(dep_col_label=5)
		test_list.append(excinfo.value.message == 'Parameter `dep_col_label` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.plot.CsvSource(file_name=file_name, dep_col_label='Col99')
		test_list.append(excinfo.value.message == 'Column COL99 (dependent column label) could not be found in comma-separated file {0} header'.format(file_name))	# Thess assignments should not raise an exception
		# These assignments should not raise an exception
		putil.plot.CsvSource(dep_col_label=None)
		putil.plot.CsvSource(file_name=file_name, dep_col_label='Col3')
		assert test_list == [True, True]

	def test_empty_indep_var_after_filter(self, tmpdir, tmp_csv_file):	#pylint: disable=W0621,W0613,C0103,R0201
		""" Test if object behaves correctly when the independent variable is empty after data filter is applied """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		with pytest.raises(ValueError) as excinfo:
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':10})
		assert excinfo.value.message == 'Filtered independent variable is empty'

	def test_empty_dep_var_after_filter(self, tmpdir, tmp_csv_file):	#pylint: disable=W0621,W0613,C0103,R0201
		""" Test if object behaves correctly when the dependent variable is empty after data filter is applied """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		with pytest.raises(ValueError) as excinfo:
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col5', dfilter={'Col1':0})
		assert excinfo.value.message == 'Filtered dependent variable is empty'

	def test_data_reversed(self, tmpdir, tmp_csv_file):	#pylint: disable=W0621,W0613,C0103,R0201
		""" Test if object behaves correctly when the independent dat is descending order """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col6', dep_col_label='Col3', dfilter={'Col1':0})
		assert ((obj.indep_var == numpy.array([3, 4, 5])).all(), (obj.dep_var == numpy.array([1, 4, 2])).all()) == (True, True)

	def test_fproc_wrong_type(self):	#pylint: disable=C0103,R0201
		""" Test if object behaves correctly when fproc is of the wrong type """
		def fproc1():	#pylint: disable=C0111
			return True
		def fproc2(*args):	#pylint: disable=C0111,W0613
			return True
		def fproc3(**kwargs):	#pylint: disable=C0111,W0613
			return True
		def fproc4(*args, **kwargs):	#pylint: disable=C0111,W0613
			return True
		test_list = list()
		# These assignments should raise an exception
		with pytest.raises(TypeError) as excinfo:
			putil.plot.CsvSource(fproc=5)
		test_list.append(excinfo.value.message == 'Parameter `fproc` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.plot.CsvSource(fproc=fproc1)
		test_list.append(excinfo.value.message == 'Parameter `fproc` (function fproc1) does not have at least 2 arguments')
		# These assignments should not raise an exception
		putil.plot.CsvSource(fproc=fproc2)
		putil.plot.CsvSource(fproc=fproc3)
		putil.plot.CsvSource(fproc=fproc4)
		assert test_list == [True]*2

	def test_fproc_wrong_return(self, tmpdir, tmp_csv_file):	#pylint: disable=W0621,W0613,C0103,R0201,R0912,R0914
		""" Test if object behaves correctly when fproc returns the wrong type and/or number of parameters """
		file_name = str(tmpdir.join('sub/tmp.csv'))
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
		# These assignments should raise an exception
		with pytest.raises(TypeError) as excinfo:
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc1)
		test_list.append(excinfo.value.message == 'Parameter `fproc` (function fproc1) return value is of the wrong type')
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc2)
		test_list.append(excinfo.value.message == 'Parameter `fproc` (function fproc2) returned an illegal number of values')
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
		msg = 'Processing function fproc13 threw an exception when called with the following arguments:\n'
		msg += 'indep_var: [ 1.0, 2.0, 3.0 ]\n'
		msg += 'dep_var: [ 1.0, 2.0, 3.0 ]\n'
		msg += 'par1: 13\n'
		msg += 'Exception error: Test exception message'
		test_list.append(excinfo.value.message == msg)
		# These assignments should not raise an exception
		putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc3)
		putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc7)
		assert test_list == [True]*11

	def test_fproc_eargs_wrong_type(self):	#pylint: disable=W0621,W0613,C0103,R0201
		""" Test if object behaves correctly when fprog_eargs is of the wrong type """
		# This assignment should raise an exception
		with pytest.raises(TypeError) as excinfo:
			putil.plot.CsvSource(fproc_eargs=5)
		comp = excinfo.value.message == 'Parameter `fproc_eargs` is of the wrong type'
		# These assignments should not raise an exception
		putil.plot.CsvSource(fproc_eargs=None)
		putil.plot.CsvSource(fproc_eargs={'arg1':23})
		assert comp == True

	def test_fproc_eargs_parameter_name_validation(self):	#pylint: disable=W0621,W0613,C0103,R0201
		""" Test if object behaves correctly when checking if the arguments in the fprog_eargs dictionary exist """
		def fproc1(indep_var, dep_var):	#pylint: disable=C0111,W0613
			pass
		def fproc2(indep_var, dep_var, par1, par2):	#pylint: disable=C0111,W0613
			pass
		def fproc3(indep_var, dep_var, par3, par4, *args):	#pylint: disable=C0111,W0613
			pass
		def fproc4(indep_var, dep_var, par5, par6, **kwargs):	#pylint: disable=C0111,W0613
			pass
		def fproc5(indep_var, dep_var, par7, par8, *args, **kwargs):	#pylint: disable=C0111,W0613
			pass
		test_list = list()
		# These assignments should raise an exception
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.CsvSource(fproc=fproc1, fproc_eargs={'par1':5})
		test_list.append(excinfo.value.message == 'Extra argument `par1` not found in parameter `fproc` (function fproc1) definition')
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.CsvSource(fproc=fproc2, fproc_eargs={'par3':5})
		test_list.append(excinfo.value.message == 'Extra argument `par3` not found in parameter `fproc` (function fproc2) definition')
		# These assignments should not raise an exception
		putil.plot.CsvSource(fproc=fproc3, fproc_eargs={'par99':5})
		putil.plot.CsvSource(fproc=fproc4, fproc_eargs={'par98':5})
		putil.plot.CsvSource(fproc=fproc5, fproc_eargs={'par97':5})
		assert test_list == [True]*2

	def test_fproc_works(self, tmpdir, tmp_csv_file):	#pylint: disable=W0621,W0613,C0103,R0201
		""" Test if object behaves correctly when executing function defined in fproc parameter with extra arguments defined in fproc_eargs parameter """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		def fproc1(indep_var, dep_var, indep_offset, dep_offset):	#pylint: disable=C0111,W0613
			return indep_var+indep_offset, dep_var+dep_offset
		obj = putil.plot.CsvSource(file_name=file_name, indep_col_label='Col2', dep_col_label='Col3', dfilter={'Col1':0}, fproc=fproc1, fproc_eargs={'indep_offset':3, 'dep_offset':100})
		print obj.indep_var
		print obj.dep_var
		assert [(obj.indep_var == numpy.array([4, 5, 6])).all(), (obj.dep_var == numpy.array([102, 104, 101])).all()] == [True]*2

	def test_str(self, tmpdir, tmp_csv_file):	#pylint: disable=W0621,W0613,C0103,R0201
		""" Test that str behaves correctly """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		def fproc1(indep_var, dep_var):	#pylint: disable=C0111,W0613
			return indep_var*1e-3, dep_var+1
		def fproc2(indep_var, dep_var, par1, par2):	#pylint: disable=C0111,W0613
			return indep_var+par1, dep_var-par2
		comp = list()
		# Null object
		obj = str(putil.plot.CsvSource())
		ref = 'File name: None\nData filter: None\nIndependent column label: None\nDependent column label: None\nProcessing function: None\nProcessing function extra arguments: None\n'
		ref += 'Independent variable minimum: -inf\nIndependent variable maximum: +inf\nIndependent variable: None\nDependent variable: None'
		comp.append(obj == ref)
		# indep_min set
		obj = str(putil.plot.CsvSource(indep_min=10))
		ref = 'File name: None\nData filter: None\nIndependent column label: None\nDependent column label: None\nProcessing function: None\nProcessing function extra arguments: None\n'
		ref += 'Independent variable minimum: 10\nIndependent variable maximum: +inf\nIndependent variable: None\nDependent variable: None'
		comp.append(obj == ref)
		# indep_max set
		obj = str(putil.plot.CsvSource(indep_min=10, indep_max=20))
		ref = 'File name: None\nData filter: None\nIndependent column label: None\nDependent column label: None\nProcessing function: None\nProcessing function extra arguments: None\n'
		ref += 'Independent variable minimum: 10\nIndependent variable maximum: 20\nIndependent variable: None\nDependent variable: None'
		comp.append(obj == ref)
		# file name
		obj = str(putil.plot.CsvSource(file_name=file_name, indep_min=10, indep_max=20))
		ref = 'File name: {0}\nData filter: None\nIndependent column label: None\nDependent column label: None\nProcessing function: None\nProcessing function extra arguments: None\n'.format(file_name)
		ref += 'Independent variable minimum: 10\nIndependent variable maximum: 20\nIndependent variable: None\nDependent variable: None'
		comp.append(obj == ref)
		# dfilter
		obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_min=10, indep_max=20))
		ref = 'File name: {0}\nData filter: \n   COL1: 0\nIndependent column label: None\nDependent column label: None\nProcessing function: None\nProcessing function extra arguments: None\n'.format(file_name)
		ref += 'Independent variable minimum: 10\nIndependent variable maximum: 20\nIndependent variable: None\nDependent variable: None'
		comp.append(obj == ref)
		# indep_col_label
		obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', indep_min=2, indep_max=200))
		ref = 'File name: {0}\nData filter: \n   COL1: 0\nIndependent column label: COL2\nDependent column label: None\nProcessing function: None\nProcessing function extra arguments: None\n'.format(file_name)
		ref += 'Independent variable minimum: 2\nIndependent variable maximum: 200\nIndependent variable: [ 2.0, 3.0 ]\nDependent variable: None'
		comp.append(obj == ref)
		# dep_col_label
		obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3', indep_min=2, indep_max=200))
		ref = 'File name: {0}\nData filter: \n   COL1: 0\nIndependent column label: COL2\nDependent column label: COL3\nProcessing function: None\nProcessing function extra arguments: None\n'.format(file_name)
		ref += 'Independent variable minimum: 2\nIndependent variable maximum: 200\nIndependent variable: [ 2.0, 3.0 ]\nDependent variable: [ 4.0, 1.0 ]'
		comp.append(obj == ref)
		# fproc
		obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3', indep_min=2e-3, indep_max=200, fproc=fproc1))
		ref = 'File name: {0}\nData filter: \n   COL1: 0\nIndependent column label: COL2\nDependent column label: COL3\nProcessing function: fproc1\nProcessing function extra arguments: None\n'.format(file_name)
		ref += 'Independent variable minimum: 0.002\nIndependent variable maximum: 200\nIndependent variable: [ 0.002, 0.003 ]\nDependent variable: [ 5.0, 2.0 ]'
		comp.append(obj == ref)
		# fproc_eargs
		obj = str(putil.plot.CsvSource(file_name=file_name, dfilter={'Col1':0}, indep_col_label='Col2', dep_col_label='Col3', indep_min=-2, indep_max=200, fproc=fproc2, fproc_eargs={'par1':3, 'par2':4}))
		ref = 'File name: {0}\nData filter: \n   COL1: 0\nIndependent column label: COL2\nDependent column label: COL3\nProcessing function: fproc2\nProcessing function extra arguments: \n   par1: 3\n   par2: 4\n'.format(file_name)
		ref += 'Independent variable minimum: -2\nIndependent variable maximum: 200\nIndependent variable: [ 4.0, 5.0, 6.0 ]\nDependent variable: [ -2.0, 0.0, -3.0 ]'
		comp.append(obj == ref)
		assert comp == 9*[True]

	def test_complete(self, tmpdir, tmp_csv_file):	#pylint: disable=W0621,W0613,C0103,R0201
		""" Test that _complete() method behaves correctly """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		comp = list()
		obj = putil.plot.CsvSource()
		comp.append(obj._complete() == False)	#pylint: disable=W0212
		obj.file_name = file_name
		comp.append(obj._complete() == False)	#pylint: disable=W0212
		obj.dfilter = {'Col1':0}
		comp.append(obj._complete() == False)	#pylint: disable=W0212
		obj.indep_col_label = 'Col2'
		comp.append(obj._complete() == False)	#pylint: disable=W0212
		obj.dep_col_label = 'Col3'
		comp.append(obj._complete() == True)	#pylint: disable=W0212
		assert comp == 5*[True]

	def test_cannot_delete_attributes(self):	#pylint: disable=C0103,R0201
		""" Test that del method raises an exception on all class attributes """
		obj = putil.plot.CsvSource()
		test_list = list()
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
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.Series(data_source=putil.plot.BasicSource(), label='test')
		test_list.append(excinfo.value.message == 'Parameter `data_source` is not fully specified')
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.Series(data_source=5, label='test')
		test_list.append(excinfo.value.message == 'Parameter `data_source` does not have `indep_var` attribute')
		obj = TestSource()
		obj.indep_var = numpy.array([5, 6, 7, 8])	#pylint: disable=W0201
		with pytest.raises(RuntimeError) as excinfo:
			putil.plot.Series(data_source=obj, label='test')
		test_list.append(excinfo.value.message == 'Parameter `data_source` does not have `dep_var` attribute')
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
		test_list.append(excinfo.value.message == 'Parameter `label` is of the wrong type')
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
		test_list.append(excinfo.value.message == 'Parameter `color` is of the wrong type')
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
			putil.plot.Series(data_source=default_source, label='test', marker=5)
		test_list.append(excinfo.value.message == 'Parameter `marker` is of the wrong type')
		# These assignments should not raise an exception
		obj = putil.plot.Series(data_source=default_source, label='test', marker=False)
		test_list.append(obj.marker == False)
		obj = putil.plot.Series(data_source=default_source, label='test', marker=True)
		test_list.append(obj.marker == True)
		obj = putil.plot.Series(data_source=default_source, label='test')
		test_list.append(obj.marker == True)
		assert test_list == [True]*4

	def test_interp_wrong_type(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test interp data validation """
		# These assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Series(data_source=default_source, label='test', interp=5)
		test_list.append(excinfo.value.message == 'Parameter `interp` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.plot.Series(data_source=default_source, label='test', interp='NOT_AN_OPTION')
		test_list.append(excinfo.value.message == "Parameter `interp` is not one of ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG'] (case insensitive)")
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
		test_list.append(excinfo.value.message == 'Parameter `line_style` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.plot.Series(data_source=default_source, label='test', line_style='x')
		test_list.append(excinfo.value.message == "Parameter `line_style` is not one of ['-', '--', '-.', ':'] (case insensitive)")
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
		test_list.append(excinfo.value.message == 'Parameter `secondary_axis` is of the wrong type')
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
			putil.plot.Series(data_source=default_source, label='test', marker=False, interp=None, line_style=None)
		test_list.append(excinfo.value.message == 'Series options make it not plottable')
		obj = putil.plot.Series(data_source=default_source, label='test', marker=True, interp='CUBIC', line_style=None)
		with pytest.raises(RuntimeError) as excinfo:
			obj.marker = False
		test_list.append(excinfo.value.message == 'Series options make it not plottable')
		obj = putil.plot.Series(data_source=default_source, label='test', marker=False, interp='CUBIC', line_style='-')
		with pytest.raises(RuntimeError) as excinfo:
			obj.interp = None
		test_list.append(excinfo.value.message == 'Series options make it not plottable')
		obj = putil.plot.Series(data_source=default_source, label='test', marker=False, interp='CUBIC', line_style='-')
		with pytest.raises(RuntimeError) as excinfo:
			obj.line_style = None
		test_list.append(excinfo.value.message == 'Series options make it not plottable')
		assert test_list == [True]*4

	def test_str(self, default_source):	#pylint: disable=C0103,R0201,W0621
		""" Test that str behaves correctly """
		obj = putil.plot.Series(data_source=default_source, label='test')
		ret = ''
		ret += 'Data source: putil.plot.BasicSource class object\n'
		ret += 'Independent variable: [ 5.0, 6.0, 7.0, 8.0 ]\n'
		ret += 'Dependent variable: [ 0.0, -10.0, 5.0, 4.0 ]\n'
		ret += 'Label: test\n'
		ret += 'Color: k\n'
		ret += 'Marker: True\n'
		ret += 'Interpolation: CUBIC\n'
		ret += 'Line style: -\n'
		ret += 'Secondary axis: False'
		assert str(obj) == ret

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
		images_dict_list = gen_ref_images.unittest_image(mode='test', test_dir=str(tmpdir))
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
		test_list.append(excinfo.value.message == 'Parameter `primary_axis_label` is of the wrong type')
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
		test_list.append(excinfo.value.message == 'Parameter `primary_axis_units` is of the wrong type')
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
		test_list.append(excinfo.value.message == 'Parameter `secondary_axis_label` is of the wrong type')
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
		test_list.append(excinfo.value.message == 'Parameter `secondary_axis_units` is of the wrong type')
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
		test_list.append(excinfo.value.message == 'Parameter `log_dep_axis` is of the wrong type')
		# These assignments should not raise an exception
		obj = putil.plot.Panel(series=default_series, log_dep_axis=False)
		test_list.append(obj.log_dep_axis == False)
		obj = putil.plot.Panel(series=default_series, log_dep_axis=True)
		test_list.append(obj.log_dep_axis == True)
		obj = putil.plot.Panel(series=default_series)
		test_list.append(obj.log_dep_axis == False)
		assert test_list == [True]*4

	def test_legend_props_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test legend_props data validation """
		# These assignments should raise an exception
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.plot.Panel(series=default_series, legend_props=5)
		test_list.append(excinfo.value.message == 'Parameter `legend_props` is of the wrong type')
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

	def test_intelligent_ticks(self):	#pylint: disable=C0103,R0201,W0621
		""" Test that intelligent_tick methods works for all scenarios """
		test_list = list()
		#
		vector = numpy.array([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
		obj = putil.plot._intelligent_ticks2(vector, min(vector), max(vector), tight=False, calc_ticks=True)	#pylint: disable=W0212
		test_list.append(obj == ([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6], ['0.8', '0.9', '1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6'], 0.8, 1.6, ' '))
		print obj
		#
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot._intelligent_ticks2(vector, min(vector), max(vector), tight=False, calc_ticks=True)	#pylint: disable=W0212
		test_list.append(obj == ([1, 2, 3, 4, 5, 6, 7], ['1', '2', '3', '4', '5', '6', '7'], 1, 7, ' '))
		print obj
		#
		vector = numpy.array([10, 20, 30, 40, 50, 60, 70])
		obj = putil.plot._intelligent_ticks2(vector, min(vector), max(vector), tight=False, calc_ticks=True)	#pylint: disable=W0212
		test_list.append(obj == ([10, 20, 30, 40, 50, 60, 70], ['10', '20', '30', '40', '50', '60', '70'], 10, 70, ' '))
		print obj
		#
		vector = numpy.array([1000, 2000, 3000, 4000, 5000, 6000, 7000])
		obj = putil.plot._intelligent_ticks2(vector, min(vector), max(vector), tight=False, calc_ticks=True)	#pylint: disable=W0212
		test_list.append(obj == ([1, 2, 3, 4, 5, 6, 7], ['1', '2', '3', '4', '5', '6', '7'], 1, 7, 'k'))
		print obj
		#
		vector = numpy.array([200e6, 300e6, 400e6, 500e6, 600e6, 700e6, 800e6, 900e6, 1000e6])
		obj = putil.plot._intelligent_ticks2(vector, min(vector), max(vector), tight=False, calc_ticks=True)	#pylint: disable=W0212
		test_list.append(obj == ([200, 300, 400, 500, 600, 700, 800, 900, 1000], ['200', '300', '400', '500', '600', '700', '800', '900', '1k'], 200, 1000, 'M'))
		print obj
		#
		vector = numpy.array([105, 107.7, 215, 400.2, 600, 700, 800, 810, 820, 830, 840, 850, 900, 905])
		import pdb; pdb.set_trace()
		obj = putil.plot._intelligent_ticks2(vector, min(vector), max(vector), tight=False, calc_ticks=True)	#pylint: disable=W0212
		test_list.append(obj == ([105.0, 193.88888888888889, 282.77777777777777, 371.66666666666663, 460.55555555555554, 549.4444444444445, 638.3333333333333, 727.2222222222222, 816.1111111111111, 905.0],
						   ['105.0', '193.88888888888889', '282.77777777777777', '371.66666666666663', '460.55555555555554', '549.4444444444445', '638.3333333333333', '727.2222222222222', '816.1111111111111', '905.0'],
						   105, 905, ' '))
		print obj
		#
		assert test_list == [True]*5
