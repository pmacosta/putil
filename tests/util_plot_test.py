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
	# __init__ path
	with pytest.raises(TypeError) as excinfo1:
		util_plot.BasicSource(indep_min='a')
	comp1 = excinfo1.value.message == 'Parameter indep_min is of the wrong type'
	with pytest.raises(TypeError) as excinfo2:
		util_plot.BasicSource(indep_min=False)
	comp2 = excinfo2.value.message == 'Parameter indep_min is of the wrong type'
	util_plot.BasicSource(indep_min=None)
	util_plot.BasicSource(indep_min=1)
	util_plot.BasicSource(indep_min=2.0)
	# Managed attribute path
	obj = util_plot.BasicSource()
	with pytest.raises(TypeError) as excinfo3:
		obj.indep_min = 'a'
	comp3 = excinfo3.value.message == 'Parameter indep_min is of the wrong type'
	with pytest.raises(TypeError) as excinfo4:
		obj.indep_min = False
	comp4 = excinfo4.value.message == 'Parameter indep_min is of the wrong type'
	obj.indep_min = None
	obj.indep_min = 1
	obj.indep_min = 2.0
	assert (comp1, comp2, comp3, comp4) == (True, True, True, True)

def test_basic_source_indep_max_type():	#pylint: disable-msg=C0103
	"""
	Tests indep_max type validation
	"""
	# __init__ path
	with pytest.raises(TypeError) as excinfo1:
		util_plot.BasicSource(indep_max='a')
	comp1 = excinfo1.value.message == 'Parameter indep_max is of the wrong type'
	with pytest.raises(TypeError) as excinfo2:
		util_plot.BasicSource(indep_max=False)
	comp2 = excinfo2.value.message == 'Parameter indep_max is of the wrong type'
	util_plot.BasicSource(indep_max=None)
	util_plot.BasicSource(indep_max=1)
	util_plot.BasicSource(indep_max=2.0)
	# Managed attribute path
	obj = util_plot.BasicSource()
	with pytest.raises(TypeError) as excinfo3:
		obj.indep_max = 'a'
	comp3 = excinfo3.value.message == 'Parameter indep_max is of the wrong type'
	with pytest.raises(TypeError) as excinfo4:
		obj.indep_max = False
	comp4 = excinfo4.value.message == 'Parameter indep_max is of the wrong type'
	obj.indep_max = None
	obj.indep_max = 1
	obj.indep_max = 2.0
	assert (comp1, comp2, comp3, comp4) == (True, True, True, True)

def test_basic_source_indep_var_type():	#pylint: disable-msg=C0103
	"""
	Tests indep_var type validation
	"""
	# __init__ path
	with pytest.raises(TypeError) as excinfo1:
		util_plot.BasicSource(indep_var='a')
	comp1 = excinfo1.value.message == 'Parameter indep_max is of the wrong type'
	with pytest.raises(ValueError) as excinfo2:
		util_plot.BasicSource(indep_var=numpy.array([1.0, 2.0, 0.0, 3.0]))
	comp2 = excinfo2.value.message == 'Parameter indep_max is of the wrong type'
	util_plot.BasicSource(indep_var=None)
	util_plot.BasicSource(indep_var=numpy.array([1, 2, 0, 3]))
	util_plot.BasicSource(indep_var=numpy.array([1.0, 2.0, 0.0, 3.0]))
	assert (comp1, comp2) == (True, True)

