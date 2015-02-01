# gen_ref_images.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

"""
Generate reference images to be used for putil.plot unit testing
"""

import math
import numpy
import itertools

import putil.plot
import putil.misc

def unittest_series_images(mode=None, test_dir=None):	#pylint: disable=R0914
	""" Images for Series() class """
	mode = 'ref' if mode is None else mode.lower()
	ref_dir = './support/ref_images/'
	test_dir = './test_images' if test_dir is None else test_dir
	marker_list = [False, True]
	interp_list = ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']
	line_style_list = ['-', '--', '-.', ':']
	line_style_desc = {'-':'solid', '--':'dashed', '-.':'dash-dot', ':':'dot'}
	master_list = [marker_list, interp_list, line_style_list]
	comb_list = itertools.product(*master_list)	#pylint: disable-msg=W0142
	output_list = list()
	for marker, interp, line_style in comb_list:
		ref_file_name = '{0}/series_marker_{1}_interp_{2}_line_style_{3}.png'.format(ref_dir, 'true' if marker else 'false', interp.lower(), line_style_desc[line_style])
		test_file_name = '{0}/series_marker_{1}_interp_{2}_line_style_{3}.png'.format(test_dir, 'true' if marker else 'false', interp.lower(), line_style_desc[line_style])
		output_list.append({'ref_file_name':ref_file_name, 'test_file_name':test_file_name})
		print 'Generating image {0}'.format(ref_file_name if mode == 'ref' else test_file_name)
		series1 = putil.plot.Series(
			data_source=putil.plot.BasicSource(indep_var=numpy.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), dep_var=numpy.array([0.9, 2.5, 3, 3.5, 5.9, 6.6, 7.1, 7.9, 9.9, 10.5])),
			label='test series',
			marker='o' if marker else None,
			interp=interp,
			line_style=line_style
		)
		panel_obj = putil.plot.Panel(
			series=series1,
			primary_axis_label='Dependent axis',
			primary_axis_units='-',
		)
		fig_obj = putil.plot.Figure(
			panels=panel_obj,
			indep_var_label='Independent axis',
			indep_var_units='',
			log_indep_axis=False,
			fig_width=8,
			fig_height=6,
			title='marker: {0}\ninterp: {1}\nline_style: {2}'.format(marker, interp, line_style)
		)
		if mode == 'ref':
			putil.misc.make_dir(ref_file_name)
		fig_obj.save(ref_file_name if mode == 'ref' else test_file_name)
	return output_list

def unittest_panel_images(mode=None, test_dir=None):	#pylint: disable=R0912,R0914,R0915
	""" Images for Panel() class """
	mode = 'ref' if mode is None else mode.lower()
	ref_dir = './support/ref_images/'
	test_dir = './test_images' if test_dir is None else test_dir
	axis_type_list = ['single', 'linear', 'log', 'filter']
	series_in_axis = ['primary', 'secondary', 'both']
	master_list = [axis_type_list, series_in_axis]
	comb_list = itertools.product(*master_list)	#pylint: disable-msg=W0142
	output_list = list()
	ds1_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300, 400]), dep_var=numpy.array([1, 2, 3, 4]))
	ds2_obj = putil.plot.BasicSource(indep_var=numpy.array([300, 400, 500, 600, 700]), dep_var=numpy.array([3, 4, 5, 6, 7]))
	ds3_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300]), dep_var=numpy.array([20, 40, 50]))
	ds4_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300]), dep_var=numpy.array([10, 25, 35]))
	ds5_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300, 400]), dep_var=numpy.array([10, 20, 30, 40]))
	ds6_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300, 400]), dep_var=numpy.array([20, 30, 40, 100]))
	ds7_obj = putil.plot.BasicSource(indep_var=numpy.array([200]), dep_var=numpy.array([50]))
	ds8_obj = putil.plot.BasicSource(indep_var=numpy.array([200]), dep_var=numpy.array([20]))
	indep_var = numpy.array([1e3, 2e3, 3e3, 4e3, 5e3, 6e3, 7e3, 8e3, 9e3, 1e4, 2e4, 3e4, 4e4, 5e4, 6e4, 7e4, 8e4, 9e4, 1e5, 2e5, 3e5, 4e5, 5e5, 6e5, 7e5, 8e5, 9e5, 1e6])
	dep_var = numpy.array([20*math.log10(math.sqrt(abs(1/(1+((1j*2*math.pi*freq)/(2*math.pi*1e4)))))) for freq in indep_var])
	ds9_obj = putil.plot.BasicSource(indep_var=indep_var, dep_var=dep_var)
	series1_obj = putil.plot.Series(data_source=ds1_obj, label='series 1', marker='o', interp='STRAIGHT', line_style='-', color='k')
	series2_obj = putil.plot.Series(data_source=ds2_obj, label='series 2', marker='o', interp='STRAIGHT', line_style='-', color='b')
	series3_obj = putil.plot.Series(data_source=ds3_obj, label='series 3', marker='o', interp='STRAIGHT', line_style='-', color='g', secondary_axis=True)
	series4_obj = putil.plot.Series(data_source=ds4_obj, label='series 4', marker='o', interp='STRAIGHT', line_style='-', color='r', secondary_axis=True)
	series5_obj = putil.plot.Series(data_source=ds5_obj, label='series 5', marker='o', interp='STRAIGHT', line_style='-', color='m', secondary_axis=True)
	series6_obj = putil.plot.Series(data_source=ds6_obj, label='series 6', marker='o', interp='STRAIGHT', line_style='-', color='c', secondary_axis=True)
	series7_obj = putil.plot.Series(data_source=ds7_obj, label='series 7', marker='o', interp='STRAIGHT', line_style='-', color='y')
	series8_obj = putil.plot.Series(data_source=ds8_obj, label='series 8', marker='o', interp='STRAIGHT', line_style='--', color='k', secondary_axis=True)
	series9_obj = putil.plot.Series(data_source=ds9_obj, label='series 9', marker=None, interp='CUBIC', line_style='-', color='k')
	for axis_type, in_axis in comb_list:
		ref_file_name = '{0}/panel_{1}_axis_series_in_{2}_axis.png'.format(ref_dir, axis_type, in_axis)
		test_file_name = '{0}/panel_{1}_axis_series_in_{2}_axis.png'.format(test_dir, axis_type, in_axis)
		if (axis_type != 'filter') or ((axis_type == 'filter') and (in_axis == 'primary')):
			output_list.append({'ref_file_name':ref_file_name, 'test_file_name':test_file_name})
			print 'Generating image {0}'.format(ref_file_name if mode == 'ref' else test_file_name)
		if axis_type == 'linear':
			if in_axis == 'both':
				series_obj = [series1_obj, series2_obj, series3_obj, series4_obj]
			elif in_axis == 'primary':
				series_obj = [series1_obj, series2_obj]
			elif in_axis == 'secondary':
				series_obj = [series3_obj, series4_obj]
		elif axis_type == 'log':
			if in_axis == 'both':
				series_obj = [series1_obj, series5_obj]
			elif in_axis == 'primary':
				series_obj = [series1_obj]
			elif in_axis == 'secondary':
				series_obj = [series6_obj]
		if axis_type == 'single':
			if in_axis == 'both':
				series_obj = [series7_obj, series8_obj]
			elif in_axis == 'primary':
				series_obj = [series7_obj]
			elif in_axis == 'secondary':
				series_obj = [series8_obj]
		if axis_type == 'filter':
			if in_axis == 'both':
				pass
			elif in_axis == 'primary':
				series_obj = [series9_obj]
			elif in_axis == 'secondary':
				pass
		if (axis_type != 'filter') or ((axis_type == 'filter') and (in_axis == 'primary')):
			panel_obj = putil.plot.Panel(
				series=series_obj,
				primary_axis_label='Primary axis' if in_axis in ['primary', 'both'] else None,
				primary_axis_units='-' if in_axis in ['primary', 'both'] else None,
				secondary_axis_label='Secondary axis' if in_axis in ['secondary', 'both'] else None,
				secondary_axis_units='-' if in_axis in ['secondary', 'both'] else None,
				log_dep_axis=True if axis_type == 'log' else False
			)
			fig_obj = putil.plot.Figure(
				panels=panel_obj,
				indep_var_label='Independent axis',
				indep_var_units='',
				log_indep_axis=(axis_type == 'filter'),
				fig_width=8,
				fig_height=6,
				title='Axis: {0}\nSeries in axis: {1}'.format(axis_type, in_axis),
			)
			if mode == 'ref':
				putil.misc.make_dir(ref_file_name)
			fig_obj.save(ref_file_name if mode == 'ref' else test_file_name)
	return output_list

def unittest_figure_images(mode=None, test_dir=None):	#pylint: disable=R0912,R0914,R0915
	""" Images for Figure() class """
	mode = 'ref' if mode is None else mode.lower()
	ref_dir = './support/ref_images/'
	test_dir = './test_images' if test_dir is None else test_dir
	output_list = list()
	ds1_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300, 400]), dep_var=numpy.array([1, 2, 3, 4]))
	ds2_obj = putil.plot.BasicSource(indep_var=numpy.array([300, 400, 500, 600, 700]), dep_var=numpy.array([3, 4, 5, 6, 7]))
	ds4_obj = putil.plot.BasicSource(indep_var=numpy.array([50, 100, 500, 1000, 1100]), dep_var=numpy.array([1.2e3, 100, 1, 300, 20]))
	indep_var = numpy.array([1e3, 2e3, 3e3, 4e3, 5e3, 6e3, 7e3, 8e3, 9e3, 1e4, 2e4, 3e4, 4e4, 5e4, 6e4, 7e4, 8e4, 9e4, 1e5, 2e5, 3e5, 4e5, 5e5, 6e5, 7e5, 8e5, 9e5, 1e6])
	dep_var = numpy.array([20*math.log10(math.sqrt(abs(1/(1+((1j*2*math.pi*freq)/(2*math.pi*1e4)))))) for freq in indep_var])
	ds3_obj = putil.plot.BasicSource(indep_var=indep_var, dep_var=dep_var)
	series1_obj = putil.plot.Series(data_source=ds1_obj, label='series 1', marker='o', interp='STRAIGHT', line_style='-', color='k')
	series2_obj = putil.plot.Series(data_source=ds2_obj, label='series 2', marker='o', interp='STRAIGHT', line_style='-', color='b', secondary_axis=True)
	series3_obj = putil.plot.Series(data_source=ds3_obj, label='series 3', marker=None, interp='CUBIC', line_style='-', color='k')
	series4_obj = putil.plot.Series(data_source=ds4_obj, label='series 3', marker='+', interp='CUBIC', line_style='-', color='r')
	panel1_obj = putil.plot.Panel(
		series=series1_obj,
		primary_axis_label='Primary axis #1',
		primary_axis_units='-',
		secondary_axis_label='Secondary axis #1',
		secondary_axis_units='-',
		log_dep_axis=False
	)
	panel2_obj = putil.plot.Panel(
		series=series2_obj,
		primary_axis_label='Primary axis #2',
		primary_axis_units='-',
		secondary_axis_label='Secondary axis #2',
		secondary_axis_units='-',
		log_dep_axis=False
	)
	panel3_obj = putil.plot.Panel(
		series=series3_obj,
		primary_axis_label='Primary axis #3',
		primary_axis_units='-',
		secondary_axis_label='Secondary axis #3',
		secondary_axis_units='-',
		log_dep_axis=False
	)
	#for axis_type in ['linear', 'logarithmic']:
	#	ref_file_name = '{0}/figure_{1}_axis.png'.format(ref_dir, axis_type)
	#	test_file_name = '{0}/figure_{1}_axis.png'.format(test_dir, axis_type)
	#	print 'Generating image {0}'.format(ref_file_name if mode == 'ref' else test_file_name)
	#	fig_obj = putil.plot.Figure(
	#		panels=[panel1_obj, panel2_obj] if axis_type == 'linear' else [panel1_obj, panel3_obj],
	#		indep_var_label='Independent axis',
	#		indep_var_units='',
	#		log_indep_axis=False if axis_type == 'linear' else True,
	#		fig_width=8,
	#		fig_height=6,
	#		title='{0} axis'.format(axis_type),
	#	)
	#	if mode == 'ref':
	#		putil.misc.make_dir(ref_file_name)
	#	fig_obj.save(ref_file_name if mode == 'ref' else test_file_name)
	#
	panel4_obj = putil.plot.Panel(
		series=series4_obj,
		primary_axis_label='Primary axis #3',
		primary_axis_units='-',
		secondary_axis_label='Secondary axis #3',
		secondary_axis_units='-',
		log_dep_axis=False
	)
	for num in range(0, 8):
		panel1_obj.show_indep_axis = num in [4, 5, 6, 7]
		panel2_obj.show_indep_axis = num in [2, 3, 6, 7]
		panel4_obj.show_indep_axis = num in [1, 3, 5, 7]
		panel1_flabel = 'yes' if panel1_obj.show_indep_axis else 'no'
		panel2_flabel = 'yes' if panel2_obj.show_indep_axis else 'no'
		panel4_flabel = 'yes' if panel4_obj.show_indep_axis else 'no'
		ref_file_name = '{0}/figure_multiple_indep_axis_panel1_{1}_panel2_{2}_panel_{3}.png'.format(ref_dir, panel1_flabel, panel2_flabel, panel4_flabel)
		test_file_name = '{0}/figure_multiple_indep_axis_panel1_{1}_panel2_{2}_panel_{3}.png'.format(test_dir, panel1_flabel, panel2_flabel, panel4_flabel)
		fig_obj = putil.plot.Figure(
			panels=[panel1_obj, panel2_obj, panel4_obj],
			indep_var_label='Independent axis',
			indep_var_units='',
			log_indep_axis=False,
			fig_width=8,
			fig_height=15,
			title='Multiple independent axis\nPanel 1 {0}, panel 2 {1}, panel 3 {2}'.format(panel1_flabel, panel2_flabel, panel4_flabel),
		)
		if mode == 'ref':
			putil.misc.make_dir(ref_file_name)
		print 'Generating image {0}'.format(ref_file_name if mode == 'ref' else test_file_name)
		fig_obj.save(ref_file_name if mode == 'ref' else test_file_name)

	return output_list

if __name__ == '__main__':
	unittest_series_images(mode='ref')
	unittest_panel_images(mode='ref')
	unittest_figure_images(mode='ref')
