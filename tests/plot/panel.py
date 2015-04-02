# panel.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import numpy, os, pytest, sys

import putil.plot
from .fixtures import compare_images, IMGTOL
sys.path.append('..')
from gen_ref_images import unittest_panel_images	#pylint: disable=F0401


###
# Tests for Panel
###

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

	def test_display_indep_axis_wrong_type(self, default_series):	#pylint: disable=C0103,R0201,W0621
		""" Test display_indep_axis data validation """
		putil.test.assert_exception(putil.plot.Panel, {'series':default_series, 'display_indep_axis':5}, RuntimeError, 'Argument `display_indep_axis` is not valid')
		# These assignments should not raise an exception
		obj = putil.plot.Panel(series=default_series, display_indep_axis=False)
		assert obj.display_indep_axis == False
		obj = putil.plot.Panel(series=default_series, display_indep_axis=True)
		assert obj.display_indep_axis == True
		obj = putil.plot.Panel(series=default_series)
		assert obj.display_indep_axis == False

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
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([31.5, 35, 38.5], ['31.5', '35.0', '38.5'], 31.5, 38.5, 1e-6, 'u')
		# print obj
		# 1
		# Scaling with more data samples after 1.0
		vector = numpy.array([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6], ['0.8', '0.9', '1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6'], 0.8, 1.6, 1, ' ')
		# print obj
		# 2
		# Regular, should not have any scaling
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([1, 2, 3, 4, 5, 6, 7], ['1', '2', '3', '4', '5', '6', '7'], 1, 7, 1, ' ')
		# print obj
		# 3
		# Regular, should not have any scaling
		vector = numpy.array([10, 20, 30, 40, 50, 60, 70])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([10, 20, 30, 40, 50, 60, 70], ['10', '20', '30', '40', '50', '60', '70'], 10, 70, 1, ' ')
		# print obj
		# 4
		# Scaling
		vector = numpy.array([1000, 2000, 3000, 4000, 5000, 6000, 7000])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([1, 2, 3, 4, 5, 6, 7], ['1', '2', '3', '4', '5', '6', '7'], 1, 7, 1e3, 'k')
		# print obj
		# 5
		# Scaling
		vector = numpy.array([200e6, 300e6, 400e6, 500e6, 600e6, 700e6, 800e6, 900e6, 1000e6])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([200, 300, 400, 500, 600, 700, 800, 900, 1000], ['200', '300', '400', '500', '600', '700', '800', '900', '1k'], 200, 1000, 1e6, 'M')
		# print obj
		# 6
		# No tick marks to place all data points on grid, space uniformly
		vector = numpy.array([105, 107.7, 215, 400.2, 600, 700, 800, 810, 820, 830, 840, 850, 900, 905])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([105.0, 193.8888888889, 282.7777777778, 371.6666666667, 460.5555555556, 549.4444444444, 638.3333333333, 727.2222222222, 816.1111111111, 905.0],
						   ['105', '194', '283', '372', '461', '549', '638', '727', '816', '905'], 105, 905, 1, ' ')
		# print obj
		# 7
		# Ticks marks where some data points can be on grid
		vector = numpy.array([10, 20, 30, 40, 41, 50, 60, 62, 70, 75.5, 80])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([10, 20, 30, 40, 50, 60, 70, 80], ['10', '20', '30', '40', '50', '60', '70', '80'], 10, 80, 1, ' ')
		# print obj
		# 8
		# Tight = False
		# One sample
		vector = numpy.array([1e-9])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=False)	#pylint: disable=W0212
		assert obj == ([0.9, 1, 1.1], ['0.9', '1.0', '1.1'], 0.9, 1.1, 1e-9, 'n')
		# print obj
		# 9
		# Scaling with more data samples after 1.0
		vector = numpy.array([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=False)	#pylint: disable=W0212
		assert obj == ([0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7], ['0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7'], 0.7, 1.7, 1, ' ')
		# print obj
		# 10
		# Scaling with more data samples before 1.0
		vector = numpy.array([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=False)	#pylint: disable=W0212
		assert obj == ([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2], ['0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2'], 0.2, 1.2, 1, ' ')
		# print obj
		# 11
		# Regular, with some overshoot
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), 7.5, tight=False)	#pylint: disable=W0212
		assert obj == ([0, 1, 2, 3, 4, 5, 6, 7, 8], ['0', '1', '2', '3', '4', '5', '6', '7', '8'], 0, 8, 1, ' ')
		# print obj
		# 12
		# Regular, with some undershoot
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot.functions._intelligent_ticks(vector, 0.1, max(vector), tight=False)	#pylint: disable=W0212
		assert obj == ([0, 1, 2, 3, 4, 5, 6, 7, 8], ['0', '1', '2', '3', '4', '5', '6', '7', '8'], 0, 8, 1, ' ')
		# print obj
		# 13
		# Regular, with large overshoot
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), 20, tight=False)	#pylint: disable=W0212
		assert obj == ([0, 1, 2, 3, 4, 5, 6, 7, 8], ['0', '1', '2', '3', '4', '5', '6', '7', '8'], 0, 8, 1, ' ')
		# print obj
		# 14
		# Regular, with large undershoot
		vector = numpy.array([1, 2, 3, 4, 5, 6, 7])
		obj = putil.plot.functions._intelligent_ticks(vector, -10, max(vector), tight=False)	#pylint: disable=W0212
		assert obj == ([0, 1, 2, 3, 4, 5, 6, 7, 8], ['0', '1', '2', '3', '4', '5', '6', '7', '8'], 0, 8, 1, ' ')
		# print obj
		# 15
		# Scaling, minimum as reference
		vector = 1e9+(numpy.array([10, 20, 30, 40, 50, 60, 70, 80])*1e3)
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([1.00001, 1.00002, 1.00003, 1.00004, 1.00005, 1.00006, 1.00007, 1.00008], ['1.00001', '1.00002', '1.00003', '1.00004', '1.00005', '1.00006', '1.00007', '1.00008'], 1.00001, 1.00008, 1e9, 'G')
		# print obj
		# 16
		# Scaling, delta as reference
		vector = numpy.array([10.1e6, 20e6, 30e6, 40e6, 50e6, 60e6, 70e6, 80e6, 90e6, 100e6, 20.22e9])
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([10.1, 2255.6444444444, 4501.1888888889, 6746.7333333333, 8992.2777777778, 11237.8222222222, 13483.3666666667, 15728.9111111111, 17974.4555555556, 20220.0], \
						   ['10.1', '2.3k', '4.5k', '6.7k', '9.0k', '11.2k', '13.5k', '15.7k', '18.0k', '20.2k'], 10.1, 20220.0, 1e6, 'M')
		# print obj
		# 17
		# Scaling, maximum as reference
		vector = (numpy.array([0.7, 0.8, 0.9, 1.1, 1.2, 1.3, 1.4, 1.5])*1e12)
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=True)	#pylint: disable=W0212
		assert obj == ([0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5], ['0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3', '1.4', '1.5'], 0.7, 1.5, 1e12, 'T')
		# print obj
		# 18
		# Log axis
		# Tight False
		vector = (numpy.array([2e3, 3e4, 4e5, 5e6, 6e7]))
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), max(vector), tight=True, log_axis=True)	#pylint: disable=W0212
		assert obj == ([1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1k', '10k', '100k'], 1, 100000, 1000, 'k')
		# 19
		# Tight True
		# Left side
		vector = (numpy.array([2e3, 3e4, 4e5, 5e6, 6e7]))
		obj = putil.plot.functions._intelligent_ticks(vector, 500, max(vector), tight=False, log_axis=True)	#pylint: disable=W0212
		assert obj == ([1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1k', '10k', '100k'], 1, 100000, 1000, 'k')
		# print obj
		# 20
		# Right side
		vector = (numpy.array([2e3, 3e4, 4e5, 5e6, 6e7]))
		obj = putil.plot.functions._intelligent_ticks(vector, min(vector), 1e9, tight=False, log_axis=True)	#pylint: disable=W0212
		assert obj == ([1, 10, 100, 1000, 10000, 100000], ['1', '10', '100', '1k', '10k', '100k'], 1, 100000, 1000, 'k')
		# print obj
		# 21
		# Both
		# Right side
		vector = (numpy.array([2e3, 3e4, 4e5, 5e6, 6e7]))
		obj = putil.plot.functions._intelligent_ticks(vector, 500, 1e9, tight=False, log_axis=True)	#pylint: disable=W0212
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
		ret += 'Display independent axis: False\n'
		ret += 'Legend properties:\n'
		ret += '   cols: 1\n'
		ret += '   pos: BEST'
		assert str(obj) == ret
		obj = putil.plot.Panel(series=default_series, primary_axis_label='Output', primary_axis_units='Volts', secondary_axis_label='Input', secondary_axis_units='Watts', display_indep_axis=True)
		ret = 'Series 0:\n'
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
		ret += 'Display independent axis: True\n'
		ret += 'Legend properties:\n'
		ret += '   cols: 1\n'
		ret += '   pos: BEST'
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
		images_dict_list = unittest_panel_images(mode='test', test_dir=str(tmpdir))
		for images_dict in images_dict_list:
			ref_file_name = images_dict['ref_file_name']
			ref_ci_file_name = images_dict['ref_ci_file_name']
			test_file_name = images_dict['test_file_name']
			metrics = compare_images(ref_file_name, test_file_name)
			result = (metrics[0] < IMGTOL) and (metrics[1] < IMGTOL)
			metrics_ci = compare_images(ref_ci_file_name, test_file_name)
			result_ci = (metrics_ci[0] < IMGTOL) and (metrics_ci[1] < IMGTOL)
			if (not result) and (not result_ci):
				print 'Images do not match'
				print 'Reference image: file://{0}'.format(os.path.realpath(ref_file_name))
				print 'Reference CI image: file://{0}'.format(os.path.realpath(ref_ci_file_name))
				print 'Actual image: file://{0}'.format(os.path.realpath(test_file_name))
			# print 'Comparison: {0} with {1} -> {2} {3}'.format(ref_file_name, test_file_name, result, metrics)
			assert result
