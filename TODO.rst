Task List
=========

* Clean up repository

* plot module:

  + Use an abstract base class to derive BasicSource and CsVSource classes

  + Write MultiCsvSeriesPanel, with potentially this signature:

    .. code-block:: python 

		def __init__(self, indep_col_label, dep_col_label, indep_min, indep_max, fproc, fproc_eargs, file_name=None, series=None, interp='CUBIC', line_style='-', primary_axis_label='', primary_axis_units='', secondary_axis_label='', secondary_axis_units='', log_dep_axis=False, legend_props=None, display_indep_axis=False):

	* **indep_col_label**: same as :py:class:`putil.plot.CsvSource` :code:`indep_col_label` argument

	* **dep_col_label**: same as :py:class:`putil.plot.CsvSource` :code:`dep_col_label` argument

	* **indep_min**: same as :py:class:`putil.plot.CsvSource` :code:`indep_min` argument

	* **indep_max**: same as :py:class:`putil.plot.CsvSource` :code:`indep_max` argument

	* **fproc**: same as :py:class:`putil.plot.CsvSource` :code:`fproc` argument

	* **fproc_eargs**: same as :py:class:`putil.plot.CsvSource` :code:`fproc_eargs` argument

	* **file_name**: CSV file to extract series from

	The :code:`file_name` argument, if given, is the default comma-separated values (CSV) file to extract series from. The :code:`series` argument is a list of dictionaries with the folowing structure:

	* **file_name**: CSV file to extract series from, overrides :code:`file_name` argument, default :code:`file_name`

	* **label**: same as :py:class:`putil.plot.Series` :code:`label` argument

    * **secondary_axis**: same as :py:class:`putil.plot.Series` :code:`secondary_axis` argument

	* **dfilter**: same as :py:class:`putil.plot.Series` :code:`dfilter` argument

	The idea is to mnimize code in situations where data is parameterized and the data for each parameter is in a separate CSV file with the same header, OR in situations where
	the data is in one file but parameterized by one of the data columns. The colors and markers would be selected automatically. There could also be a MultiCsvSeriesPanel.add_series()
	method to add more CsvSeries or BasicSeries objects.

