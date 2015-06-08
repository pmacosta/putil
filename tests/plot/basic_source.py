# basic_source.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0201,W0212,W0232,W0612

import numpy
import pytest

import putil.misc
import putil.plot
import putil.test


###
# Tests for BasicSource
###
class TestBasicSource(object):
	""" Tests for BasicSource """
	def test_indep_min_type(self):
		""" Tests indep_min type validation """
		# __init__ path
		# Wrong types
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{
				'indep_var':numpy.array([1, 2, 3]),
				'dep_var':numpy.array([10, 20, 30]),
				'indep_min':'a'
			},
			RuntimeError,
			'Argument `indep_min` is not valid'
		)
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{
				'indep_var':numpy.array([1, 2, 3]),
				'dep_var':numpy.array([10, 20, 30]),
				'indep_min':False
			},
			RuntimeError,
			'Argument `indep_min` is not valid'
		)
		# Valid values, these should not raise an exception
		for param_value in [1, 2.0]:
			putil.plot.BasicSource(
				indep_var=numpy.array([1, 2, 3]),
				dep_var=numpy.array([10, 20, 30]),
				indep_min=param_value
			)
		# Managed attribute path
		# Wrong types
		obj = putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([10, 20, 30])
		)
		for param_value in ['a', False]:
			with pytest.raises(RuntimeError) as excinfo:
				obj.indep_min = param_value
			assert putil.test.get_exmsg(excinfo) == 'Argument `indep_min` is not valid'
		# Valid values, these should not raise an exception
		for param_value in [1, 2.0]:
			obj.indep_min = param_value
			assert obj.indep_min == param_value

	def test_indep_max_type(self):
		""" Tests indep_max type validation """
		# __init__ path
		# Wrong types
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{
				'indep_var':numpy.array([1, 2, 3]),
				'dep_var':numpy.array([10, 20, 30]),
				'indep_max':'a'
			},
			RuntimeError,
			'Argument `indep_max` is not valid'
		)
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{
				'indep_var':numpy.array([1, 2, 3]),
				'dep_var':numpy.array([10, 20, 30]),
				'indep_max':False
			},
			RuntimeError,
			'Argument `indep_max` is not valid'
		)
		# Valid values, these should not raise an exception
		for param_value in [1, 2.0]:
			putil.plot.BasicSource(
				indep_var=numpy.array([1, 2, 3]),
				dep_var=numpy.array([10, 20, 30]),
				indep_max=param_value
			)
		# Managed attribute path
		# Wrong types
		obj = putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([10, 20, 30])
		)
		for param_value in ['a', False]:
			with pytest.raises(RuntimeError) as excinfo:
				obj.indep_max = param_value
			assert putil.test.get_exmsg(excinfo) == 'Argument `indep_max` is not valid'
		# Valid values, these should not raise an exception
		for param_value in [1, 2.0]:
			obj.indep_max = param_value
			assert obj.indep_max == param_value

	def test_indep_min_greater_than_indep_max(self):
		"""
		Test if object behaves correctly when indep_min and indep_max
		are incongruous
		"""
		# Assign indep_min first
		obj = putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([10, 20, 30]),
			indep_min=0.5)

		with pytest.raises(ValueError) as excinfo:
			obj.indep_max = 0
		assert putil.test.get_exmsg(excinfo) == ('Argument `indep_min` is greater '
										 'than argument `indep_max`')
		# Assign indep_max first
		obj = putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([10, 20, 30])
		)
		obj.indep_max = 40
		with pytest.raises(ValueError) as excinfo:
			obj.indep_min = 50
		assert putil.test.get_exmsg(excinfo) == ('Argument `indep_min` is greater '
										 'than argument `indep_max`')

	def test_indep_var_type(self):
		""" Tests indep_var type validation """
		# __init__ path
		# Wrong type
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{'indep_var':None, 'dep_var':numpy.array([10, 20, 30])},
			RuntimeError,
			'Argument `indep_var` is not valid'
		)
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{'indep_var':'a', 'dep_var':numpy.array([10, 20, 30])},
			RuntimeError,
			'Argument `indep_var` is not valid'
		)
		# Non monotonically increasing vector
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{
				'indep_var':numpy.array([1.0, 2.0, 0.0, 3.0]),
				'dep_var':numpy.array([10, 20, 30])
			},
			RuntimeError,
			'Argument `indep_var` is not valid'
		)
		# Empty vector
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{'indep_var':numpy.array([]), 'dep_var':numpy.array([10, 20, 30])},
			RuntimeError,
			'Argument `indep_var` is not valid'
		)
		# Valid values, these should not raise any exception
		assert (putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([10, 20, 30])
		).indep_var == numpy.array([1, 2, 3])).all()
		assert (putil.plot.BasicSource(
			indep_var=numpy.array([4.0, 5.0, 6.0]),
			dep_var=numpy.array([10, 20, 30])
		).indep_var == numpy.array([4.0, 5.0, 6.0])).all()
		# Invalid range bounding
		# Assign indep_min via attribute
		obj = putil.plot.BasicSource(
			numpy.array([1, 2, 3]),
			dep_var=numpy.array([10, 20, 30])
		)
		with pytest.raises(ValueError) as excinfo:
			obj.indep_min = 45
		assert (
			putil.test.get_exmsg(excinfo) ==
			('Argument `indep_var` is empty after '
			 '`indep_min`/`indep_max` range bounding')
		)
		# Assign indep_max via attribute
		obj = putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([10, 20, 30])
		)
		with pytest.raises(ValueError) as excinfo:
			obj.indep_max = 0
		assert (
			putil.test.get_exmsg(excinfo) ==
			('Argument `indep_var` is empty after '
			 '`indep_min`/`indep_max` range bounding')
		)
		# Assign both indep_min and indep_max via __init__ path
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{
				'indep_var':numpy.array([1, 2, 3]),
				'dep_var':numpy.array([10, 20, 30]),
				'indep_min':4, 'indep_max':10
			},
			ValueError,
			'Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding'
		)
		# Managed attribute path
		obj = putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([10, 20, 30])
		)
		# Wrong type
		assert (obj.indep_var == numpy.array([1, 2, 3])).all()
		with pytest.raises(RuntimeError) as excinfo:
			obj.indep_var = None
		assert putil.test.get_exmsg(excinfo) == 'Argument `indep_var` is not valid'
		with pytest.raises(RuntimeError) as excinfo:
			obj.indep_var = 'a'
		assert putil.test.get_exmsg(excinfo) == 'Argument `indep_var` is not valid'
		# Non monotonically increasing vector
		with pytest.raises(RuntimeError) as excinfo:
			obj.indep_var = numpy.array([1.0, 2.0, 0.0, 3.0])
		assert putil.test.get_exmsg(excinfo) == 'Argument `indep_var` is not valid'
		# Valid values, these should not raise any exception
		obj.indep_var = numpy.array([4.0, 5.0, 6.0])
		assert (obj.indep_var == numpy.array([4.0, 5.0, 6.0])).all()

	def test_dep_var_type(self):
		""" Tests dep_var type validation """
		# __init__ path
		# Wrong type
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{'indep_var':numpy.array([1, 2, 3]), 'dep_var':None},
			RuntimeError,
			'Argument `dep_var` is not valid'
		)
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{'indep_var':numpy.array([1, 2, 3]), 'dep_var':'a'},
			RuntimeError,
			'Argument `dep_var` is not valid'
		)
		# Empty vector
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{'indep_var':numpy.array([1, 2, 3]), 'dep_var':[]},
			RuntimeError,
			'Argument `dep_var` is not valid'
		)
		# Valid values, these should not raise any exception
		assert (putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([1, 2, 3])
		).dep_var == numpy.array([1, 2, 3])).all()
		assert (putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([4.0, 5.0, 6.0])
		).dep_var == numpy.array([4.0, 5.0, 6.0])).all()
		# Managed attribute path
		obj = putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([1, 2, 3])
		)
		# Wrong type
		with pytest.raises(RuntimeError) as excinfo:
			obj.dep_var = 'a'
		assert putil.test.get_exmsg(excinfo) == 'Argument `dep_var` is not valid'
		# Empty vector
		with pytest.raises(RuntimeError) as excinfo:
			obj.dep_var = numpy.array([])
		assert putil.test.get_exmsg(excinfo) == 'Argument `dep_var` is not valid'
		# Valid values, these should not raise any exception
		obj.dep_var = numpy.array([1, 2, 3])
		assert (obj.dep_var == numpy.array([1, 2, 3])).all()
		obj.dep_var = numpy.array([4.0, 5.0, 6.0])
		assert (obj.dep_var == numpy.array([4.0, 5.0, 6.0])).all()

	def test_indep_var_and_dep_var_do_not_have_the_same_number_of_elements(self):
		""" Tests dep_var type validation """
		# Both set at object creation
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{
				'indep_var':numpy.array([10, 20, 30]),
				'dep_var':numpy.array([1, 2, 3, 4, 5, 6]),
				'indep_min':30,
				'indep_max':50
			},
			ValueError,
			'Arguments `indep_var` and `dep_var` must have the same number of elements'
		)
		putil.test.assert_exception(
			putil.plot.BasicSource,
			{
				'indep_var':numpy.array([10, 20, 30]),
				'dep_var':numpy.array([1, 2]),
				'indep_min':30,
				'indep_max':50
			},
			ValueError,
			'Arguments `indep_var` and `dep_var` must have the same number of elements'
		)
		# indep_var set first
		obj = putil.plot.BasicSource(
			indep_var=numpy.array([10, 20, 30, 40, 50, 60]),
			dep_var=numpy.array([1, 2, 3, 4, 5, 6]),
			indep_min=30,
			indep_max=50)
		with pytest.raises(ValueError) as excinfo:
			obj.dep_var = numpy.array([100, 200, 300])
		assert (
			putil.test.get_exmsg(excinfo) ==
			('Arguments `indep_var` and `dep_var` '
			 'must have the same number of elements')
		)
		# dep_var set first
		obj = putil.plot.BasicSource(
			indep_var=numpy.array([10, 20, 30]),
			dep_var=numpy.array([100, 200, 300]),
			indep_min=30,
			indep_max=50
		)
		with pytest.raises(ValueError) as excinfo:
			obj.indep_var = numpy.array([10, 20, 30, 40, 50, 60])
		assert (
			putil.test.get_exmsg(excinfo) ==
			('Arguments `indep_var` and `dep_var` '
			 'must have the same number of elements')
		)
	def test_complete(self):
		""" Test that _complete property behaves correctly """
		obj = putil.plot.BasicSource(
			indep_var=numpy.array([10, 20, 30]),
			dep_var=numpy.array([100, 200, 300]),
			indep_min=0,
			indep_max=50
		)
		obj._indep_var = None
		assert not obj._complete
		obj = putil.plot.BasicSource(
			indep_var=numpy.array([10, 20, 30]),
			dep_var=numpy.array([100, 200, 300]),
			indep_min=0,
			indep_max=50
		)
		assert obj._complete

	def test_str(self):
		""" Test that str behaves correctly """
		# Full set
		obj = str(putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([10, 20, 30]),
			indep_min=-10,
			indep_max=20.0)
		)
		ref = ('Independent variable minimum: -10\n'
			   'Independent variable maximum: 20.0\n'
			   'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
			   'Dependent variable: [ 10.0, 20.0, 30.0 ]')
		assert obj == ref
		# indep_min not set
		obj = str(putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([10, 20, 30]),
			indep_max=20.0)
		)
		ref = ('Independent variable minimum: -inf\n'
			   'Independent variable maximum: 20.0\n'
			   'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
			   'Dependent variable: [ 10.0, 20.0, 30.0 ]')
		assert obj == ref
		# indep_max not set
		obj = str(putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([10, 20, 30]),
			indep_min=-10)
		)
		ref = ('Independent variable minimum: -10\n'
			   'Independent variable maximum: +inf\n'
			   'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
			   'Dependent variable: [ 10.0, 20.0, 30.0 ]')
		assert obj == ref
		# indep_min and indep_max not set
		obj = str(putil.plot.BasicSource(
			indep_var=numpy.array([1, 2, 3]),
			dep_var=numpy.array([10, 20, 30]))
		)
		ref = ('Independent variable minimum: -inf\n'
			   'Independent variable maximum: +inf\n'
			   'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
			   'Dependent variable: [ 10.0, 20.0, 30.0 ]')
		assert obj == ref

	def test_cannot_delete_attributes(self):
		""" Test that del method raises an exception on all class attributes """
		obj = putil.plot.BasicSource(
			indep_var=numpy.array([10, 20, 30]),
			dep_var=numpy.array([100, 200, 300])
		)
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_min
		assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_max
		assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.indep_var
		assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.dep_var
		assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
