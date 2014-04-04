#pylint: disable-msg=C0302
"""
Utility classes, methods and functions to handle plotting
"""

import os
import math
import numpy
from scipy import stats
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d  #pylint: disable-msg=E0611

import util_csv
import util_eng
import util_misc

class RawSource(object):
	"""
	Container to hold data sets intended for plotting

	:param	indep_var:			independent variable vector
	:param	indep_var:			Numpy vector
	:param	dep_var:			dependent variable vector
	:param	dep_var:			Numpy vector
	:type	indep_min:			number
	:type	indep_min:			number
	:param	indep_max:			maximum independent variable value
	:type	indep_max:			number
	"""
	def __init__(self, indep_var, dep_var, indep_min=None, indep_max=None):
		self.current_indep_var = None
		self.current_dep_var = None
		self.current_indep_min = None
		self.current_indep_max = None
		self.indep_min(indep_min)
		self.indep_max(indep_max)
		self.load_data(indep_var, dep_var)

	def indep_var(self):
		"""
		Returns the independent variable data (if loaded)

		:rtype:		Numpy vector
		:raises:	RuntimeError (No independent variable data set loaded)
		"""
		if self.current_indep_var is None:
			raise RuntimeError('No independent variable data set loaded')
		else:
			return self.current_indep_var

	def dep_var(self):
		"""
		Returns the independent variable data (if loaded)

		:rtype:		Numpy vector
		:raises:	RuntimeError (No dependent variable data set loaded)
		"""
		if self.current_dep_var is None:
			raise RuntimeError('No dependent variable data set loaded')
		else:
			return self.current_dep_var

	def indep_min(self, *num):
		"""
		Sets or returns the minimum independent variable limit

		:param	num:	minimum independent variable limit
		:type	num:	number
		:rtype:			number
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Minimum independent variable limit must be number)
		"""
		if len(num) == 0:
			return self.current_indep_min
		if len(num) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_indep_min = num[0]
		if self.current_indep_min is not None:
			if util_misc.isnumber(self.current_indep_min) is False:
				raise TypeError('Minimum independent variable limit must be number')
			self.current_indep_min = float(self.current_indep_min)

	def indep_max(self, *num):
		"""
		Sets or returns the maximum independent variable limit

		:param	num:	maximum independent variable limit
		:type	num:	number
		:rtype:			number
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Maximum independent variable limit must be number)
		"""
		if len(num) == 0:
			return self.current_indep_max
		if len(num) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_indep_max = num[0]
		if self.current_indep_max is not None:
			if util_misc.isnumber(self.current_indep_max) is False:
				raise TypeError('Maximum independent variable limit must be number')
			self.current_indep_max = float(self.current_indep_max)

	def load_data(self, indep_var, dep_var):	#pylint: disable-msg=R0912,R0915
		"""
		Retrieves data from file based on specified parameters

		:raises:
		 * RuntimeError (Independent variable data set is empty)

		 * ValueError (Independent data set element *[number]* (*[value]*) is not a number)

		 * RuntimeError (Dependent variable data set is empty)

		 * ValueError (Dependent data set element *[number]* (*[value]*) is not a number)

		 * RuntimeError (Independent variable data set is empty after indep_min thresholding)

		 * RuntimeError (Dependent variable data set is empty after indep_min thresholding)

		 * RuntimeError (Independent variable data set is empty after indep_max thresholding)

		 * RuntimeError (Dependent variable data set is empty after indep_max thresholding)
		"""
		# Retrieve data and check data integrity
		self.current_indep_var = numpy.array(indep_var)
		if len(self.current_indep_var) == 0:
			raise RuntimeError('Independent variable data set is empty')
		for index, num in enumerate(self.current_indep_var):
			if util_misc.isnumber(num) is False:
				raise ValueError('Independent data set element {0} ({1}) is not a number'.format(index, num))
		self.current_dep_var = numpy.array(dep_var)
		if len(self.current_dep_var) == 0:
			raise RuntimeError('Dependent variable data set is empty')
		for index, num in enumerate(self.current_dep_var):
			if util_misc.isnumber(num) is False:
				raise ValueError('Dependent data set element {0} ({1}) is not a number'.format(index, num))
		# Flip data if it is in descending order (affects interpolation)
		if self.current_indep_var[0] > self.current_indep_var[-1]:
			self.current_indep_var = self.current_indep_var[::-1]
			self.current_dep_var = self.current_dep_var[::-1]
		# Apply minimum/maximum global filters
		if self.current_indep_min is not None:
			self.current_indep_var, self.current_dep_var = _series_threshold(self.current_indep_var, self.current_dep_var, self.current_indep_min, 'MIN')
		if len(self.current_indep_var) == 0:
			raise RuntimeError('Independent variable data set is empty after indep_min thresholding')
		if len(self.current_dep_var) == 0:
			raise RuntimeError('Dependent variable data set is empty after indep_min thresholding')
		if self.current_indep_max is not None:
			self.current_indep_var, self.current_dep_var = _series_threshold(self.current_indep_var, self.current_dep_var, self.current_indep_max, 'MAX')
		if len(self.current_indep_var) == 0:
			raise RuntimeError('Independent variable data set is empty after indep_max thresholding')
		if len(self.current_dep_var) == 0:
			raise RuntimeError('Dependent variable data set is empty after indep_max thresholding')

	def __str__(self):
		"""
		Print comma-separated value source information
		"""
		ret = ''
		ret += 'Independent variable minimum: {0}\n'.format(self.indep_min())
		ret += 'Independent variable maximum: {0}\n'.format(self.indep_max())
		ret += 'Independent variable: '
		try:
			ret += str(self.indep_var())+'\n'
		except:	#pylint: disable-msg=W0702
			ret += 'None\n'
		ret += 'Dependent variable: '
		try:
			ret += str(self.dep_var())
		except:	#pylint: disable-msg=W0702
			ret += 'None'
		return ret

	def _complete(self):
		"""
		Returns True if object is fully specified, otherwise returns False
		"""
		return True if (self.current_indep_var is not None) and (self.current_dep_var is not None) else False


class CsvSource(object):	#pylint: disable-msg=R0902
	"""
	Retrieves plot series data from a comma-separated file

	:param	file_name:			comma-separated file name
	:type	file_name:			string
	:param	fdef:				data filter definition. See :py:meth:`util_plot.CsvSource.data_filter()`
	:type	fdef:				dictionary
	:param	indep_col_label:	independent variable column label
	:type	indep_col_label:	string
	:param	dep_col_label:		dependent variable column label
	:type	dep_col_label:		string
	:param	indep_min:			minimum independent variable value
	:type	indep_min:			number
	:param	indep_max:			maximum independent variable value
	:type	indep_max:			number
	:param	fproc:				processing function. See :py:meth:`util_plot.CsvSource.processing_function()`
	:type	fproc:				function pointer
	:param	fproc_eargs:		processing function extra arguments. See :py:meth:`util_plot.CsvSource.processing_function_extra_arguments()`
	:type	fproc_eargs:		dictionary
	:raises:
	 * Same as :py:meth:`util_plot.CsvSource.file_name()`

	 * Same as :py:meth:`util_plot.CsvSource.data_filter()`

	 * Same as :py:meth:`util_plot.CsvSource.indep_col_label()`

	 * Same as :py:meth:`util_plot.CsvSource.dep_col_label()`

	 * Same as :py:meth:`util_plot.CsvSource.indep_min()`

	 * Same as :py:meth:`util_plot.CsvSource.indep_max()`

	 * Same as :py:meth:`util_plot.CsvSource.processing_function()`

	 * Same as :py:meth:`util_plot.CsvSource.processing_function_extra_arguments()`
	"""
	def __init__(self, file_name, indep_col_label, dep_col_label, fdef=None, indep_min=None, indep_max=None, fproc=None, fproc_eargs=None):	#pylint: disable-msg=R0913
		self.current_file_name = None
		self.current_data_filter = None
		self.current_indep_col_label = None
		self.current_dep_col_label = None
		self.current_indep_min = None
		self.current_indep_max = None
		self.current_fproc = None
		self.current_fproc_eargs = None
		self.current_indep_var = None
		self.current_dep_var = None
		self.file_name(file_name)
		self.data_filter(fdef)
		self.indep_col_label(indep_col_label)
		self.dep_col_label(dep_col_label)
		self.indep_min(indep_min)
		self.indep_max(indep_max)
		self.processing_function(fproc)
		self.processing_function_extra_arguments(fproc_eargs)
		self.load_data()

	def file_name(self, *name):
		"""
		Sets or returns the comma-separated file from which a data series is going to be extracted

		:param	name:	comma-separated file name
		:type	name:	string
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Comma-separated file name must be a string)

		 * IOError (Comma-separated file **name** could not be found)

		.. warning:: The first line of the comma-separated file must contain unique headers for each column
		"""
		if len(name) == 0:
			return self.current_file_name
		if len(name) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_file_name = name[0]
		if isinstance(self.current_file_name, str) is False:
			raise TypeError('Comma-separated file name must be a string')
		if os.path.exists(self.current_file_name) is False:
			raise IOError('Comma-separated file {0} could not be found)'.format(name))

	def data_filter(self, *fdef):
		"""
		Sets or returns the data filter

		:param	fdef:	filter definition
		:type	fdef:	dictionary
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Filter definition must be a dictionary)

		.. note:: The filter definition dictionary consists of a series of key-value pairs. For each key-value pair, the filter key is a column name in the comma-separated file; all rows which cointain the specified filter value \
		for the specified filter column are going to be kept for that particular key-value pair. The overall data set is the intersection of all the filter dictionary key-value data sets.

		"""
		if len(fdef) == 0:
			return self.current_data_filter
		if len(fdef) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_data_filter = fdef[0]
		if self.current_data_filter is not None:
			if isinstance(self.current_data_filter, dict) is False:
				raise TypeError('Filter definition must be a dictionary')

	def indep_col_label(self, *label):
		"""
		Sets or returns the independent variable column label

		:param	label:	independent variable column label
		:type	label:	string
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Independent variable column label must be a string)
		"""
		if len(label) == 0:
			return self.current_indep_col_label
		if len(label) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_indep_col_label = label[0]
		if isinstance(self.current_indep_col_label, str) is False:
			raise TypeError('Independent variable column label must be a string')

	def dep_col_label(self, *label):
		"""
		Sets or returns the dependent variable column label

		:param	label:	dependent variable column label
		:type	label:	string
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Dependent variable column label must be a string)
		"""
		if len(label) == 0:
			return self.current_dep_col_label
		if len(label) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_dep_col_label = label[0]
		if isinstance(self.current_dep_col_label, str) is False:
			raise TypeError('Dependent variable column label must be a string')

	def indep_min(self, *num):
		"""
		Sets or returns the minimum independent variable limit

		:param	num:	minimum independent variable limit
		:type	num:	number
		:rtype:			number
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Minimum independent variable limit must be number)
		"""
		if len(num) == 0:
			return self.current_indep_min
		if len(num) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_indep_min = num[0]
		if self.current_indep_min is not None:
			if util_misc.isnumber(self.current_indep_min) is False:
				raise TypeError('Minimum independent variable limit must be number')
			self.current_indep_min = float(self.current_indep_min)

	def indep_max(self, *num):
		"""
		Sets or returns the maximum independent variable limit

		:param	num:	maximum independent variable limit
		:type	num:	number
		:rtype:			number
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Maximum independent variable limit must be number)
		"""
		if len(num) == 0:
			return self.current_indep_max
		if len(num) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_indep_max = num[0]
		if self.current_indep_max is not None:
			if util_misc.isnumber(self.current_indep_max) is False:
				raise TypeError('Maximum independent variable limit must be number')
			self.current_indep_max = float(self.current_indep_max)

	def processing_function(self, *fproc):
		"""
		Sets or returns the data processing function pointer

		:param	fproc:	processing function
		:type	fproc:	function pointer
		:rtype:			function pointer
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Processing function parameter must be a function pointer)

		.. note::
		   The processing function is useful to do "light" data massaging, like scaling, etc; it is called after the data has been retrieved from the comma-separated value and the resulting filtered data set has been \
		   thresholded by **indep_var_min** and **dep_var_min** (if applicable).

		   The processing function is given two arguments, a Numpy vector representing the independent variable array (first argument) and a \
		   Numpy vector representing the dependent variable array (second argument). The expected return value is a two-element Numpy vector tuple, its first element being the processed independent variable array, and the second \
		   element being the processed dependent variable array.
		"""
		if len(fproc) == 0:
			return self.current_fproc
		if len(fproc) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_fproc = fproc[0]
		if self.current_fproc is not None:
			if hasattr(self.current_fproc, '__call__') is False:
				raise TypeError('Processing function parameter msut be a function pointer')

	def processing_function_extra_arguments(self, *eargs):	#pylint: disable-msg=C0103
		"""
		Sets or returns the extra arguments for the data processing function

		:param	eargs:	extra arguments
		:type	eargs:	dictionary
		:rtype:			dictionary
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Processing function extra arguments must be a dictionary)

		.. note::
		   Extra parameters can be passed to the processing function using **fproc_eargs**. For example, if **fproc_eargs** is ``{'par1':5, 'par2':[1, 2, 3]}`` then a valid processing function would be::

		       def my_proc_func(indep_var, dep_var, par1, part):
		           # Do some data processing
		           return indep_var, dep_var
		"""
		if len(eargs) == 0:
			return self.current_fproc_eargs
		if len(eargs) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_fproc_eargs = eargs[0]
		if self.current_fproc_eargs is not None:
			if isinstance(self.current_fproc_eargs, dict) is False:
				raise TypeError('Processing function extra arguments must be a dictionary')

	def indep_var(self):
		"""
		Returns the independent variable data (if loaded)

		:rtype:		Numpy vector
		:raises:	RuntimeError (No independent variable data set loaded)
		"""
		if self.current_indep_var is None:
			raise RuntimeError('No independent variable data set loaded')
		else:
			return self.current_indep_var

	def dep_var(self):
		"""
		Returns the independent variable data (if loaded)

		:rtype:		Numpy vector
		:raises:	RuntimeError (No dependent variable data set loaded)
		"""
		if self.current_dep_var is None:
			raise RuntimeError('No dependent variable data set loaded')
		else:
			return self.current_dep_var

	def load_data(self):	#pylint: disable-msg=R0912,R0915
		"""
		Retrieves data from file based on specified parameters

		:raises:
		 * RuntimeError (Filter column *[column header]* not found in comma-separated file *[file name]* header)

		 * RuntimeError (Filtered independent variable data set is empty)

		 * ValueError (Independent data set element *[index]* (*[value]*) is not a number)

		 * RuntimeError (Filtered dependent variable data set is empty)

		 * ValueError (Dependent data set element *[index]* (*[value]*) is not a number)

		 * RuntimeError (Illegal number of parameters returned by processing function)

		 * RuntimeError (Independent variable data set is empty after external function processing)

		 * ValueError (Independent data set element *[index]* (*[value]*) is not a number after external function processing)

		 * RuntimeError (Dependent variable data set is empty after external function processing)

		 * ValueError (Dependent data set element *[index]* (*[value]*) is not a number after external function processing)

		 * RuntimeError (Size of independent and dependent data sets is not the same after external function processing)

		 * RuntimeError (Independent variable data set is empty after **indep_min** thresholding)

		 * RuntimeError (Dependent variable data set is empty after **indep_min** thresholding)

		 * RuntimeError (Independent variable data set is empty after **indep_max** thresholding)

		 * RuntimeError (Dependent variable data set is empty after **indep_max** thresholding)
		"""
		if self._complete() is True:
			csv_obj = util_csv.CsvFile(self.file_name())
			# Apply CSV data filters
			if (self.data_filter() is not None) and (len(self.data_filter()) > 0):
				for col in self.data_filter():
					if col.upper() not in csv_obj.header():
						raise RuntimeError('Filter column {0} not found in comma-separated file {1} header'.format(col, self.file_name()))
				csv_obj.set_filter(self.data_filter())
			else:
				csv_obj.reset_filter()
			# Retrieve data and check data integrity
			self.current_indep_var = numpy.array(csv_obj.filtered_data(self.indep_col_label()))
			if len(self.current_indep_var) == 0:
				raise RuntimeError('Filtered independent variable data set is empty')
			for index, num in enumerate(self.current_indep_var):
				if util_misc.isnumber(num) is False:
					raise ValueError('Independent data set element {0} ({1}) is not a number'.format(index, num))
			self.current_dep_var = numpy.array(csv_obj.filtered_data(self.dep_col_label()))
			if len(self.current_dep_var) == 0:
				raise RuntimeError('Filtered dependent variable data set is empty')
			for index, num in enumerate(self.current_dep_var):
				if util_misc.isnumber(num) is False:
					raise ValueError('Dependent data set element {0} ({1}) is not a number'.format(index, num))
			# Flip data if it is in descending order (affects interpolation)
			if self.current_indep_var[0] > self.current_indep_var[-1]:
				self.current_indep_var = self.current_indep_var[::-1]
				self.current_dep_var = self.current_dep_var[::-1]
			# Apply minimum/maximum global filters
			if self.processing_function() is not None:
				if self.processing_function_extra_arguments() is None:
					ret = self.processing_function()(self.current_indep_var, self.current_dep_var)
				else:
					ret = self.processing_function()(self.current_indep_var, self.current_dep_var, **self.processing_function_extra_arguments())
				if len(ret) != 2:
					raise RuntimeError('Illegal number of parameters returned by processing function')
				self.current_indep_var = ret[0]
				self.current_dep_var = ret[1]
				# Check data integrity after external processing
				if len(self.current_indep_var) == 0:
					raise RuntimeError('Independent variable data set is empty after external function processing')
				for index, num in enumerate(self.current_indep_var):
					if util_misc.isnumber(num) is False:
						raise ValueError('Independent data set element {0} ({1}) is not a number after external function processing'.format(index, num))
				if len(self.current_dep_var) == 0:
					raise RuntimeError('Dependent variable data set is empty after external function processing')
				for index, num in enumerate(self.current_dep_var):
					if util_misc.isnumber(num) is False:
						raise ValueError('Dependent data set element {0} ({1}) is not a number after external function processing'.format(index, num))
				if len(self.current_indep_var) != len(self.current_dep_var):
					raise RuntimeError('Size of independent and dependent data sets is not the same after external function processing')
			if self.current_indep_min is not None:
				self.current_indep_var, self.current_dep_var = _series_threshold(self.current_indep_var, self.current_dep_var, self.current_indep_min, 'MIN')
			if len(self.current_indep_var) == 0:
				raise RuntimeError('Independent variable data set is empty after indep_min thresholding')
			if len(self.current_dep_var) == 0:
				raise RuntimeError('Dependent variable data set is empty after indep_min thresholding')
			if self.current_indep_max is not None:
				self.current_indep_var, self.current_dep_var = _series_threshold(self.current_indep_var, self.current_dep_var, self.current_indep_max, 'MAX')
			if len(self.current_indep_var) == 0:
				raise RuntimeError('Independent variable data set is empty after indep_max thresholding')
			if len(self.current_dep_var) == 0:
				raise RuntimeError('Dependent variable data set is empty after indep_max thresholding')

	def __str__(self):
		"""
		Print comma-separated value source information
		"""
		ret = ''
		ret += 'File name: {0}\n'.format(self.file_name())
		ret += 'Data filter: {0}\n'.format('None' if self.data_filter() is None else '')
		if self.data_filter() is not None:
			for key, value in self.data_filter().iteritems():
				ret += '   {0}: {1}\n'.format(key, value)
		ret += 'Independent column label: {0}\n'.format(self.indep_col_label())
		ret += 'Dependent column label: {0}\n'.format(self.dep_col_label())
		ret += 'Independent variable minimum: {0}\n'.format(self.indep_min())
		ret += 'Independent variable maximum: {0}\n'.format(self.indep_max())
		ret += 'Processing function: {0}\n'.format('None' if self.processing_function() is None else self.processing_function().__name__)
		ret += 'Independent variable: '
		try:
			ret += str(self.indep_var())+'\n'
		except:	#pylint: disable-msg=W0702
			ret += 'None\n'
		ret += 'Dependent variable: '
		try:
			ret += str(self.dep_var())
		except:	#pylint: disable-msg=W0702
			ret += 'None'
		return ret

	def _complete(self):
		"""
		Returns True if object is fully specified, otherwise returns False
		"""
		return True if (self.file_name() is not None) and (self.indep_col_label() is not None) and (self.dep_col_label() is not None) else False


class Series(object):	#pylint: disable-msg=R0902
	"""
	Specifies a series within a panel

	:param	data_source:	data source object
	:type	data_source:	:py:class:`util_plot.RawSource()` object or :py:class:`util_plot.CsvSource()` object or others conforming to the data source specification
	:param	label:			series label
	:type	label:			string
	:param	color:			series color
	:type	color:			Matplotlib color
	:param	marker:			plot data markers flag
	:type	marker:			boolean
	:param	interp:			interpolation option, one of NONE, STRAIGHT, STEP, CUBIC or LINREG (case insensitive)
	:type	interp:			string
	:param	line_style:		line style, one of `-`, `--`, `-.` or `:`
	:type	line_style:		Matplotlib line specification
	:param	secondary_axis:	secondary axis flag
	:type	secondary_axis:	boolean
	:raises:
	 * Same as :py:meth:`util_plot.Series.data_source()`

	 * Same as :py:meth:`util_plot.Series.label()`

	 * Same as :py:meth:`util_plot.Series.color()`

	 * Same as :py:meth:`util_plot.Series.marker()`

	 * Same as :py:meth:`util_plot.Series.interp()`

	 * Same as :py:meth:`util_plot.Series.line_style()`

	 * Same as :py:meth:`util_plot.Series.secondary_axis()`
	"""
	def __init__(self, data_source, label, color='k', marker=True, interp='CUBIC', line_style='-', secondary_axis=False):	#pylint: disable-msg=R0913
		self.interp_options = ['NONE', 'STRAIGHT', 'STEP', 'CUBIC', 'LINREG']
		self.scaled_interp_curve_indep_var = None
		self.scaled_interp_curve_dep_var = None
		self.scaled_indep_var = None
		self.scaled_dep_var = None
		self.interp_curve_indep_var = None
		self.interp_curve_dep_var = None
		self.current_data_source = None
		self.current_label = None
		self.current_color = None
		self.current_marker = None
		self.current_interp = None
		self.current_line_style = None
		self.current_secondary_axis = None
		self.current_indep_var = None
		self.current_dep_var = None
		self.data_source(data_source)
		self.label(label)
		self.color(color)
		self.marker(marker)
		self.interp(interp)
		self.line_style(line_style)
		self.secondary_axis(secondary_axis)

	def data_source(self, *data_source):
		"""
		Sets or returns data set source object. The independent and dependent data sets are obtained once the data source is set.

		:param	data_source:	data source object
		:type	data_source:	:py:class:`util_plot.RawSource()` object, :py:class:`util_plot.CsvSource()` object or others conforming to the data source specification
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * RuntimeError (Data source object does not have indep_var() method)

		 * RuntimeError (Data source object does not have dep_var() method)

		 * RuntimeError (Data source object is not fully specified)

		 * Same as :py:meth:`util_plot.RawSource.indep_var()` or :py:meth:`util_plot.CsvSource.indep_var()` or exceptions thrown by custom data source class while handling independent variable retrieval

		 * Same as :py:meth:`util_plot.RawSource.dep_var()` or :py:meth:`util_plot.CsvSource.dep_var()` or exceptions thrown by custom data source class while handling dependent variable retrieval

		.. note:: The data source object must have ``indep_var()`` and ``dep_var()`` methods returning Numpy vectors to be valid.

		"""
		if len(data_source) == 0:
			return self.current_data_source
		if len(data_source) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_data_source = data_source[0]
		for method in ['indep_var', 'dep_var']:
			if method not in dir(self.current_data_source):
				raise RuntimeError('Data source object does not have {0}() method'.format(method))
		if self.current_data_source._complete() is False:	#pylint: disable-msg=W0212
			raise RuntimeError('Data source object is not fully specified')
		self.indep_var(self.current_data_source.indep_var())
		self.dep_var(self.current_data_source.dep_var())
		self._calculate_curve()

	def indep_var(self, *vector):
		"""
		Sets or returns the independent variable data (if loaded)

		:param	vector:	independent array vector
		:type	vector:	Numpy array
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * RuntimeError (Independent variable data set needs to be a Numpy vector)

		 * RuntimeError (ndependent variable data set needs to be a vector)

		 * RuntimeError (Independent variable data set is empty)

		 * RuntimeError (Independent data set element *[number]* (*[value]*) is not a number)
		"""
		if len(vector) == 0:
			return self.current_indep_var
		if len(vector) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_indep_var = vector[0]
		try:
			if len(self.current_indep_var.shape) > 1:
				raise RuntimeError('Independent variable data set needs to be a vector')
		except:
			raise RuntimeError('Independent variable data set needs to be a Numpy vector')
		if len(self.current_indep_var) == 0:
			raise RuntimeError('Independent variable data set is empty')
		for index, num in enumerate(self.current_indep_var):
			if util_misc.isnumber(num) is False:
				raise ValueError('Independent data set element {0} ({1}) is not a number'.format(index, num))
		self._calculate_curve()

	def dep_var(self, *vector):
		"""
		Sets or returns the dependent variable data (if loaded)

		:param	vector:	dependent array vector
		:type	vector:	Numpy array
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * RuntimeError (Dependent variable data set needs to be a Numpy vector)

		 * RuntimeError (Dependent variable data set needs to be a vector)

		 * RuntimeError (Dependent variable data set is empty)

		 * RuntimeError (Dependent data set element *[number]* (*[value]*) is not a number)
		"""
		if len(vector) == 0:
			return self.current_dep_var
		if len(vector) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_dep_var = vector[0]
		try:
			if len(self.current_dep_var.shape) > 1:
				raise RuntimeError('Dependent variable data set needs to be a vector')
		except:
			raise RuntimeError('Dependent variable data set needs to be a Numpy vector')
		if len(self.current_dep_var) == 0:
			raise RuntimeError('Dependent variable data set is empty')
		for index, num in enumerate(self.current_dep_var):
			if util_misc.isnumber(num) is False:
				raise ValueError('Dependent data set element {0} ({1}) is not a number'.format(index, num))
		self._calculate_curve()

	def interp_indep_var(self):
		"""
		Returns the (scaled) independent variable of the interpolated curve
		"""
		return self.scaled_interp_curve_indep_var

	def interp_dep_var(self):
		"""
		Returns the (scaled) dependent variable of the interpolated curve
		"""
		return self.scaled_interp_curve_dep_var

	def label(self, *text):
		"""
		Sets or returns the series label

		:param	text:	series label
		:type	text:	string
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Series label must be a string)
		"""
		if len(text) == 0:
			return self.current_label
		if len(text) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_label = text[0]
		if isinstance(self.current_label, str) is False:
			raise TypeError('Series label must be a string')

	def color(self, *spec):	#pylint: disable-msg=R0912
		"""
		Sets or returns the series color

		:param	spec:	series color
		:type	spec:	Matplotlib color
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Invalid color specification)
		"""
		if len(spec) == 0:
			return self.current_color
		if len(spec) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_color = spec[0]
		if isinstance(self.current_color, str) is True:
			valid_html_colors = ['aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'black', 'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue',
						'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkkhaki', 'darkmagenta',
						'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue',
						'dimgray', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'honeydew',
						'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan',
						'lightgoldenrodyellow', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightsteelblue', 'lightyellow', 'lime', 'limegreen',
						'linen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred',
						'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen',
						'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen',
						'seashell', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquois', 'violet', 'wheat', 'white', 'whitesmoke',
						'yellow', 'yellowgreen']
			self.current_color = self.current_color.strip()
			valid_color_spec = True if (len(self.current_color) == 1) and (self.current_color in 'bgrcmykw') else False	# Basic built-in colors
			valid_color_spec = True if (valid_color_spec is True) or (valid_html_colors.index(self.current_color.lower()) != -1) else False	# HTML colors
			if valid_color_spec is False:	# Grayscale format
				try:
					value = float(self.current_color)
					valid_color_spec = True if (value >= 0.0) and (value <= 1.0) else False
				except:	#pylint: disable-msg=W0702
					pass
			if (valid_color_spec is False) and (self.current_color[0] == '#') and (len(self.current_color) == 7):	# HTML hex string
				for char in self.current_color:
					if util_misc.ishex(char) is False:
						break
				else:
					valid_color_spec = True
		elif ((isinstance(self.current_color, list) is True) or (isinstance(self.current_color, set) is True) or (isinstance(self.current_color, tuple) is True)) and \
			((len(self.current_color) == 3) or (len(self.current_color) == 4)):	# RGB or RGBA tuple
			valid_color_spec = True
			for num in range(len(self.current_color)):
				if (isinstance(self.current_color[num], float) is False) or ((isinstance(self.current_color[num], float) is True) and ((self.current_color[num] < 0.0) or (self.current_color[num] > 1.0))):
					valid_color_spec = False
					break
		if valid_color_spec is False:
			raise TypeError('Invalid color specification')

	def marker(self, *flag):
		"""
		Sets or returns the plot data markers flag

		:param	flag:	plot data markers flag
		:type	flag:	boolean
		:rtype:			boolean
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Plot markers flag must be boolean)
		"""
		if len(flag) == 0:
			return self.current_marker
		if len(flag) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_marker = flag[0]
		if isinstance(self.current_marker, bool) is False:
			raise TypeError('Marker flag must be boolean')

	def interp(self, *option):
		"""
		Sets or returns the interpolation option

		:param	option:	interpolation option, one of NONE, STRAIGHT, CUBIC or LINREG (case insensitive)
		:type	option:	string
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Interpolation option is not a string)

		 * ValueError (Interpolation option not one of NONE, STRAIGHT, STEP, CUBIC or LINREG)
		"""
		if len(option) == 0:
			return self.current_interp
		if len(option) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_interp = option[0]
		if isinstance(self.current_interp, str) is False:
			raise TypeError('Interpolation option is not a string')
		self.current_interp = self.current_interp.upper()
		if self.current_interp not in self.interp_options:
			raise ValueError('Interpolation option not one of NONE, STRAIGHT, STEP, CUBIC or LINREG')
		self._calculate_curve()

	def line_style(self, *style):
		"""
		Sets or returns the line style

		:param	style:	line style, one of `-`, `--`, `-.` or `:`
		:type	style:	Matplotlib line specification
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Line style must be a string)

		 * ValueError (Illegal line style specification)
		"""
		if len(style) == 0:
			return self.current_line_style
		if len(style) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_line_style = style[0]
		if isinstance(self.current_line_style, str) is False:
			raise TypeError('Line style must be a string')
		self.current_line_style = self.current_line_style.strip()
		if (self.current_line_style != '') and (self.current_line_style != '-') and (self.current_line_style != '--') and (self.current_line_style != '-.') and (self.current_line_style != ':'):
			raise ValueError('Illegal line style specification')

	def secondary_axis(self, *flag):
		"""
		Sets or returns the secondary axis flag

		:param	flag:	secondary axis flag
		:type	flag:	boolean
		:rtype:			boolean
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Secondary axis flag must be boolean)
		"""
		if len(flag) == 0:
			return self.current_secondary_axis
		if len(flag) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_secondary_axis = flag[0]
		if isinstance(self.current_secondary_axis, bool) is False:
			raise TypeError('Secondary axis flag must be boolean')

	def __str__(self):
		"""
		Print series object information
		"""
		ret = ''
		ret += 'Data source: {0}{1} class object\n'.format(None if self.data_source() is None else self.data_source().__module__, '' if self.data_source() is None else '.'+self.data_source().__class__.__name__)
		ret += 'Independent variable: {0}\n'.format(self.indep_var())
		ret += 'Dependent variable: {0}\n'.format(self.dep_var())
		ret += 'Label: {0}\n'.format(self.label())
		ret += 'Color: {0}\n'.format(self.color())
		ret += 'Marker: {0}\n'.format(self.marker())
		ret += 'Interpolation: {0}\n'.format(self.interp())
		ret += 'Line style: {0}\n'.format(self.line_style())
		ret += 'Secondary axis: {0}'.format(self.secondary_axis())
		return ret

	def _complete(self):
		"""
		Returns True if series is fully specified, otherwise returns False
		"""
		return True if (self.current_indep_var is not None) and (self.current_dep_var is not None) and (self.current_data_source is not None) else False

	def _calculate_curve(self):
		"""
		Compute curve to interpolate between data points
		"""
		if (self.interp() != 'NONE') and (self.current_indep_var is not None) and (self.current_dep_var is not None):
			if self.interp() == 'CUBIC':
				self.interp_curve_indep_var = numpy.linspace(min(self.current_indep_var), max(self.current_indep_var), 500)  #pylint: disable-msg=E1101
				finterp = interp1d(self.current_indep_var, self.current_dep_var, kind='cubic')
				self.interp_curve_dep_var = finterp(self.interp_curve_indep_var)
			elif self.interp() == 'LINREG':
				slope, intercept, r_value, p_value, std_err = stats.linregress(self.current_indep_var, self.current_dep_var)	#pylint: disable-msg=W0612
				self.interp_curve_indep_var = self.current_indep_var
				self.interp_curve_dep_var = intercept+(slope*self.current_indep_var)

	def _scale_indep_var(self, scaling_factor):
		"""
		Scale independent variable
		"""
		self.scaled_indep_var = self.indep_var()/scaling_factor
		if self.interp_curve_indep_var is not None:
			self.scaled_interp_curve_indep_var = self.interp_curve_indep_var/scaling_factor

	def _scale_dep_var(self, scaling_factor):
		"""
		Scale dependent variable
		"""
		self.scaled_dep_var = self.dep_var()/scaling_factor
		if self.interp_curve_dep_var is not None:
			self.scaled_interp_curve_dep_var = self.interp_curve_dep_var/scaling_factor

	def _legend_artist(self, legend_scale=1.5):
		"""
		Creates artist (marker -if used- and line style -if used-)
		"""
		return plt.Line2D((0, 1), (0, 0), color=self.color(), marker='o' if self.marker() is True else '', linestyle=self.line_style() if (self.line_style() != '') and (self.interp() != 'NONE') else '',
					linewidth=(2.5 if (self.line_style() != '') and (self.interp() != 'NONE') else 0.0)/legend_scale, markeredgecolor=self.color(), markersize=14/legend_scale,
					markeredgewidth=5/legend_scale, markerfacecolor='w')

	def _draw_series(self, axarr, log_indep, log_dep):
		"""
		Draw series
		"""
		label_printed = False
		fplot = axarr.plot if (log_indep is False) and (log_dep is False) else (axarr.semilogx if (log_indep is True) and (log_dep is False) else (axarr.loglog if (log_indep is True) and (log_dep is True) else axarr.semilogy))
		if (self.interp() == 'CUBIC') or (self.interp() == 'LINREG') and (self.line_style() != ''):
			fplot(self.scaled_interp_curve_indep_var, self.scaled_interp_curve_dep_var, color=self.color(), linestyle=self.line_style(), linewidth=2.5, label=self.label() if self.label() != '' else None)
			label_printed = True
		if (self.marker() is True) or ((self.marker() is False) and ((self.interp() == 'STRAIGHT') or (self.interp() == 'STEP')) and (self.line_style() != '')):
			fplot(self.scaled_indep_var, self.scaled_dep_var, color=self.color(), linestyle=self.line_style() if (self.line_style() != '') and ((self.interp() == 'STRAIGHT') or (self.interp() == 'STEP')) else '',
				  marker='o' if self.marker() is True else '', markeredgecolor=self.color(), markersize=14, markeredgewidth=5, markerfacecolor='w',
				  linewidth=2.5 if (self.line_style() != '') and ((self.interp() == 'STRAIGHT') or (self.interp() == 'STEP')) else 0, drawstyle='steps-post' if self.interp() == 'STEP' else 'default',
				  label=None if (label_printed is True) or (self.label() == '') else self.label())

class Panel(object):	#pylint: disable-msg=R0902
	"""
	Defines properties of a panel within a figure

	:param	series:					one or more data series
	:type	series:					:py:class:`util_plot.Series()` object or list of :py:class:`util_plot.Series()` objects
	:param	primary_axis_label:		primary axis label
	:type	primary_axis_label:		string
	:param	primary_axis_units:		primary dependent axis units
	:type	primary_axis_units:		string
	:param	secondary_axis_label:	secondary dependent axis label
	:type	secondary_axis_label:	string
	:param	secondary_axis_units:	secondary dependent axis units
	:type	secondary_axis_units:	string
	:param	log_dep_axis:			logarithmic dependent (primary and/or secondary) axis flag
	:type	log_dep_axis:			boolean
	:param	legend_props:			legend properties. See :py:meth:`util_plot.Panel.legend_props()`
	:type	legend_props:			dictionary
	:raises:
	 * Same as :py:meth:`util_plot.Panel.add_series()`

	 * Same as :py:meth:`util_plot.Panel.primary_axis_label()`

	 * Same as :py:meth:`util_plot.Panel.primary_axis_units()`

	 * Same as :py:meth:`util_plot.Panel.log_dep_axis()`

	 * Same as :py:meth:`util_plot.Panel.secondary_axis_label()`

	 * Same as :py:meth:`util_plot.Panel.secondary_axis_units()`

	 * Same as :py:meth:`util_plot.Panel.legend_props()`
	"""
	def __init__(self, series=None, primary_axis_label='', primary_axis_units='', secondary_axis_label='', secondary_axis_units='', log_dep_axis=False, legend_props=dict()):	#pylint: disable-msg=W0102,R0913
		self.legend_pos_list = ['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center']
		self.panel_has_primary_axis = False
		self.panel_has_secondary_axis = False
		self.primary_dep_var_min = None
		self.primary_dep_var_max = None
		self.primary_dep_var_div = None
		self.primary_dep_var_unit_scale = None
		self.primary_scaled_dep_var = None
		self.primary_dep_var_locs = None
		self.primary_dep_var_labels = None
		self.secondary_dep_var_min = None
		self.secondary_dep_var_max = None
		self.secondary_dep_var_div = None
		self.secondary_dep_var_unit_scale = None
		self.secondary_scaled_dep_var = None
		self.secondary_dep_var_locs = None
		self.secondary_dep_var_labels = None
		self.legend_props_list = ['pos', 'cols']
		self.current_series_list = list()
		self.current_primary_axis_label = None
		self.current_primary_axis_units = None
		self.current_secondary_axis_label = None
		self.current_secondary_axis_units = None
		self.current_legend_props = None
		self.current_log_dep_axis = False
		self.add_series(series)
		self.primary_axis_label(primary_axis_label)
		self.primary_axis_units(primary_axis_units)
		self.secondary_axis_label(secondary_axis_label)
		self.secondary_axis_units(secondary_axis_units)
		self.log_dep_axis(log_dep_axis)
		self.legend_props(legend_props)

	def series(self):	#pylint: disable-msg=R0912,R0915
		"""
		Returns the data series objects attached to the panel

		:rtype:			:py:class:`util_plot.Series()` object or list of :py:class:`util_plot.Series()` objects
		"""
		return self.current_series_list

	def add_series(self, series):	#pylint: disable-msg=R0912,R0915
		"""
		Adds data series to panel

		:param	series: one or more data series
		:type	series:	:py:class:`util_plot.Series()` object or list of :py:class:`util_plot.Series()` objects
		:rtype:			:py:class:`util_plot.Series()` object or list of :py:class:`util_plot.Series()` objects
		:raises:
		 * RuntimeError (Series in panel have incongruent primary and secondary axis)

		 * TypeError (Series element is not a Series object)

		 * RuntimeError (Series element *[index]* is not fully specified)
		"""
		if series is not None:
			series = [series] if isinstance(series, Series) is True else series
			for num, obj in enumerate(series):
				if isinstance(obj, Series) is False:
					raise TypeError('Series element is not a Series object')
				elif obj._complete() is False:	#pylint: disable-msg=W0212
					raise RuntimeError('Series element {0} is not fully specified'.format(num))
			if len(self.current_series_list) == 0:
				self.current_series_list = series
			else:
				for new_obj in series:
					for old_obj in self.current_series_list:
						if new_obj == old_obj:
							break
					else:
						self.current_series_list.append(new_obj)
			# Compute panel scaling factor
			global_primary_dep_var = list()
			global_secondary_dep_var = list()
			# Find union of the dependent variable data set of all panels
			for series_obj in self.current_series_list:
				if series_obj.secondary_axis() is False:
					self.panel_has_primary_axis = True
					global_primary_dep_var = numpy.unique(numpy.append(global_primary_dep_var, numpy.array([util_misc.smart_round(element, 10) for element in series_obj.dep_var()])))
					if series_obj.interp_curve_dep_var is not None:
						global_primary_dep_var = numpy.unique(numpy.append(global_primary_dep_var, numpy.array([util_misc.smart_round(element, 10) for element in series_obj.interp_curve_dep_var])))
				else:
					self.panel_has_secondary_axis = True
					global_secondary_dep_var = numpy.unique(numpy.append(global_secondary_dep_var, numpy.array([util_misc.smart_round(element, 10) for element in series_obj.dep_var()])))
					if series_obj.interp_curve_dep_var is not None:
						global_secondary_dep_var = numpy.unique(numpy.append(global_secondary_dep_var, numpy.array([util_misc.smart_round(element, 10) for element in series_obj.interp_curve_dep_var])))
			# Primary axis
			if self.panel_has_primary_axis is True:
				self.primary_dep_var_min, self.primary_dep_var_max, self.primary_dep_var_div, self.primary_dep_var_unit_scale, self.primary_scaled_dep_var = \
					_scale_series(series=global_primary_dep_var, scale=True, scale_type='delta')
				self.primary_dep_var_min = util_misc.smart_round(self.primary_dep_var_min, 10)
				self.primary_dep_var_max = util_misc.smart_round(self.primary_dep_var_max, 10)
				self.primary_dep_var_locs, self.primary_dep_var_labels, self.primary_dep_var_min, self.primary_dep_var_max = \
					_intelligent_ticks(self.primary_scaled_dep_var, min(self.primary_scaled_dep_var), max(self.primary_scaled_dep_var), tight=False)
			# Secondary axis
			if self.panel_has_secondary_axis is True:
				self.secondary_dep_var_min, self.secondary_dep_var_max, self.secondary_dep_var_div, self.secondary_dep_var_unit_scale, self.secondary_scaled_dep_var = \
					_scale_series(series=global_secondary_dep_var, scale=True, scale_type='delta')
				self.secondary_dep_var_min = util_misc.smart_round(self.secondary_dep_var_min, 10)
				self.secondary_dep_var_max = util_misc.smart_round(self.secondary_dep_var_max, 10)
				self.secondary_dep_var_locs, self.secondary_dep_var_labels, self.secondary_dep_var_min, self.secondary_dep_var_max = \
					_intelligent_ticks(self.secondary_scaled_dep_var, min(self.secondary_scaled_dep_var), max(self.secondary_scaled_dep_var), tight=False)
			# Equalize number of ticks on primary and secondary axis so that ticks are in the same percentage place within the dependent variable plotting interval
			if (self.panel_has_primary_axis is True) and (self.panel_has_secondary_axis is True):
				max_ticks = max(len(self.primary_dep_var_locs), len(self.secondary_dep_var_locs))-1
				primary_delta = (self.primary_dep_var_locs[-1]-self.primary_dep_var_locs[0])/float(max_ticks)
				secondary_delta = (self.secondary_dep_var_locs[-1]-self.secondary_dep_var_locs[0])/float(max_ticks)
				primary_start = self.primary_dep_var_locs[0]
				secondary_start = self.secondary_dep_var_locs[0]
				self.primary_dep_var_locs = list()
				self.secondary_dep_var_locs = list()
				for num in range(max_ticks+1):
					self.primary_dep_var_locs.append(primary_start+(num*primary_delta))
					self.secondary_dep_var_locs.append(secondary_start+(num*secondary_delta))
				self.primary_dep_var_locs, self.primary_dep_var_labels = _uniquify_tick_labels(self.primary_dep_var_locs, self.primary_dep_var_locs[0], self.primary_dep_var_locs[-1])
				self.secondary_dep_var_locs, self.secondary_dep_var_labels = _uniquify_tick_labels(self.secondary_dep_var_locs, self.secondary_dep_var_locs[0], self.secondary_dep_var_locs[-1])
			#
			self._scale_dep_var(self.primary_dep_var_div, self.secondary_dep_var_div)

	def primary_axis_label(self, *label):
		"""
		Sets or returns the primary axis label

		:param	label:	primary axis label
		:type	label:	string
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Primary axis label must be a string)
		"""
		if len(label) == 0:
			return self.current_primary_axis_label
		if len(label) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_primary_axis_label = label[0]
		if isinstance(self.current_primary_axis_label, str) is False:
			raise TypeError('Primary axis label must be a string')
		self.current_primary_axis_label = self.current_primary_axis_label.strip()

	def primary_axis_units(self, *units):
		"""
		Sets or returns the primary axis units

		:param	units:	primary axis units
		:type	units:	string
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Primary axis units must be a string)
		"""
		if len(units) == 0:
			return self.current_primary_axis_units
		if len(units) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_primary_axis_units = units[0]
		if isinstance(self.current_primary_axis_units, str) is False:
			raise TypeError('Primary axis units must be a string')
		self.current_primary_axis_units = self.current_primary_axis_units.strip()

	def log_dep_axis(self, *flag):
		"""
		Sets or returns the logarithmic dependent (primary and/or secondary) axis flag

		:param	flag:	logarithmic dependent (primary and/or secondary) axis flag
		:type	flag:	boolean
		:rtype:			boolean
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Logarthmic dependent (primary and/or secondary) axis flag must be boolean)
		"""
		if len(flag) == 0:
			return self.current_log_dep_axis
		if len(flag) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_log_dep_axis = flag[0]
		if isinstance(self.current_log_dep_axis, bool) is False:
			raise TypeError('Logarthmic dependent (primary and/or secondary) axis flag must be boolean')

	def secondary_axis_label(self, *label):
		"""
		Sets or returns the secondary axis label

		:param	label:	secondary axis label
		:type	label:	string
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Secondary axis label must be a string)
		"""
		if len(label) == 0:
			return self.current_secondary_axis_label
		if len(label) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_secondary_axis_label = label[0]
		if isinstance(self.current_secondary_axis_label, str) is False:
			raise TypeError('Secondary axis label must be a string')
		self.current_secondary_axis_label = self.current_secondary_axis_label.strip()

	def secondary_axis_units(self, *units):
		"""
		Sets or returns the secondary axis units

		:param	units:	secondary axis units
		:type	units:	string
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Secondary axis units must be a string)
		"""
		if len(units) == 0:
			return self.current_secondary_axis_units
		if len(units) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_secondary_axis_units = units[0]
		if isinstance(self.current_secondary_axis_units, str) is False:
			raise TypeError('Secondary axis units must be a string')
		self.current_secondary_axis_units = self.current_secondary_axis_units.strip()

	def legend_props(self, *props):
		"""
		Sets or returns the legend properties

		:param	props:	legend properties
		:type	props:	dictionary
		:rtype:			dictionary
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Legend properties must be a dictionary)

		 * ValueError (Illegal legend property *[prop]*)

		 * TypeError (Legend position has to be a string)

		 * ValueError (Illegal position specification)

		 * TypeError (Number of legend columns has to be a positive integer)

		.. note:: No legend is shown if a panel has only one series in it

		.. note:: Currently supported properties are

		     * **pos** (*string*) -- legend position, one of BEST, UPPER RIGHT, UPPER LEFT, LOWER LEFT, LOWER RIGHT, RIGHT, CENTER LEFT, CENTER RIGHT, LOWER CENTER, UPPER CENTER or CENTER (case insensitive).

		     * **cols** (integer) -- number of columns in the legend box
		"""
		if len(props) == 0:
			return self.current_legend_props
		if len(props) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_legend_props = props[0]
		if isinstance(self.current_legend_props, dict) is False:
			raise TypeError('Legend properties must be a dictionary')
		for key, value in self.current_legend_props.iteritems():
			if key not in self.legend_props_list:
				raise ValueError('Illegal legend property {0}'.format(key))
			elif (key == 'pos') and isinstance(value, str) is False:
				raise TypeError('Legend position has to be a string')
			elif (key == 'pos') and (value.lower() not in self.legend_pos_list):
				raise ValueError('Illegal position specification')
			elif ((key == 'cols') and (isinstance(value, int) is False)) or ((key == 'cols') and (isinstance(value, int) is True) and (value < 0)):
				raise TypeError('Number of legend columns has to be a positive integer')

	def __str__(self):
		"""
		Print panel information
		"""
		ret = ''
		if len(self.current_series_list) == 0:
			ret += 'Series: None\n'
		else:
			for num, element in enumerate(self.current_series_list):
				ret += 'Series {0}:\n'.format(num+1)
				temp = str(element).split('\n')
				temp = [3*' '+line for line in temp]
				ret += '\n'.join(temp)
				ret += '\n'
		ret += 'Primary axis label: {0}\n'.format(self.primary_axis_label())
		ret += 'Primary axis units: {0}\n'.format(self.primary_axis_units())
		ret += 'Secondary axis label: {0}\n'.format(self.secondary_axis_label())
		ret += 'Secondary axis units: {0}\n'.format(self.secondary_axis_units())
		ret += 'Logarithmic dependent axis: {0}\n'.format(self.log_dep_axis())
		if self.legend_props() is None:
			ret += 'Legend properties: None'
		else:
			ret += 'Legend properties\n'
			for num, (key, value) in enumerate(self.legend_props().iteritems()):
				ret += '   {0}: {1}{2}'.format(key, value, '\n' if num+1 < len(self.legend_props()) else '')
		return ret

	def _complete(self):
		"""
		Returns True if panel is fully specified, otherwise returns False
		"""
		return True if len(self.current_series_list) > 0 else False

	def _scale_indep_var(self, scaling_factor):
		"""
		Scale independent variable of panel series
		"""
		for series_obj in self.current_series_list:
			series_obj._scale_indep_var(scaling_factor)	#pylint: disable-msg=W0212

	def _scale_dep_var(self, primary_scaling_factor, secondary_scaling_factor):
		"""
		Scale dependent variable of panel series
		"""
		for series_obj in self.current_series_list:
			if series_obj.secondary_axis() is False:
				series_obj._scale_dep_var(primary_scaling_factor)	#pylint: disable-msg=W0212
			else:
				series_obj._scale_dep_var(secondary_scaling_factor)	#pylint: disable-msg=W0212

	def _draw_panel(self, fig, axarr, indep_axis_dict=None):	#pylint: disable-msg=R0912,R0914,R0915
		"""
		Drawa panel series
		"""
		if self.panel_has_secondary_axis is True:
			axarr_sec = axarr.twinx()
		# Place data series in their appropriate axis (primary or secondary)
		for series_obj in self.current_series_list:
			series_obj._draw_series(axarr if series_obj.secondary_axis() is False else axarr_sec, indep_axis_dict['log_indep'], self.log_dep_axis())	#pylint: disable-msg=W0212
		primary_height = 0
		secondary_height = 0
		indep_height = 0
		primary_width = 0
		secondary_width = 0
		indep_width = 0
		# Primary axis
		if self.panel_has_primary_axis is True:
			axarr.yaxis.grid(True, 'both')
			axarr.set_ylim((self.primary_dep_var_min, self.primary_dep_var_max), emit=True, auto=False)
			axarr.yaxis.set_ticks(self.primary_dep_var_locs)
			axarr.yaxis.set_ticklabels(self.primary_dep_var_labels)
			axarr.tick_params(axis='y', which='major', labelsize=14)
			# Calculate minimum pane height from primary axis
			primary_height = ((len(self.primary_dep_var_labels))+(len(self.primary_dep_var_labels)-1))*_get_text_prop(fig, axarr.yaxis.get_ticklabels()[0])['height']	# Minimum of one line spacing between ticks
			primary_width = max([_get_text_prop(fig, tick)['width'] for tick in axarr.yaxis.get_ticklabels()])
		else:
			axarr.yaxis.set_ticklabels([])
		if (self.primary_axis_label() != '') or (self.primary_axis_units() != ''):
			unit_scale = '' if self.primary_dep_var_unit_scale is None else self.primary_dep_var_unit_scale
			axarr.yaxis.set_label_text(self.primary_axis_label() + ('' if (unit_scale == '') and (self.primary_axis_units() == '') else \
				(' ['+unit_scale+('-' if self.primary_axis_units() == '' else self.primary_axis_units())+']')), fontdict={'fontsize':18})
			primary_height = max(primary_height, _get_text_prop(fig, axarr.yaxis.get_label())['height'])
			primary_width += 1.5*_get_text_prop(fig, axarr.yaxis.get_label())['width']
		# Secondary axis
		if self.panel_has_secondary_axis is True:
			axarr_sec.yaxis.grid(True, 'both')
			axarr_sec.set_ylim((self.secondary_dep_var_min, self.secondary_dep_var_max), emit=True, auto=False)
			axarr_sec.yaxis.set_ticks(self.secondary_dep_var_locs)
			axarr_sec.yaxis.set_ticklabels(self.secondary_dep_var_labels)
			axarr_sec.tick_params(axis='y', which='major', labelsize=14)
			# Calculate minimum pane height from primary axis
			secondary_height = ((len(self.secondary_dep_var_labels))+(len(self.secondary_dep_var_labels)-1))*_get_text_prop(fig, axarr_sec.yaxis.get_ticklabels()[0])['height']	# Minimum of one line spacing between ticks
			secondary_width = max([_get_text_prop(fig, tick)['width'] for tick in axarr.yaxis.get_ticklabels()])
		if (self.secondary_axis_label() != '') or (self.secondary_axis_units() != ''):
			unit_scale = '' if self.secondary_dep_var_unit_scale is None else self.secondary_dep_var_unit_scale
			axarr_sec.yaxis.set_label_text(self.secondary_axis_label() + ('' if (unit_scale == '') and (self.secondary_axis_units() == '') else \
				(' ['+unit_scale+('-' if self.secondary_axis_units() == '' else self.secondary_axis_units())+']')), fontdict={'fontsize':18})
			secondary_height = max(secondary_height, _get_text_prop(fig, axarr.yaxis.get_label())['height'])
			secondary_width += 1.5*_get_text_prop(fig, axarr.yaxis.get_label())['width']
		# Print legends
		if (len(self.current_series_list) > 1) and (len(self.legend_props()) > 0):
			primary_labels = []
			secondary_labels = []
			if self.panel_has_primary_axis is True:
				primary_handles, primary_labels = axarr.get_legend_handles_labels()	#pylint: disable-msg=W0612
			if self.panel_has_secondary_axis is True:
				secondary_handles, secondary_labels = axarr_sec.get_legend_handles_labels()	#pylint: disable-msg=W0612
			if (len(primary_labels) > 0) and (len(secondary_labels) > 0):
				labels = [r'$\Leftarrow$'+label for label in primary_labels]+ [label+r'$\Rightarrow$' for label in secondary_labels]
			else:
				labels = primary_labels+secondary_labels
			for label in labels:	# Only print legend if at least one series has a label
				if (label is not None) and (label != ''):
					legend_scale = 1.5
					leg_artist = [series_obj._legend_artist(legend_scale) for series_obj in self.current_series_list]	#pylint: disable-msg=W0212
					axarr.legend(leg_artist, labels, ncol=self.legend_props()['cols'] if 'cols' in self.legend_props() else len(labels),
						loc=self.legend_pos_list[self.legend_pos_list.index(self.legend_props()['pos'].lower() if 'pos' in self.legend_props() else 'lower left')], numpoints=1, fontsize=18/legend_scale)
					break
		#  Print independent axis tick marks and label
		indep_var_min = indep_axis_dict['indep_var_min']
		indep_var_max = indep_axis_dict['indep_var_max']
		indep_var_locs = indep_axis_dict['indep_var_locs']
		indep_axis_label = '' if indep_axis_dict['indep_axis_label'] is None else indep_axis_dict['indep_axis_label']
		indep_axis_units = '' if indep_axis_dict['indep_axis_units'] is None else indep_axis_dict['indep_axis_units']
		indep_axis_unit_scale = '' if indep_axis_dict['indep_axis_unit_scale'] is None else indep_axis_dict['indep_axis_unit_scale']
		axarr.set_xlim((indep_var_min, indep_var_max), emit=True, auto=False)
		axarr.xaxis.set_ticks(indep_var_locs)
		axarr.xaxis.grid(True, 'both')
		axarr.tick_params(axis='x', which='major', labelsize=14)
		if ('indep_var_labels' in indep_axis_dict) and (indep_axis_dict['indep_var_labels'] is not None):
			axarr.xaxis.set_ticklabels(indep_axis_dict['indep_var_labels'], fontsize=14)
			indep_height = _get_text_prop(fig, axarr.xaxis.get_ticklabels()[0])['height']
			min_width_label = min([_get_text_prop(fig, tick)['width'] for tick in axarr.xaxis.get_ticklabels()])
			indep_width = ((len(indep_axis_dict['indep_var_labels'])-1)*min_width_label)+sum([_get_text_prop(fig, tick)['width'] for tick in axarr.xaxis.get_ticklabels()])
		if (indep_axis_label != '') or (indep_axis_units != ''):
			axarr.xaxis.set_label_text(indep_axis_label + ('' if (indep_axis_unit_scale == '') and (indep_axis_units == '') else \
				(' ['+indep_axis_unit_scale+('-' if indep_axis_units == '' else indep_axis_units)+']')), fontdict={'fontsize':18})
			indep_height += 1.5*_get_text_prop(fig, axarr.xaxis.get_label())['height']	# Allow for half a line of spacing between tick labels and axis labels
			indep_width = max(indep_width, _get_text_prop(fig, axarr.xaxis.get_label())['width'])
		min_panel_height = max(primary_height, secondary_height)+indep_height
		min_panel_width = primary_width+secondary_width+indep_width
		return {'primary':None if self.panel_has_primary_axis is False else axarr, 'secondary':None if self.panel_has_secondary_axis is False else axarr_sec, 'min_height':min_panel_height, 'min_width':min_panel_width}


class Figure(object):	#pylint: disable-msg=R0902
	"""
	Automagically generate presentation-quality plots

	:param	panel:				one or more data panels
	:type	panel:				:py:class:`util_plot.Panel()` object or list of :py:class:`util_plot.Panel()` objects
	:param	indep_var_label:	independent variable label
	:type	indep_var_label:	string
	:param	indep_var_units:	independent variable units
	:type	indep_var_units:	string
	:param	fig_width:			hardcopy plot width
	:type	fig_width:			positive number
	:param	fig_height:			hardcopy plot height
	:type	fig_height:			positive number
	:param	title:				plot title
	:type	title:				string
	:param	log_indep:			logarithmic independent axis flag
	:type	log_indep:			boolean
	:raises:
	 * Same as :py:meth:`util_plot.Figure.add_panel()`

	 * Same as :py:meth:`util_plot.Figure.indep_var_label()`

	 * Same as :py:meth:`util_plot.Figure.indep_var_units()`

	 * Same as :py:meth:`util_plot.Figure.title()`

	 * Same as :py:meth:`util_plot.Figure.log_indep()`

	 * Same as :py:meth:`util_plot.Figure.figure_width()`

	 * Same as :py:meth:`util_plot.Figure.figure_height()`

	.. note:: The appropriate figure dimensions so that no labels are obstructed are calculated and used if **fig_width** and/or **fig_height** are not specified. The calculated figure width and/or height can be retrieved using \
	:py:meth:`util_plot.Figure.figure_width()` and/or :py:meth:`util_plot.Figure.figure_height()` methods.
	"""
	def __init__(self, panel=None, indep_var_label='', indep_var_units='', fig_width=None, fig_height=None, title='', log_indep=False):	#pylint: disable-msg=R0913
		self.fig = None
		self.axarr = None
		self.axarr_list = list()
		self.title_height = 0
		self.title_width = 0
		self.indep_var_min = None
		self.indep_var_max = None
		self.indep_var_div = None
		self.indep_var_unit_scale = None
		self.scaled_indep_var = None
		self.current_panel_list = list()
		self.current_indep_var_label = None
		self.current_indep_var_units = None
		self.current_fig_height = None
		self.current_fig_width = None
		self.current_title = None
		self.current_log_indep = False
		self.add_panel(panel)
		self.indep_var_label(indep_var_label)
		self.indep_var_units(indep_var_units)
		self.figure_height(fig_height)
		self.figure_width(fig_width)
		self.title(title)
		self.log_indep(log_indep)

	def _complete(self):
		"""
		Returns True if figire is fully specified, otherwise returns False
		"""
		return True if len(self.current_panel_list) > 0 else False

	def add_panel(self, panel):
		"""
		Adds panel to current panel list

		:param	panel:	one or more data panel
		:type	panel:	:py:class:`util_plot.Panel()` object or list of :py:class:`util_plot.panel()` objects
		:raises:
		 * TypeError (Panels must be provided in list form)

		 * TypeError (Panel element is not a panel object)

		 * RuntimeError (Panel element *[number]* is not fully specified)
		"""
		if panel is not None:
			panel = [panel] if isinstance(panel, Panel) is True else panel
			if isinstance(panel, list) is False:
				raise TypeError('Panels must be provided in list form')
			for num, obj in enumerate(panel):
				if isinstance(obj, Panel) is False:
					raise TypeError('Panel element is not a panel object')
				elif obj._complete() is False:	#pylint: disable-msg=W0212
					raise RuntimeError('Panel element {0} is not fully specified'.format(num))
			if len(self.current_panel_list) == 0:
				self.current_panel_list = panel
			else:
				for new_obj in panel:
					for old_obj in self.current_panel_list:
						if new_obj == old_obj:
							break
					else:
						self.current_panel_list.append(new_obj)

	def indep_var_label(self, *label):
		"""
		Sets or returns the plot independent variable label

		:param	label:	independent variable label
		:type	label:	string
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Independent variable label must be a string)
		"""
		if len(label) == 0:
			return self.current_indep_var_label
		if len(label) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_indep_var_label = label[0]
		if isinstance(self.current_indep_var_label, str) is False:
			raise TypeError('Independent variable label must be a string')
		self.current_indep_var_label = self.current_indep_var_label.strip()

	def indep_var_units(self, *units):
		"""
		Sets or returns the plot independent variable units

		:param	units:	independent variable units
		:type	units:	string
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Independent variable units must be a string)
		"""
		if len(units) == 0:
			return self.current_indep_var_units
		if len(units) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_indep_var_units = units[0]
		if isinstance(self.current_indep_var_units, str) is False:
			raise TypeError('Independent variable units must be a string')
		self.current_indep_var_units = self.current_indep_var_units.strip()

	def title(self, *text):
		"""
		Sets or returns the plot title

		:param	text:	plot title
		:type	text:	string
		:rtype:			string
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Plot title must be a string)
		"""
		if len(text) == 0:
			return self.current_title
		if len(text) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_title = text[0]
		if isinstance(self.current_title, str) is False:
			raise TypeError('Plot title must be a string')
		self.current_title = self.current_title.strip()

	def log_indep(self, *flag):
		"""
		Sets or returns the logarithmic independent axis flag

		:param	flag:	logarithmic independent axis flag
		:type	flag:	boolean
		:rtype:			boolean
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Logarthmic independent axis flag must be boolean)
		"""
		if len(flag) == 0:
			return self.current_log_indep
		if len(flag) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_log_indep = flag[0]
		if isinstance(self.current_log_indep, bool) is False:
			raise TypeError('Logarthmic independent axis flag must be boolean')

	def figure_width(self, *dim):
		"""
		Sets or returns the width of the hardcopy plot

		:param	dim:	hardcopy plot width (in inches)
		:type	dim:	positive number, float or integer
		:rtype:			positive number, float or integer
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Figure width must be a number)

		 * ValueError (Figure width must be a positive number)
		"""
		if len(dim) == 0:
			return self.current_fig_width
		if len(dim) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_fig_width = dim[0]
		if self.current_fig_width is not None:
			if util_misc.isnumber(self.current_fig_width) is False:
				raise TypeError('Figure width must be a number')
			if self.current_fig_width < 0:
				raise ValueError('Figure width must be a positive number')
			self.current_fig_width = float(self.current_fig_width)

	def figure_height(self, *dim):
		"""
		Sets or returns the height of the hardcopy plot

		:param	dim:	hardcopy plot height (in inches)
		:type	dim:	positive number
		:rtype:			positive number
		:raises:
		 * RuntimeError (Illegal number of parameters)

		 * TypeError (Figure height must be a number)

		 * ValueError (Figure height must be a positive number)
		"""
		if len(dim) == 0:
			return self.current_fig_height
		if len(dim) > 1:
			raise RuntimeError('Illegal number of parameters')
		self.current_fig_height = dim[0]
		if self.current_fig_height is not None:
			if util_misc.isnumber(self.current_fig_height) is False:
				raise TypeError('Figure height must be a number')
			if self.current_fig_height < 0:
				raise ValueError('Figure height must be a positive number')
			self.current_fig_height = float(self.current_fig_height)

	def draw(self):
		"""
		Generates figure

		:raises:	RuntimeError (Figure is not fully specified)
		"""
		if self._complete() is False:
			raise RuntimeError('Figure is not fully specified')
		num_panels = len(self.current_panel_list)
		plt.close('all')
		# Create required number of panels
		self.fig, self.axarr = plt.subplots(num_panels, sharex=True)	#pylint: disable-msg=W0612
		self.axarr = self.axarr if num_panels > 1 else [self.axarr]
		global_indep_var = list()
		# Find union of the independent variable data set of all panels
		for panel_obj in self.current_panel_list:
			for series_obj in panel_obj.current_series_list:
				global_indep_var = numpy.unique(numpy.append(global_indep_var, numpy.array([util_misc.smart_round(element, 10) for element in series_obj.indep_var()])))
		self.indep_var_min, self.indep_var_max, self.indep_var_div, self.indep_var_unit_scale, self.scaled_indep_var = _scale_series(series=global_indep_var, scale=True, scale_type='delta')
		self.indep_var_min = util_misc.smart_round(self.indep_var_min, 10)
		self.indep_var_max = util_misc.smart_round(self.indep_var_max, 10)
		indep_var_locs, indep_var_labels, self.indep_var_min, self.indep_var_max = _intelligent_ticks(self.scaled_indep_var, min(self.scaled_indep_var), max(self.scaled_indep_var), tight=True, calc_ticks=False)
		# Scale all panel series
		for panel_obj in self.current_panel_list:
			panel_obj._scale_indep_var(self.indep_var_div)	#pylint: disable-msg=W0212
		# Draw panels
		indep_axis_dict = {'indep_var_min':self.indep_var_min, 'indep_var_max':self.indep_var_max, 'indep_var_locs':indep_var_locs,
					 'indep_var_labels':None, 'indep_axis_label':None, 'indep_axis_units':None, 'indep_axis_unit_scale':None}
		for num, (panel_obj, axarr) in enumerate(zip(self.current_panel_list, self.axarr)):
			panel_dict = panel_obj._draw_panel(self.fig, axarr, dict(indep_axis_dict, log_indep=self.log_indep(), indep_var_labels=indep_var_labels if num == num_panels-1 else None,	#pylint: disable-msg=W0212,C0326
												  indep_axis_label=self.indep_var_label() if num == num_panels-1 else None, indep_axis_units=self.indep_var_units() if num == num_panels-1 else None,
												  indep_axis_unit_scale = self.indep_var_unit_scale if num == num_panels-1 else None))	#pylint: disable-msg=C0326
			self.axarr_list.append({'panel':num, 'primary':panel_dict['primary'], 'secondary':panel_dict['secondary'], 'min_height':panel_dict['min_height'], 'min_width':panel_dict['min_width']})
		self.title_height = 0
		self.title_width = 0
		if self.title() != '':
			title_obj = self.axarr[0].set_title(self.title(), horizontalalignment='center', verticalalignment='bottom', multialignment='center', fontsize=24)
			self.title_height = _get_text_prop(self.fig, title_obj)['height']
			self.title_width = _get_text_prop(self.fig, title_obj)['width']

	def fig_handle(self):
		"""
		Returns the Matplotlib figure handle. Useful if annotations or further customizations to the figure are needed.
		"""
		return self.fig

	def axis_list(self):
		"""
		Returns the Matplotlib figure axes handle vector. Useful if annotations or further customizations to the panel(s) are needed.
		"""
		return self.axarr_list

	def show(self):	#pylint: disable-msg=R0201
		"""
		Displays figure

		:raises:
		 * Same as :py:meth:`util_plot.Figure.draw()`
		"""
		if self.fig is None:
			self.draw()
		plt.show()

	def save(self, file_name):
		"""
		Saves figure

		:param	file_name:	File name of the hardcopy PNG
		:type	file_name:	string
		:raises:
		 * TypeError (File name must be a string)

		 * Same as :py:meth:`util_plot.Figure.draw()`
		"""
		if isinstance(file_name, str) is False:
			raise TypeError('File name must be a string')
		if self.fig is None:
			self.draw()
		# Calculate minimum figure dimensions
		axarr = self.axarr_list[0]['primary']
		legend_obj = axarr.get_legend()	#pylint: disable-msg=W0612
		min_fig_width = (max(self.title_width, max([panel_dict['min_width'] for panel_dict in self.axarr_list])))/float(self.fig.dpi)
		min_fig_height = ((len(self.axarr_list)-1)*0.00)+(((len(self.axarr_list)*max([panel_dict['min_height'] for panel_dict in self.axarr_list]))+self.title_height)/float(self.fig.dpi))
		self.figure_width(min_fig_width if self.figure_width() is None else self.figure_width())
		self.figure_height(min_fig_height if self.figure_height() is None else self.figure_height())
		self.fig.set_size_inches(max(min_fig_width, self.figure_width()), max(min_fig_height, self.figure_height()))
		file_name = os.path.expanduser(file_name)	# Matplotlib seems to have a problem with ~/, expand it to $HOME
		util_misc.make_dir(file_name)
		self.fig.savefig(file_name, dpi=self.fig.dpi)
		self.fig.savefig(file_name, bbox_inches='tight', dpi=self.fig.dpi)
		plt.close('all')

def _scale_series(series, scale=False, series_min=None, series_max=None, scale_type='delta'):	#pylint: disable-msg=R0913
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

def _process_ticks(locs, min_lim, max_lim, mant):
	"""
	Returns pretty-printed tick locations that are within the given bound
	"""
	locs = [float(loc) for loc in locs]
	bounded_locs = [loc for loc in locs if ((loc >= min_lim) or (abs(loc-min_lim) <= 1e-14)) and ((loc <= max_lim) or (abs(loc-max_lim) <= 1e-14))]
	raw_labels = [util_eng.peng(float(loc), mant, rjust=False) if ((abs(loc) >= 1) or (loc == 0)) else str(util_misc.smart_round(loc, mant)) for loc in bounded_locs]
	return (bounded_locs, [label.replace('u', '$\\mu$') for label in raw_labels])

def _intelligent_ticks(series, series_min, series_max, tight=True, calc_ticks=True):	#pylint: disable-msg=R0912,R0914,R0915
	"""
	Calculates ticks 'intelligently', trying to calculate sane tick spacing
	"""
	ideal_num_ticks = 8
	series_delta = float(series_max-series_min)
	num_ticks = 0
	sdiff = [1 if int(element) == element else 0 for element in [util_misc.smart_round(element, 10) for element in numpy.diff(series)]]	#pylint: disable-msg=E1101
	int_scale = True if sum(sdiff) == len(sdiff) else False
	min_num_ticks = 2 if series_delta == 0 else (ideal_num_ticks if int_scale is False else min(ideal_num_ticks, series_delta))
	div = 1 if (series_delta == 0) or (int_scale is True) else 10.0
	tick_list = None
	if calc_ticks is False:
		# Calculate spacing between points
		tspace = numpy.diff(series)	#pylint: disable-msg=E1101
		# Find minimum common spacing
		factors = [util_eng.peng_power(util_eng.peng(element, 3)) for element in tspace]
		divs = [div for (unit, div) in factors]	#pylint: disable-msg=W0612
		tspace_div = min(divs)
		scaled_tspace = numpy.round(numpy.array(tspace)/tspace_div, 10)	#pylint: disable-msg=E1101
		tspace_gcd = 0.5*util_misc.gcd(scaled_tspace)
		num_ticks = 1
		while num_ticks > min_num_ticks:
			tspace_gcd = 2*tspace_gcd
			# Find out number of ticks with the minimum common spacing
			num_ticks = round(1+((series_max-series_min)/(tspace_div*float(tspace_gcd))), 10)
			if (int(util_misc.smart_round(num_ticks, 10)) == round(num_ticks, 10)) and (int(util_misc.smart_round(num_ticks, 10)) >= min_num_ticks):
				num_ticks = int(round(num_ticks, 10))
				tstop = series[-1]
				tspace = tspace_gcd*tspace_div
				tick_list = numpy.linspace(series_min, series_max, num_ticks)	#pylint: disable-msg=E1101
				calc_ticks = False
	calc_ticks = True if tick_list is None else calc_ticks
	if calc_ticks is True:
		if (series_delta != 0) and (int_scale is True):
			step = 1 if series_delta <= ideal_num_ticks else math.ceil((series_max-series_min)/ideal_num_ticks)
			tick_list = [series_min-step]+[series_min+num*step for num in range(1+int(util_misc.smart_round(series_delta, 10)) if series_delta <= ideal_num_ticks else ideal_num_ticks)]
			tstart = tick_list[0]
			tstop = tick_list[-1]
		else:
			# round() allows for deltas closer to the next engineering unit to get the bigger scale while deltas closer to the smaller engineering scale get smaller scale
			scale = 1.0 if (series_delta == 0) or (int_scale is True) else 10**(round(math.log10(util_eng.peng_int(util_eng.peng(series_delta, 3)))))
			tight = False if (series_delta == 0) or (int_scale is True) else tight
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
	loc, labels = _uniquify_tick_labels(tick_list, series_min if tight is True else tstart, series_max if tight is True else tstop)
	return (loc, labels, tstart if series_delta == 0 else series_min, tstop if series_delta == 0 else series_max)

def _uniquify_tick_labels(tick_list, tmin, tmax):
	"""
	Calculate minimum tick mantissa given tick spacing
	"""
	# Step 1: Look at two contiguous ticks and lower mantissa till they are no more right zeros
	mant = 10
	for mant in range(10, -1, -1):
		if (str(util_eng.peng_mant(util_eng.peng(tick_list[-1], mant)))[-1] != '0') or (str(util_eng.peng_mant(util_eng.peng(tick_list[-2], mant)))[-1] != '0'):
			break
	# Step 2: Confirm labels are unique
	unique_mant_found = False
	while mant >= 0:
		loc, labels = _process_ticks(tick_list, tmin, tmax, mant)
		if sum([1 if labels[index] != labels[index+1] else 0 for index in range(0, len(labels[:-1]))]) == len(labels)-1:
			unique_mant_found = True if unique_mant_found is False else unique_mant_found
			mant -= 1
		else:
			mant += 1
			if unique_mant_found is True:
				loc, labels = _process_ticks(tick_list, tmin, tmax, mant)
				break
	return loc, labels

def _series_threshold(indep_var, dep_var, threshold, threshold_type):
	"""
	Chops series given a threshold
	"""
	indexes = numpy.where(numpy.array(indep_var) >= threshold) if threshold_type.upper() == 'MIN' else numpy.where(numpy.array(indep_var) <= threshold)  #pylint: disable-msg=E1101
	indep_var = numpy.array(indep_var)[indexes]  #pylint: disable-msg=E1101
	dep_var = numpy.array(dep_var)[indexes]  #pylint: disable-msg=E1101
	return indep_var, dep_var

def _get_text_prop(fig, text_obj):
	"""
	Return length of text in pixels
	"""
	renderer = fig.canvas.get_renderer()
	bbox = text_obj.get_window_extent(renderer=renderer).transformed(fig.dpi_scale_trans.inverted())
	return {'width':bbox.width*fig.dpi, 'height':bbox.height*fig.dpi}

def _get_panel_prop(fig, axarr):
	"""
	Return height of (sub)panel in pixels
	"""
	renderer = fig.canvas.get_renderer()
	bbox = axarr.get_window_extent(renderer=renderer).transformed(fig.dpi_scale_trans.inverted())
	return {'width':bbox.width*fig.dpi, 'height':bbox.height*fig.dpi}

def parametrized_color_space(series, offset=0, color='binary'):
	"""
	Computes a colors space where lighter colors correspond to lower parameter values

	:param	series:	data series
	:type	series:	Numpy vector
	:param	offset:	offset of the first (lightest) color
	:type	offset: float between 0 and 1
	:param	color:	color pallete. One of binary, Blues, BuGn, BuPu, gist_yarg, GnBu, Greens, Greys, Oranges, OrRd, PuBu, PuBuGn, PuRd, Purples, RdPu, Reds, YlGn, YlGnBu, YlOrBr, YlOrRd (case sensitive). \
	See `<http://arnaud.ensae.net/Rressources/RColorBrewer.pdf>`_ for a visual description of the colors.
	:type	color:	string
	:rtype:			Matplotlib color
	:raises:
	 * raise TypeError (Series has to be a list)

	 * raise RuntimeError (Series is empty)

	 * raise TypeError (Element *[index]* (*[value]*) is not a number)

	 * raise ValueError (Element *[index]* (*[value]*) is out of normal range [0, 1])

	 * raise TypeError (Offset has to be a number)

	 * raise ValueError (Offset is out of normal range [0, 1])
	"""
	if isinstance(series, list) is False:
		raise TypeError('Series has to be a list')
	if len(series) == 0:
		raise RuntimeError('Series is empty')
	for num, element in enumerate(series):
		if util_misc.isnumber(element) is False:
			raise TypeError('Element {0} ({1}) is not a number'.format(num, element))
		if (element < 0) or (element > 1):
			raise ValueError('Element {0} ({1}) is out of normal range [0, 1]'.format(num, element))
	if util_misc.isnumber(offset) is False:
		raise TypeError('Offset has to be a number')
	if (offset < 0) or (offset > 1):
		raise ValueError('Offset is out of normal range [0, 1]')
	color_name_list = ['binary', 'Blues', 'BuGn', 'BuPu', 'gist_yarg', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']
	color_pallete_list = [plt.cm.binary, plt.cm.Blues, plt.cm.BuGn, plt.cm.BuPu, plt.cm.gist_yarg, plt.cm.GnBu, plt.cm.Greens, plt.cm.Greys, plt.cm.Oranges, plt.cm.OrRd, plt.cm.PuBu,	#pylint: disable-msg=E1101
					   plt.cm.PuBuGn, plt.cm.PuRd, plt.cm.Purples, plt.cm.RdPu, plt.cm.Reds, plt.cm.YlGn, plt.cm.YlGnBu, plt.cm.YlOrBr, plt.cm.YlOrRd]	#pylint: disable-msg=E1101
	if color not in color_name_list:
		raise ValueError('Color pallete is not valid')
	color_dict = dict(zip(color_name_list, color_pallete_list))
	#color_dict = {'binary':plt.cm.binary, 'Blues':plt.cm.Blues, 'BuGn':plt.cm.BuGn, 'BuPu':plt.cm.BuPu, 'gist_yarg':plt.cm.gist_yarg, 'GnBu':plt.cm.GnBu, 'Greens':plt.cm.Greens, 'Greys':plt.cm.Greys,	#pylint: disable-msg=E1101
	#		'Oranges':plt.cm.Oranges, 'OrRd':plt.cm.OrRd, 'PuBu':plt.cm.PuBu, 'PuBuGn':plt.cm.PuBuGn, 'PuRd':plt.cm.PuRd, 'Purples':plt.cm.Purples, 'RdPu':plt.cm.RdPu, 'Reds':plt.cm.Reds,	#pylint: disable-msg=E1101
	#		'YlGn':plt.cm.YlGn, 'YlGnBu':plt.cm.YlGnBu, 'YlOrBr':plt.cm.YlOrBr, 'YlOrRd':plt.cm.YlOrRd}	#pylint: disable-msg=E1101
	return [color_dict[color](util_misc.normalize(value, series, offset)) for value in series]	#pylint: disable-msg=E1101
