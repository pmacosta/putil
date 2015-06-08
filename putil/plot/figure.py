# figure.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,R0201,R0914,W0105,W0212

from __future__ import print_function
import numpy
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

import putil.exh
import putil.misc
import putil.pcontracts
from .panel import Panel
from .constants import TITLE_FONT_SIZE
from .functions import _intelligent_ticks


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
if sys.version_info.major == 2:
	import __builtin__
else:
	import builtins as __builtin__
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_plot_figure
exobj_plot = trace_ex_plot_figure.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
def _first_label(label_list):
	""" Find first non-blank label """
	for label_index, label_obj in enumerate(label_list):
		if ((label_obj.get_text() is not None) and
		   (label_obj.get_text().strip() != '')):
			return label_index
	return None


def _get_text_prop(fig, text_obj):
	""" Return length of text in pixels """
	renderer = fig.canvas.get_renderer()
	bbox = text_obj.get_window_extent(renderer=renderer).transformed(
		fig.dpi_scale_trans.inverted()
	)
	return {'width':bbox.width*fig.dpi, 'height':bbox.height*fig.dpi}


def _get_yaxis_size(fig_obj, tick_labels, axis_label):
	""" Compute Y axis height and width """
	# Minimum of one line spacing between vertical ticks
	axis_height = axis_width = 0
	label_index = _first_label(tick_labels)
	if label_index:
		label_height = _get_text_prop(fig_obj, tick_labels[label_index])['height']
		axis_height = (2*len(tick_labels)-1)*label_height
		axis_width = max([
			num
			for num in [_get_text_prop(fig_obj, tick)['width']
			for tick in tick_labels]
			if isinstance(num, int) or isinstance(num, float)
		])
	# axis_label is a Text object, which is never None, it has the x, y
	# coordinates and axis label text, even if is = ''
	axis_height = max(axis_height, _get_text_prop(fig_obj, axis_label)['height'])
	axis_width = axis_width+(1.5*_get_text_prop(fig_obj, axis_label)['width'])
	return axis_height, axis_width


def _get_xaxis_size(fig_obj, tick_labels, axis_label):
	""" Compute Y axis height and width """
	# Minimum of one smallest label separation between horizontal ticks
	min_label_width = min([
		num
		for num in [_get_text_prop(fig_obj, tick)['width']
		for tick in tick_labels]
		if isinstance(num, int) or isinstance(num, float)
	])
	axis_width = ((len(tick_labels)-1)*min_label_width)+sum([
		num
		for num in [_get_text_prop(fig_obj, tick)['width']
		for tick in tick_labels]
		if isinstance(num, int) or isinstance(num, float)
	])
	# axis_label is a Text object, which is never None, it has the x, y
	# coordinates and axis label text, even if is = ''
	axis_height = 1.5*_get_text_prop(fig_obj, axis_label)['height']
	axis_width = max(axis_width, _get_text_prop(fig_obj, axis_label)['width'])
	return axis_height, axis_width


###
# Class
###
class Figure(object):
	r"""
	Generates presentation-quality plots

	:param	panels:				one or more data panels
	:type	panels:				:py:class:`putil.plot.Panel` *object or list
	 of* :py:class:`putil.plot.Panel` *objects*
	:param	indep_var_label:	independent variable label
	:type	indep_var_label:	string
	:param	indep_var_units:	independent variable units
	:type	indep_var_units:	string
	:param	fig_width:			hard copy plot width in inches
	:type	fig_width:			:ref:`PositiveRealNum`
	:param	fig_height:			hard copy plot height in inches
	:type	fig_height:			:ref:`PositiveRealNum`
	:param	title:				plot title
	:type	title:				string
	:param	log_indep_axis:		Flag that indicates whether the independent
	 axis is linear (False) or logarithmic (True)
	:type	log_indep_axis:		boolean

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for
	.. putil.plot.figure.Figure.__init__

	:raises:
	 * RuntimeError (Argument \`fig_height\` is not valid)

	 * RuntimeError (Argument \`fig_width\` is not valid)

	 * RuntimeError (Argument \`indep_var_label\` is not valid)

	 * RuntimeError (Argument \`indep_var_units\` is not valid)

	 * RuntimeError (Argument \`log_indep_axis\` is not valid)

	 * RuntimeError (Argument \`panels\` is not valid)

	 * RuntimeError (Argument \`title\` is not valid)

	 * RuntimeError (Figure object is not fully specified)

	 * RuntimeError (Figure size is too small: minimum width = *[min_width]*,
	   minimum height *[min_height]*)

	 * TypeError (Panel *[panel_num]* is not fully specified)

	 * ValueError (Figure cannot cannot be plotted with a logarithmic
	   independent axis because panel *[panel_num]*, series *[series_num]*
	   contains negative independent data points)

	.. [[[end]]]

	.. note:: The appropriate figure dimensions so that no labels are
	 obstructed are calculated and used if the arguments **fig_width** and/or
	 **fig_height** are not specified. The calculated figure width and/or
	 height can be retrieved using the :py:attr:`putil.plot.Figure.fig_width`
	 and/or :py:attr:`putil.plot.Figure.fig_height` attributes.

	"""
	# pylint: disable=R0902,R0913
	def __init__(self, panels=None, indep_var_label='', indep_var_units='',
		fig_width=None, fig_height=None, title='', log_indep_axis=False):
		self._exh = putil.exh.get_or_create_exh_obj()
		# Public attributes
		self._fig, self._panels, self._indep_var_label = None, None, None
		self._title, self._log_indep_axis = None, None
		self._fig_width, self._fig_height = None, None
		self._indep_var_units, self._indep_var_div = None, None
		self._axes_list = list()
		# Assignment of arguments to attributes
		self._set_indep_var_label(indep_var_label)
		self._set_indep_var_units(indep_var_units)
		self._set_title(title)
		self._set_log_indep_axis(log_indep_axis)
		self._set_fig_width(fig_width)
		self._set_fig_height(fig_height)
		self._set_panels(panels)

	def __iter__(self):
		r"""
		Returns an iterator over the panel object(s) in the figure. For example:

		.. =[=cog
		.. import docs.support.incfile
		.. docs.support.incfile.incfile('plot_example_7.py', cog)
		.. =]=
		.. code-block:: python

		    # plot_example_7.py
		    from __future__ import print_function
		    import numpy, putil.plot

		    def figure_iterator_example(no_print):
		        source1 = putil.plot.BasicSource(
		            indep_var=numpy.array([1, 2, 3, 4]),
		            dep_var=numpy.array([1, -10, 10, 5])
		        )
		        source2 = putil.plot.BasicSource(
		            indep_var=numpy.array([100, 200, 300, 400]),
		            dep_var=numpy.array([50, 75, 100, 125])
		        )
		        series1 = putil.plot.Series(
		            data_source=source1,
		            label='Goals'
		        )
		        series2 = putil.plot.Series(
		            data_source=source2,
		            label='Saves',
		            color='b',
		            marker=None,
		            interp='STRAIGHT',
		            line_style='--'
		        )
		        panel1 = putil.plot.Panel(
		            series=series1,
		            primary_axis_label='Average',
		            primary_axis_units='A',
		            display_indep_axis=False
		        )
		        panel2 = putil.plot.Panel(
		            series=series2,
		            primary_axis_label='Standard deviation',
		            primary_axis_units=r'$\sqrt{{A}}$',
		            display_indep_axis=True
		        )
		        figure = putil.plot.Figure(
		            panels=[panel1, panel2],
		            indep_var_label='Time',
		            indep_var_units='sec',
		            title='Sample Figure'
		        )
		        if not no_print:
		            for num, panel in enumerate(figure):
		                print('Panel {0}:'.format(num+1))
		                print(panel)
		                print('')
		        else:
		            return figure

		.. =[=end=]=

		.. code-block:: python

			>>> import docs.support.plot_example_7 as mod
			>>> mod.figure_iterator_example(False)
			Panel 1:
			Series 0:
			   Independent variable: [ 1.0, 2.0, 3.0, 4.0 ]
			   Dependent variable: [ 1.0, -10.0, 10.0, 5.0 ]
			   Label: Goals
			   Color: k
			   Marker: o
			   Interpolation: CUBIC
			   Line style: -
			   Secondary axis: False
			Primary axis label: Average
			Primary axis units: A
			Secondary axis label: not specified
			Secondary axis units: not specified
			Logarithmic dependent axis: False
			Display independent axis: False
			Legend properties:
			   cols: 1
			   pos: BEST
			<BLANKLINE>
			Panel 2:
			Series 0:
			   Independent variable: [ 100.0, 200.0, 300.0, 400.0 ]
			   Dependent variable: [ 50.0, 75.0, 100.0, 125.0 ]
			   Label: Saves
			   Color: b
			   Marker: None
			   Interpolation: STRAIGHT
			   Line style: --
			   Secondary axis: False
			Primary axis label: Standard deviation
			Primary axis units: $\sqrt{{A}}$
			Secondary axis label: not specified
			Secondary axis units: not specified
			Logarithmic dependent axis: False
			Display independent axis: True
			Legend properties:
			   cols: 1
			   pos: BEST
			<BLANKLINE>

        """
		return iter(self._panels)

	def __nonzero__(self):	# pragma: no cover
		"""
		Returns :code:`True` if the figure has at least a panel associated with
		it, :code:`False` otherwise
		"""
		return self._panels is not None

	def __bool__(self):	# pragma: no cover
		"""
		Returns :code:`True` if the figure has at least a panel associated with
		it, :code:`False` otherwise
		"""
		return self._panels is not None

	def _get_indep_axis_scale(self):
		return self._indep_var_div

	def _get_indep_var_label(self):
		return self._indep_var_label

	@putil.pcontracts.contract(indep_var_label='None|str')
	def _set_indep_var_label(self, indep_var_label):
		self._indep_var_label = indep_var_label
		self._draw(force_redraw=True)

	def _get_indep_var_units(self):
		return self._indep_var_units

	@putil.pcontracts.contract(indep_var_units='None|str')
	def _set_indep_var_units(self, indep_var_units):
		self._indep_var_units = indep_var_units
		self._draw(force_redraw=True)

	def _get_title(self):
		return self._title

	@putil.pcontracts.contract(title='None|str')
	def _set_title(self, title):
		self._title = title
		self._draw(force_redraw=True)

	def _get_log_indep_axis(self):
		return self._log_indep_axis

	@putil.pcontracts.contract(log_indep_axis='None|bool')
	def _set_log_indep_axis(self, log_indep_axis):
		self._log_indep_axis = log_indep_axis
		self._draw(force_redraw=True)

	def _get_fig_width(self):
		return self._fig_width

	@putil.pcontracts.contract(fig_width='None|positive_real_num')
	def _set_fig_width(self, fig_width):
		self._fig_width = fig_width

	def _get_fig_height(self):
		return self._fig_height

	@putil.pcontracts.contract(fig_height='None|positive_real_num')
	def _set_fig_height(self, fig_height):
		self._fig_height = fig_height

	def _get_panels(self):
		return self._panels

	def _set_panels(self, panels):
		self._panels = ((panels if isinstance(panels, list) else [panels])
					   if panels is not None else
					   panels)
		if self.panels is not None:
			self._validate_panels()
		self._draw(force_redraw=True)

	def _validate_panels(self):
		"""
		Verifies that elements of panel list are of the right type and
		fully specified
		"""
		self._exh.add_exception(
			exname='invalid_panel',
			extype=RuntimeError,
			exmsg='Argument `panels` is not valid'
		)
		self._exh.add_exception(
			exname='panel_not_fully_specified',
			extype=TypeError,
			exmsg='Panel *[panel_num]* is not fully specified'
		)
		for num, obj in enumerate(self.panels):
			self._exh.raise_exception_if(
				exname='invalid_panel',
				condition=type(obj) is not Panel)

			self._exh.raise_exception_if(
				exname='panel_not_fully_specified',
				condition=not obj._complete,
				edata={'field':'panel_num', 'value':num}
			)

	def _get_fig(self):
		return self._fig

	def _get_axes_list(self):
		return self._axes_list

	def _get_complete(self):
		""" Returns True if figure is fully specified, otherwise returns False """
		return (self.panels is not None) and (len(self.panels) > 0)

	def _draw(self, force_redraw=False, raise_exception=False):
		# pylint: disable=C0326,W0612
		self._exh.add_exception(
			exname='log_axis',
			extype=ValueError,
			exmsg='Figure cannot cannot be plotted with a logarithmic '
				  'independent axis because panel *[panel_num]*, series '
				  '*[series_num]* contains negative independent data points'
		)
		self._exh.add_exception(
			exname='not_fully_specified',
			extype=RuntimeError,
			exmsg='Figure object is not fully specified'
		)
		if (self._complete) and force_redraw:
			num_panels = len(self.panels)
			plt.close('all')
			# Create required number of panels
			self._fig, axes = plt.subplots(num_panels, sharex=True)
			axes = axes if isinstance(axes, type(numpy.array([]))) else [axes]
			glob_indep_var = list()
			# Find union of the independent variable data set of all panels
			for panel_num, panel_obj in enumerate(self.panels):
				for series_num, series_obj in enumerate(panel_obj.series):
					if ((self.log_indep_axis is not None) and
					   self.log_indep_axis and (min(series_obj.indep_var) < 0)):
						self._exh.raise_exception_if(
							exname='log_axis',
							condition=bool((self.log_indep_axis is not None) and
									  self.log_indep_axis and
									  (min(series_obj.indep_var) < 0)),
							edata=[
								{'field':'panel_num', 'value':panel_num},
								{'field':'series_num', 'value':series_num}
							]
						)
					glob_indep_var = numpy.unique(numpy.append(
						glob_indep_var,
						numpy.array([
							putil.eng.round_mantissa(element, 10)
							for element in series_obj.indep_var
						])
					))
			(indep_var_locs,
			indep_var_labels,
			indep_var_min,
			indep_var_max,
			self._indep_var_div,
			indep_var_unit_scale) = (
				_intelligent_ticks(
					glob_indep_var,
					min(glob_indep_var),
					max(glob_indep_var),
					tight=True,
					log_axis=self.log_indep_axis
				))
			# Scale all panel series
			for panel_obj in self.panels:
				panel_obj._scale_indep_var(self._indep_var_div)
			# Draw panels
			indep_axis_dict = {
				'indep_var_min':indep_var_min,
				'indep_var_max':indep_var_max,
				'indep_var_locs':indep_var_locs,
				'indep_var_labels':None,
				'indep_axis_label':None,
				'indep_axis_units':None,
				'indep_axis_unit_scale':None
			}
			indep_axis_dict = {
				'log_indep':self.log_indep_axis,
				'indep_var_min':indep_var_min,
				'indep_var_max':indep_var_max,
				'indep_var_locs':indep_var_locs,
				'indep_var_labels':indep_var_labels,
				'indep_axis_label':self.indep_var_label,
				'indep_axis_units':self.indep_var_units,
				'indep_axis_unit_scale':indep_var_unit_scale
			}
			panels_with_indep_axis_list = [
				num for num, panel_obj in enumerate(self.panels)
				if panel_obj.display_indep_axis
			]
			panels_with_indep_axis_list = ([num_panels-1]
										  if len(panels_with_indep_axis_list) == 0 else
										  panels_with_indep_axis_list)
			for num, (panel_obj, axarr) in enumerate(zip(self.panels, axes)):
				panel_dict = panel_obj._draw_panel(
					axarr, indep_axis_dict, num in panels_with_indep_axis_list
				)
				self._axes_list.append({
					'number':num,
					'primary':panel_dict['primary'],
					'secondary':panel_dict['secondary']
				})
			if self.title not in [None, '']:
				axes[0].set_title(
					self.title,
					horizontalalignment='center',
					verticalalignment='bottom',
					multialignment='center',
					fontsize=TITLE_FONT_SIZE
				)
			#self._fig.canvas.draw()
			# Draw figure otherwise some bounding boxes return NaN
			FigureCanvasAgg(self._fig).draw()
			self._calculate_figure_size()
		elif (not self._complete) and (raise_exception):
			self._exh.raise_exception_if(
				exname='not_fully_specified',
				condition=True
			)

	def _calculate_figure_size(self):
		""" Calculates minimum panel and figure size """
		self._exh.add_exception(
			exname='fig_small',
			extype=RuntimeError,
			exmsg='Figure size is too small: minimum width = *[min_width]*, '
				  'minimum height *[min_height]*'
		)
		title_height = title_width = 0
		title = self._fig.axes[0].get_title()
		if (title is not None) and (title.strip() != ''):
			title_obj = self._fig.axes[0].title
			title_height = _get_text_prop(self._fig, title_obj)['height']
			title_width = _get_text_prop(self._fig, title_obj)['width']
		xaxis_dims = [
			_get_xaxis_size(
				self._fig,
				axis_obj.xaxis.get_ticklabels(),
				axis_obj.xaxis.get_label()
			) for axis_obj in self._fig.axes
		]
		yaxis_dims = [
			_get_yaxis_size(
				self._fig,
				axis_obj.yaxis.get_ticklabels(),
				axis_obj.yaxis.get_label()
			) for axis_obj in self._fig.axes
		]
		panel_dims = [
			(yaxis_height+xaxis_height, yaxis_width+xaxis_width)
			for (yaxis_height, yaxis_width), (xaxis_height, xaxis_width)
			in zip(yaxis_dims, xaxis_dims)
		]
		min_fig_width = round(
			(
				max(
					title_width,
					max([panel_width for _, panel_width in panel_dims])
				)
			)/float(self._fig.dpi),
			2
		)
		min_fig_height = round(
			(
				(
					(
						len(self._axes_list)*max([
							panel_height
							for panel_height, _ in panel_dims
						])
					)+title_height
				)/float(self._fig.dpi)),
			2
		)
		self._exh.raise_exception_if(
			exname='fig_small',
			condition=bool(((self.fig_width is not None) and
					  (self.fig_width < min_fig_width)) or
					  ((self.fig_height is not None) and
					  (self.fig_height < min_fig_height))),
			edata=[
				{'field':'min_width', 'value':min_fig_width},
				{'field':'min_height', 'value':min_fig_height}
			]
		)
		self.fig_width = min_fig_width if self.fig_width is None else self.fig_width
		self.fig_height = (min_fig_height
						  if self.fig_height is None
						  else self.fig_height)

	def show(self):
		"""
		Displays the figure

		.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for
		.. putil.plot.figure.Figure.show

		:raises:
		 * RuntimeError (Figure object is not fully specified)

		 * ValueError (Figure cannot cannot be plotted with a logarithmic
		   independent axis because panel *[panel_num]*, series *[series_num]*
		   contains negative independent data points)

		.. [[[end]]]
		"""
		self._draw(force_redraw=self._fig is None, raise_exception=True)
		plt.show()

	@putil.pcontracts.contract(fname='file_name')
	def save(self, fname):
		r"""
		Saves the figure in PNG format to a file

		:param	fname:	File name
		:type	fname:	:ref:`FileName`

		.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for
		.. putil.plot.figure.Figure.save

		:raises:
		 * RuntimeError (Argument \`fname\` is not valid)

		 * RuntimeError (Figure object is not fully specified)

		 * ValueError (Figure cannot cannot be plotted with a logarithmic
		   independent axis because panel *[panel_num]*, series *[series_num]*
		   contains negative independent data points)

		.. [[[end]]]
		"""
		self._exh.add_exception(
			exname='fig_not_fully_specified',
			extype=RuntimeError,
			exmsg='Figure object is not fully specified'
		)
		self._exh.raise_exception_if(
			exname='fig_not_fully_specified',
			condition=not self._complete
		)
		self._draw(force_redraw=self._fig is None, raise_exception=True)
		self.fig.set_size_inches(self.fig_width, self.fig_height)
		# Matplotlib seems to have a problem with ~/, expand it to $HOME
		fname = os.path.expanduser(fname)
		putil.misc.make_dir(fname)
		self._fig.savefig(fname, bbox_inches='tight', dpi=self._fig.dpi)
		plt.close('all')

	def __str__(self):
		r"""
		Prints figure information. For example:

			>>> from __future__ import print_function
			>>> import docs.support.plot_example_7 as mod
			>>> print(mod.figure_iterator_example(True))	#doctest: +ELLIPSIS
			Panel 0:
			   Series 0:
			      Independent variable: [ 1.0, 2.0, 3.0, 4.0 ]
			      Dependent variable: [ 1.0, -10.0, 10.0, 5.0 ]
			      Label: Goals
			      Color: k
			      Marker: o
			      Interpolation: CUBIC
			      Line style: -
			      Secondary axis: False
			   Primary axis label: Average
			   Primary axis units: A
			   Secondary axis label: not specified
			   Secondary axis units: not specified
			   Logarithmic dependent axis: False
			   Display independent axis: False
			   Legend properties:
			      cols: 1
			      pos: BEST
			Panel 1:
			   Series 0:
			      Independent variable: [ 100.0, 200.0, 300.0, 400.0 ]
			      Dependent variable: [ 50.0, 75.0, 100.0, 125.0 ]
			      Label: Saves
			      Color: b
			      Marker: None
			      Interpolation: STRAIGHT
			      Line style: --
			      Secondary axis: False
			   Primary axis label: Standard deviation
			   Primary axis units: $\sqrt{{A}}$
			   Secondary axis label: not specified
			   Secondary axis units: not specified
			   Logarithmic dependent axis: False
			   Display independent axis: True
			   Legend properties:
			      cols: 1
			      pos: BEST
			Independent variable label: Time
			Independent variable units: sec
			Logarithmic independent axis: False
			Title: Sample Figure
			Figure width: ...
			Figure height: ...
			<BLANKLINE>
		"""
		ret = ''
		if (self.panels is None) or (len(self.panels) == 0):
			ret += 'Panels: None\n'
		else:
			for num, element in enumerate(self.panels):
				ret += 'Panel {0}:\n'.format(num)
				temp = str(element).split('\n')
				temp = [3*' '+line for line in temp]
				ret += '\n'.join(temp)
				ret += '\n'
		ret += 'Independent variable label: {0}\n'.format(
			self.indep_var_label
			if self.indep_var_label not in ['', None] else
			'not specified'
		)
		ret += 'Independent variable units: {0}\n'.format(
			self.indep_var_units
			if self.indep_var_units not in ['', None] else
			'not specified'
		)
		ret += 'Logarithmic independent axis: {0}\n'.format(self.log_indep_axis)
		ret += 'Title: {0}\n'.format(
			self.title if self.title not in ['', None] else 'not specified'
		)
		ret += 'Figure width: {0}\n'.format(self.fig_width)
		ret += 'Figure height: {0}\n'.format(self.fig_height)
		return ret

	_complete = property(_get_complete)

	indep_var_label = property(
		_get_indep_var_label,
		_set_indep_var_label,
		doc='Figure independent axis label'
	)
	r"""
	Gets or sets the figure independent variable label

	:type: string or None, default is ''

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for
	.. putil.plot.figure.Figure.indep_var_label

	:raises: (when assigned)

	 * RuntimeError (Argument \`indep_var_label\` is not valid)

	 * RuntimeError (Figure object is not fully specified)

	 * ValueError (Figure cannot cannot be plotted with a logarithmic
	   independent axis because panel *[panel_num]*, series *[series_num]*
	   contains negative independent data points)

	.. [[[end]]]
	"""

	indep_var_units = property(
		_get_indep_var_units,
		_set_indep_var_units,
		doc='Figure independent axis units'
	)
	r"""
	Gets or sets the figure independent variable units

	:type: string or None, default is ''

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for
	.. putil.plot.figure.Figure.indep_var_units

	:raises: (when assigned)

	 * RuntimeError (Argument \`indep_var_units\` is not valid)

	 * RuntimeError (Figure object is not fully specified)

	 * ValueError (Figure cannot cannot be plotted with a logarithmic
	   independent axis because panel *[panel_num]*, series *[series_num]*
	   contains negative independent data points)

	.. [[[end]]]
	"""

	title = property(_get_title, _set_title, doc='Figure title')
	r"""
	Gets or sets the figure title

	:type: string or None, default is ''

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for
	.. putil.plot.figure.Figure.title

	:raises: (when assigned)

	 * RuntimeError (Argument \`title\` is not valid)

	 * RuntimeError (Figure object is not fully specified)

	 * ValueError (Figure cannot cannot be plotted with a logarithmic
	   independent axis because panel *[panel_num]*, series *[series_num]*
	   contains negative independent data points)

	.. [[[end]]]
	"""

	log_indep_axis = property(
		_get_log_indep_axis,
		_set_log_indep_axis,
		doc='Figure log_indep_axis'
	)
	r"""
	Gets or sets the figure logarithmic independent axis flag; indicates
	whether the independent axis is linear (False) or logarithmic (True)

	:type: boolean, default is False

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for
	.. putil.plot.figure.Figure.log_indep_axis

	:raises: (when assigned)

	 * RuntimeError (Argument \`log_indep_axis\` is not valid)

	 * RuntimeError (Figure object is not fully specified)

	 * ValueError (Figure cannot cannot be plotted with a logarithmic
	   independent axis because panel *[panel_num]*, series *[series_num]*
	   contains negative independent data points)

	.. [[[end]]]
	"""

	fig_width = property(
		_get_fig_width,
		_set_fig_width,
		doc='Width of the hard copy plot'
	)
	r"""
	Gets or sets the width (in inches) of the hard copy plot

	:type: :ref:`PositiveRealNum`

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for
	.. putil.plot.figure.Figure.fig_width

	:raises: (when assigned) RuntimeError (Argument \`fig_width\` is not
	 valid)

	.. [[[end]]]
	"""

	fig_height = property(
		_get_fig_height,
		_set_fig_height,
		doc='height of the hard copy plot'
	)
	r"""
	Gets or sets the height (in inches) of the hard copy plot

	:type: :ref:`PositiveRealNum`

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for
	.. putil.plot.figure.Figure.fig_height

	:raises: (when assigned) RuntimeError (Argument \`fig_height\` is not
	 valid)

	.. [[[end]]]
	"""

	panels = property(_get_panels, _set_panels, doc='Figure panel(s)')
	r"""
	Gets or sets the figure panel(s)

	:type: :py:class:`putil.plot.Panel` object or list of
	 :py:class:`putil.plot.panel` objects

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for
	.. putil.plot.figure.Figure.panels

	:raises: (when assigned)

	 * RuntimeError (Argument \`fig_height\` is not valid)

	 * RuntimeError (Argument \`fig_width\` is not valid)

	 * RuntimeError (Argument \`panels\` is not valid)

	 * RuntimeError (Figure object is not fully specified)

	 * RuntimeError (Figure size is too small: minimum width = *[min_width]*,
	   minimum height *[min_height]*)

	 * TypeError (Panel *[panel_num]* is not fully specified)

	 * ValueError (Figure cannot cannot be plotted with a logarithmic
	   independent axis because panel *[panel_num]*, series *[series_num]*
	   contains negative independent data points)

	.. [[[end]]]
	"""

	fig = property(_get_fig, doc='Figure handle')
	"""
	Gets the Matplotlib figure handle. Useful if annotations or further
	customizations to the figure are needed

	:type: Matplotlib figure handle if figure is fully specified, otherwise None
	"""

	axes_list = property(_get_axes_list, doc='Matplotlib figure axes handle list')
	"""
	Gets the Matplotlib figure axes handle list. Useful if annotations or
	further customizations to the panel(s) are needed. Each panel has an entry
	in the list, which is sorted in the order the panels are plotted (top to
	bottom). Each panel entry is a dictionary containing the following
	key-value pairs:

	* **number** (*integer*) -- panel number, panel 0 is the top-most panel

	* **primary** (*Matplotlib axis object*) -- axis handle for the primary
	  axis, None if the figure has not primary axis

	* **secondary** (*Matplotlib axis object*) -- axis handle for the
	  secondary axis, None if the figure has no secondary axis

	:type: list
	"""

	indep_axis_scale = property(
		_get_indep_axis_scale,
		doc='Independent axis scale'
	)
	"""
	Gets the scale of the figure independent axis

	:type:	float or None if figure has no panels associated with it
	"""
