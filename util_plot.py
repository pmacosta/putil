"""
Utility classes, methods and functions to handle plotting
"""

import math
import numpy
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d  #pylint: disable-msg=E0611

import util_eng
import util_misc

def scale_series(series, scale=False, series_min=None, series_max=None, scale_type='delta'):	#pylint: disable-msg=R0913
	"""
	Scales series, 'delta' with the series span, 'min' with the series minimum
	"""
	series_min = min(series) if series_min is None else series_min
	series_max = max(series) if series_max is None else series_max
	series_delta = series_max-series_min
	if scale is False:
		(unit, div) = (' ', 1)
	else:
		(unit, div) = util_eng.peng_power(util_eng.peng(series_delta if scale_type == 'delta' else (series_min if scale_type == 'min' else series_max), 3))
		(first_unit, first_div) = util_eng.peng_power(util_eng.peng(series_min/div, 3))	#pylint: disable-msg=W0612
		if abs(1.00-(div*first_div)) < 1e-10:
			(unit, div) = util_eng.peng_power(util_eng.peng(series_min, 3))
		series = series/div
		series_min = series_min/div
		series_max = series_max/div

	return (series_min, series_max, div, unit.replace('u', '$\\mu$').strip(), series)

def process_ticks(locs, min_lim, max_lim, mant):
	"""
	Returns pretty-printed tick locations that are within the given bound
	"""
	bounded_locs = [loc for loc in locs if ((loc >= min_lim) or (abs(loc-min_lim) <= 1e-14)) and ((loc <= max_lim) or (abs(loc-max_lim) <= 1e-14))]
	raw_labels = [util_eng.peng(float(loc), mant, rjust=False) if ((abs(loc) >= 1) or (loc == 0)) else str(round(loc, mant)) for loc in bounded_locs]
	return (bounded_locs, [label.replace('u', '$\\mu$') for label in raw_labels])

def intelligent_ticks(series, series_min, series_max, tight=True, calc_ticks=True):	#pylint: disable-msg=R0912,R0914,R0915
	"""
	Calculates ticks 'intelligently', trying to calculate sane tick spacing
	"""
	div = 10.0
	num_ticks = 0
	series_delta = series_max-series_min
	min_num_ticks = 2 if series_delta == 0 else 8
	if calc_ticks is False:
		# Calculate spacing between points
		tspace = numpy.diff(series)	#pylint: disable-msg=E1101
		# Find minimum common spacing
		factors = [util_eng.peng_power(util_eng.peng(element, 3)) for element in tspace]
		divs = [div for (unit, div) in factors]	#pylint: disable-msg=W0612
		tspace_div = min(divs)
		scaled_tspace = numpy.round(numpy.array(tspace)/tspace_div, 10)	#pylint: disable-msg=E1101
		tspace_gcd = 0.5*util_misc.gcd(scaled_tspace)
		num_ticks = 20
		while num_ticks > 19:
			tspace_gcd = 2*tspace_gcd
			# Find out number of ticks with the minimum common spacing
			num_ticks = round(1+((series_max-series_min)/(tspace_div*float(tspace_gcd))), 10)
			if (round(float(int(round(num_ticks, 10))), 10) == round(num_ticks, 10)) and (int(round(num_ticks, 10)) >= min_num_ticks):
				num_ticks = int(round(num_ticks, 10))
				tstop = series[-1]
				tspace = tspace_gcd*tspace_div
				tick_list = numpy.linspace(series_min, series_max, num_ticks)	#pylint: disable-msg=E1101
				calc_ticks = False
	if calc_ticks is True:
		# round() allows for deltas closer to the next engineering unit to get the bigger scale while deltas closer to the smaller engineering scale get smaller scale
		scale = 1.0 if series_delta == 0 else 10**(round(math.log10(util_eng.peng_int(util_eng.peng(series_delta, 3)))))
		tight = False if series_delta == 0 else tight
		while num_ticks < min_num_ticks:
			tspace = scale/div
			tstart = float(int(series_min/tspace)*tspace) if abs(int(series_min/tspace)) > 0 else -tspace
			if tight is True:
				tstart = tstart+tspace if tstart <= series_min else tstart				# Quantization of first tick could place it lower than the minimum, adjust for this case
				tstart = tstart+tspace if tstart-series_min < (tspace/3) else tstart		# Avoid placing a tick mark less that 1/3 of the tick space
			else:
				tstart = tstart-tspace if tstart >= series_min else tstart				# Start at the grid tick immediately below the lowest data value
				tstart = tstart-tspace if series_min-tstart <= (tspace/10) else tstart	# Add a tick mark if signal is really close to bottom tick
			tstop = float(int(series_max/tspace)*tspace)
			if tight is True:
				tstop = tstop-tspace if tstop >= series_max else tstop					# Quantization of last tick could place it higher than the maximum, adjust for this case
				tstop = tstop-tspace if series_max-tstop < (tspace/3) else tstop			# Avoid placing a tick mark less that 1/4 of the tick space
			else:
				tstop = tstop+tspace if tstop <= series_max else tstop					# Stop at the grid tick immediately above the highest data value
				tstop = tstop+tspace if tstop-series_max <= (tspace/10) else tstop		# Add a tick mark if signal is really close to top tick
			num_ticks = int(round((tstop-tstart)/tspace))+1
			div = 2.0*div if num_ticks < min_num_ticks else div
		tick_list = ([series_min] if tight is True else [])+[tstart+(n*tspace) for n in range(0, num_ticks)]+([series_max] if tight is True else [])
	# Calculate minimum mantissa given tick spacing
	# Step 1: Look at two contiguous ticks and lower mantissa till they are no more right zeros
	mant = 0
	if tspace < 1:
		for mant in range(10, -1, -1):
			if (str(util_eng.peng_mant(util_eng.peng(tstop, mant)))[-1] != '0') or (str(util_eng.peng_mant(util_eng.peng(tstop-tspace, mant)))[-1] != '0'):
				break
	# Step 2: Confirm labels are unique
	labels_unique = False
	while labels_unique is False:
		(loc, labels) = process_ticks(tick_list, series_min if tight is True else tstart, series_max if tight is True else tstop, mant)
		if sum([1 if labels[index] != labels[index+1] else 0 for index in range(0, len(labels[:-1]))]) == len(labels)-1:
			labels_unique = True
		else:
			mant += 1
	return (loc, labels, tstart if series_delta == 0 else series_min, tstop if series_delta == 0 else series_max)

def series_threshold(indep_var, dep_var, threshold, threshold_type):
	"""
	Chops series given a threshold
	"""
	indexes = numpy.where(numpy.array(indep_var) >= threshold) if threshold_type.upper() == 'MIN' else numpy.where(numpy.array(indep_var) <= threshold)  #pylint: disable-msg=E1101
	indep_var = numpy.array(indep_var)[indexes]  #pylint: disable-msg=E1101
	dep_var = numpy.array(dep_var)[indexes]  #pylint: disable-msg=E1101
	return indep_var, dep_var

def get_series_from_csv(master_source_list, master_filter_list, master_indep_col_list, master_dep_col_list, master_proc_list, indep_min=None, indep_max=None):	#pylint: disable-msg=R0913,R0914
	"""
	Get series for plotting from a CSV file
	"""
	master_indep_var_list = list()
	master_dep_var_list = list()
	for source_list, filter_list, indep_col_list, dep_col_list, proc_list in zip(master_source_list, master_filter_list, master_indep_col_list, master_dep_col_list, master_proc_list):
		raw_indep_var_list = list()
		raw_dep_var_list = list()
		for num, (dsource, dfilter, dindep_col, ddep_col, dproc) in enumerate(zip(source_list, filter_list, indep_col_list, dep_col_list, proc_list)):
			if dfilter is None:
				dsource.reset_filter()
			else:
				dsource.set_filter(dfilter)
			indep_var = numpy.array(dsource.filtered_data(dindep_col))  #pylint: disable-msg=E1101
			dep_var = numpy.array(dsource.filtered_data(ddep_col))  #pylint: disable-msg=E1101
			if dproc is not None:
				indep_var, dep_var = dproc(num, indep_var, dep_var)
			if indep_min is not None:
				indep_var, dep_var = series_threshold(indep_var, dep_var, indep_min, 'MIN')
			if indep_max is not None:
				indep_var, dep_var = series_threshold(indep_var, dep_var, indep_max, 'MAX')
			raw_indep_var_list.append(indep_var)
			raw_dep_var_list.append(dep_var)
		master_indep_var_list.append(raw_indep_var_list)
		master_dep_var_list.append(raw_dep_var_list)

	return master_indep_var_list, master_dep_var_list

def plot_single_pane_from_csv(source_list, filter_list, indep_col_list, dep_col_list, label_list, color_list, proc_list, label_prop_list,	#pylint: disable-msg=R0913,R0914
		 indep_var_label, indep_var_units, dep_var_label, dep_var_units, title_text, log_plot, output_file_name, indep_min=None, indep_max=None):
	"""
	Plot multiple series extracted from CSV file(s) in one panel
	"""
	(raw_indep_var_list, raw_dep_var_list) = get_series_from_csv(source_list, filter_list, indep_col_list, dep_col_list, proc_list, indep_min, indep_max)
	plot_single_panel(raw_indep_var_list, raw_dep_var_list, label_list, color_list, dep_var_label, dep_var_units, label_prop_list, indep_var_label, indep_var_units, title_text, log_plot, output_file_name)


def process_panel_series(raw_indep_var_list, raw_dep_var_list, dep_var_label, dep_var_units, label_list, color_list, legend_prop):	#pylint: disable-msg=R0913,R0914
	"""
	Processes all the series to be plotted in one panel
	"""
	smooth_indep_var_list = list()
	smooth_dep_var_list = list()
	for indep_var, dep_var in zip(raw_indep_var_list, raw_dep_var_list):
		smooth_indep_var = numpy.linspace(min(indep_var), max(indep_var), 500)  #pylint: disable-msg=E1101
		finterp = interp1d(indep_var, dep_var, kind='cubic')
		smooth_indep_var_list.append(smooth_indep_var)
		smooth_dep_var_list.append(finterp(smooth_indep_var))
	# Calculate maximum (in)dependent variable range
	master_indep_var = list()
	master_dep_var = list()
	for indep_var, dep_var in zip(raw_indep_var_list, raw_dep_var_list):
		master_indep_var = numpy.unique(numpy.append(master_indep_var, numpy.round(indep_var, 10)))  #pylint: disable-msg=E1101
		master_dep_var = numpy.unique(numpy.append(master_dep_var, numpy.round(dep_var, 10)))  #pylint: disable-msg=E1101
	(indep_var_min, indep_var_max, indep_var_div, indep_var_unit_scale, scaled_indep_var) = scale_series(series=master_indep_var, scale=True, scale_type='delta')
	(indep_var_locs, indep_var_labels, indep_var_min, indep_var_max) = intelligent_ticks(scaled_indep_var, min(scaled_indep_var), max(scaled_indep_var), tight=True, calc_ticks=False)
	(dep_var_min, dep_var_max, dep_var_div, dep_var_unit_scale, scaled_dep_var) = scale_series(series=master_dep_var, scale=True, scale_type='delta')
	(dep_var_locs, dep_var_labels, dep_var_min, dep_var_max) = intelligent_ticks(scaled_dep_var, min(scaled_dep_var), max(scaled_dep_var), tight=False)
	ret_dict = dict()
	ret_dict['raw_indep_var_list'] = raw_indep_var_list
	ret_dict['raw_dep_var_list'] = raw_dep_var_list
	ret_dict['smooth_indep_var_list'] = smooth_indep_var_list
	ret_dict['smooth_dep_var_list'] = smooth_dep_var_list
	ret_dict['master_indep_var'] = master_indep_var
	ret_dict['master_dep_var'] = master_dep_var
	ret_dict['indep_var_props'] = {'indep_var_min': indep_var_min, 'indep_var_max': indep_var_max, 'indep_var_div': indep_var_div, 'indep_var_unit_scale': indep_var_unit_scale, 'scaled_indep_var': scaled_indep_var,
			'indep_var_locs': indep_var_locs, 'indep_var_labels': indep_var_labels}
	ret_dict['dep_var_props'] = {'dep_var_min': dep_var_min, 'dep_var_max': dep_var_max, 'dep_var_div': dep_var_div, 'dep_var_unit_scale': dep_var_unit_scale, 'scaled_dep_var': scaled_dep_var,
			'dep_var_locs': dep_var_locs, 'dep_var_labels': dep_var_labels, 'dep_var_label':dep_var_label, 'dep_var_units':dep_var_units}
	ret_dict['color_list'] = color_list
	ret_dict['label_list'] = label_list
	ret_dict['legend_prop'] = legend_prop
	return ret_dict

def get_text_prop(fig, text_obj):
	"""
	Return length of text in pixels
	"""
	renderer = fig.canvas.get_renderer()
	bbox = text_obj.get_window_extent(renderer=renderer).transformed(fig.dpi_scale_trans.inverted())
	return {'width':bbox.width*fig.dpi, 'height':bbox.height*fig.dpi}

def get_panel_prop(fig, axarr):
	"""
	Return height of (sub)panel in pixels
	"""
	renderer = fig.canvas.get_renderer()
	bbox = axarr.get_window_extent(renderer=renderer).transformed(fig.dpi_scale_trans.inverted())
	return {'width':bbox.width*fig.dpi, 'height':bbox.height*fig.dpi}

def plot_single_panel(master_indep_var_list, master_dep_var_list, master_label_list, master_color_list, master_dep_var_label_list, master_dep_var_units_list, master_legend_prop_list,	#pylint: disable-msg=R0912,R0913,R0914,R0915
		indep_var_label, indep_var_units, title_text, log_plot, output_file_name):
	"""
	Plot multiple series in one panel
	"""
	legend_pos_list = ['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center']
	panel_dicts = [process_panel_series(raw_indep_var_list, raw_dep_var_list, dep_var_label, dep_var_units, label_list, color_list, legend_prop) for \
			raw_indep_var_list, raw_dep_var_list, dep_var_label, dep_var_units, label_list, color_list, legend_prop in \
			zip(master_indep_var_list, master_dep_var_list, master_dep_var_label_list, master_dep_var_units_list, master_label_list, master_color_list, master_legend_prop_list)]
	num_panels = len(panel_dicts)
	# Determine horizontal axis
	master_indep_var = list()
	for panel_dict in panel_dicts:
		master_indep_var = numpy.unique(numpy.append(master_indep_var, numpy.round(panel_dict['master_indep_var'], 10)))  #pylint: disable-msg=E1101
	(indep_var_min, indep_var_max, indep_var_div, indep_var_unit_scale, scaled_indep_var) = scale_series(series=master_indep_var, scale=True, scale_type='delta')
	(indep_var_locs, indep_var_labels, indep_var_min, indep_var_max) = intelligent_ticks(scaled_indep_var, min(scaled_indep_var), max(scaled_indep_var), tight=True, calc_ticks=False)

	plt.close('all')
	#fig = plt.figure()
	#axarr = num_panels*[0]
	(fig, axarr) = plt.subplots(num_panels, sharex=True)	#pylint: disable-msg=W0612
	max_ytitle_height = 0
	max_ytitle_width = 0
	max_ylabel_width = 0
	max_panel_height = 0
	for panel_num, panel_dict in enumerate(panel_dicts):
		#axarr[panel_num] = fig.add_subplot(num_panels, 1, panel_num, sharex=True)	#pylint: disable-msg=W0612
		for raw_indep_var, raw_dep_var, smooth_indep_var, smooth_dep_var, color, label_text in \
				zip(panel_dict['raw_indep_var_list'], panel_dict['raw_dep_var_list'], panel_dict['smooth_indep_var_list'], panel_dict['smooth_dep_var_list'],
						panel_dict['color_list'], panel_dict['label_list']):
			# Plot smooth lines
			if log_plot is True:
				axarr[panel_num].semilogx(smooth_indep_var/indep_var_div, smooth_dep_var/panel_dict['dep_var_props']['dep_var_div'], color=color, linewidth=2.5, label=label_text)
			else:
				axarr[panel_num].plot(smooth_indep_var/indep_var_div, smooth_dep_var/panel_dict['dep_var_props']['dep_var_div'], color=color, linewidth=2.5, label=label_text)
			# Plot markers with data points
			if log_plot is True:
				axarr[panel_num].semilogx(raw_indep_var/indep_var_div, raw_dep_var/panel_dict['dep_var_props']['dep_var_div'],
						color=color, linestyle='', marker='o', markeredgecolor=color, markersize=14, markeredgewidth=5, markerfacecolor='w')
			else:
				axarr[panel_num].plot(raw_indep_var/indep_var_div, raw_dep_var/panel_dict['dep_var_props']['dep_var_div'],
						color=color, linestyle='', marker='o', markeredgecolor=color, markersize=14, markeredgewidth=5, markerfacecolor='w')
		axarr[panel_num].grid(True, 'both')
		plt.ylim((panel_dict['dep_var_props']['dep_var_min'], panel_dict['dep_var_props']['dep_var_max']), emit=True, auto=False)
		plt.yticks(panel_dict['dep_var_props']['dep_var_locs'], panel_dict['dep_var_props']['dep_var_labels'])
		ylabel = axarr[panel_num].set_ylabel(panel_dict['dep_var_props']['dep_var_label']+' ['+panel_dict['dep_var_props']['dep_var_unit_scale']+ \
				('-' if panel_dict['dep_var_props']['dep_var_units'] is None else panel_dict['dep_var_props']['dep_var_units'])+']', fontdict={'fontsize':18})
		axarr[panel_num].tick_params(axis='both', which='major', labelsize=14)
		ylabel_height = get_text_prop(fig, ylabel)['height']	# Text is rotated
		panel_height = get_panel_prop(fig, axarr[panel_num])['height']
		panel_width = get_panel_prop(fig, axarr[panel_num])['width']
		max_ytitle_height = max(max_ytitle_height, ylabel_height)
		max_ylabel_width = max(max_ylabel_width, get_text_prop(fig, ylabel)['width'])
		max_ytitle_width = max(max_ytitle_width, get_text_prop(fig, ylabel)['width'])
		max_panel_height = max(max_panel_height, panel_height)
		# Print legends
		if len(panel_dict['raw_indep_var_list']) > 1:
			handles, labels = axarr[panel_num].get_legend_handles_labels()	#pylint: disable-msg=W0612
			leg_artist = [plt.Line2D((0, 1), (0, 0), color=color, marker='o', linestyle='-', linewidth=2.5, markeredgecolor=color, markersize=14, markeredgewidth=5, markerfacecolor='w') for color in panel_dict['color_list']]
			if 'cols' in panel_dict['legend_prop']:
				axarr[panel_num].legend(leg_artist, labels, ncol=panel_dict['legend_prop']['cols'] if 'cols' in panel_dict['legend_prop'] else len(labels),
					loc=legend_pos_list[legend_pos_list.index(panel_dict['legend_prop']['pos'])], numpoints=1)
	# Calculate maximum panel height
	common_panel_height = max(max_ytitle_height, max_panel_height)
	#  Print independent variable tick marks and label
	plt.xlim((indep_var_min, indep_var_max), emit=True, auto=False)
	plt.xticks(indep_var_locs, indep_var_labels)
	plt.xlabel(indep_var_label +' ['+indep_var_unit_scale+('-' if indep_var_units is None else indep_var_units)+']', fontdict={'fontsize':18})
	# Calculate width of panel to avoid overlapping labels
	tot_width = 0
	(fig2, axarr2) = plt.subplots(1, sharex=True)
	for label in indep_var_labels:
		tlabel = axarr2.text(1, 1, label, fontdict={'fontsize':18})
		tot_width += (18+get_panel_prop(fig2, tlabel)['width'])
	tot_width += max_ylabel_width+max_ytitle_width+2*18
	tot_width /= fig.dpi
	# Print title
	if title_text is not None:
		fig.suptitle('\n'.join(title_text), horizontalalignment='center', verticalalignment='bottom', multialignment='center', fontsize=24)
	# Save or show plot
	if output_file_name is not None:
		height = 1+(num_panels*(0.5+(common_panel_height/fig.dpi)))
		fig.set_size_inches(tot_width, height)
		util_misc.make_dir(output_file_name)
		fig.savefig(output_file_name, bbox_inches='tight', dpi=fig.dpi)
		#fig.clear()
		plt.close('all')
	else:
		plt.show()

def parametrized_color_space(series, offset=0):
	"""
	Computes a colors space where lighter colors correspond to lower parameter values
	"""
	return [plt.cm.YlOrBr(util_misc.normalize(value, series, offset)) for value in series]	#pylint: disable-msg=E1101
