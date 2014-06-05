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

def unittest_image(mode=None, test_dir=None):	#pylint: disable=R0914
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

if __name__ == '__main__':
	unittest_image(mode='ref')
