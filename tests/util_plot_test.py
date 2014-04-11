"""
util_plot unit tests
"""

import numpy
import pytest

import util_plot

# Tests for BasicSource
def test_basic_source_indep_min_type():	#pylint: disable-msg=C0103
	"""
	Tests indep_min type validation
	"""
	comp = list()
	# __init__ path
	# Wrong types
	with pytest.raises(TypeError) as excinfo:
		util_plot.BasicSource(indep_min='a')
	comp.append(excinfo.value.message == 'Parameter indep_min is of the wrong type')
	with pytest.raises(TypeError) as excinfo:
		util_plot.BasicSource(indep_min=False)
	comp.append(excinfo.value.message == 'Parameter indep_min is of the wrong type')
	# Valid values, these should not raise an exception
	comp.append(util_plot.BasicSource(indep_min=None).indep_min == None)
	comp.append(util_plot.BasicSource(indep_min=1).indep_min == 1)
	comp.append(util_plot.BasicSource(indep_min=2.0).indep_min == 2.0)
	# Managed attribute path
	# Wrong types
	obj = util_plot.BasicSource()
	with pytest.raises(TypeError) as excinfo:
		obj.indep_min = 'a'
	comp.append(excinfo.value.message == 'Parameter indep_min is of the wrong type')
	with pytest.raises(TypeError) as excinfo:
		obj.indep_min = False
	comp.append(excinfo.value.message == 'Parameter indep_min is of the wrong type')
	# Valid values, these should not raise an exception
	obj.indep_min = None
	comp.append(obj.indep_min == None)
	obj.indep_min = 1
	comp.append(obj.indep_min == 1)
	obj.indep_min = 2.0
	comp.append(obj.indep_min == 2.0)
	assert comp == 10*[True]

def test_basic_source_indep_max_type():	#pylint: disable-msg=C0103
	"""
	Tests indep_max type validation
	"""
	comp = list()
	# __init__ path
	# Wrong types
	with pytest.raises(TypeError) as excinfo:
		util_plot.BasicSource(indep_max='a')
	comp.append(excinfo.value.message == 'Parameter indep_max is of the wrong type')
	with pytest.raises(TypeError) as excinfo:
		util_plot.BasicSource(indep_max=False)
	comp.append(excinfo.value.message == 'Parameter indep_max is of the wrong type')
	# Valid values, these should not raise an exception
	comp.append(util_plot.BasicSource(indep_max=None).indep_max == None)
	comp.append(util_plot.BasicSource(indep_max=1).indep_max == 1)
	comp.append(util_plot.BasicSource(indep_max=2.0).indep_max == 2.0)
	# Managed attribute path
	# Wrong types
	obj = util_plot.BasicSource()
	with pytest.raises(TypeError) as excinfo:
		obj.indep_max = 'a'
	comp.append(excinfo.value.message == 'Parameter indep_max is of the wrong type')
	with pytest.raises(TypeError) as excinfo:
		obj.indep_max = False
	comp.append(excinfo.value.message == 'Parameter indep_max is of the wrong type')
	# Valid values, these should not raise an exception
	obj.indep_max = None
	comp.append(obj.indep_max == None)
	obj.indep_max = 1
	comp.append(obj.indep_max == 1)
	obj.indep_max = 2.0
	comp.append(obj.indep_max == 2.0)
	assert comp == 10*[True]

def test_basic_source_indep_min_greater_than_indep_max():	#pylint: disable-msg=C0103
	"""
	Test if object behaves correctly when indep_min and indep_max are incongrous
	"""
	comp = list()
	# Assign indep_min first
	obj = util_plot.BasicSource(indep_min=45)
	with pytest.raises(ValueError) as excinfo:
		obj.indep_max = 0
	comp.append(excinfo.value.message == 'Parameter indep_min is greater than parameter indep_max')
	# Assign indep_max first
	obj = util_plot.BasicSource()
	obj.indep_max = 40
	with pytest.raises(ValueError) as excinfo:
		obj.indep_min = 50
	comp.append(excinfo.value.message == 'Parameter indep_min is greater than parameter indep_max')
	assert comp == 2*[True]

def test_basic_source_indep_var_type():	#pylint: disable-msg=C0103
	"""
	Tests indep_var type validation
	"""
	comp = list()
	# __init__ path
	# Wrong type
	with pytest.raises(TypeError) as excinfo:
		util_plot.BasicSource(indep_var='a')
	comp.append(excinfo.value.message == 'Parameter indep_var is of the wrong type')
	# Non monotonically increasing vector
	with pytest.raises(ValueError) as excinfo:
		util_plot.BasicSource(indep_var=numpy.array([1.0, 2.0, 0.0, 3.0]))
	comp.append(excinfo.value.message == 'Parameter indep_var is not an increasing Numpy vector')
	# Empty vector
	with pytest.raises(ValueError) as excinfo:
		util_plot.BasicSource(indep_var=numpy.array([]))
	comp.append(excinfo.value.message == 'Parameter indep_var is empty')
	# Valid values, these should not raise any exception
	comp.append(util_plot.BasicSource(indep_var=None).indep_var == None)
	comp.append((util_plot.BasicSource(indep_var=numpy.array([1, 2, 3])).indep_var == numpy.array([1, 2, 3])).all())
	comp.append((util_plot.BasicSource(indep_var=numpy.array([4.0, 5.0, 6.0])).indep_var == numpy.array([4.0, 5.0, 6.0])).all)
	# Invalid thresholding
	# Assign indep_min via __init__ path
	obj = util_plot.BasicSource(indep_min=45)
	with pytest.raises(ValueError) as excinfo:
		obj.indep_var = numpy.array([1, 2, 3])
	comp.append(excinfo.value.message == 'Parameter indep_var is empty after indep_min/indep_max thresholding')
	# Assign indep_min via attribute
	obj = util_plot.BasicSource(indep_var=numpy.array([1, 2, 3]))
	with pytest.raises(ValueError) as excinfo:
		obj.indep_min = 10
	comp.append(excinfo.value.message == 'Parameter indep_var is empty after indep_min/indep_max thresholding')
	# Assign indep_max via attribute
	obj = util_plot.BasicSource(indep_max=0)
	with pytest.raises(ValueError) as excinfo:
		obj.indep_var = numpy.array([1, 2, 3])
	comp.append(excinfo.value.message == 'Parameter indep_var is empty after indep_min/indep_max thresholding')
	# Assign indep_max via attribute
	obj = util_plot.BasicSource(indep_var=numpy.array([1, 2, 3]))
	with pytest.raises(ValueError) as excinfo:
		obj.indep_max = 0
	comp.append(excinfo.value.message == 'Parameter indep_var is empty after indep_min/indep_max thresholding')
	# Assign both indep_min and indep_max via __init__ path
	with pytest.raises(ValueError) as excinfo:
		util_plot.BasicSource(indep_var=numpy.array([1, 2, 3]), indep_min=4, indep_max=10)
	comp.append(excinfo.value.message == 'Parameter indep_var is empty after indep_min/indep_max thresholding')
	# Managed attribute path
	obj = util_plot.BasicSource()
	# Wrong type
	with pytest.raises(TypeError) as excinfo:
		util_plot.BasicSource(indep_var='a')
	comp.append(excinfo.value.message == 'Parameter indep_var is of the wrong type')
	# Non monotonically increasing vector
	with pytest.raises(ValueError) as excinfo:
		obj.indep_var = numpy.array([1.0, 2.0, 0.0, 3.0])
	comp.append(excinfo.value.message == 'Parameter indep_var is not an increasing Numpy vector')
	# Empty vector
	with pytest.raises(ValueError) as excinfo:
		obj.indep_var = numpy.array([])
	comp.append(excinfo.value.message == 'Parameter indep_var is empty')
	obj.indep_var = None
	obj.indep_var = numpy.array([1, 2, 3])
	obj.indep_var = numpy.array([4.0, 5.0, 6.0])
	assert comp == 14*[True]

