# gen_ref_images.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Generate reference images to be used for putil.plot unit testing
"""

import numpy
import itertools

import putil.plot
import putil.misc

def unittest_series_images(mode=None, test_dir=None):	#pylint: disable=R0914
	""" Main loop """
	mode = 'ref' if mode is None else mode.lower()
	ref_dir = './ref_images/'
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
			marker=marker,
			interp=interp,
			line_style=line_style
		)
		panel_obj = putil.plot.Panel(
			series=series1,
			primary_axis_label='Dependent axis',
			primary_axis_units='-',
		)
		fig_obj = putil.plot.Figure(
			panel=panel_obj,
			indep_var_label='Independent axis',
			indep_var_units='',
			log_indep=False,
			fig_width=8,
			fig_height=6,
			title='marker: {0}\ninterp: {1}\nline_style: {2}'.format(marker, interp, line_style)
		)
		if mode == 'ref':
			putil.misc.make_dir(ref_file_name)
		fig_obj.save(ref_file_name if mode == 'ref' else test_file_name)
	return output_list

def unittest_panel_images(mode=None, test_dir=None):	#pylint: disable=R0914
	""" Main loop """
	mode = 'ref' if mode is None else mode.lower()
	ref_dir = './ref_images/'
	test_dir = './test_images' if test_dir is None else test_dir
	axis_type_list = ['linear', 'log']
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
	ds7_obj = putil.plot.BasicSource(indep_var=numpy.array([100, 200, 300, 400]), dep_var=numpy.array([20, 30, 40, 50]))
	ds8_obj = putil.plot.BasicSource(indep_var=numpy.array([100]), dep_var=numpy.array([20]))
	series1_obj = putil.plot.Series(data_source=ds1_obj, label='series 1', marker=True, interp='STRAIGHT', line_style='-', color='k')
	series2_obj = putil.plot.Series(data_source=ds2_obj, label='series 2', marker=True, interp='STRAIGHT', line_style='-', color='b')
	series3_obj = putil.plot.Series(data_source=ds3_obj, label='series 3', marker=True, interp='STRAIGHT', line_style='-', color='g', secondary_axis=True)
	series4_obj = putil.plot.Series(data_source=ds4_obj, label='series 4', marker=True, interp='STRAIGHT', line_style='-', color='r', secondary_axis=True)
	series5_obj = putil.plot.Series(data_source=ds5_obj, label='series 5', marker=True, interp='STRAIGHT', line_style='-', color='m', secondary_axis=True)
	series6_obj = putil.plot.Series(data_source=ds6_obj, label='series 6', marker=True, interp='STRAIGHT', line_style='-', color='c', secondary_axis=True)
	series7_obj = putil.plot.Series(data_source=ds7_obj, label='series 7', marker=True, interp='STRAIGHT', line_style='-', color='y')
	series8_obj = putil.plot.Series(data_source=ds8_obj, label='series 8', marker=True, interp='STRAIGHT', line_style='--', color='k')
	for axis_type, in_axis in comb_list:
		ref_file_name = '{0}/panel_{1}_axis_series_in_{2}_axis.png'.format(ref_dir, axis_type, in_axis)
		test_file_name = '{0}/panel_{1}_axis_series_in_{2}_axis.png'.format(test_dir, axis_type, in_axis)
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
		panel_obj = putil.plot.Panel(
			series=series_obj,
			primary_axis_label='Primary axis' if in_axis in ['primary', 'both'] else None,
			primary_axis_units='-' if in_axis in ['primary', 'both'] else None,
			secondary_axis_label='Secondary axis' if in_axis in ['secondary', 'both'] else None,
			secondary_axis_units='-' if in_axis in ['secondary', 'both'] else None,
			log_dep_axis=True if axis_type == 'log' else False
	)
		fig_obj = putil.plot.Figure(
			panel=panel_obj,
			indep_var_label='Independent axis',
			indep_var_units='',
			log_indep=False,
			fig_width=8,
			fig_height=6,
			title='Axis: {0}\nSeries in axis: {1}'.format(axis_type, in_axis)
		)
		if mode == 'ref':
			putil.misc.make_dir(ref_file_name)
		fig_obj.save(ref_file_name if mode == 'ref' else test_file_name)
	return output_list

if __name__ == '__main__':
	#unittest_series_images(mode='ref')
	unittest_panel_images(mode='ref')
