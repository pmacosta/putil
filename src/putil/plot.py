# plot.py 	#pylint: disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Utility classes, methods and functions to handle plotting
"""

import os
import math
import numpy
from scipy import stats
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d  #pylint: disable=E0611
from collections import OrderedDict

import putil.pcsv
import putil.eng
import putil.misc
import putil.check

PRECISION = 10	# Number of mantissa significant digits
"""
Number of mantissa significant digits

:type:	integer
"""	#pylint: disable=W0105

class BasicSource(object):	#pylint: disable=R0902,R0903
	"""
	Container to hold data sets intended for plotting

	:param	indep_var:			independent variable vector
	:type	indep_var:			increasing real Numpy vector
	:param	dep_var:			dependent variable vector
	:type	dep_var:			real Numpy vector
	:param	indep_min:			mini:mum independent variable value
	:type	indep_min:			number
	:param	indep_max:			maximum independent variable value
	:type	indep_max:			number
	:rtype:						:py:class:`putil.plot.BasicSource()` object
	:raises:
	 * Same as :py:attr:`putil.plot.BasicSource.indep_var`

	 * Same as :py:attr:`putil.plot.BasicSource.dep_var`

	 * Same as :py:attr:`putil.plot.BasicSource.indep_min`

	 * Same as :py:attr:`putil.plot.BasicSource.indep_max`
	"""
	def __init__(self, indep_var=None, dep_var=None, indep_min=None, indep_max=None):
		# Private attributes
		self._raw_indep_var, self._raw_dep_var, self._indep_var_indexes, self._min_indep_var_index, self._max_indep_var_index = None, None, None, None, None
		# Public attributes
		self._indep_var, self._dep_var, self._indep_min, self._indep_max = None, None, None, None
		# Assign minimum and maximum first so as not to trigger unnecessary tresholding if the dependent and independent variables are already assigned
		self._set_indep_min(indep_min)
		self._set_indep_max(indep_max)
		self._set_indep_var(indep_var)
		self._set_dep_var(dep_var)

	def _get_indep_var(self):	#pylint: disable=C0111
		return self._indep_var

	@putil.check.check_parameter('indep_var', putil.check.PolymorphicType([None, putil.check.IncreasingRealNumpyVector()]))
	def _set_indep_var(self, indep_var):	#pylint: disable=C0111
		if (indep_var is not None) and (self._raw_dep_var is not None) and (len(self._raw_dep_var) != len(indep_var)):
			raise ValueError('Parameters `indep_var` and `dep_var` must have the same number of elements')
		self._raw_indep_var = putil.misc.smart_round(indep_var, PRECISION)
		self._update_indep_var()	# Apply minimum and maximum range bounding and assign it to self._indep_var and thus this is what self.indep_var returns
		self._update_dep_var()

	def _get_dep_var(self):	#pylint: disable=C0111
		return self._dep_var

	@putil.check.check_parameter('dep_var', putil.check.PolymorphicType([None, putil.check.RealNumpyVector()]))
	def _set_dep_var(self, dep_var):	#pylint: disable=C0111
		if (dep_var is not None) and (self._raw_indep_var is not None) and (len(self._raw_indep_var) != len(dep_var)):
			raise ValueError('Parameters `indep_var` and `dep_var` must have the same number of elements')
		self._raw_dep_var = putil.misc.smart_round(dep_var, PRECISION)
		self._update_dep_var()

	def _get_indep_min(self):	#pylint: disable=C0111
		return self._indep_min

	@putil.check.check_parameter('indep_min', putil.check.PolymorphicType([None, putil.check.Real()]))
	def _set_indep_min(self, indep_min):	#pylint: disable=C0111
		if (self.indep_max is not None) and (indep_min is not None) and (self.indep_max < indep_min):
			raise ValueError('Parameter `indep_min` is greater than parameter `indep_max`')
		self._indep_min = putil.misc.smart_round(indep_min, PRECISION) if not isinstance(indep_min, int) else indep_min
		self._update_indep_var()	# Apply minimum and maximum range bounding and assign it to self._indep_var and thus this is what self.indep_var returns
		self._update_dep_var()

	def _get_indep_max(self):	#pylint: disable=C0111
		return self._indep_max

	@putil.check.check_parameter('indep_max', putil.check.PolymorphicType([None, putil.check.Real()]))
	def _set_indep_max(self, indep_max):	#pylint: disable=C0111
		if (self.indep_min is not None) and (indep_max is not None) and (indep_max < self.indep_min):
			raise ValueError('Parameter `indep_min` is greater than parameter `indep_max`')
		self._indep_max = putil.misc.smart_round(indep_max, PRECISION) if not isinstance(indep_max, int) else indep_max
		self._update_indep_var()	# Apply minimum and maximum range bounding and assign it to self._indep_var and thus this is what self.indep_var returns
		self._update_dep_var()

	def _update_indep_var(self):
		""" Update independent variable according to its minimum and maximum limits """
		if self._raw_indep_var is not None:
			self._indep_var_indexes = numpy.where((self._raw_indep_var >= (self.indep_min if self.indep_min is not None else self._raw_indep_var[0])) & \
				(self._raw_indep_var <= (self.indep_max if self.indep_max is not None else self._raw_indep_var[-1])))
			self._indep_var = self._raw_indep_var[self._indep_var_indexes]
			if len(self.indep_var) == 0:
				raise ValueError('Parameter `indep_var` is empty after `indep_min`/`indep_max` range bounding')

	def _update_dep_var(self):
		""" Update dependent variable (if assigned) to match the independent variable range bounding """
		self._dep_var = self._raw_dep_var
		if (self._indep_var_indexes is not None) and (self._raw_dep_var is not None):
			self._dep_var = self._raw_dep_var[self._indep_var_indexes]

	def __str__(self):
		""" Print comma-separated value source information """
		ret = ''
		ret += 'Independent variable minimum: {0}\n'.format('-inf' if self.indep_min is None else self.indep_min)
		ret += 'Independent variable maximum: {0}\n'.format('+inf' if self.indep_max is None else self.indep_max)
		ret += 'Independent variable: {0}\n'.format(putil.misc.numpy_pretty_print(self.indep_var, width=50, indent=len('Independent variable: ')))
		ret += 'Dependent variable: {0}'.format(putil.misc.numpy_pretty_print(self.dep_var, width=50, indent=len('Dependent variable: ')))
		return ret

	def _complete(self):
		""" Returns True if object is fully specified, otherwise returns False """
		return (self.indep_var is not None) and (self.dep_var is not None)

	# Managed attributes
	indep_min = property(_get_indep_min, _set_indep_min, None, doc='Minimum of independent variable')
	"""
	Minimum independent variable limit

	:type:		real number
	:raises:
	 * TypeError (Parameter `indep_min` is of the wrong type)

	 * ValueError (Parameter `indep_var` is empty after `indep_min`/`indep_max` range bounding)

	 * ValueError (Parameter `indep_min` is greater than parameter `indep_max`)
	"""	#pylint: disable=W0105

	indep_max = property(_get_indep_max, _set_indep_max, None, doc='Maximum of independent variable')
	"""
	Maximum independent variable limit

	:type:		real number
	:raises:
	 * TypeError (Parameter `indep_max` is of the wrong type)

	 * ValueError (Parameter `indep_var` is empty after `indep_min`/`indep_max` range bounding)

	 * ValueError (Parameter `indep_min` is greater than parameter `indep_max`)
	"""	#pylint: disable=W0105

	indep_var = property(_get_indep_var, _set_indep_var, None, doc='Independent variable Numpy vector')
	"""
	Independent variable data

	:type:		increasing real Numpy vector
	:raises:
	 * TypeError (Parameter `indep_var` is of the wrong type)

	 * ValueError (Parameters `indep_var` and `dep_var` must have the same number of elements)

	 * ValueError (Parameters `indep_var` is empty after `indep_min`/`indep_max` range bounding)
	"""	#pylint: disable=W0105

	dep_var = property(_get_dep_var, _set_dep_var, None, doc='Dependent variable Numpy vector')
	"""
	Dependent variable data

	:type:		real Numpy vector
	:raises:
	 * TypeError (Parameter `dep_var` is of the wrong type)

	 * ValueError (Parameters `indep_var` and `dep_var` must have the same number of elements)
	"""	#pylint: disable=W0105

class CsvSource(BasicSource):	#pylint: disable=R0902,R0903
	"""
	Retrieves data set from a comma-separated file

	:param	file_name:			comma-separated file name
	:type	file_name:			string
	:param	indep_col_label:	independent variable column label
	:type	indep_col_label:	string (case insensitive)
	:param	dep_col_label:		dependent variable column label
	:type	dep_col_label:		string (case insensitive)
	:param	dfilter:			data filter definition. See :py:meth:`putil.plot.CsvSource.data_filter()`
	:type	dfilter:			dictionary
	:param	indep_min:			minimum independent variable value
	:type	indep_min:			number
	:param	indep_max:			maximum independent variable value
	:type	indep_max:			number
	:param	fproc:				processing function
	:type	fproc:				function pointer
	:param	fproc_eargs:		processing function extra arguments
	:type	fproc_eargs:		dictionary
	:rtype:						:py:class:`putil.plot.CsvSource()` object
	:raises:
	 * Same as :py:attr:`putil.plot.BasicSource.indep_var`

	 * Same as :py:attr:`putil.plot.BasicSource.dep_var`

	 * Same as :py:attr:`putil.plot.BasicSource.indep_min`

	 * Same as :py:attr:`putil.plot.BasicSource.indep_max`

	 * Same as :py:attr:`putil.plot.CsvSource.file_name`

	 * Same as :py:attr:`putil.plot.CsvSource.dfilter`

	 * Same as :py:attr:`putil.plot.CsvSource.indep_col_label`

	 * Same as :py:attr:`putil.plot.CsvSource.dep_col_label`

	 * Same as :py:attr:`putil.plot.CsvSource.fproc`

	 * Same as :py:attr:`putil.plot.CsvSource.fproc_eargs`
	"""
	def __init__(self, file_name=None, indep_col_label=None, dep_col_label=None, dfilter=None, indep_min=None, indep_max=None, fproc=None, fproc_eargs=None):	#pylint: disable=R0913
		BasicSource.__init__(self, indep_var=None, dep_var=None, indep_min=indep_min, indep_max=indep_max)
		# Private attributes
		self._csv_obj, self._reverse_data = None, False
		# Public attributes
		self._file_name, self._dfilter, self._indep_col_label, self._dep_col_label, self._fproc, self._fproc_eargs = None, None, None, None, None, None
		self._set_indep_col_label(indep_col_label)
		self._set_dep_col_label(dep_col_label)
		self._set_fproc(fproc)
		self._set_fproc_eargs(fproc_eargs)
		self._set_dfilter(dfilter)
		self._set_file_name(file_name)

	def _get_file_name(self):	#pylint: disable=C0111
		return self._file_name

	@putil.check.check_parameter('file_name', putil.check.PolymorphicType([None, putil.check.File(check_existance=True)]))
	def _set_file_name(self, file_name):	#pylint: disable=C0111
		if file_name is not None:
			self._file_name = file_name
			self._csv_obj = putil.pcsv.CsvFile(file_name)
			self._apply_dfilter()	# This also gets indep_var and dep_var from file
			self._process_data()

	def _get_dfilter(self):	#pylint: disable=C0111
		return self._dfilter

	@putil.check.check_parameter('dfilter', putil.check.PolymorphicType([None, dict]))
	def _set_dfilter(self, dfilter):	#pylint: disable=C0111
		self._dfilter = dict([(key.upper(), value) for key, value in dfilter.items()]) if isinstance(dfilter, dict) else dfilter 	# putil.pcsv is case insensitive and all caps
		self._apply_dfilter()
		self._process_data()

	def _get_indep_col_label(self):	#pylint: disable=C0111
		return self._indep_col_label

	@putil.check.check_parameter('indep_col_label', putil.check.PolymorphicType([None, str]))
	def _set_indep_col_label(self, indep_col_label):	#pylint: disable=C0111
		self._indep_col_label = indep_col_label.upper() if isinstance(indep_col_label, str) else indep_col_label	# putil.pcsv is case insensitive and all caps
		self._check_indep_col_label()
		self._apply_dfilter()
		self._process_data()

	def _get_dep_col_label(self):	#pylint: disable=C0111
		return self._dep_col_label

	@putil.check.check_parameter('dep_col_label', putil.check.PolymorphicType([None, str]))
	def _set_dep_col_label(self, dep_col_label):	#pylint: disable=C0111
		self._dep_col_label = dep_col_label.upper() if isinstance(dep_col_label, str) else dep_col_label	 	# putil.pcsv is case insensitive and all caps
		self._check_dep_col_label()
		self._apply_dfilter()
		self._process_data()

	def _get_fproc(self):	#pylint: disable=C0111
		return self._fproc

	@putil.check.check_parameter('fproc', putil.check.PolymorphicType([None, putil.check.Function()]))
	def _set_fproc(self, fproc):	#pylint: disable=C0111
		if fproc is not None:
			args = putil.check.get_function_args(fproc)
			if (fproc is not None) and (len(args) < 2) and ('*args' not in args) and ('**kwargs' not in args):
				raise ValueError('Parameter `fproc` (function {0}) does not have at least 2 arguments'.format(fproc.__name__))
		self._fproc = fproc
		self._check_fproc_eargs()
		self._process_data()

	def _get_fproc_eargs(self):	#pylint: disable=C0111
		return self._fproc_eargs

	@putil.check.check_parameter('fproc_eargs', putil.check.PolymorphicType([None, dict]))
	def _set_fproc_eargs(self, fproc_eargs):	#pylint: disable=C0111
		# Check that extra argnuments to see if they are in the function definition
		self._fproc_eargs = fproc_eargs
		self._check_fproc_eargs()
		self._process_data()

	def _check_fproc_eargs(self):
		""" Checks that the extra arguments are in the processing function definition """
		if (self.fproc is not None) and (self.fproc_eargs is not None):
			args = putil.check.get_function_args(self._fproc)
			for key in self.fproc_eargs:
				if (key not in args) and ('*args' not in args) and ('**kwargs' not in args):
					raise RuntimeError('Extra argument `{0}` not found in parameter `fproc` (function {1}) definition'.format(key, self.fproc.__name__))

	def _check_indep_col_label(self):
		""" Check that independent column label can be found in comma-separated file header """
		if (self._csv_obj is not None) and (self.indep_col_label is not None) and (self.indep_col_label not in self._csv_obj.header()):
			raise ValueError('Column {0} (independent column label) could not be found in comma-separated file {1} header'.format(self.indep_col_label, self.file_name))

	def _check_dep_col_label(self):
		""" Check that dependent column label can be found in comma-separated file header """
		if (self._csv_obj is not None) and (self.dep_col_label is not None) and (self.dep_col_label not in self._csv_obj.header()):
			raise ValueError('Column {0} (dependent column label) could not be found in comma-separated file {1} header'.format(self.dep_col_label, self.file_name))

	def _check_dfilter(self):
		""" Check that columns in filter specification can be found in comma-separated file header """
		if (self._csv_obj is not None) and (self.dfilter is not None):
			for key in self.dfilter:
				if key not in self._csv_obj.header():
					raise ValueError('Column {0} in data filter not found in comma-separated file {1} header'.format(key, self.file_name))

	def _apply_dfilter(self):
		""" Apply data filters to loaded data """
		self._check_dfilter()
		if (self.dfilter is not None) and (len(self.dfilter) > 0) and (self._csv_obj is not None):
			self._csv_obj.set_filter(self.dfilter)
		elif self._csv_obj is not None:
			self._csv_obj.reset_filter()
		self._get_indep_var_from_file()
		self._get_dep_var_from_file()

	def _get_indep_var_from_file(self):
		""" Retrieve independent data variable from comma-separated file """
		if (self._csv_obj is not None) and (self.indep_col_label is not None):
			self._check_indep_col_label()	# When object is given all parameters at construction the column label checking cannot happen at property assignment because file data is not yet loaded
			data = numpy.array(self._csv_obj.filtered_data(self.indep_col_label))
			if (len(data) == 0) or ((data == [None]*len(data)).all()):
				raise ValueError('Filtered independent variable is empty')
			# Flip data if it is in descending order (affects interpolation)
			if max(numpy.diff(data)) < 0:
				self._reverse_data = True
				data = data[::-1]
				if self.dep_var is not None:
					self._set_dep_var(self.dep_var[::-1])
			self._set_indep_var(data)

	def _get_dep_var_from_file(self):
		""" Retrieve dependent data variable from comma-separated file """
		if (self._csv_obj is not None) and (self.dep_col_label is not None):
			self._check_dep_col_label()	# When object is given all parameters at construction the column label checking cannot happen at property assignment because file data is not yet loaded
			data = numpy.array(self._csv_obj.filtered_data(self.dep_col_label))
			if (len(data) == 0) or ((data == [None]*len(data)).all()):
				raise ValueError('Filtered dependent variable is empty')
			self._set_dep_var(data[::-1] if self._reverse_data else data)

	def _process_data(self):
		""" Process data through call-back function """
		if (self.fproc is not None) and (self.indep_var is not None) and (self.dep_var is not None):
			try:
				ret = self.fproc(self.indep_var, self.dep_var) if self.fproc_eargs is None else self.fproc(self.indep_var, self.dep_var, **self.fproc_eargs)
			except Exception as error_msg:
				msg = 'Processing function {0} threw an exception when called with the following arguments:\n'.format(self.fproc.__name__)
				msg += 'indep_var: {0}\n'.format(putil.misc.numpy_pretty_print(self.indep_var, limit=10))
				msg += 'dep_var: {0}\n'.format(putil.misc.numpy_pretty_print(self.indep_var, limit=10))
				if self.fproc_eargs is not None:
					for key, value in self.fproc_eargs.items():
						msg += '{0}: {1}\n'.format(key, value)
				msg += 'Exception error: {0}'.format(error_msg)
				raise RuntimeError(msg)
			if (not isinstance(ret, list)) and (not isinstance(ret, tuple)):
				raise TypeError('Parameter `fproc` (function {0}) return value is of the wrong type'.format(self.fproc.__name__))
			if len(ret) != 2:
				raise RuntimeError('Parameter `fproc` (function {0}) returned an illegal number of values'.format(self.fproc.__name__))
			indep_var = ret[0]
			dep_var = ret[1]
			self._check_var(indep_var, 'independent variable')
			self._check_var(dep_var, 'dependent variable')
			if len(indep_var) != len(dep_var):
				raise ValueError('Processed independent and dependent variables are of different length')
			# The processing function could potentially expand (say, via interpolation) or shorten the data set length. To avoid errors that dependent and independet variables have different number of elements
			# while setting the first processed variable (either independent or dependent) both are "reset" to None first
			self._set_indep_var(None)
			self._set_dep_var(None)
			self._set_indep_var(indep_var)
			self._set_dep_var(dep_var)

	def _check_var(self, var, name):	#pylint:disable=R0201
		""" Validate (in)dependent variable returned by processing function """
		if isinstance(var, type(numpy.array([]))) and ((len(var) == 0) or ((var == [None]*len(var)).all())):
			raise ValueError('Processed {0} is empty'.format(name))
		if not putil.check.type_match(var, putil.check.IncreasingRealNumpyVector() if name == 'independent variable' else putil.check.RealNumpyVector()):
			raise TypeError('Processed {0} is of the wrong type'.format(name))

	def __str__(self):
		""" Print comma-separated value source information """
		ret = ''
		ret += 'File name: {0}\n'.format(self.file_name)
		ret += 'Data filter: {0}\n'.format(self.dfilter if self.dfilter is None else '')
		if self.dfilter is not None:
			odfilter = OrderedDict(sorted(self.dfilter.items(), key=lambda t: t[0]))
			for key, value in odfilter.iteritems():
				ret += '   {0}: {1}\n'.format(key, value)
		ret += 'Independent column label: {0}\n'.format(self.indep_col_label)
		ret += 'Dependent column label: {0}\n'.format(self.dep_col_label)
		ret += 'Processing function: {0}\n'.format('None' if self.fproc is None else self.fproc.__name__)
		ret += 'Processing function extra arguments: {0}\n'.format(self.fproc_eargs if self.fproc_eargs is None else '')
		if self.fproc_eargs is not None:
			ofproc_eargs = OrderedDict(sorted(self.fproc_eargs.items(), key=lambda t: t[0]))
			for key, value in ofproc_eargs.iteritems():
				ret += '   {0}: {1}\n'.format(key, value)
		ret += BasicSource.__str__(self)
		return ret

	def _complete(self):
		""" Returns True if object is fully specified, otherwise returns False """
		return (self.file_name is not None) and (self.indep_col_label is not None) and (self.dep_col_label is not None)

	file_name = property(_get_file_name, _set_file_name, doc='Comma-separated file name')
	"""
	Comma-separated file from which data series is to be extracted

	:type:		string
	:raises:
	 * TypeError (Parameter `file_name` is of the wrong type)

	 * IOError (File *[file_name]* could not be found)

	 * Same as :py:attr:`putil.plot.CsvSource.dfilter`

	.. warning:: The first line of the comma-separated file must contain unique headers for each column
	"""	#pylint: disable=W0105

	dfilter = property(_get_dfilter, _set_dfilter, doc='Data filter dictionary')
	"""
	Data filter

	:type:		dictionary
	:raises:
	 * TypeError (Parameter `dfilter` is of the wrong type)

	 * ValueError (Filtered independent variable is empty)

	 * ValueError (Filtered dependent variable is empty)

	 * ValueError (Column *[column]* in data filter not found in comma-separated file *[file_name]* header)

	 * Same as :py:attr:`putil.plot.CsvSource.fproc`

	 * Same as :py:attr:`putil.plot.CsvSource.fproc_eargs`

	.. note::
	   The filter definition dictionary consists of a series of key-value pairs. For each key-value pair, the filter key is a column name in the comma-separated file; all rows which cointain the specified filter \
	   value for the specified filter column are going to be kept for that particular key-value pair. The overall data set is the intersection of all the filter dictionary key-value data sets.
	"""	#pylint: disable=W0105

	indep_col_label = property(_get_indep_col_label, _set_indep_col_label, doc='Independent column label (column name)')
	"""
	Independent variable column label (column name)

	:type:	string
	:raises:
	 * TypeError (Parameter `indep_col_label` is of the wrong type)

	 * ValueError (Column *[indep_col_label]* (independent column label) could not be found in comma-separated file *[file_name]* header)

	 * ValueError (Filtered independent variable is empty)

	 * Same as :py:attr:`putil.plot.CsvSource.dfilter`
	"""	#pylint: disable=W0105

	dep_col_label = property(_get_dep_col_label, _set_dep_col_label, doc='Dependent column label (column name)')
	"""
	Dependent variable column label (column name)

	:type:	string
	:raises:
	 * TypeError (Parameter `dep_col_label` is of the wrong type)

	 * ValueError (Column *[dep_col_label]* (dependent column label) could not be found in comma-separated file *[file_name]* header)

	 * ValueError (Filtered dependent variable is empty)

	 * Same as :py:attr:`putil.plot.CsvSource.dfilter`
	"""	#pylint: disable=W0105

	fproc = property(_get_fproc, _set_fproc, doc='Processing function')
	"""
	Data processing function pointer

	:type:	function pointer
	:raises:
	 * TypeError (Parameter `fproc` is of the wrong type)

	 * TypeError (Parameter `fproc` (function *[function name pointed by fproc]*) return value is of the wrong type)

	 * TypeError (Processed independent variable is of the wrong type)

	 * TypeError (Processed dependent variable is of the wrong type)

	 * ValueError (Processed independent variable is empty)

	 * ValueError (Processed dependent variable is empty)

	 * ValueError (Parameter `fproc` (function *[function name pointed by fproc]*) does not have at least 2 arguments)

	 * ValueError (Processed independent and dependent variables are of different length)

	 * RuntimeError (Parameter `fproc` (function *[function name pointed by fproc]*) returned an illegal number of values)

	 * RuntimeError (Processing function *[function name pointed by fproc]* threw an exception when called with the following arguments [...])

	 * Same as :py:attr:`putil.plot.BasicSource.indep_var`

	 * Same as :py:attr:`putil.plot.BasicSource.dep_var`

	 * Same as :py:attr:`putil.plot.CsvSource.fproc_eargs`

	.. note::
	   The processing function is useful to do "light" data massaging, like scaling, etc; it is called after the data has been retrieved from the comma-separated value and the resulting filtered data set has been \
	   thresholded by **indep_var_min** and **dep_var_min** (if applicable).

	   The processing function is given two arguments, a Numpy vector representing the independent variable array (first argument) and a Numpy vector representing the dependent variable array (second argument). \
	   The expected return value is a two-element Numpy vector tuple, its first element being the processed independent variable array, and the second element being the processed dependent variable array.
	"""	#pylint: disable=W0105

	fproc_eargs = property(_get_fproc_eargs, _set_fproc_eargs, doc='Processing function extra argument dictionary')
	"""
	Extra arguments for the data processing function

	:type:	dictionary
	:raises:
	 * TypeError (Parameter `fproc_eargs` is of the wrong type)

	 * ValueError (Extra argument `par1` not found in parameter `fproc` (function *[function name pointed by fproc]*) definition)

	 * Same as :py:attr:`putil.plot.CsvSource.fproc`

	.. note::
	   Extra parameters can be passed to the processing function using **fproc_eargs**. For example, if **fproc_eargs** is ``{'par1':5, 'par2':[1, 2, 3]}`` then a valid processing function would be::

	       def my_proc_func(indep_var, dep_var, par1, par2):
	           # Do some data processing
	           return indep_var, dep_var
	"""	#pylint: disable=W0105

	# indep_var is read only
	indep_var = property(BasicSource._get_indep_var, None, doc='Independent variable Numpy vector')	#pylint: disable=E0602

	# dep_var is read only
	dep_var = property(BasicSource._get_dep_var, None, doc='Dependent variable Numpy vector')	#pylint: disable=E0602

class Series(object):	#pylint: disable=R0902,R0903
	"""
	Specifies a series within a panel

	:param	data_source:	data source object
	:type	data_source:	:py:class:`putil.plot.BasicSource()` object or :py:class:`putil.plot.CsvSource()` object or others conforming to the data source specification
	:param	label:			series label, to be used in panel legend
	:type	label:			string
	:param	color:			series color
	:type	color:			Matplotlib color
	:param	marker:			plot data markers flag
	:type	marker:			boolean
	:param	interp:			interpolation option, one of STRAIGHT, STEP, CUBIC or LINREG (case insensitive)
	:type	interp:			string
	:param	line_style:		line style, one of `-`, `--`, `-.` or `:`
	:type	line_style:		Matplotlib line specification
	:param	secondary_axis:	secondary axis flag
	:type	secondary_axis:	boolean
	:raises:
	 * Same as :py:meth:`putil.plot.Series.data_source`

	 * Same as :py:meth:`putil.plot.Series.label`

	 * Same as :py:meth:`putil.plot.Series.color`

	 * Same as :py:meth:`putil.plot.Series.marker`

	 * Same as :py:meth:`putil.plot.Series.interp`

	 * Same as :py:meth:`putil.plot.Series.line_style`

	 * Same as :py:meth:`putil.plot.Series.secondary_axis`
	"""
	def __init__(self, data_source, label, color='k', marker=True, interp='CUBIC', line_style='-', secondary_axis=False):	#pylint: disable=R0913
		# Series plotting attributes
		self._ref_linewidth = 2.5
		self._ref_markersize = 14
		self._ref_markeredgewidth = 5
		self._ref_markerfacecolor = 'w'
		# Private attributes
		self._scaling_factor_indep_var, self._scaling_factor_dep_var = 1, 1
		self._marker_spec, self._linestyle_spec, self._linewidth_spec = None, None, None
		# Public attributes
		self.scaled_indep_var, self.scaled_dep_var = None, None
		self.interp_indep_var, self.interp_dep_var = None, None
		self.indep_var, self.dep_var = None, None
		self.scaled_interp_indep_var, self.scaled_interp_dep_var = None, None
		self._data_source, self._label, self._color, self._marker, self._interp, self._line_style, self._secondary_axis = None, None, 'k', True, 'CUBIC', '-', False
		self._set_label(label)
		self._set_color(color)
		self._set_marker(marker)
		self._set_interp(interp)
		self._set_line_style(line_style)
		self._set_secondary_axis(secondary_axis)
		self._set_data_source(data_source)

	def _get_data_source(self):	#pylint: disable=C0111
		return self._data_source

	def _set_data_source(self, data_source):	#pylint: disable=C0111
		if data_source is not None:
			for method in ['indep_var', 'dep_var']:
				if method not in dir(data_source):
					raise RuntimeError('Parameter `data_source` does not have `{0}` attribute'.format(method))
			if ('_complete' in dir(data_source)) and (not data_source._complete()):	#pylint: disable=W0212
				raise RuntimeError('Parameter `data_source` is not fully specified')
			self._data_source = data_source
			self.indep_var = self.data_source.indep_var
			self.dep_var = self.data_source.dep_var
			self._validate_source_length_cubic_interp()
			self._calculate_curve()

	def _get_label(self):	#pylint: disable=C0111
		return self._label

	@putil.check.check_parameter('label', putil.check.PolymorphicType([None, str]))
	def _set_label(self, label):	#pylint: disable=C0111
		self._label = label

	def _get_color(self):	#pylint: disable=C0111
		return self._color

	@putil.check.check_parameter('color', putil.check.PolymorphicType([None, putil.check.Number(), str, list, tuple]))
	def _set_color(self, color):	#pylint: disable=C0111
		valid_html_colors = [
			'aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'black', 'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue',
			'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkkhaki', 'darkmagenta',
			'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue',
			'dimgray', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'honeydew',
			'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan',
			'lightgoldenrodyellow', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightsteelblue', 'lightyellow', 'lime', 'limegreen',
			'linen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred',
			'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen',
			'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen',
			'seashell', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquois', 'violet', 'wheat', 'white', 'whitesmoke',
			'yellow', 'yellowgreen'
		]
		self._color = color.lower().strip() if isinstance(color, str) else (float(color) if putil.check.Number().includes(color) else color)
		check_list = list()
		# No color specification
		check_list.append(self.color is None)
		# Gray scale color specification, checked by decorator
		check_list.append(putil.check.NumberRange(minimum=0.0, maximum=1.0).includes(self.color))
		# Basic built-in Matplotlib specification
		check_list.append(isinstance(self.color, str) and (len(self.color) == 1) and (self.color in 'bgrcmykw'))
		# HTML color name specification
		check_list.append(isinstance(self.color, str) and (self.color in valid_html_colors))
		# HTML hex color specification
		check_list.append(isinstance(self.color, str) and (self.color[0] == '#') and (len(self.color) == 7) and ((numpy.array([putil.misc.ishex(char) for char in self.color[1:]]) == numpy.array([True]*6)).all()))
		# RGB or RGBA tuple
		check_list.append((type(self.color) in [list, tuple]) and (len(self.color) in [3, 4]) and \
			((numpy.array([True if putil.check.Number().includes(comp) and putil.check.NumberRange(minimum=0.0, maximum=1.0).includes(comp) else False for comp in self.color]) == numpy.array([True]*len(self.color))).all()))
		if not True in check_list:
			raise TypeError('Invalid color specification')

	def _get_marker(self):	#pylint: disable=C0111
		return self._marker

	@putil.check.check_parameter('marker', bool)
	def _set_marker(self, marker):	#pylint: disable=C0111
		self._marker = marker
		self._check_series_is_plottable()
		self._marker_spec = 'o' if self.marker else ''

	def _get_interp(self):	#pylint: disable=C0111
		return self._interp

	@putil.check.check_parameter('interp', putil.check.PolymorphicType([None, putil.check.OneOf(['STRAIGHT', 'STEP', 'CUBIC', 'LINREG'])]))
	def _set_interp(self, interp):	#pylint: disable=C0111
		self._interp = interp.upper().strip() if isinstance(interp, str) else interp
		self._check_series_is_plottable()
		self._validate_source_length_cubic_interp()
		self._update_linestyle_spec()
		self._update_linewidth_spec()
		self._calculate_curve()

	def _get_line_style(self):	#pylint: disable=C0111
		return self._line_style

	@putil.check.check_parameter('line_style', putil.check.PolymorphicType([None, putil.check.OneOf(['-', '--', '-.', ':'])]))
	def _set_line_style(self, line_style):	#pylint: disable=C0111
		self._line_style = line_style
		self._update_linestyle_spec()
		self._update_linewidth_spec()
		self._check_series_is_plottable()

	def _get_secondary_axis(self):	#pylint: disable=C0111
		return self._secondary_axis

	@putil.check.check_parameter('secondary_axis', putil.check.PolymorphicType([None, bool]))
	def _set_secondary_axis(self, secondary_axis):	#pylint: disable=C0111
		self._secondary_axis = secondary_axis

	def __str__(self):
		""" Print series object information """
		ret = ''
		ret += 'Data source: {0}{1} class object\n'.format(None if self.data_source is None else self.data_source.__module__, '' if self.data_source is None else '.'+self.data_source.__class__.__name__)
		ret += 'Independent variable: {0}\n'.format(putil.misc.numpy_pretty_print(self.indep_var, width=50))
		ret += 'Dependent variable: {0}\n'.format(putil.misc.numpy_pretty_print(self.dep_var, width=50))
		ret += 'Label: {0}\n'.format(self.label)
		ret += 'Color: {0}\n'.format(self.color)
		ret += 'Marker: {0}\n'.format(self.marker)
		ret += 'Interpolation: {0}\n'.format(self.interp)
		ret += 'Line style: {0}\n'.format(self.line_style)
		ret += 'Secondary axis: {0}'.format(self.secondary_axis)
		return ret

	def _check_series_is_plottable(self):
		""" Check that the combination of marker, line style and line width width will produce a printable series """
		if (not self.marker) and ((not self.interp) or (not self.line_style)):
			raise RuntimeError('Series options make it not plottable')

	def _validate_source_length_cubic_interp(self):	#pylint:disable=C0103
		""" Test if data source has minimum length to calculate cubic interpolation """
		if (self.interp == 'CUBIC') and (self.indep_var is not None) and (self.dep_var is not None) and (self.indep_var.shape[0] < 4):
			raise ValueError('At least 4 data points are needed for CUBIC interpolation')

	def _complete(self):
		""" Returns True if series is fully specified, otherwise returns False """
		return self.data_source is not None

	def _calculate_curve(self):
		""" Compute curve to interpolate between data points """
		if (self.interp is not None) and (self.indep_var is not None) and (self.dep_var is not None):
			if self.interp == 'CUBIC':
				self.interp_indep_var = numpy.linspace(min(self.indep_var), max(self.indep_var), 500)  #pylint: disable=E1101
				finterp = interp1d(self.indep_var, self.dep_var, kind='cubic')
				self.interp_dep_var = finterp(self.interp_indep_var)
			elif self.interp == 'LINREG':
				slope, intercept, r_value, p_value, std_err = stats.linregress(self.indep_var, self.dep_var)	#pylint: disable=W0612
				self.interp_indep_var = self.indep_var
				self.interp_dep_var = intercept+(slope*self.indep_var)
		self._scale_indep_var(self._scaling_factor_indep_var)
		self._scale_dep_var(self._scaling_factor_dep_var)

	def _scale_indep_var(self, scaling_factor):
		""" Scale independent variable """
		self._scaling_factor_indep_var = float(scaling_factor)
		self.scaled_indep_var = self.indep_var/self._scaling_factor_indep_var if self.indep_var is not None else self.scaled_indep_var
		self.scaled_interp_indep_var = self.interp_indep_var/self._scaling_factor_indep_var if self.interp_indep_var is not None else self.scaled_interp_indep_var

	def _scale_dep_var(self, scaling_factor):
		""" Scale dependent variable """
		self._scaling_factor_dep_var = float(scaling_factor)
		self.scaled_dep_var = self.dep_var/self._scaling_factor_dep_var if self.dep_var is not None else self.scaled_dep_var
		self.scaled_interp_dep_var = self.interp_dep_var/self._scaling_factor_dep_var if self.interp_dep_var is not None else self.scaled_interp_dep_var

	def _update_linestyle_spec(self):
		""" Update line style specification to be used in series drawing """
		self._linestyle_spec = self.line_style if (self.line_style is not None) and (self.interp is not None) else ''

	def _update_linewidth_spec(self):
		""" Update line width specification to be used in series drawing """
		self._linewidth_spec = self._ref_linewidth if (self.line_style is not None) and (self.interp is not None) else 0.0

	def _legend_artist(self, legend_scale=1.5):
		""" Creates artist (marker -if used- and line style -if used-) """
		return plt.Line2D(
			(0, 1),
			(0, 0),
			color=self.color,
			marker=self._marker_spec,
			linestyle=self._linestyle_spec,
			linewidth=self._linewidth_spec/legend_scale,
			markeredgecolor=self.color,
			markersize=self._ref_markersize/legend_scale,
			markeredgewidth=self._ref_markeredgewidth/legend_scale,
			markerfacecolor=self._ref_markerfacecolor
		)

	def _draw_series(self, axarr, log_indep, log_dep):
		""" Draw series """
		fplot = axarr.plot if (not log_indep) and (not log_dep) else (axarr.semilogx if log_indep and (not log_dep) else (axarr.loglog if (log_indep) and (log_dep) else axarr.semilogy))
		# Plot line
		if self.line_style is not None:
			fplot(
				self.scaled_indep_var if self.interp in ['STRAIGHT', 'STEP'] else self.scaled_interp_indep_var,
				self.scaled_dep_var if self.interp in ['STRAIGHT', 'STEP'] else self.scaled_interp_dep_var,
				color=self.color,
				linestyle=self.line_style,
				linewidth=self._ref_linewidth,
				drawstyle='steps-post' if self.interp == 'STEP' else 'default',
				label=self.label
			)
		# Plot markers
		if self.marker:
			fplot(
				self.scaled_indep_var,
				self.scaled_dep_var,
				color=self.color,
				linestyle='',
				linewidth=0,
				drawstyle='steps-post' if self.interp == 'STEP' else 'default',
				marker=self._marker_spec,
				markeredgecolor=self.color,
				markersize=self._ref_markersize,
				markeredgewidth=self._ref_markeredgewidth,
				markerfacecolor=self._ref_markerfacecolor,
				label=self.label if self.line_style is None else None
			)

	data_source = property(_get_data_source, _set_data_source, doc='Data source')
	"""
	Data source object. The independent and dependent data sets are obtained once the source is set.

	:type:	:py:class:`putil.plot.BasicSource()` object, :py:class:`putil.plot.CsvSource()` object or others conforming to the data source specification
	:raises:
	 * TypeError (Parameter `data_source` is of the wrong type)

	 * RuntimeError (Parameter `data_source` does not have `indep_var` attribute)

	 * RuntimeError (Parameter `data_source` does not have `dep_var` attribute)

	 * RuntimeError (Parameter `data_source` is not fully specified)

	 * Same as :py:meth:`putil.plot.BasicSource.indep_var` or :py:meth:`putil.plot.CsvSource.indep_var` or exceptions thrown by custom data source class while handling independent variable retrieval

	 * Same as :py:meth:`putil.plot.BasicSource.dep_var()` or :py:meth:`putil.plot.CsvSource.dep_var` or exceptions thrown by custom data source class while handling dependent variable retrieval

	.. note:: The data source object must have ``indep_var`` and ``dep_var`` attributes returning Numpy vectors to be valid.
	"""	#pylint: disable=W0105

	label = property(_get_label, _set_label, doc='Series label')
	"""
	Series label, to be used in panel legend

	:type:	string
	:raises: TypeError (Parameter `label` is of the wrong type)
	"""	#pylint: disable=W0105

	color = property(_get_color, _set_color, doc='Series line and marker color')
	"""
	Series line and marker color

	:type:	Matplotlib color
	:raises:
	 * TypeError (Parameter `color` is of the wrong type)

	 * TypeError (Invalid color specification)
	"""	#pylint: disable=W0105

	marker = property(_get_marker, _set_marker, doc='Plot data point markers flag')
	"""
	Plot data point markers flag

	:type:	boolean
	:raises: TypeError (Parameter `marker` is of the wrong type)
	"""	#pylint: disable=W0105

	interp = property(_get_interp, _set_interp, doc='Series interpolation option, one of `STRAIGHT`, `CUBIC` or `LINREG` (case insensitive)')
	"""
	Interpolation option, one of STRAIGHT, CUBIC or LINREG (case insensitive)

	:type:	string
	:raises:
	 * TypeError (Parameter `interp` is of the wrong type)

	 * ValueError (Parameter `interp` is not one of ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG'] (case insensitive))
	"""	#pylint: disable=W0105

	line_style = property(_get_line_style, _set_line_style, doc='Series line style, one of `-`, `--`, `-.` or `:`')
	"""
	Line style, one of `-`, `--`, `-.` or `:`

	:type:	Matplotlib line specification
	:raises:
	 * TypeError (Parameter `line_syle` is of the wrong type)

	 * ValueError (Parameter `line_style` is not one of ['-', '--', '-.', ':'] (case insensitive))
	"""	#pylint: disable=W0105

	secondary_axis = property(_get_secondary_axis, _set_secondary_axis, doc='Series secondary axis flag')
	"""
	Secondary axis flag. If true, the series belongs to the secondary (right) panel axis.

	:type:	boolean
	:raises: TypeError (Parameter `secondary_axis` is of the wrong type)
	"""	#pylint: disable=W0105

class Panel(object):	#pylint: disable=R0902,R0903
	"""
	Defines properties of a panel within a figure

	:param	series:					one or more data series
	:type	series:					:py:class:`putil.plot.Series()` object or list of :py:class:`putil.plot.Series()` objects
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
	:param	legend_props:			legend properties. See :py:meth:`putil.plot.Panel.legend_props()`
	:type	legend_props:			dictionary
	:raises:
	 * Same as :py:meth:`putil.plot.Panel.add_series()`

	 * Same as :py:meth:`putil.plot.Panel.primary_axis_label()`

	 * Same as :py:meth:`putil.plot.Panel.primary_axis_units()`

	 * Same as :py:meth:`putil.plot.Panel.log_dep_axis()`

	 * Same as :py:meth:`putil.plot.Panel.secondary_axis_label()`

	 * Same as :py:meth:`putil.plot.Panel.secondary_axis_units()`

	 * Same as :py:meth:`putil.plot.Panel.legend_props()`
	"""
	def __init__(self, series=None, primary_axis_label='', primary_axis_units='', secondary_axis_label='', secondary_axis_units='', log_dep_axis=False, legend_props={'pos':'BEST', 'cols':1}):	#pylint: disable=W0102,R0913
		# Private attributes
		self._series, self._primary_axis_label, self._secondary_axis_label, self._primary_axis_units, self._secondary_axis_units, self._log_dep_axis, self._legend_props = None, None, None, None, None, None, {'pos':'BEST', 'cols':1}
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
		self.legend_props_pos_list = ['BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER']
		self._set_series(series)
		self._set_primary_axis_label(primary_axis_label)
		self._set_primary_axis_units(primary_axis_units)
		self._set_secondary_axis_label(secondary_axis_label)
		self._set_secondary_axis_units(secondary_axis_units)
		self._set_log_dep_axis(log_dep_axis)
		self._set_legend_props(legend_props)

	def _get_series(self):	#pylint: disable=C0111
		return self._series

	def _set_series(self, series):	#pylint: disable=C0111,R0912
		self._series = (series if isinstance(series, list) else [series]) if series is not None else series
		if self.series is not None:
			self._validate_series()
			self.panel_has_primary_axis = any([not series_obj.secondary_axis for series_obj in self.series])
			self.panel_has_secondary_axis = any([series_obj.secondary_axis for series_obj in self.series])
			# Compute panel scaling factor
			global_primary_dep_var = list()
			global_secondary_dep_var = list()
			# Find union of the dependent variable data set of all panels
			for series_obj in self.series:
				if not series_obj.secondary_axis:
					global_primary_dep_var = numpy.unique(numpy.append(global_primary_dep_var, numpy.array([putil.misc.smart_round(element, 10) for element in series_obj.dep_var])))
					if series_obj.interp_dep_var is not None:
						global_primary_dep_var = numpy.unique(numpy.append(global_primary_dep_var, numpy.array([putil.misc.smart_round(element, 10) for element in series_obj.interp_dep_var])))
				else:
					global_secondary_dep_var = numpy.unique(numpy.append(global_secondary_dep_var, numpy.array([putil.misc.smart_round(element, 10) for element in series_obj.dep_var])))
					if series_obj.interp_dep_var is not None:
						global_secondary_dep_var = numpy.unique(numpy.append(global_secondary_dep_var, numpy.array([putil.misc.smart_round(element, 10) for element in series_obj.interp_dep_var])))
			# Primary axis
			if self.panel_has_primary_axis is True:
				self.primary_dep_var_min, self.primary_dep_var_max, self.primary_dep_var_div, self.primary_dep_var_unit_scale, self.primary_scaled_dep_var = \
					_scale_series(series=global_primary_dep_var, scale=True, scale_type='delta')
				self.primary_dep_var_min = putil.misc.smart_round(self.primary_dep_var_min, 10)
				self.primary_dep_var_max = putil.misc.smart_round(self.primary_dep_var_max, 10)
				self.primary_dep_var_locs, self.primary_dep_var_labels, self.primary_dep_var_min, self.primary_dep_var_max = \
					intelligent_ticks2(self.primary_scaled_dep_var, min(self.primary_scaled_dep_var), max(self.primary_scaled_dep_var), tight=False)
			# Secondary axis
			if self.panel_has_secondary_axis is True:
				self.secondary_dep_var_min, self.secondary_dep_var_max, self.secondary_dep_var_div, self.secondary_dep_var_unit_scale, self.secondary_scaled_dep_var = \
					_scale_series(series=global_secondary_dep_var, scale=True, scale_type='delta')
				self.secondary_dep_var_min = putil.misc.smart_round(self.secondary_dep_var_min, 10)
				self.secondary_dep_var_max = putil.misc.smart_round(self.secondary_dep_var_max, 10)
				self.secondary_dep_var_locs, self.secondary_dep_var_labels, self.secondary_dep_var_min, self.secondary_dep_var_max = \
					intelligent_ticks2(self.secondary_scaled_dep_var, min(self.secondary_scaled_dep_var), max(self.secondary_scaled_dep_var), tight=False)
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

	def _get_primary_axis_label(self):	#pylint: disable=C0111
		return self._primary_axis_label

	@putil.check.check_parameter('primary_axis_label', putil.check.PolymorphicType([None, str]))
	def _set_primary_axis_label(self, primary_axis_label):	#pylint: disable=C0111
		self._primary_axis_label = primary_axis_label

	def _get_primary_axis_units(self):	#pylint: disable=C0111
		return self._primary_axis_units

	@putil.check.check_parameter('primary_axis_units', putil.check.PolymorphicType([None, str]))
	def _set_primary_axis_units(self, primary_axis_units):	#pylint: disable=C0111
		self._primary_axis_units = primary_axis_units

	def _get_secondary_axis_label(self):	#pylint: disable=C0111
		return self._secondary_axis_label

	@putil.check.check_parameter('secondary_axis_label', putil.check.PolymorphicType([None, str]))
	def _set_secondary_axis_label(self, secondary_axis_label):	#pylint: disable=C0111
		self._secondary_axis_label = secondary_axis_label

	def _get_secondary_axis_units(self):	#pylint: disable=C0111
		return self._secondary_axis_units

	@putil.check.check_parameter('secondary_axis_units', putil.check.PolymorphicType([None, str]))
	def _set_secondary_axis_units(self, secondary_axis_units):	#pylint: disable=C0111
		self._secondary_axis_units = secondary_axis_units

	def _get_log_dep_axis(self):	#pylint: disable=C0111
		return self._log_dep_axis

	@putil.check.check_parameter('log_dep_axis', putil.check.PolymorphicType([None, bool]))
	def _set_log_dep_axis(self, log_dep_axis):	#pylint: disable=C0111
		self._log_dep_axis = log_dep_axis

	def _get_legend_props(self):	#pylint: disable=C0111
		return self._legend_props

	@putil.check.check_parameter('legend_props', putil.check.PolymorphicType([None, dict]))
	def _set_legend_props(self, legend_props):	#pylint: disable=C0111
		ref_pos_obj = putil.check.OneOf(self.legend_props_pos_list)
		self._legend_props = legend_props if legend_props is not None else {'pos':'BEST', 'cols':1}
		if self.legend_props is not None:
			self._legend_props.setdefault('pos', 'BEST')
			self._legend_props.setdefault('cols', 1)
			for key, value in self.legend_props.iteritems():
				if key not in self.legend_props_list:
					raise ValueError('Illegal legend property `{0}`'.format(key))
				elif (key == 'pos') and (not ref_pos_obj.includes(self.legend_props['pos'])):
					raise TypeError(ref_pos_obj.exception('pos')['msg'].replace('Parameter', 'Legend property'))
				elif ((key == 'cols') and (not isinstance(value, int))) or ((key == 'cols') and (isinstance(value, int) is True) and (value < 0)):
					raise TypeError('Legend property `cols` is of the wrong type')
			self._legend_props['pos'] = self._legend_props['pos'].upper()

	def __str__(self):
		"""
		Print panel information
		"""
		ret = ''
		if len(self.series) == 0:
			ret += 'Series: None\n'
		else:
			for num, element in enumerate(self.series):
				ret += 'Series {0}:\n'.format(num+1)
				temp = str(element).split('\n')
				temp = [3*' '+line for line in temp]
				ret += '\n'.join(temp)
				ret += '\n'
		ret += 'Primary axis label: {0}\n'.format(self.primary_axis_label)
		ret += 'Primary axis units: {0}\n'.format(self.primary_axis_units)
		ret += 'Secondary axis label: {0}\n'.format(self.secondary_axis_label)
		ret += 'Secondary axis units: {0}\n'.format(self.secondary_axis_units)
		ret += 'Logarithmic dependent axis: {0}\n'.format(self.log_dep_axis)
		if self.legend_props is None:
			ret += 'Legend properties: None'
		else:
			ret += 'Legend properties\n'
			for num, (key, value) in enumerate(self.legend_props.iteritems()):
				ret += '   {0}: {1}{2}'.format(key, value, '\n' if num+1 < len(self.legend_props) else '')
		return ret

	def _validate_series(self):
		""" Verifies that elements of series list are of the right type and fully specified """
		for num, obj in enumerate(self.series):
			if type(obj) is not Series:
				raise TypeError('Parameter `series` is of the wrong type')
			if not obj._complete():	#pylint: disable=W0212
				raise RuntimeError('Series element {0} is not fully specified'.format(num))

	def _complete(self):
		""" Returns True if panel is fully specified, otherwise returns False """
		return (self.series is not None) and (len(self.series) > 0)

	def _scale_indep_var(self, scaling_factor):
		""" Scale independent variable of panel series """
		for series_obj in self.series:
			series_obj._scale_indep_var(scaling_factor)	#pylint: disable=W0212

	def _scale_dep_var(self, primary_scaling_factor, secondary_scaling_factor):
		""" Scale dependent variable of panel series """
		for series_obj in self.series:
			if not series_obj.secondary_axis:
				series_obj._scale_dep_var(primary_scaling_factor)	#pylint: disable=W0212
			else:
				series_obj._scale_dep_var(secondary_scaling_factor)	#pylint: disable=W0212

	def _draw_panel(self, fig, axarr, indep_axis_dict=None):	#pylint: disable=R0912,R0914,R0915
		""" Draw panel series """
		if self.panel_has_secondary_axis is True:
			axarr_sec = axarr.twinx()
		# Place data series in their appropriate axis (primary or secondary)
		for series_obj in self.series:
			series_obj._draw_series(axarr if not series_obj.secondary_axis else axarr_sec, indep_axis_dict['log_indep'], self.log_dep_axis)	#pylint: disable=W0212
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
			if (self.primary_axis_label not in [None, '']) or (self.primary_axis_units not in [None, '']):
				unit_scale = '' if self.primary_dep_var_unit_scale is None else self.primary_dep_var_unit_scale
				axarr.yaxis.set_label_text(self.primary_axis_label + ('' if (unit_scale == '') and (self.primary_axis_units == '') else \
					(' ['+unit_scale+('-' if self.primary_axis_units == '' else self.primary_axis_units)+']')), fontdict={'fontsize':18})
				primary_height = max(primary_height, _get_text_prop(fig, axarr.yaxis.get_label())['height'])
				primary_width += 1.5*_get_text_prop(fig, axarr.yaxis.get_label())['width']
		else:
			axarr.yaxis.set_ticklabels([])
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
			if (self.secondary_axis_label not in [None, '']) or (self.secondary_axis_units not in [None, '']):
				unit_scale = '' if self.secondary_dep_var_unit_scale is None else self.secondary_dep_var_unit_scale
				axarr_sec.yaxis.set_label_text(self.secondary_axis_label + ('' if (unit_scale == '') and (self.secondary_axis_units == '') else \
					(' ['+unit_scale+('-' if self.secondary_axis_units == '' else self.secondary_axis_units)+']')), fontdict={'fontsize':18})
				secondary_height = max(secondary_height, _get_text_prop(fig, axarr.yaxis.get_label())['height'])
				secondary_width += 1.5*_get_text_prop(fig, axarr.yaxis.get_label())['width']
		# Print legends
		if (len(self.series) > 1) and (len(self.legend_props) > 0):
			primary_labels = []
			secondary_labels = []
			if self.panel_has_primary_axis is True:
				primary_handles, primary_labels = axarr.get_legend_handles_labels()	#pylint: disable=W0612
			if self.panel_has_secondary_axis is True:
				secondary_handles, secondary_labels = axarr_sec.get_legend_handles_labels()	#pylint: disable=W0612
			if (len(primary_labels) > 0) and (len(secondary_labels) > 0):
				labels = [r'$\Leftarrow$'+label for label in primary_labels]+ [label+r'$\Rightarrow$' for label in secondary_labels]
			else:
				labels = primary_labels+secondary_labels
			for label in labels:	# Only print legend if at least one series has a label
				if (label is not None) and (label != ''):
					legend_scale = 1.5
					leg_artist = [series_obj._legend_artist(legend_scale) for series_obj in self.series]	#pylint: disable=W0212
					axarr.legend(leg_artist, labels, ncol=self.legend_props['cols'] if 'cols' in self.legend_props else len(labels),
						loc=self.legend_pos_list[self.legend_pos_list.index(self.legend_props['pos'].lower() if 'pos' in self.legend_props else 'lower left')], numpoints=1, fontsize=18/legend_scale)
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
		return {'primary':None if not self.panel_has_primary_axis else axarr, 'secondary':None if not self.panel_has_secondary_axis else axarr_sec, 'min_height':min_panel_height, 'min_width':min_panel_width}

	series = property(_get_series, _set_series, doc='Panel series')
	"""
	Panel series

	:type:	:py:class:`putil.plot.Series()` object or list of :py:class:`putil.plot.Series()` objects
	:raises:
	 * RuntimeError (Series in panel have incongruent primary and secondary axis)

	 * TypeError (Series element is not a Series object)

	 * RuntimeError (Series element *[index]* is not fully specified)
	"""	#pylint: disable=W0105

	primary_axis_label = property(_get_primary_axis_label, _set_primary_axis_label, doc='Panel primary axis label')
	"""
	Panel primary axis label

	:type:	string
	:raises: TypeError (Parameter `primary_axis_label` is of the wrong type)
	"""	#pylint: disable=W0105

	secondary_axis_label = property(_get_secondary_axis_label, _set_secondary_axis_label, doc='Panel secondary axis label')
	"""
	Panel secondary axis label

	:type:	string
	:raises: TypeError (Parameter `secondary_axis_label` is of the wrong type)
	"""	#pylint: disable=W0105

	primary_axis_units = property(_get_primary_axis_units, _set_primary_axis_units, doc='Panel primary axis units')
	"""
	Panel primary axis units

	:type:	string
	:raises: TypeError (Parameter `primary_axis_units` is of the wrong type)
	"""	#pylint: disable=W0105

	secondary_axis_units = property(_get_secondary_axis_units, _set_secondary_axis_units, doc='Panel secondary axis units')
	"""
	Panel secondary axis units

	:type:	string
	:raises: TypeError (Parameter `secondary_axis_units` is of the wrong type)
	"""	#pylint: disable=W0105

	log_dep_axis = property(_get_log_dep_axis, _set_log_dep_axis, doc='Panel logarithmic dependent axis flag')
	"""
	Panel logarithmic dependent axis flag

	:type:	boolean
	:raises: TypeError (Parameter `log_dep_axis` is of the wrong type)
	"""	#pylint: disable=W0105

	legend_props = property(_get_legend_props, _set_legend_props, doc='Panel legend box properties')
	"""
	Panel legend box properties

	:type	props:	dictionary
	:rtype:			dictionary
	:raises:
	 * TypeError (Parameter `legend_props` is of the wrong type)

	 * TypeError (Parameter `legend_props` key `props` is not one of BEST, UPPER RIGHT, UPPER LEFT, LOWER LEFT, LOWER RIGHT, RIGHT, CENTER LEFT, CENTER RIGHT, LOWER CENTER, UPPER CENTER or CENTER (case insensitive))

	 * TypeError ((Parameter `legend_props` key `cols` is of the wrong type)

	.. note:: No legend is shown if a panel has only one series in it

	.. note:: Currently supported properties are

	     * **pos** (*string*) -- legend position, one of BEST, UPPER RIGHT, UPPER LEFT, LOWER LEFT, LOWER RIGHT, RIGHT, CENTER LEFT, CENTER RIGHT, LOWER CENTER, UPPER CENTER or CENTER (case insensitive).

	     * **cols** (integer) -- number of columns in the legend box
	"""	#pylint: disable=W0105

class Figure(object):	#pylint: disable=R0902
	"""
	Automagically generate presentation-quality plots

	:param	panel:				one or more data panels
	:type	panel:				:py:class:`putil.plot.Panel()` object or list of :py:class:`putil.plot.Panel()` objects
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
	 * Same as :py:meth:`putil.plot.Figure.add_panel()`

	 * Same as :py:meth:`putil.plot.Figure.indep_var_label()`

	 * Same as :py:meth:`putil.plot.Figure.indep_var_units()`

	 * Same as :py:meth:`putil.plot.Figure.title()`

	 * Same as :py:meth:`putil.plot.Figure.log_indep()`

	 * Same as :py:meth:`putil.plot.Figure.figure_width()`

	 * Same as :py:meth:`putil.plot.Figure.figure_height()`

	.. note:: The appropriate figure dimensions so that no labels are obstructed are calculated and used if **fig_width** and/or **fig_height** are not specified. The calculated figure width and/or height can be retrieved using \
	:py:meth:`putil.plot.Figure.figure_width()` and/or :py:meth:`putil.plot.Figure.figure_height()` methods.
	"""
	def __init__(self, panel=None, indep_var_label='', indep_var_units='', fig_width=None, fig_height=None, title='', log_indep=False):	#pylint: disable=R0913
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
		:type	panel:	:py:class:`putil.plot.Panel()` object or list of :py:class:`putil.plot.panel()` objects
		:raises:
		 * TypeError (Panels must be provided in list form)

		 * TypeError (Panel element is not a panel object)

		 * RuntimeError (Panel element *[number]* is not fully specified)
		"""
		if panel is not None:
			panel = [panel] if isinstance(panel, Panel) is True else panel
			if not isinstance(panel, list):
				raise TypeError('Panels must be provided in list form')
			for num, obj in enumerate(panel):
				if not isinstance(obj, Panel):
					raise TypeError('Panel element is not a panel object')
				elif not obj._complete():	#pylint: disable=W0212
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
		if not isinstance(self.current_indep_var_label, str):
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
		if not isinstance(self.current_indep_var_units, str):
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
		if not isinstance(self.current_title, str):
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
		if not isinstance(self.current_log_indep, bool):
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
			if not putil.misc.isnumber(self.current_fig_width):
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
			if not putil.misc.isnumber(self.current_fig_height):
				raise TypeError('Figure height must be a number')
			if self.current_fig_height < 0:
				raise ValueError('Figure height must be a positive number')
			self.current_fig_height = float(self.current_fig_height)

	def draw(self):
		"""
		Generates figure

		:raises:	RuntimeError (Figure is not fully specified)
		"""
		if not self._complete():
			raise RuntimeError('Figure is not fully specified')
		num_panels = len(self.current_panel_list)
		plt.close('all')
		# Create required number of panels
		self.fig, self.axarr = plt.subplots(num_panels, sharex=True)	#pylint: disable=W0612
		self.axarr = self.axarr if num_panels > 1 else [self.axarr]
		global_indep_var = list()
		# Find union of the independent variable data set of all panels
		for panel_obj in self.current_panel_list:
			for series_obj in panel_obj.series:
				global_indep_var = numpy.unique(numpy.append(global_indep_var, numpy.array([putil.misc.smart_round(element, 10) for element in series_obj.indep_var])))
		self.indep_var_min, self.indep_var_max, self.indep_var_div, self.indep_var_unit_scale, self.scaled_indep_var = _scale_series(series=global_indep_var, scale=True, scale_type='delta')
		self.indep_var_min = putil.misc.smart_round(self.indep_var_min, 10)
		self.indep_var_max = putil.misc.smart_round(self.indep_var_max, 10)
		import pdb; pdb.set_trace()
		indep_var_locs, indep_var_labels, self.indep_var_min, self.indep_var_max = intelligent_ticks2(self.scaled_indep_var, min(self.scaled_indep_var), max(self.scaled_indep_var), tight=True, calc_ticks=False)
		# Scale all panel series
		for panel_obj in self.current_panel_list:
			panel_obj._scale_indep_var(self.indep_var_div)	#pylint: disable=W0212
		# Draw panels
		indep_axis_dict = {'indep_var_min':self.indep_var_min, 'indep_var_max':self.indep_var_max, 'indep_var_locs':indep_var_locs,
					 'indep_var_labels':None, 'indep_axis_label':None, 'indep_axis_units':None, 'indep_axis_unit_scale':None}
		for num, (panel_obj, axarr) in enumerate(zip(self.current_panel_list, self.axarr)):
			panel_dict = panel_obj._draw_panel(self.fig, axarr, dict(indep_axis_dict, log_indep=self.log_indep(), indep_var_labels=indep_var_labels if num == num_panels-1 else None,	#pylint: disable=W0212,C0326
												  indep_axis_label=self.indep_var_label() if num == num_panels-1 else None, indep_axis_units=self.indep_var_units() if num == num_panels-1 else None,
												  indep_axis_unit_scale = self.indep_var_unit_scale if num == num_panels-1 else None))	#pylint: disable=C0326
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

	def show(self):	#pylint: disable=R0201
		"""
		Displays figure

		:raises:
		 * Same as :py:meth:`putil.plot.Figure.draw()`
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

		 * Same as :py:meth:`putil.plot.Figure.draw()`
		"""
		if not isinstance(file_name, str):
			raise TypeError('File name must be a string')
		if self.fig is None:
			self.draw()
		# Calculate minimum figure dimensions
		axarr = self.axarr_list[0]['primary']
		legend_obj = axarr.get_legend()	#pylint: disable=W0612
		min_fig_width = (max(self.title_width, max([panel_dict['min_width'] for panel_dict in self.axarr_list])))/float(self.fig.dpi)
		min_fig_height = ((len(self.axarr_list)-1)*0.00)+(((len(self.axarr_list)*max([panel_dict['min_height'] for panel_dict in self.axarr_list]))+self.title_height)/float(self.fig.dpi))
		self.figure_width(min_fig_width if self.figure_width() is None else self.figure_width())
		self.figure_height(min_fig_height if self.figure_height() is None else self.figure_height())
		self.fig.set_size_inches(max(min_fig_width, self.figure_width()), max(min_fig_height, self.figure_height()))
		file_name = os.path.expanduser(file_name)	# Matplotlib seems to have a problem with ~/, expand it to $HOME
		putil.misc.make_dir(file_name)
		self.fig.savefig(file_name, dpi=self.fig.dpi)
		self.fig.savefig(file_name, bbox_inches='tight', dpi=self.fig.dpi)
		plt.close('all')

def _scale_series(series, scale=False, series_min=None, series_max=None, scale_type='delta'):	#pylint: disable=R0913
	"""
	Scales series, 'delta' with the series span, 'min' with the series minimum
	"""
	series_min = min(series) if series_min is None else series_min
	series_max = max(series) if series_max is None else series_max
	series_delta = series_max-series_min
	if not scale:
		(unit, div) = (' ', 1)
	else:
		(unit, div) = putil.eng.peng_power(putil.eng.peng(series_delta if scale_type == 'delta' else (series_min if scale_type == 'min' else series_max), 3))
		(first_unit, first_div) = putil.eng.peng_power(putil.eng.peng(series_min/div, 3))	#pylint: disable=W0612
		if abs(1.00-(div*first_div)) < 1e-10:
			(unit, div) = putil.eng.peng_power(putil.eng.peng(series_min, 3))
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
	raw_labels = [putil.eng.peng(float(loc), mant, rjust=False) if ((abs(loc) >= 1) or (loc == 0)) else str(putil.misc.smart_round(loc, mant)) for loc in bounded_locs]
	return (bounded_locs, [label.replace('u', '$\\mu$') for label in raw_labels])

def intelligent_ticks2(series, series_min, series_max, tight=True, calc_ticks=True):	#pylint: disable=R0912,R0914,R0915
	""" Calculates ticks 'intelligently', trying to calculate sane tick spacing """
	calc_ticks = calc_ticks
	tight = tight
	max_ticks = 10
	min_ticks = 6
	# Handle 1-point series
	if len(series) == 1:
		series_min = series_max = series[0]
		tick_list = [series_min, series[0], series_max]
		tight = False
	else:
		series_delta = putil.misc.smart_round(float(series_max-series_min), PRECISION)
		working_series = series[:]
		tick_list = list()
		num_ticks = max_ticks
		spacing_gcd = 2
		while (num_ticks >= min_ticks) and (spacing_gcd > 1):
			data_spacing = [putil.misc.smart_round(element, PRECISION) for element in numpy.diff(working_series)]
			spacing_gcd = putil.misc.gcd(data_spacing)
			num_ticks = (series_delta/spacing_gcd)+1
			if (num_ticks >= min_ticks) and (num_ticks <= max_ticks):
				tick_list = numpy.linspace(putil.misc.smart_round(min(series), PRECISION), putil.misc.smart_round(max(series), PRECISION), num_ticks)
				break
			min_data_spacing = min(data_spacing)
			working_series = [element for element, spacing in zip(series[1:], data_spacing) if spacing != min_data_spacing]
		tick_list = tick_list if len(tick_list) > 0 else numpy.linspace(min(series), max(series), max_ticks)
	tick_list = numpy.array(tick_list)
	opt_min = _scale_ticks(tick_list, 'MIN')
	opt_max = _scale_ticks(tick_list, 'MAX')
	opt_delta = _scale_ticks(tick_list, 'DELTA')
	opt = opt_min if (opt_min['count'] <= opt_max['count']) and (opt_min['count'] <= opt_delta['count']) else (opt_max if (opt_max['count'] <= opt_min['count']) and (opt_max['count'] <= opt_delta['count']) else opt_max)
	#return (opt['loc'], opt['labels'], opt['min'], opt['max'], opt['unit'])
	return (opt['loc'], opt['labels'], opt['min'], opt['max'])

def _scale_ticks(tick_list, mode):
	""" Scale series taking the reference to be the series start, stop or delta """
	mode = mode.strip().upper()
	tick_min = tick_list[0]
	tick_max = tick_list[-1]
	tick_delta = tick_max-tick_min
	tick_ref = tick_min if mode == 'MIN' else (tick_max if mode == 'MAX' else tick_delta)
	(unit, scale) = putil.eng.peng_power(putil.eng.peng(tick_ref, 3))
	rollback = sum((tick_list/scale) >= 1000) > sum((tick_list/scale) < 1000)
	scale = 1 if rollback else scale
	unit = putil.eng.peng_unit_math(unit, +1) if rollback else unit
	tick_list = numpy.array([putil.misc.smart_round(element/scale, PRECISION) for element in tick_list])
	tick_min = putil.misc.smart_round(tick_min/scale, PRECISION)
	tick_max = putil.misc.smart_round(tick_max/scale, PRECISION)
	loc, labels = _uniquify_tick_labels(tick_list, tick_min, tick_max)
	count = len(''.join(labels))
	return {'loc':loc, 'labels':labels, 'unit':unit, 'min':tick_min, 'max':tick_max, 'count':count}

def _intelligent_ticks(series, series_min, series_max, tight=True, calc_ticks=True):	#pylint: disable=R0912,R0914,R0915
	"""
	Calculates ticks 'intelligently', trying to calculate sane tick spacing
	"""
	ideal_num_ticks = 8
	series_delta = float(series_max-series_min)
	num_ticks = 0
	sdiff = [1 if int(element) == element else 0 for element in [putil.misc.smart_round(element, 10) for element in numpy.diff(series)]]	#pylint: disable=E1101
	int_scale = True if sum(sdiff) == len(sdiff) else False
	min_num_ticks = 2 if series_delta == 0 else (ideal_num_ticks if int_scale is False else min(ideal_num_ticks, series_delta))
	div = 1 if (series_delta == 0) or (int_scale is True) else 10.0
	tick_list = None
	if calc_ticks is False:
		# Calculate spacing between points
		tspace = numpy.diff(series)	#pylint: disable=E1101
		# Find minimum common spacing
		factors = [putil.eng.peng_power(putil.eng.peng(element, 3)) for element in tspace]
		divs = [div for (unit, div) in factors]	#pylint: disable=W0612
		tspace_div = min(divs)
		scaled_tspace = numpy.round(numpy.array(tspace)/tspace_div, 10)	#pylint: disable=E1101
		tspace_gcd = 0.5*putil.misc.gcd(scaled_tspace)
		num_ticks = 1
		while num_ticks > min_num_ticks:
			tspace_gcd = 2*tspace_gcd
			# Find out number of ticks with the minimum common spacing
			num_ticks = round(1+((series_max-series_min)/(tspace_div*float(tspace_gcd))), 10)
			if (int(putil.misc.smart_round(num_ticks, 10)) == round(num_ticks, 10)) and (int(putil.misc.smart_round(num_ticks, 10)) >= min_num_ticks):
				num_ticks = int(round(num_ticks, 10))
				tstop = series[-1]
				tspace = tspace_gcd*tspace_div
				tick_list = numpy.linspace(series_min, series_max, num_ticks)	#pylint: disable=E1101
				calc_ticks = False
	calc_ticks = True if tick_list is None else calc_ticks
	if calc_ticks is True:
		if (series_delta != 0) and (int_scale is True):
			step = 1 if series_delta <= ideal_num_ticks else math.ceil((series_max-series_min)/ideal_num_ticks)
			tick_list = [series_min-step]+[series_min+num*step for num in range(1+int(putil.misc.smart_round(series_delta, 10)) if series_delta <= ideal_num_ticks else ideal_num_ticks)]
			tstart = tick_list[0]
			tstop = tick_list[-1]
		else:
			# round() allows for deltas closer to the next engineering unit to get the bigger scale while deltas closer to the smaller engineering scale get smaller scale
			scale = 1.0 if (series_delta == 0) or (int_scale is True) else 10**(round(math.log10(putil.eng.peng_int(putil.eng.peng(series_delta, 3)))))
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
		if (str(putil.eng.peng_mant(putil.eng.peng(tick_list[-1], mant)))[-1] != '0') or (str(putil.eng.peng_mant(putil.eng.peng(tick_list[-2], mant)))[-1] != '0'):
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
	indexes = numpy.where(numpy.array(indep_var) >= threshold) if threshold_type.upper() == 'MIN' else numpy.where(numpy.array(indep_var) <= threshold)  #pylint: disable=E1101
	indep_var = numpy.array(indep_var)[indexes]  #pylint: disable=E1101
	dep_var = numpy.array(dep_var)[indexes]  #pylint: disable=E1101
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
		if putil.misc.isnumber(element) is False:
			raise TypeError('Element {0} ({1}) is not a number'.format(num, element))
		if (element < 0) or (element > 1):
			raise ValueError('Element {0} ({1}) is out of normal range [0, 1]'.format(num, element))
	if putil.misc.isnumber(offset) is False:
		raise TypeError('Offset has to be a number')
	if (offset < 0) or (offset > 1):
		raise ValueError('Offset is out of normal range [0, 1]')
	color_name_list = ['binary', 'Blues', 'BuGn', 'BuPu', 'gist_yarg', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']
	color_pallete_list = [plt.cm.binary, plt.cm.Blues, plt.cm.BuGn, plt.cm.BuPu, plt.cm.gist_yarg, plt.cm.GnBu, plt.cm.Greens, plt.cm.Greys, plt.cm.Oranges, plt.cm.OrRd, plt.cm.PuBu,	#pylint: disable=E1101
					   plt.cm.PuBuGn, plt.cm.PuRd, plt.cm.Purples, plt.cm.RdPu, plt.cm.Reds, plt.cm.YlGn, plt.cm.YlGnBu, plt.cm.YlOrBr, plt.cm.YlOrRd]	#pylint: disable=E1101
	if color not in color_name_list:
		raise ValueError('Color pallete is not valid')
	color_dict = dict(zip(color_name_list, color_pallete_list))
	#color_dict = {'binary':plt.cm.binary, 'Blues':plt.cm.Blues, 'BuGn':plt.cm.BuGn, 'BuPu':plt.cm.BuPu, 'gist_yarg':plt.cm.gist_yarg, 'GnBu':plt.cm.GnBu, 'Greens':plt.cm.Greens, 'Greys':plt.cm.Greys,	#pylint: disable=E1101
	#		'Oranges':plt.cm.Oranges, 'OrRd':plt.cm.OrRd, 'PuBu':plt.cm.PuBu, 'PuBuGn':plt.cm.PuBuGn, 'PuRd':plt.cm.PuRd, 'Purples':plt.cm.Purples, 'RdPu':plt.cm.RdPu, 'Reds':plt.cm.Reds,	#pylint: disable=E1101
	#		'YlGn':plt.cm.YlGn, 'YlGnBu':plt.cm.YlGnBu, 'YlOrBr':plt.cm.YlOrBr, 'YlOrRd':plt.cm.YlOrRd}	#pylint: disable=E1101
	return [color_dict[color](putil.misc.normalize(value, series, offset)) for value in series]	#pylint: disable=E1101
