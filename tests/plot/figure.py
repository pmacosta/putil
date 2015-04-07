# figure.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import matplotlib, mock, numpy, os, pytest, sys

import putil.plot
from .fixtures import compare_images, IMGTOL
sys.path.append('..')
from gen_ref_images import unittest_figure_images	#pylint: disable=F0401


###
# Tests for Figure
###
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
		assert (obj.fig_width-5.6 < 1e-10) or (obj.fig_width-5.61 < 1e-10)	# CI images are 6.09
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
		# Continuous integration image is 5.61in wide
		putil.test.assert_exception(putil.plot.Figure, {'panels':default_panel, 'indep_var_label':'Input', 'indep_var_units':'Amps', 'title':'My graph', 'fig_width':0.1, 'fig_height':200},\
							  RuntimeError, 'Figure size is too small: minimum width = 5.6[1]*, minimum height 2.66')
		putil.test.assert_exception(putil.plot.Figure, {'panels':default_panel, 'indep_var_label':'Input', 'indep_var_units':'Amps', 'title':'My graph', 'fig_width':200, 'fig_height':0.1},\
							  RuntimeError, 'Figure size is too small: minimum width = 5.6[1]*, minimum height 2.66')
		putil.test.assert_exception(putil.plot.Figure, {'panels':default_panel, 'indep_var_label':'Input', 'indep_var_units':'Amps', 'title':'My graph', 'fig_width':0.1, 'fig_height':0.1},\
							  RuntimeError, 'Figure size is too small: minimum width = 5.6[1]*, minimum height 2.66')

	def test_complete(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test that _complete property behaves correctly """
		obj = putil.plot.Figure(panels=None)
		assert obj._complete == False	#pylint: disable=W0212
		obj.panels = default_panel
		assert obj._complete == True	#pylint: disable=W0212
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
		ret += '   Display independent axis: False\n'
		ret += '   Legend properties:\n'
		ret += '      cols: 1\n'
		ret += '      pos: BEST\n'
		ret += 'Independent variable label: Input\n'
		ret += 'Independent variable units: Amps\n'
		ret += 'Logarithmic independent axis: False\n'
		ret += 'Title: My graph\n'
		ret_ci = ret + 'Figure width: 5.61\n'
		ret += 'Figure width: 5.6\n'
		ret_ci += 'Figure height: 2.66\n'
		ret += 'Figure height: 2.66\n'
		assert (str(obj) == ret) or (str(obj) == ret_ci)

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
		with mock.patch('putil.plot.figure.plt.show', side_effect=mock_show):
			obj.show()
		out, _ = capsys.readouterr()
		assert out == 'show called\n'

	def test_iterator(self, default_panel):	#pylint: disable=C0103,R0201,W0621
		""" Test that __iter__() method behaves correctly """
		ds1_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300, 400]), dep_var=numpy.array([1, 2, 3, 4]))
		series1_obj = putil.plot.Series(data_source=ds1_obj, label='series 1', interp=None)
		panel2 = putil.plot.Panel(series=series1_obj)
		obj = putil.plot.Figure(panels=[default_panel, panel2])
		for num, panel in enumerate(obj):
			if num == 0:
				assert panel == default_panel
			if num == 1:
				assert panel == panel2

	def test_images(self, tmpdir):	#pylint: disable=C0103,R0201,W0621
		""" Compare images to verify correct plotting of figure """
		tmpdir.mkdir('test_images')
		images_dict_list = unittest_figure_images(mode='test', test_dir=str(tmpdir))
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
