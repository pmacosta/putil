"""
util_plot library usage example
"""

def main():
	"""
	Example of how to use the util_plot library to generate presentation-quality plots
	"""
	import numpy
	import putil.plot
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
		marker=True,
		interp='CUBIC',
		line_style='-',
		secondary_axis=False
	)]
	series2_obj = [putil.plot.Series(
		data_source=putil.plot.BasicSource(
			indep_var=numpy.array([0e-3, 1e-3, 2e-3]),
			dep_var=numpy.array([4, 7, 8]),
		),
		label='Source 2',
		color='r',
		marker=True,
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
		marker=True,
		interp='STRAIGHT',
		line_style='--',
		secondary_axis=True
	)]
	panel_obj = putil.plot.Panel(
		series=series1_obj+series2_obj+series3_obj,
		primary_axis_label='Primary axis label',
		primary_axis_units='-',
		secondary_axis_label='Secondary axis label',
		secondary_axis_units='W',
		legend_props={'pos':'lower right', 'cols':1}
	)
	fig_obj = putil.plot.Figure(
		panel=panel_obj,
		indep_var_label='Indep. var.',
		indep_var_units='S',
		log_indep=False,
		fig_width=None,
		fig_height=None,
		title='Library putil.plot Example'
	)
	fig_obj.draw()
	fig_obj.save('./example_plot.png')

def series1_proc_func(indep_var, dep_var, xoffset):	#pylint: disable=W0613
	"""
	Process data 1 series
	"""
	return (indep_var*1e-3)-xoffset, dep_var

if __name__ == '__main__':
	main()
