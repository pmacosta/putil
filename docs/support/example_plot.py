# example_plot.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111


def main():
	"""
	Example of how to use the putil.plot library
	to generate presentation-quality plots
	"""
	import numpy
	import putil.plot
	###
	# Series definition (Series class)
	###
	# Extract data from a comma-separated (csv) file using the CsvSource class
	series1_obj = [putil.plot.Series(
		data_source=putil.plot.CsvSource(
			file_name='data.csv',
			dfilter={'value1':1},
			indep_col_label='value2',
			dep_col_label='value3',
			indep_min=None,
			indep_max=None,
			fproc=series1_proc_func,
			fproc_eargs={'xoffset':1e-3}
		),
		label='Source 1',
		color='k',
		marker='o',
		interp='CUBIC',
		line_style='-',
		secondary_axis=False
	)]
	# Literal data can be used with the BasicSource class
	series2_obj = [putil.plot.Series(
		data_source=putil.plot.BasicSource(
			indep_var=numpy.array([0e-3, 1e-3, 2e-3]),
			dep_var=numpy.array([4, 7, 8]),
		),
		label='Source 2',
		color='r',
		marker='s',
		interp='STRAIGHT',
		line_style='--',
		secondary_axis=False
	)]
	series3_obj = [putil.plot.Series(
		data_source=putil.plot.BasicSource(
			indep_var=numpy.array([0.5e-3, 1e-3, 1.5e-3]),
			dep_var=numpy.array([10, 9, 6]),
		),
		label='Source 3',
		color='b',
		marker='h',
		interp='STRAIGHT',
		line_style='--',
		secondary_axis=True
	)]
	series4_obj = [putil.plot.Series(
		data_source=putil.plot.BasicSource(
			indep_var=numpy.array([0.3e-3, 1.8e-3, 2.5e-3]),
			dep_var=numpy.array([8, 8, 8]),
		),
		label='Source 4',
		color='g',
		marker='D',
		interp='STRAIGHT',
		line_style=None,
		secondary_axis=True
	)]
	###
	# Panels definition (Panel class)
	###
	panel_obj = putil.plot.Panel(
		series=series1_obj+series2_obj+series3_obj+series4_obj,
		primary_axis_label='Primary axis label',
		primary_axis_units='-',
		secondary_axis_label='Secondary axis label',
		secondary_axis_units='W',
		legend_props={'pos':'lower right', 'cols':1}
	)
	###
	# Figure definition (Figure class)
	###
	fig_obj = putil.plot.Figure(
		panels=panel_obj,
		indep_var_label='Indep. var.',
		indep_var_units='S',
		log_indep_axis=False,
		fig_width=4*2.25,
		fig_height=3*2.25,
		title='Library putil.plot Example'
	)
	# Save figure
	fig_obj.save('./example_plot.png')

def series1_proc_func(indep_var, dep_var, xoffset):	#pylint: disable=W0613
	"""
	Process data 1 series
	"""
	return (indep_var*1e-3)-xoffset, dep_var

if __name__ == '__main__':
	main()
