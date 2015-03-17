# plot.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302

import os
import math
import numpy
import inspect
from scipy import stats
import matplotlib.path
import matplotlib.markers
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d  #pylint: disable=E0611
from matplotlib.backends.backend_agg import FigureCanvasAgg
from collections import OrderedDict

import putil.exh
import putil.eng
import putil.pcsv
import putil.misc
import putil.check
import putil.pcontracts

# Exception tracing initialization code
"""
[[[cog
import trace_ex_plot
exobj_plot = trace_ex_plot.trace_module(no_print=True)
]]]
[[[end]]]
"""	#pylint: disable=W0105

###
# Module properties
###
PRECISION = 10
"""
Number of mantissa significant digits used in all computations

:type:	integer
"""	#pylint: disable=W0105

LINE_WIDTH = 2.5
"""
Series line width in points

:type: float
"""	#pylint: disable=W0105

MARKER_SIZE = 14
"""
Series marker size in points

:type: integer
"""	#pylint: disable=W0105

MIN_TICKS = 6
"""
Minimum number of ticks desired for the independent and dependent axis of a panel

:type:	integer
"""	#pylint: disable=W0105

SUGGESTED_MAX_TICKS = 10
"""
Maximum number of ticks desired for the independent and dependent axis of a panel. It is possible for a panel to have more than SUGGESTED_MAX_TICKS in the dependent axis
if one or more series are plotted with an interpolation function and at least one interpolated curve goes above or below the maximum and minimum data
points of the panel. In this case the panel will have SUGGESTED_MAX_TICKS+1 ticks if some interpolation curve is above the maximum data point of the panel or
below the minimum data point of the panel; or the panel will have SUGGESTED_MAX_TICKS+2 ticks if some interpolation curve(s) is(are) above the maximum data point
of the panel and below the minimum data point of the panel.

:type:	integer
"""	#pylint: disable=W0105

TITLE_FONT_SIZE = 24
"""
Font size in points for figure title

:type:	integer
"""	#pylint: disable=W0105

AXIS_LABEL_FONT_SIZE = 18
"""
Font size in points for axis labels

:type:	integer
"""	#pylint: disable=W0105

AXIS_TICKS_FONT_SIZE = 14
"""
Font size in points for axis tick labels

:type:	integer
"""	#pylint: disable=W0105

LEGEND_SCALE = 1.5
"""
Scale factor for panel legend. The legend font size in points is equal to the axis font size divided by the legend scale.

:type:	number
"""	#pylint: disable=W0105

###
# Contracts
###
@putil.pcontracts.new_contract()
def real_num(num):
	r"""
	Contract to validate if a number is an integer or a float

	:param	vector: Real number (float or integer) or None
	:type	vector: RealNum
	:raises: :code:`RuntimeError ('Argument \`*[argument_name]*\` is not valid')`. The token :code:`'*[argument_name]*'` is replaced by the *name* of the argument the contract is attached to

	:rtype: None
	"""
	if (num == None) or ((isinstance(num, int) or isinstance(num, float)) and (not isinstance(num, bool))):
		return None
	raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def function(obj):
	r"""
	Contract to validate if an object is a function pointer

	:param	vector: Function object
	:type	vector: Function object
	:raises: :code:`RuntimeError ('Argument \`*[argument_name]*\` is not valid')`. The token :code:`'*[argument_name]*'` is replaced by the *name* of the argument the contract is attached to

	:rtype: None
	"""
	if (obj == None) or inspect.isfunction(obj):
		return None
	raise ValueError(putil.pcontracts.get_exdesc())


def _check_real_numpy_vector(vector):
	if (type(vector) != numpy.ndarray) or ((type(vector) == numpy.ndarray) and ((len(vector.shape) > 1) or ((len(vector.shape) == 1) and (vector.shape[0] == 0)))):
		return True
	if (vector.dtype.type == numpy.array([0]).dtype.type) or (vector.dtype.type == numpy.array([0.0]).dtype.type):
		return False
	return True


@putil.pcontracts.new_contract()
def real_numpy_vector(vector):
	r"""
	Contract to validate if the elements of a Numpy vector contains integer or floating numbers

	:param	vector: Numpy vector in which each item is a number
	:type	vector: RealNumpyVector
	:raises: :code:`RuntimeError ('Argument \`*[argument_name]*\` is not valid')`. The token :code:`'*[argument_name]*'` is replaced by the *name* of the argument the contract is attached to

	:rtype: None
	"""
	if _check_real_numpy_vector(vector):
		raise ValueError(putil.pcontracts.get_exdesc())


def _check_increasing_real_numpy_vector(vector):	#pylint: disable=C0103
	if (type(vector) != numpy.ndarray) or ((type(vector) == numpy.ndarray) and ((len(vector.shape) > 1) or ((len(vector.shape) == 1) and (vector.shape[0] == 0)))):
		return True
	if ((vector.dtype.type == numpy.array([0]).dtype.type) or (vector.dtype.type == numpy.array([0.0]).dtype.type)) and ((vector.shape[0] == 1) or ((vector.shape[0] > 1) and (not min(numpy.diff(vector)) <= 0))):
		return False
	return True


@putil.pcontracts.new_contract()
def increasing_real_numpy_vector(vector):
	r"""
	Contract to validate if the elements of a Numpy vector contains numbers that are monotonically increasing

	:param	vector: Non-empty Numpy vector in which each item is a number strictly greater than the previous one
	:type	vector: IncreasingNumpyVector
	:raises: :code:`RuntimeError ('Argument \`*[argument_name]*\` is not valid')`. The token :code:`'*[argument_name]*'` is replaced by the *name* of the argument the contract is attached to

	:rtype: None
	"""
	if _check_increasing_real_numpy_vector(vector):
		raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract(argument_invalid='Argument `*[argument_name]*` is not valid',\
							   argument_bad_choice=(ValueError, "Argument `*[argument_name]*` is not one of ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG'] (case insensitive)"))
def interpolation_option(option):
	r"""
	Contract to validate if a string is a valid series interpolation type

	:param	option: Series interpololation type, one of *None*, 'STRAIGHT', 'STEP', 'CUBIC' or 'LINREG'
	:type	option: string
	:raises:
	 * :code:`RuntimeError ('Argument \`*[argument_name]*\` is not valid')`. The token :code:`'*[argument_name]*'` is replaced by the *name* of the argument the contract is attached to

	 * :code:`RuntimeError ('Argument \`*[argument_name]*\` is not one of ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG'] (case insensitive)')`. The token :code:`'*[argument_name]*'` is replaced by the *name* of the argument
	   the contract is attached to

	:rtype: None
	"""
	exdesc = putil.pcontracts.get_exdesc()
	if (option != None) and (not isinstance(option, str)):
		raise ValueError(exdesc['argument_invalid'])
	if (option == None) or (option and any([item.lower() == option.lower() for item in ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']])):
		return None
	raise ValueError(exdesc['argument_bad_choice'])


@putil.pcontracts.new_contract(argument_invalid='Argument `*[argument_name]*` is not valid', argument_bad_choice=(ValueError, "Argument `*[argument_name]*` is not one of ['-', '--', '-.', ':']"))
def line_style_option(option):
	r"""
	Contract to validate if a string is a valid Matplot lib line style

	:param	option: Series line style, one of *None*, '-', '--', '-.' or ':'
	:type	option: string
	:raises:
	 * :code:`RuntimeError ('Argument \`*[argument_name]*\` is not valid')`. The token :code:`'*[argument_name]*'` is replaced by the *name* of the argument the contract is attached to

	 * :code:`RuntimeError ('Argument \`*[argument_name]*\` is not one of ['-', '--', '-.', ':']')`. The token :code:`'*[argument_name]*'` is replaced by the *name* of the argument the contract is attached to

	:rtype: None
	"""
	exdesc = putil.pcontracts.get_exdesc()
	if (option != None) and (not isinstance(option, str)):
		raise ValueError(exdesc['argument_invalid'])
	if option in [None, '-', '--', '-.', ':']:
		return None
	raise ValueError(exdesc['argument_bad_choice'])


def _legend_position_validation(option):
	""" Contract to validate if a string is a valid legend position """
	if (option != None) and (not isinstance(option, str)):
		return True
	if (option == None) or (option and any([item.lower() == option.lower() for item in\
			['BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER']])):
		return False
	return True


###
# Classes
###
class BasicSource(object):	#pylint: disable=R0902,R0903
	"""
	Objects of this class hold a given data set intended for plotting. It is intended as a convenient way to plot manually-entered data or data coming from
	a source that does not export to a comma-separated values (CSV) file.

	:param	indep_var:			independent variable vector
	:type	indep_var:			increasing real Numpy vector
	:param	dep_var:			dependent variable vector
	:type	dep_var:			real Numpy vector
	:param	indep_min:			minimum independent variable value
	:type	indep_min:			number or None
	:param	indep_max:			maximum independent variable value
	:type	indep_max:			number or None
	:rtype:						:py:class:`putil.plot.BasicSource()` object

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.BasicSource.__init__

	:raises:
	 * RuntimeError (Argument `dep_var` is not valid)

	 * RuntimeError (Argument `indep_max` is not valid)

	 * RuntimeError (Argument `indep_min` is not valid)

	 * RuntimeError (Argument `indep_var` is not valid)

	 * ValueError (Argument `indep_min` is greater than argument `indep_max`)

	 * ValueError (Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding)

	 * ValueError (Arguments `indep_var` and `dep_var` must have the same number of elements)

	.. [[[end]]]
	"""
	def __init__(self, indep_var, dep_var, indep_min=None, indep_max=None):
		# Private attributes
		self._exh = putil.exh.get_or_create_exh_obj()
		self._raw_indep_var, self._raw_dep_var, self._indep_var_indexes, self._min_indep_var_index, self._max_indep_var_index = None, None, None, None, None
		# Public attributes
		self._indep_var, self._dep_var, self._indep_min, self._indep_max = None, None, None, None
		# Assignment of arguments to attributes
		# Assign minimum and maximum first so as not to trigger unnecessary tresholding if the dependent and independent variables are already assigned
		self._set_indep_min(indep_min)
		self._set_indep_max(indep_max)
		self._set_indep_var(indep_var)
		self._set_dep_var(dep_var)

	def _get_indep_var(self):	#pylint: disable=C0111
		return self._indep_var	#pylint: disable=W0212

	@putil.pcontracts.contract(indep_var='increasing_real_numpy_vector')
	def _set_indep_var(self, indep_var):	#pylint: disable=C0111
		self._exh.add_exception(exname='num_elements', extype=ValueError, exmsg='Arguments `indep_var` and `dep_var` must have the same number of elements')
		self._exh.raise_exception_if(exname='num_elements', condition=(indep_var is not None) and (self._raw_dep_var is not None) and (len(self._raw_dep_var) != len(indep_var)))	#pylint: disable=W0212
		self._raw_indep_var = putil.misc.smart_round(indep_var, PRECISION)	#pylint: disable=W0212
		self._update_indep_var()	# Apply minimum and maximum range bounding and assign it to self._indep_var and thus this is what self.indep_var returns	#pylint: disable=W0212
		self._update_dep_var()	#pylint: disable=W0212

	def _get_dep_var(self):	#pylint: disable=C0111
		return self._dep_var	#pylint: disable=W0212

	@putil.pcontracts.contract(dep_var='real_numpy_vector')
	def _set_dep_var(self, dep_var):	#pylint: disable=C0111
		self._exh.add_exception(exname='num_elements', extype=ValueError, exmsg='Arguments `indep_var` and `dep_var` must have the same number of elements')
		self._exh.raise_exception_if(exname='num_elements', condition=(dep_var is not None) and (self._raw_indep_var is not None) and (len(self._raw_indep_var) != len(dep_var)))	#pylint: disable=W0212
		self._raw_dep_var = putil.misc.smart_round(dep_var, PRECISION)	#pylint: disable=W0212
		self._update_dep_var()	#pylint: disable=W0212

	def _get_indep_min(self):	#pylint: disable=C0111
		return self._indep_min	#pylint: disable=W0212

	@putil.pcontracts.contract(indep_min='real_num')
	def _set_indep_min(self, indep_min):	#pylint: disable=C0111
		self._exh.add_exception(exname='min_max', extype=ValueError, exmsg='Argument `indep_min` is greater than argument `indep_max`')
		self._exh.raise_exception_if(exname='min_max', condition=(self.indep_max is not None) and (indep_min is not None) and (self.indep_max < indep_min))
		self._indep_min = putil.misc.smart_round(indep_min, PRECISION) if not isinstance(indep_min, int) else indep_min	#pylint: disable=W0212
		self._update_indep_var()	# Apply minimum and maximum range bounding and assign it to self._indep_var and thus this is what self.indep_var returns	#pylint: disable=W0212
		self._update_dep_var()	#pylint: disable=W0212

	def _get_indep_max(self):	#pylint: disable=C0111
		return self._indep_max	#pylint: disable=W0212

	@putil.pcontracts.contract(indep_max='real_num')
	def _set_indep_max(self, indep_max):	#pylint: disable=C0111
		self._exh.add_exception(exname='min_max', extype=ValueError, exmsg='Argument `indep_min` is greater than argument `indep_max`')
		self._exh.raise_exception_if(exname='min_max', condition=(self.indep_min is not None) and (indep_max is not None) and (indep_max < self.indep_min))
		self._indep_max = putil.misc.smart_round(indep_max, PRECISION) if not isinstance(indep_max, int) else indep_max	#pylint: disable=W0212
		self._update_indep_var()	# Apply minimum and maximum range bounding and assign it to self._indep_var and thus this is what self.indep_var returns	#pylint: disable=W0212
		self._update_dep_var()	#pylint: disable=W0212

	def _update_indep_var(self):
		""" Update independent variable according to its minimum and maximum limits """
		self._exh.add_exception(exname='empty', extype=ValueError, exmsg='Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding')
		if self._raw_indep_var is not None:	#pylint: disable=W0212
			min_indexes = (self._raw_indep_var >= (self.indep_min if self.indep_min is not None else self._raw_indep_var[0]))	#pylint: disable=W0212
			max_indexes = (self._raw_indep_var <= (self.indep_max if self.indep_max is not None else self._raw_indep_var[-1]))	#pylint: disable=W0212
			self._indep_var_indexes = numpy.where(min_indexes & max_indexes)	#pylint: disable=W0212
			self._indep_var = self._raw_indep_var[self._indep_var_indexes]	#pylint: disable=W0212
			self._exh.raise_exception_if(exname='empty', condition=len(self.indep_var) == 0)

	def _update_dep_var(self):
		""" Update dependent variable (if assigned) to match the independent variable range bounding """
		self._dep_var = self._raw_dep_var	#pylint: disable=W0212
		if (self._indep_var_indexes is not None) and (self._raw_dep_var is not None):	#pylint: disable=W0212
			self._dep_var = self._raw_dep_var[self._indep_var_indexes]	#pylint: disable=W0212

	def __str__(self):
		""" Print comma-separated value source information """
		ret = ''
		ret += 'Independent variable minimum: {0}\n'.format('-inf' if self.indep_min is None else self.indep_min)	#pylint: disable=W0212
		ret += 'Independent variable maximum: {0}\n'.format('+inf' if self.indep_max is None else self.indep_max)	#pylint: disable=W0212
		ret += 'Independent variable: {0}\n'.format(putil.misc.pprint_vector(self.indep_var, width=50, indent=len('Independent variable: ')))	#pylint: disable=W0212
		ret += 'Dependent variable: {0}'.format(putil.misc.pprint_vector(self.dep_var, width=50, indent=len('Dependent variable: ')))	#pylint: disable=W0212
		return ret

	def _complete(self):
		""" Returns True if object is fully specified, otherwise returns False """
		return (self.indep_var is not None) and (self.dep_var is not None)

	# Managed attributes
	indep_min = property(_get_indep_min, _set_indep_min, None, doc='Minimum of independent variable')
	"""
	Minimum independent variable limit

	:type:		number or None, default is *None*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.BasicSource.indep_min

	:raises: (when assigned)

	 * RuntimeError (Argument `indep_min` is not valid)

	 * ValueError (Argument `indep_min` is greater than argument `indep_max`)

	 * ValueError (Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	indep_max = property(_get_indep_max, _set_indep_max, None, doc='Maximum of independent variable')
	"""
	Maximum independent variable limit

	:type:		number or None, default is *None*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.BasicSource.indep_max

	:raises: (when assigned)

	 * RuntimeError (Argument `indep_max` is not valid)

	 * ValueError (Argument `indep_min` is greater than argument `indep_max`)

	 * ValueError (Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	indep_var = property(_get_indep_var, _set_indep_var, None, doc='Independent variable Numpy vector')
	"""
	Independent variable data

	:type:		increasing real Numpy vector

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.BasicSource.indep_var

	:raises: (when assigned)

	 * RuntimeError (Argument `indep_var` is not valid)

	 * ValueError (Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding)

	 * ValueError (Arguments `indep_var` and `dep_var` must have the same number of elements)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	dep_var = property(_get_dep_var, _set_dep_var, None, doc='Dependent variable Numpy vector')
	"""
	Dependent variable data

	:type:		real Numpy vector

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.BasicSource.dep_var

	:raises: (when assigned)

	 * RuntimeError (Argument `dep_var` is not valid)

	 * ValueError (Arguments `indep_var` and `dep_var` must have the same number of elements)

	.. [[[end]]]
	"""	#pylint: disable=W0105


class CsvSource(object):	#pylint: disable=R0902,R0903
	r"""
	Objects of this class hold a data set from a CSV file intended for plotting. The raw data from the file can be filtered and a callback function can be used for more general data pre-processing.

	:param	file_name:			comma-separated file name
	:type	file_name:			string
	:param	indep_col_label:	independent variable column label
	:type	indep_col_label:	string (case insensitive)
	:param	dep_col_label:		dependent variable column label
	:type	dep_col_label:		string (case insensitive)
	:param	dfilter:			data filter definition. See :py:attr:`putil.plot.CsvSource.dfilter`
	:type	dfilter:			dictionary or None
	:param	indep_min:			minimum independent variable value
	:type	indep_min:			number or None
	:param	indep_max:			maximum independent variable value
	:type	indep_max:			number or None
	:param	fproc:				data processing function
	:type	fproc:				function pointer or None
	:param	fproc_eargs:		data processing function extra arguments
	:type	fproc_eargs:		dictionary or None
	:rtype:						:py:class:`putil.plot.CsvSource()` object

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.CsvSource.__init__

	:raises:
	 * IOError (File `*[file_name]*` could not be found)

	 * RuntimeError (Argument `col` is not valid)

	 * RuntimeError (Argument `dep_col_label` is not valid)

	 * RuntimeError (Argument `dep_var` is not valid)

	 * RuntimeError (Argument `dfilter` is not valid)

	 * RuntimeError (Argument `file_name` is not valid)

	 * RuntimeError (Argument `filtered` is not valid)

	 * RuntimeError (Argument `fproc_eargs` is not valid)

	 * RuntimeError (Argument `fproc` (function *[func_name]*) returned an illegal number of values)

	 * RuntimeError (Argument `fproc` is not valid)

	 * RuntimeError (Argument `indep_col_label` is not valid)

	 * RuntimeError (Argument `indep_max` is not valid)

	 * RuntimeError (Argument `indep_min` is not valid)

	 * RuntimeError (Argument `indep_var` is not valid)

	 * RuntimeError (Column headers are not unique)

	 * RuntimeError (File *[file_name]* has no valid data)

	 * RuntimeError (File *[file_name]* is empty)

	 * RuntimeError (Processing function *[func_name]* raised an exception when called with the following arguments: ``\n`` indep_var: *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n`` fproc_eargs: *[fproc_eargs_value]*
	   ``\n`` Exception error: *[exception_error_message]*)

	 * TypeError (Argument `fproc` (function *[func_name]*) return value is not valid)

	 * TypeError (Processed dependent variable is not valid)

	 * TypeError (Processed independent variable is not valid)

	 * ValueError (Argument `dfilter` is empty)

	 * ValueError (Argument `fproc` (function *[func_name]*) does not have at least 2 arguments)

	 * ValueError (Argument `indep_min` is greater than argument `indep_max`)

	 * ValueError (Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding)

	 * ValueError (Arguments `indep_var` and `dep_var` must have the same number of elements)

	 * ValueError (Column *[col_name]* (dependent column label) could not be found in comma-separated file *[file_name]* header)

	 * ValueError (Column *[col_name]* (independent column label) could not be found in comma-separated file *[file_name]* header)

	 * ValueError (Column *[col_name]* in data filter not found in comma-separated file *[file_name]* header)

	 * ValueError (Column *[column_name]* not found in header)

	 * ValueError (Extra argument `*[arg_name]*` not found in argument `fproc` (function *[func_name]*) definition)

	 * ValueError (Filtered dependent variable is empty)

	 * ValueError (Filtered independent variable is empty)

	 * ValueError (Processed dependent variable is empty)

	 * ValueError (Processed independent and dependent variables are of different length)

	 * ValueError (Processed independent variable is empty)

	.. [[[end]]]
	"""
	def __init__(self, file_name, indep_col_label, dep_col_label, dfilter=None, indep_min=None, indep_max=None, fproc=None, fproc_eargs=None):	#pylint: disable=R0913
		# Private attributes
		self._exh = putil.exh.get_or_create_exh_obj()
		self._raw_indep_var, self._raw_dep_var, self._indep_var_indexes, self._min_indep_var_index, self._max_indep_var_index = None, None, None, None, None
		self._csv_obj, self._reverse_data = None, False
		# Public attributes
		self._indep_var, self._dep_var, self._indep_min, self._indep_max = None, None, None, None
		self._file_name, self._dfilter, self._indep_col_label, self._dep_col_label, self._fproc, self._fproc_eargs = None, None, None, None, None, None
		# Assignment of arguments to attributes
		self._set_fproc(fproc)
		self._set_fproc_eargs(fproc_eargs)
		self._set_dfilter(dfilter)
		self._set_indep_col_label(indep_col_label)
		self._set_dep_col_label(dep_col_label)
		self._set_indep_min(indep_min)	#pylint: disable=W0212
		self._set_indep_max(indep_max)	#pylint: disable=W0212
		self._set_file_name(file_name)

	def _get_file_name(self):	#pylint: disable=C0111
		return self._file_name

	@putil.pcontracts.contract(file_name='file_name_exists')
	def _set_file_name(self, file_name):	#pylint: disable=C0111
		self._file_name = file_name
		self._csv_obj = putil.pcsv.CsvFile(file_name)
		self._apply_dfilter()	# This also gets indep_var and dep_var from file
		self._process_data()

	def _get_dfilter(self):	#pylint: disable=C0111
		return self._dfilter

	@putil.pcontracts.contract(dfilter='None|dict')
	def _set_dfilter(self, dfilter):	#pylint: disable=C0111
		self._dfilter = dict([(key, value) for key, value in dfilter.items()]) if isinstance(dfilter, dict) else dfilter 	# putil.pcsv is case insensitive and all caps
		self._apply_dfilter()
		self._process_data()

	def _get_indep_col_label(self):	#pylint: disable=C0111
		return self._indep_col_label

	@putil.pcontracts.contract(indep_col_label=str)
	def _set_indep_col_label(self, indep_col_label):	#pylint: disable=C0111
		self._indep_col_label = indep_col_label if isinstance(indep_col_label, str) else indep_col_label	# putil.pcsv is case insensitive and all caps
		self._check_indep_col_label()
		self._apply_dfilter()
		self._process_data()

	def _get_dep_col_label(self):	#pylint: disable=C0111
		return self._dep_col_label

	@putil.pcontracts.contract(dep_col_label=str)
	def _set_dep_col_label(self, dep_col_label):	#pylint: disable=C0111
		self._dep_col_label = dep_col_label if isinstance(dep_col_label, str) else dep_col_label	 	# putil.pcsv is case insensitive and all caps
		self._check_dep_col_label()
		self._apply_dfilter()
		self._process_data()

	def _get_indep_var(self):	#pylint: disable=C0111
		return self._indep_var	#pylint: disable=W0212

	@putil.pcontracts.contract(indep_var='increasing_real_numpy_vector')
	def _set_indep_var(self, indep_var):	#pylint: disable=C0111
		self._exh.add_exception(exname='same', extype=ValueError, exmsg='Arguments `indep_var` and `dep_var` must have the same number of elements')
		self._exh.raise_exception_if(exname='same', condition=(indep_var is not None) and (self._raw_dep_var is not None) and (len(self._raw_dep_var) != len(indep_var)))	#pylint: disable=W0212
		self._raw_indep_var = putil.misc.smart_round(indep_var, PRECISION)	#pylint: disable=W0212
		self._update_indep_var()	# Apply minimum and maximum range bounding and assign it to self._indep_var and thus this is what self.indep_var returns	#pylint: disable=W0212
		self._update_dep_var()	#pylint: disable=W0212

	def _get_dep_var(self):	#pylint: disable=C0111
		return self._dep_var	#pylint: disable=W0212

	@putil.pcontracts.contract(dep_var='real_numpy_vector')
	def _set_dep_var(self, dep_var):	#pylint: disable=C0111
		self._exh.add_exception(exname='same', extype=ValueError, exmsg='Arguments `indep_var` and `dep_var` must have the same number of elements')
		self._exh.raise_exception_if(exname='same', condition=(dep_var is not None) and (self._raw_indep_var is not None) and (len(self._raw_indep_var) != len(dep_var)))	#pylint: disable=W0212
		self._raw_dep_var = putil.misc.smart_round(dep_var, PRECISION)	#pylint: disable=W0212
		self._update_dep_var()	#pylint: disable=W0212

	def _get_indep_min(self):	#pylint: disable=C0111
		return self._indep_min	#pylint: disable=W0212

	@putil.pcontracts.contract(indep_min='real_num')
	def _set_indep_min(self, indep_min):	#pylint: disable=C0111
		self._exh.add_exception(exname='min_max', extype=ValueError, exmsg='Argument `indep_min` is greater than argument `indep_max`')
		self._exh.raise_exception_if(exname='min_max', condition=(self.indep_max is not None) and (indep_min is not None) and (self.indep_max < indep_min))
		self._indep_min = putil.misc.smart_round(indep_min, PRECISION) if not isinstance(indep_min, int) else indep_min	#pylint: disable=W0212
		self._update_indep_var()	# Apply minimum and maximum range bounding and assign it to self._indep_var and thus this is what self.indep_var returns	#pylint: disable=W0212
		self._update_dep_var()	#pylint: disable=W0212

	def _get_indep_max(self):	#pylint: disable=C0111
		return self._indep_max	#pylint: disable=W0212

	@putil.pcontracts.contract(indep_max='real_num')
	def _set_indep_max(self, indep_max):	#pylint: disable=C0111
		self._exh.add_exception(exname='min_max', extype=ValueError, exmsg='Argument `indep_min` is greater than argument `indep_max`')
		self._exh.raise_exception_if(exname='min_max', condition=(self.indep_min is not None) and (indep_max is not None) and (indep_max < self.indep_min))
		self._indep_max = putil.misc.smart_round(indep_max, PRECISION) if not isinstance(indep_max, int) else indep_max	#pylint: disable=W0212
		self._update_indep_var()	# Apply minimum and maximum range bounding and assign it to self._indep_var and thus this is what self.indep_var returns	#pylint: disable=W0212
		self._update_dep_var()	#pylint: disable=W0212

	def _update_indep_var(self):
		""" Update independent variable according to its minimum and maximum limits """
		self._exh.add_exception(exname='empty', extype=ValueError, exmsg='Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding')
		if self._raw_indep_var is not None:	#pylint: disable=W0212
			min_indexes = (self._raw_indep_var >= (self.indep_min if self.indep_min is not None else self._raw_indep_var[0]))	#pylint: disable=W0212
			max_indexes = (self._raw_indep_var <= (self.indep_max if self.indep_max is not None else self._raw_indep_var[-1]))	#pylint: disable=W0212
			self._indep_var_indexes = numpy.where(min_indexes & max_indexes)	#pylint: disable=W0212
			self._indep_var = self._raw_indep_var[self._indep_var_indexes]	#pylint: disable=W0212
			self._exh.raise_exception_if(exname='empty', condition=len(self.indep_var) == 0)

	def _update_dep_var(self):
		""" Update dependent variable (if assigned) to match the independent variable range bounding """
		self._dep_var = self._raw_dep_var	#pylint: disable=W0212
		if (self._indep_var_indexes is not None) and (self._raw_dep_var is not None):	#pylint: disable=W0212
			self._dep_var = self._raw_dep_var[self._indep_var_indexes]	#pylint: disable=W0212

	def _get_fproc(self):	#pylint: disable=C0111
		return self._fproc

	@putil.pcontracts.contract(fproc='function')
	def _set_fproc(self, fproc):	#pylint: disable=C0111
		self._exh.add_exception(exname='min_args', extype=ValueError, exmsg='Argument `fproc` (function *[func_name]*) does not have at least 2 arguments')
		if fproc is not None:
			args = putil.check.get_function_args(fproc)
			self._exh.raise_exception_if(exname='min_args', condition=(fproc is not None) and (len(args) < 2) and ('*args' not in args) and ('**kwargs' not in args), edata={'field':'func_name', 'value':fproc.__name__})
		self._fproc = fproc
		self._check_fproc_eargs()
		self._process_data()

	def _get_fproc_eargs(self):	#pylint: disable=C0111
		return self._fproc_eargs

	@putil.pcontracts.contract(fproc_eargs='None|dict')
	def _set_fproc_eargs(self, fproc_eargs):	#pylint: disable=C0111
		# Check that extra arguments to see if they are in the function definition
		self._fproc_eargs = fproc_eargs
		self._check_fproc_eargs()
		self._process_data()

	def _check_fproc_eargs(self):
		""" Checks that the extra arguments are in the processing function definition """
		self._exh.add_exception(exname='extra_args', extype=ValueError, exmsg='Extra argument `*[arg_name]*` not found in argument `fproc` (function *[func_name]*) definition')
		if (self.fproc is not None) and (self.fproc_eargs is not None):
			args = putil.check.get_function_args(self._fproc)
			for key in self.fproc_eargs:
				self._exh.raise_exception_if(exname='extra_args', condition=(key not in args) and ('*args' not in args) and ('**kwargs' not in args),\
							  edata=[{'field':'func_name', 'value':self.fproc.__name__}, {'field':'arg_name', 'value':key}])

	def _check_indep_col_label(self):
		""" Check that independent column label can be found in comma-separated file header """
		self._exh.add_exception(exname='label', extype=ValueError, exmsg='Column *[col_name]* (independent column label) could not be found in comma-separated file *[file_name]* header')
		self._exh.raise_exception_if(exname='label', condition=(self._csv_obj is not None) and (self.indep_col_label is not None) and (self.indep_col_label not in self._csv_obj.header),\
					  edata=[{'field':'col_name', 'value':self.indep_col_label}, {'field':'file_name', 'value':self.file_name}])

	def _check_dep_col_label(self):
		""" Check that dependent column label can be found in comma-separated file header """
		self._exh.add_exception(exname='label', extype=ValueError, exmsg='Column *[col_name]* (dependent column label) could not be found in comma-separated file *[file_name]* header')
		self._exh.raise_exception_if(exname='label', condition=(self._csv_obj is not None) and (self.dep_col_label is not None) and (self.dep_col_label not in self._csv_obj.header),\
					  edata=[{'field':'col_name', 'value':self.dep_col_label}, {'field':'file_name', 'value':self.file_name}])

	def _check_dfilter(self):
		""" Check that columns in filter specification can be found in comma-separated file header """
		self._exh.add_exception(exname='dfilter', extype=ValueError, exmsg='Column *[col_name]* in data filter not found in comma-separated file *[file_name]* header')
		if (self._csv_obj is not None) and (self.dfilter is not None):
			for key in self.dfilter:
				self._exh.raise_exception_if(exname='dfilter', condition=key not in self._csv_obj.header, edata=[{'field':'col_name', 'value':key}, {'field':'file_name', 'value':self.file_name}])

	def _apply_dfilter(self):
		""" Apply data filters to loaded data """
		self._check_dfilter()
		if (self.dfilter is not None) and (len(self.dfilter) > 0) and (self._csv_obj is not None):
			self._csv_obj.dfilter = self.dfilter
		elif self._csv_obj is not None:
			self._csv_obj.reset_dfilter()
		self._get_indep_var_from_file()
		self._get_dep_var_from_file()

	def _get_indep_var_from_file(self):
		""" Retrieve independent data variable from comma-separated file """
		self._exh.add_exception(exname='empty', extype=ValueError, exmsg='Filtered independent variable is empty')
		if (self._csv_obj is not None) and (self.indep_col_label is not None):
			self._check_indep_col_label()	# When object is given all arguments at construction the column label checking cannot happen at property assignment because file data is not yet loaded
			data = numpy.array([row[0] for row in self._csv_obj.data(self.indep_col_label, filtered=True)])
			self._exh.raise_exception_if(exname='empty', condition=(len(data) == 0) or bool(((data == [None]*len(data)).all())))
			# Flip data if it is in descending order (affects interpolation)
			if max(numpy.diff(data)) < 0:
				self._reverse_data = True
				data = data[::-1]
			self._set_indep_var(data)	#pylint: disable=W0212

	def _get_dep_var_from_file(self):
		""" Retrieve dependent data variable from comma-separated file """
		self._exh.add_exception(exname='empty', extype=ValueError, exmsg='Filtered dependent variable is empty')
		if (self._csv_obj is not None) and (self.dep_col_label is not None):
			self._check_dep_col_label()	# When object is given all arguments at construction the column label checking cannot happen at property assignment because file data is not yet loaded
			data = numpy.array([row[0] for row in self._csv_obj.data(self.dep_col_label, filtered=True)])
			self._exh.raise_exception_if(exname='empty', condition=(len(data) == 0) or bool(((data == [None]*len(data)).all())))
			self._set_dep_var(data[::-1] if self._reverse_data else data)	#pylint: disable=W0212

	def _process_data(self):
		""" Process data through call-back function """
		self._exh.add_exception(exname='invalid_ret', extype=TypeError, exmsg='Argument `fproc` (function *[func_name]*) return value is not valid')
		self._exh.add_exception(exname='illegal_ret', extype=RuntimeError, exmsg='Argument `fproc` (function *[func_name]*) returned an illegal number of values')
		self._exh.add_exception(exname='length', extype=ValueError, exmsg='Processed independent and dependent variables are of different length')
		self._exh.add_exception(exname='empty_indep_var', extype=ValueError, exmsg='Processed independent variable is empty')
		self._exh.add_exception(exname='illegal_indep_var', extype=TypeError, exmsg='Processed independent variable is not valid')
		self._exh.add_exception(exname='empty_dep_var', extype=ValueError, exmsg='Processed dependent variable is empty')
		self._exh.add_exception(exname='illegal_dep_var', extype=TypeError, exmsg='Processed dependent variable is not valid')
		msg = 'Processing function *[func_name]* raised an exception when called with the following arguments:\nindep_var: *[indep_var_value]*\ndep_var: *[dep_var_value]*\nfproc_eargs: *[fproc_eargs_value]*\n'+\
			  'Exception error: *[exception_error_message]*'
		self._exh.add_exception(exname='proc_fun_ex', extype=RuntimeError, exmsg=msg)
		if (self.fproc is not None) and (self.indep_var is not None) and (self.dep_var is not None):
			try:
				ret = self.fproc(self.indep_var, self.dep_var) if self.fproc_eargs is None else self.fproc(self.indep_var, self.dep_var, **self.fproc_eargs)
			except Exception as error_msg:	#pylint: disable=W0703
				if (self.fproc_eargs == None) or (not self.fproc_eargs):
					eamsg = 'None'
				else:
					eamsg = '\n'
					for key, value in self.fproc_eargs.items():
						eamsg += '   {0}: {1}\n'.format(key, value)
					eamsg = eamsg.rstrip()
				self._exh.raise_exception_if(exname='proc_fun_ex', condition=True, edata=[{'field':'func_name', 'value':self.fproc.__name__}, {'field':'indep_var_value', 'value':putil.misc.pprint_vector(self.indep_var, limit=10)},
					{'field':'dep_var_value', 'value':putil.misc.pprint_vector(self.indep_var, limit=10)}, {'field':'fproc_eargs_value', 'value':eamsg}, {'field':'exception_error_message', 'value':str(error_msg)}])
			self._exh.raise_exception_if(exname='invalid_ret', condition=(not isinstance(ret, list)) and (not isinstance(ret, tuple)), edata={'field':'func_name', 'value':self.fproc.__name__})
			self._exh.raise_exception_if(exname='illegal_ret', condition=len(ret) != 2, edata={'field':'func_name', 'value':self.fproc.__name__})
			indep_var = ret[0]
			dep_var = ret[1]
			self._exh.raise_exception_if(exname='empty_indep_var', condition=isinstance(indep_var, type(numpy.array([]))) and ((len(indep_var) == 0) or bool(((indep_var == [None]*len(indep_var)).all()))))
			self._exh.raise_exception_if(exname='illegal_indep_var', condition=_check_increasing_real_numpy_vector(indep_var))
			self._exh.raise_exception_if(exname='empty_dep_var', condition=isinstance(dep_var, type(numpy.array([]))) and ((len(dep_var) == 0) or bool(((dep_var == [None]*len(dep_var)).all()))))
			self._exh.raise_exception_if(exname='illegal_dep_var', condition=_check_real_numpy_vector(dep_var))
			self._exh.raise_exception_if(exname='length', condition=len(indep_var) != len(dep_var))
			# The processing function could potentially expand (say, via interpolation) or shorten the data set length. To avoid errors that dependent and independent variables have different number of elements
			# while setting the first processed variable (either independent or dependent) both are "reset" to some dummy value first
			self._raw_indep_var = None
			self._raw_dep_var = None
			self._indep_var_indexes = None
			self._set_indep_var(indep_var)	#pylint: disable=W0212
			self._set_dep_var(dep_var)	#pylint: disable=W0212

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
		ret += 'Independent variable minimum: {0}\n'.format('-inf' if self.indep_min is None else self.indep_min)	#pylint: disable=W0212
		ret += 'Independent variable maximum: {0}\n'.format('+inf' if self.indep_max is None else self.indep_max)	#pylint: disable=W0212
		ret += 'Independent variable: {0}\n'.format(putil.misc.pprint_vector(self.indep_var, width=50, indent=len('Independent variable: ')))	#pylint: disable=W0212
		ret += 'Dependent variable: {0}'.format(putil.misc.pprint_vector(self.dep_var, width=50, indent=len('Dependent variable: ')))	#pylint: disable=W0212
		return ret

	def _complete(self):
		""" Returns True if object is fully specified, otherwise returns False """
		return (self.indep_var is not None) and (self.dep_var is not None)

	file_name = property(_get_file_name, _set_file_name, doc='Comma-separated file name')
	r"""
	Comma-separated file from which data series is to be extracted. It is assumed that the first line of file contains unique headers for each column

	:type:		string

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.CsvSource.file_name

	:raises: (when assigned)

	 * IOError (File `*[file_name]*` could not be found)

	 * RuntimeError (Argument `col` is not valid)

	 * RuntimeError (Argument `dep_var` is not valid)

	 * RuntimeError (Argument `dfilter` is not valid)

	 * RuntimeError (Argument `file_name` is not valid)

	 * RuntimeError (Argument `filtered` is not valid)

	 * RuntimeError (Argument `fproc` (function *[func_name]*) returned an illegal number of values)

	 * RuntimeError (Argument `indep_var` is not valid)

	 * RuntimeError (Column headers are not unique)

	 * RuntimeError (File *[file_name]* has no valid data)

	 * RuntimeError (File *[file_name]* is empty)

	 * RuntimeError (Processing function *[func_name]* raised an exception when called with the following arguments: ``\n`` indep_var: *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n`` fproc_eargs: *[fproc_eargs_value]*
	   ``\n`` Exception error: *[exception_error_message]*)

	 * TypeError (Argument `fproc` (function *[func_name]*) return value is not valid)

	 * TypeError (Processed dependent variable is not valid)

	 * TypeError (Processed independent variable is not valid)

	 * ValueError (Argument `dfilter` is empty)

	 * ValueError (Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding)

	 * ValueError (Arguments `indep_var` and `dep_var` must have the same number of elements)

	 * ValueError (Column *[col_name]* (dependent column label) could not be found in comma-separated file *[file_name]* header)

	 * ValueError (Column *[col_name]* (independent column label) could not be found in comma-separated file *[file_name]* header)

	 * ValueError (Column *[col_name]* in data filter not found in comma-separated file *[file_name]* header)

	 * ValueError (Column *[column_name]* not found in header)

	 * ValueError (Filtered dependent variable is empty)

	 * ValueError (Filtered independent variable is empty)

	 * ValueError (Processed dependent variable is empty)

	 * ValueError (Processed independent and dependent variables are of different length)

	 * ValueError (Processed independent variable is empty)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	dfilter = property(_get_dfilter, _set_dfilter, doc='Data filter dictionary')
	r"""
	Data filter consisting of a series of individual filters. Each individual filter in turn consists of column name (dictionary key) and a column value (dictionary value). All rows which contain the specified value in the
	specified column are kept for that particular individual filter. The overall data set is the intersection of all the data sets specified by each individual filter. For example, if the file name to be processed is:

	+------+-----+--------+
	| Ctrl | Ref | Result |
	+======+=====+========+
	|    1 |   3 |     10 |
	+------+-----+--------+
	|    1 |   4 |     20 |
	+------+-----+--------+
	|    2 |   4 |     30 |
	+------+-----+--------+
	|    2 |   5 |     40 |
	+------+-----+--------+

	Then the filter specification ``dfilter = {'Ctrl':2, 'Ref':5}`` would result in the following filtered data set:

	+------+-----+--------+
	| Ctrl | Ref | Result |
	+======+=====+========+
	|    2 |   5 |     40 |
	+------+-----+--------+

	However, the filter specification ``dfilter = {'Ctrl':2, 'Ref':3}`` would result in an exception because the data set specified by the `Ctrl` individual filter does not overlap with the data set specified by
	the `Ref` individual filter.

	:type:		dictionary, default is *None*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.CsvSource.dfilter

	:raises: (when assigned)

	 * RuntimeError (Argument `dfilter` is not valid)

	 * RuntimeError (Argument `fproc` (function *[func_name]*) returned an illegal number of values)

	 * RuntimeError (Processing function *[func_name]* raised an exception when called with the following arguments: ``\n`` indep_var: *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n`` fproc_eargs: *[fproc_eargs_value]*
	   ``\n`` Exception error: *[exception_error_message]*)

	 * TypeError (Argument `fproc` (function *[func_name]*) return value is not valid)

	 * TypeError (Processed dependent variable is not valid)

	 * TypeError (Processed independent variable is not valid)

	 * ValueError (Column *[col_name]* in data filter not found in comma-separated file *[file_name]* header)

	 * ValueError (Filtered dependent variable is empty)

	 * ValueError (Filtered independent variable is empty)

	 * ValueError (Processed dependent variable is empty)

	 * ValueError (Processed independent and dependent variables are of different length)

	 * ValueError (Processed independent variable is empty)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	indep_col_label = property(_get_indep_col_label, _set_indep_col_label, doc='Independent column label (column name)')
	r"""
	Independent variable column label (column name)

	:type:	string

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.CsvSource.indep_col_label

	:raises: (when assigned)

	 * RuntimeError (Argument `fproc` (function *[func_name]*) returned an illegal number of values)

	 * RuntimeError (Argument `indep_col_label` is not valid)

	 * RuntimeError (Processing function *[func_name]* raised an exception when called with the following arguments: ``\n`` indep_var: *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n`` fproc_eargs: *[fproc_eargs_value]*
	   ``\n`` Exception error: *[exception_error_message]*)

	 * TypeError (Argument `fproc` (function *[func_name]*) return value is not valid)

	 * TypeError (Processed dependent variable is not valid)

	 * TypeError (Processed independent variable is not valid)

	 * ValueError (Column *[col_name]* (independent column label) could not be found in comma-separated file *[file_name]* header)

	 * ValueError (Column *[col_name]* in data filter not found in comma-separated file *[file_name]* header)

	 * ValueError (Filtered dependent variable is empty)

	 * ValueError (Filtered independent variable is empty)

	 * ValueError (Processed dependent variable is empty)

	 * ValueError (Processed independent and dependent variables are of different length)

	 * ValueError (Processed independent variable is empty)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	dep_col_label = property(_get_dep_col_label, _set_dep_col_label, doc='Dependent column label (column name)')
	r"""
	Dependent variable column label (column name)

	:type:	string

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.CsvSource.dep_col_label

	:raises: (when assigned)

	 * RuntimeError (Argument `dep_col_label` is not valid)

	 * RuntimeError (Argument `fproc` (function *[func_name]*) returned an illegal number of values)

	 * RuntimeError (Processing function *[func_name]* raised an exception when called with the following arguments: ``\n`` indep_var: *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n`` fproc_eargs: *[fproc_eargs_value]*
	   ``\n`` Exception error: *[exception_error_message]*)

	 * TypeError (Argument `fproc` (function *[func_name]*) return value is not valid)

	 * TypeError (Processed dependent variable is not valid)

	 * TypeError (Processed independent variable is not valid)

	 * ValueError (Column *[col_name]* (dependent column label) could not be found in comma-separated file *[file_name]* header)

	 * ValueError (Column *[col_name]* in data filter not found in comma-separated file *[file_name]* header)

	 * ValueError (Filtered dependent variable is empty)

	 * ValueError (Filtered independent variable is empty)

	 * ValueError (Processed dependent variable is empty)

	 * ValueError (Processed independent and dependent variables are of different length)

	 * ValueError (Processed independent variable is empty)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	indep_min = property(_get_indep_min, _set_indep_min, None, doc='Minimum of independent variable')
	"""
	Minimum independent variable limit

	:type:		number or None, default is *None*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.CsvSource.indep_min

	:raises: (when assigned)

	 * RuntimeError (Argument `indep_min` is not valid)

	 * ValueError (Argument `indep_min` is greater than argument `indep_max`)

	 * ValueError (Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	indep_max = property(_get_indep_max, _set_indep_max, None, doc='Maximum of independent variable')
	"""
	Maximum independent variable limit

	:type:		number or None, default is *None*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.CsvSource.indep_max

	:raises: (when assigned)

	 * RuntimeError (Argument `indep_max` is not valid)

	 * ValueError (Argument `indep_min` is greater than argument `indep_max`)

	 * ValueError (Argument `indep_var` is empty after `indep_min`/`indep_max` range bounding)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	fproc = property(_get_fproc, _set_fproc, doc='Processing function')
	r"""
	Data processing function pointer. The processing function is useful for "light" data massaging, like scaling, unit conversion, etc.; it is called after the data has been retrieved from the comma-separated value and\
	the resulting filtered data set has been thresholded by **indep_var_min** and **dep_var_min** (if applicable).

	The processing function is given two arguments, a Numpy vector containing the independent variable array (first argument) and a Numpy vector containing the dependent variable array (second argument). \
	The expected return value is a two-element Numpy vector tuple, its first element being the processed independent variable array, and the second element being the processed dependent variable array. One valid processing \
	function could be::

		def my_proc_func(indep_var, dep_var):
			# indep_var is a Numpy vector, in this example  time, in seconds
			# dep_var is a Numpy vector
			indep_var = indep_var/1e-12	# Want to plot time in pico-seconds
			dep_var = dep_var-dep_var[0]	# Want to remove initial offset
			return indep_var, dep_var	# Return value is a 2-element tuple

	:type:	function pointer, default is *None*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.CsvSource.fproc

	:raises: (when assigned)

	 * RuntimeError (Argument `fproc` (function *[func_name]*) returned an illegal number of values)

	 * RuntimeError (Argument `fproc` is not valid)

	 * RuntimeError (Processing function *[func_name]* raised an exception when called with the following arguments: ``\n`` indep_var: *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n`` fproc_eargs: *[fproc_eargs_value]*
	   ``\n`` Exception error: *[exception_error_message]*)

	 * TypeError (Argument `fproc` (function *[func_name]*) return value is not valid)

	 * TypeError (Processed dependent variable is not valid)

	 * TypeError (Processed independent variable is not valid)

	 * ValueError (Argument `fproc` (function *[func_name]*) does not have at least 2 arguments)

	 * ValueError (Extra argument `*[arg_name]*` not found in argument `fproc` (function *[func_name]*) definition)

	 * ValueError (Processed dependent variable is empty)

	 * ValueError (Processed independent and dependent variables are of different length)

	 * ValueError (Processed independent variable is empty)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	fproc_eargs = property(_get_fproc_eargs, _set_fproc_eargs, doc='Processing function extra argument dictionary')
	#pylint: disable=W1401
	r"""
	Extra arguments for the data processing function. The arguments are specified by key-value pairs of a dictionary, for each dictionary element the dictionary key specifies the argument name and the dictionary value
	specifies the argument value. The extra parameters are passed by keyword so they must appear in the function definition explicitly or keyword variable argument collection must be used (\*\*kwargs, for example).

	For example, if ``fproc_eargs={'par1':5, 'par2':[1, 2, 3]}`` then a valid processing function is::

		def my_proc_func(indep_var, dep_var, par1, par2):
			print '2*5 = 10 = {0}'.format(2*par1)
			print 'sum([1, 2, 3]) = 6 = {0}'.format(sum(par2))
			return indep_var+(2*par1), dep_var+sum(par2)

	:type:	dictionary, default is *None*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.CsvSource.fproc_eargs

	:raises: (when assigned)

	 * RuntimeError (Argument `fproc_eargs` is not valid)

	 * RuntimeError (Argument `fproc` (function *[func_name]*) returned an illegal number of values)

	 * RuntimeError (Processing function *[func_name]* raised an exception when called with the following arguments: ``\n`` indep_var: *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n`` fproc_eargs: *[fproc_eargs_value]*
	   ``\n`` Exception error: *[exception_error_message]*)

	 * TypeError (Argument `fproc` (function *[func_name]*) return value is not valid)

	 * TypeError (Processed dependent variable is not valid)

	 * TypeError (Processed independent variable is not valid)

	 * ValueError (Extra argument `*[arg_name]*` not found in argument `fproc` (function *[func_name]*) definition)

	 * ValueError (Processed dependent variable is empty)

	 * ValueError (Processed independent and dependent variables are of different length)

	 * ValueError (Processed independent variable is empty)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	# indep_var is read only
	indep_var = property(_get_indep_var, None, doc='Independent variable Numpy vector (read only)')	#pylint: disable=W0212,E0602

	# dep_var is read only
	dep_var = property(_get_dep_var, None, doc='Dependent variable Numpy vector (read only)')	#pylint: disable=W0212,E0602


class Series(object):	#pylint: disable=R0902,R0903
	"""
	Specifies a series within a panel

	:param	data_source:	data source object
	:type	data_source:	:py:class:`putil.plot.BasicSource()` object or :py:class:`putil.plot.CsvSource()` object or others conforming to the data source specification
	:param	label:			series label, to be used in panel legend
	:type	label:			string
	:param	color:			series color. All `Matplotlib colors <http://matplotlib.org/api/colors_api.html>`_ are supported.
	:type	color:			polymorphic
	:param	marker:			marker type. All `Matplotlib marker types <http://matplotlib.org/api/markers_api.html>`_ are supported. *None* indicates no marker.
	:type	marker:			string or None
	:param	interp:			interpolation option, one of None (no interpolation) 'STRAIGHT' (straight line connects data points), 'STEP' (horizontal segments between data points), 'CUBIC' (cubic interpolation between \
	data points) or 'LINREG' (linear regression based on data points). The interpolation option is case insensitive.
	:type	interp:			string or None
	:param	line_style:		line style.   All `Matplotlib line styles <http://matplotlib.org/api/artist_api.html#matplotlib.lines.Line2D.set_linestyle>`_ are supported. *None* indicates no line.
	:type	line_style:		string or None
	:param	secondary_axis:	secondary axis flag
	:type	secondary_axis:	boolean

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Series.__init__

	:raises:
	 * RuntimeError (Argument `color` is not valid)

	 * RuntimeError (Argument `data_source` does not have an `dep_var` attribute)

	 * RuntimeError (Argument `data_source` does not have an `indep_var` attribute)

	 * RuntimeError (Argument `data_source` is not fully specified)

	 * RuntimeError (Argument `interp` is not valid)

	 * RuntimeError (Argument `label` is not valid)

	 * RuntimeError (Argument `line_style` is not valid)

	 * RuntimeError (Argument `marker` is not valid)

	 * RuntimeError (Argument `secondary_axis` is not valid)

	 * RuntimeError (Series options make it not plottable)

	 * TypeError (Invalid color specification)

	 * ValueError (Argument `interp` is not one of ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG'] (case insensitive))

	 * ValueError (Argument `line_style` is not one of ['-', '--', '-.', ':'])

	 * ValueError (At least 4 data points are needed for CUBIC interpolation)

	.. [[[end]]]
	"""
	def __init__(self, data_source, label, color='k', marker='o', interp='CUBIC', line_style='-', secondary_axis=False):	#pylint: disable=R0913
		# Series plotting attributes
		self._exh = putil.exh.get_or_create_exh_obj()
		self._ref_linewidth = LINE_WIDTH
		self._ref_markersize = MARKER_SIZE
		self._ref_markeredgewidth = self._ref_markersize*(5.0/14.0)
		self._ref_markerfacecolor = 'w'
		# Private attributes
		self._scaling_factor_indep_var, self._scaling_factor_dep_var = 1, 1
		self._marker_spec, self._linestyle_spec, self._linewidth_spec = None, None, None
		# Public attributes
		self.scaled_indep_var, self.scaled_dep_var = None, None
		self.interp_indep_var, self.interp_dep_var = None, None
		self.indep_var, self.dep_var = None, None
		self.scaled_interp_indep_var, self.scaled_interp_dep_var = None, None
		self._data_source, self._label, self._color, self._marker, self._interp, self._line_style, self._secondary_axis = None, None, 'k', 'o', 'CUBIC', '-', False
		# Assignment of arguments to attributes
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
		self._exh.add_exception(exname='indep_var_attribute', extype=RuntimeError, exmsg='Argument `data_source` does not have an `indep_var` attribute')
		self._exh.add_exception(exname='dep_var_attribute', extype=RuntimeError, exmsg='Argument `data_source` does not have an `dep_var` attribute')
		self._exh.add_exception(exname='full_spec', extype=RuntimeError, exmsg='Argument `data_source` is not fully specified')
		if data_source is not None:
			self._exh.raise_exception_if(exname='indep_var_attribute', condition='indep_var' not in dir(data_source))
			self._exh.raise_exception_if(exname='dep_var_attribute', condition='dep_var' not in dir(data_source))
			self._exh.raise_exception_if(exname='full_spec', condition=('_complete' in dir(data_source)) and (not data_source._complete()))	#pylint: disable=W0212
			self._data_source = data_source
			self.indep_var = self.data_source.indep_var
			self.dep_var = self.data_source.dep_var
			self._validate_source_length_cubic_interp()
			self._calculate_curve()

	def _get_label(self):	#pylint: disable=C0111
		return self._label

	@putil.pcontracts.contract(label='None|str')
	def _set_label(self, label):	#pylint: disable=C0111
		self._label = label

	def _get_color(self):	#pylint: disable=C0111
		return self._color

	@putil.pcontracts.contract(color='real_num|str|list|tuple')
	def _set_color(self, color):	#pylint: disable=C0111
		self._exh.add_exception(exname='invalid_color', extype=TypeError, exmsg='Invalid color specification')
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
		self._exh.raise_exception_if(exname='invalid_color', condition=not True in check_list)

	def _get_marker(self):	#pylint: disable=C0111
		return self._marker

	def _set_marker(self, marker):	#pylint: disable=C0111
		self._exh.add_exception(exname='invalid_marker', extype=RuntimeError, exmsg='Argument `marker` is not valid')
		self._exh.raise_exception_if(exname='invalid_marker', condition=not self._validate_marker(marker))
		self._marker = marker
		self._marker_spec = self.marker if self.marker not in ["None", None, ' ', ''] else ''
		self._check_series_is_plottable()

	def _get_interp(self):	#pylint: disable=C0111
		return self._interp

	@putil.pcontracts.contract(interp='interpolation_option')
	def _set_interp(self, interp):	#pylint: disable=C0111
		self._interp = interp.upper().strip() if isinstance(interp, str) else interp
		self._check_series_is_plottable()
		self._validate_source_length_cubic_interp()
		self._update_linestyle_spec()
		self._update_linewidth_spec()
		self._calculate_curve()

	def _get_line_style(self):	#pylint: disable=C0111
		return self._line_style

	@putil.pcontracts.contract(line_style='line_style_option')
	def _set_line_style(self, line_style):	#pylint: disable=C0111
		self._line_style = line_style
		self._update_linestyle_spec()
		self._update_linewidth_spec()
		self._check_series_is_plottable()

	def _get_secondary_axis(self):	#pylint: disable=C0111
		return self._secondary_axis

	@putil.pcontracts.contract(secondary_axis='None|bool')
	def _set_secondary_axis(self, secondary_axis):	#pylint: disable=C0111
		self._secondary_axis = secondary_axis

	def __str__(self):
		""" Print series object information """
		ret = ''
		ret += 'Data source: {0}{1} class object\n'.format(None if self.data_source is None else self.data_source.__module__, '' if self.data_source is None else '.'+self.data_source.__class__.__name__)
		ret += 'Independent variable: {0}\n'.format(putil.misc.pprint_vector(self.indep_var, width=50))
		ret += 'Dependent variable: {0}\n'.format(putil.misc.pprint_vector(self.dep_var, width=50))
		ret += 'Label: {0}\n'.format(self.label)
		ret += 'Color: {0}\n'.format(self.color)
		ret += 'Marker: {0}\n'.format(self._print_marker())
		ret += 'Interpolation: {0}\n'.format(self.interp)
		ret += 'Line style: {0}\n'.format(self.line_style)
		ret += 'Secondary axis: {0}'.format(self.secondary_axis)
		return ret

	def _check_series_is_plottable(self):
		""" Check that the combination of marker, line style and line width width will produce a printable series """
		self._exh.add_exception(exname='invalid_series', extype=RuntimeError, exmsg='Series options make it not plottable')
		self._exh.raise_exception_if(exname='invalid_series', condition=(self._marker_spec == '') and ((not self.interp) or (not self.line_style)))

	def _validate_source_length_cubic_interp(self):	#pylint:disable=C0103
		""" Test if data source has minimum length to calculate cubic interpolation """
		self._exh.add_exception(exname='invalid_cubic_series', extype=ValueError, exmsg='At least 4 data points are needed for CUBIC interpolation')
		self._exh.raise_exception_if(exname='invalid_cubic_series', condition=(self.interp == 'CUBIC') and (self.indep_var is not None) and (self.dep_var is not None) and (self.indep_var.shape[0] < 4))

	def _validate_marker(self, marker):	#pylint:disable=R0201,R0911
		""" Validate if marker specification is valid """
		try:
			plt.plot(range(10), marker=marker)
		except:	#pylint: disable=W0702
			return False
		return True

	def _print_marker(self):
		""" Returns marker description """
		marker_consts = [{'value':matplotlib.markers.TICKLEFT, 'repr':'matplotlib.markers.TICKLEFT'},
						 {'value':matplotlib.markers.TICKRIGHT, 'repr':'matplotlib.markers.TICKRIGHT'},
						 {'value':matplotlib.markers.TICKUP, 'repr':'matplotlib.markers.TICKUP'},
						 {'value':matplotlib.markers.TICKDOWN, 'repr':'matplotlib.markers.TICKDOWN'},
						 {'value':matplotlib.markers.CARETLEFT, 'repr':'matplotlib.markers.CARETLEFT'},
						 {'value':matplotlib.markers.CARETRIGHT, 'repr':'matplotlib.markers.CARETRIGHT'},
						 {'value':matplotlib.markers.CARETUP, 'repr':'matplotlib.markers.CARETUP'},
						 {'value':matplotlib.markers.CARETDOWN, 'repr':'matplotlib.markers.CARETDOWN'}]
		marker_none = ["None", None, ' ', '']
		if self.marker in marker_none:
			return 'None'
		for const_dict in marker_consts:
			if self.marker == const_dict['value']:
				return const_dict['repr']
		if isinstance(self.marker, str):
			return self.marker
		if isinstance(self.marker, matplotlib.path.Path):
			return 'matplotlib.path.Path object'
		return str(self.marker)

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

	def _legend_artist(self, legend_scale=None):
		""" Creates artist (marker -if used- and line style -if used-) """
		legend_scale = LEGEND_SCALE if legend_scale is None else legend_scale
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
		if self.marker != '':
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
	Data source object. The independent and dependent data sets are obtained once this attribute is set. To be a valid, a data source object must have an ``indep_var`` attribute that contains a Numpy vector of increasing real \
	numbers and a ``dep_var`` attribute that contains a Numpy vector of real numbers.

	:type:	:py:class:`putil.plot.BasicSource()` object, :py:class:`putil.plot.CsvSource()` object or other objects conforming to the data source specification

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Series.data_source

	:raises: (when assigned)

	 * RuntimeError (Argument `data_source` does not have an `dep_var` attribute)

	 * RuntimeError (Argument `data_source` does not have an `indep_var` attribute)

	 * RuntimeError (Argument `data_source` is not fully specified)

	 * ValueError (At least 4 data points are needed for CUBIC interpolation)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	label = property(_get_label, _set_label, doc='Series label')
	"""
	Series label, to be used in the panel legend if the panel has more than one series.

	:type:	string

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Series.label

	:raises: (when assigned) RuntimeError (Argument `label` is not valid)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	color = property(_get_color, _set_color, doc='Series line and marker color')
	"""
	Series line and marker color. All `Matplotlib colors <http://matplotlib.org/api/colors_api.html>`_ are supported.

	:type:	polymorphic, default is *'k'* (black)

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Series.color

	:raises: (when assigned)

	 * RuntimeError (Argument `color` is not valid)

	 * TypeError (Invalid color specification)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	marker = property(_get_marker, _set_marker, doc='Plot data point markers flag')
	"""
	Series marker type. All `Matplotlib marker types <http://matplotlib.org/api/markers_api.html>`_ are supported. *None* indicates no marker.

	:type: string or None, default is *'o'* (circle)

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Series.marker

	:raises: (when assigned)

	 * RuntimeError (Argument `marker` is not valid)

	 * RuntimeError (Series options make it not plottable)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	interp = property(_get_interp, _set_interp, doc='Series interpolation option, one of `STRAIGHT`, `CUBIC` or `LINREG` (case insensitive)')
	"""
	Interpolation option, one of *None* (no interpolation) 'STRAIGHT' (straight line connects data points), 'STEP' (horizontal segments betweend data points), 'CUBIC' (cubic interpolation between \
	data points) or 'LINREG' (linear regression based on data points). The interpolation option is case insensitive.

	:type:	string, default is *'CUBIC'*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Series.interp

	:raises: (when assigned)

	 * RuntimeError (Argument `interp` is not valid)

	 * RuntimeError (Series options make it not plottable)

	 * ValueError (Argument `interp` is not one of ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG'] (case insensitive))

	 * ValueError (At least 4 data points are needed for CUBIC interpolation)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	line_style = property(_get_line_style, _set_line_style, doc='Series line style, one of `-`, `--`, `-.` or `:`')
	"""
	Line style. All `Matplotlib line styles <http://matplotlib.org/api/artist_api.html#matplotlib.lines.Line2D.set_linestyle>`_ are supported. *None* indicates no line.

	:type:	string or None, default is *'-'*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Series.line_style

	:raises: (when assigned)

	 * RuntimeError (Argument `line_style` is not valid)

	 * RuntimeError (Series options make it not plottable)

	 * ValueError (Argument `line_style` is not one of ['-', '--', '-.', ':'])

	.. [[[end]]]
	"""	#pylint: disable=W0105

	secondary_axis = property(_get_secondary_axis, _set_secondary_axis, doc='Series secondary axis flag')
	"""
	Secondary axis flag. If true, the series belongs to the secondary (right) panel axis.

	:type:	boolean, default is *False*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Series.secondary_axis

	:raises: (when assigned) RuntimeError (Argument `secondary_axis` is not valid)

	.. [[[end]]]
	"""	#pylint: disable=W0105


class Panel(object):	#pylint: disable=R0902,R0903
	"""
	Defines a panel within a figure

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
	:param	legend_props:			legend properties. See :py:attr:`putil.plot.Panel.legend_props()`
	:type	legend_props:			dictionary
	:param	show_indep_axis:		display primary axis flag
	:type	show_indep_axis:		boolean

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc(exclude=['putil.eng'])) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Panel.__init__

	:raises:
	 * RuntimeError (Argument `legend_props` is not valid)

	 * RuntimeError (Argument `log_dep_axis` is not valid)

	 * RuntimeError (Argument `primary_axis_label` is not valid)

	 * RuntimeError (Argument `primary_axis_units` is not valid)

	 * RuntimeError (Argument `secondary_axis_label` is not valid)

	 * RuntimeError (Argument `secondary_axis_units` is not valid)

	 * RuntimeError (Argument `series` is not valid)

	 * RuntimeError (Argument `show_indep_axis` is not valid)

	 * RuntimeError (Legend property `cols` is not valid)

	 * RuntimeError (Series item *[number]* is not fully specified)

	 * TypeError (Legend property `pos` is not one of ['BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER'] (case insensitive))

	 * ValueError (Illegal legend property `*[prop_name]*`)

	 * ValueError (Series item *[number]* cannot be plotted in a logarithmic axis because it contains negative data points)

	.. [[[end]]]
	"""
	def __init__(self, series=None, primary_axis_label='', primary_axis_units='', secondary_axis_label='', secondary_axis_units='', log_dep_axis=False, legend_props=None, show_indep_axis=False):	#pylint: disable=W0102,R0913
		# Default arguments
		legend_props = {'pos':'BEST', 'cols':1} if legend_props == None else legend_props
		# Private attributes
		self._exh = putil.exh.get_or_create_exh_obj()
		self._series, self._primary_axis_label, self._secondary_axis_label, self._primary_axis_units, self._secondary_axis_units, self._log_dep_axis, self._recalculate_series, self._legend_props, self._show_indep_axis = \
			None, None, None, None, None, None, False, {'pos':'BEST', 'cols':1}, None
		# Private attributes
		self._legend_pos_list = ['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center']
		self._panel_has_primary_axis, self._panel_has_secondary_axis = False, False
		self._primary_dep_var_min, self._primary_dep_var_max, self._primary_dep_var_div, self._primary_dep_var_unit_scale, self._primary_dep_var_locs, self._primary_dep_var_labels = None, None, None, None, None, None
		self._secondary_dep_var_min, self._secondary_dep_var_max, self._secondary_dep_var_div, self._secondary_dep_var_unit_scale, self._secondary_dep_var_locs, self._secondary_dep_var_labels = None, None, None, None, None, None
		self._legend_props_list = ['pos', 'cols']
		self._legend_props_pos_list = ['BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER']
		# Assignment of arguments to attributes
		self._set_log_dep_axis(log_dep_axis)	# Order here is important to avoid unnecessary re-calculating of panel axes if log_dep_axis is True
		self._set_series(series)
		self._set_primary_axis_label(primary_axis_label)
		self._set_primary_axis_units(primary_axis_units)
		self._set_secondary_axis_label(secondary_axis_label)
		self._set_secondary_axis_units(secondary_axis_units)
		self._set_legend_props(legend_props)
		self._set_show_indep_axis(show_indep_axis)

	def _get_series(self):	#pylint: disable=C0111
		return self._series

	def _set_series(self, series):	#pylint: disable=C0111,R0912,R0914
		self._series = (series if isinstance(series, list) else [series]) if series is not None else series
		self._recalculate_series = False
		if self.series is not None:
			self._validate_series()
			self._panel_has_primary_axis = any([not series_obj.secondary_axis for series_obj in self.series])
			self._panel_has_secondary_axis = any([series_obj.secondary_axis for series_obj in self.series])
			comp_prim_dep_var = (not self.log_dep_axis) and self._panel_has_primary_axis
			comp_sec_dep_var = (not self.log_dep_axis) and self._panel_has_secondary_axis
			panel_has_primary_interp_series = any([(not series_obj.secondary_axis) and (series_obj.interp_dep_var is not None) for series_obj in self.series])
			panel_has_secondary_interp_series = any([series_obj.secondary_axis and (series_obj.interp_dep_var is not None) for series_obj in self.series])	#pylint:disable=C0103
			# Compute panel scaling factor
			primary_min = prim_interp_min = secondary_min = sec_interp_min = primary_max = prim_interp_max = secondary_max = sec_interp_max = panel_min = panel_max = None
			# Find union of all data points and panel minimum and maximum. If panel has logarithmic dependent axis, limits are common and the union of the limits of both axis
			# Primary axis
			glob_prim_dep_var = numpy.unique(numpy.concatenate([series_obj.dep_var for series_obj in self.series if not series_obj.secondary_axis])) if comp_prim_dep_var else None
			prim_interp_min = min([min(series_obj.dep_var) for series_obj in self.series if (not series_obj.secondary_axis) and (series_obj.interp_dep_var is not None)]) if panel_has_primary_interp_series else None
			prim_interp_max = max([max(series_obj.dep_var) for series_obj in self.series if (not series_obj.secondary_axis) and (series_obj.interp_dep_var is not None)]) if panel_has_primary_interp_series else None
			primary_min = min(min(glob_prim_dep_var), prim_interp_min) if comp_prim_dep_var and (prim_interp_min is not None) else (min(glob_prim_dep_var) if comp_prim_dep_var else None)
			primary_max = max(max(glob_prim_dep_var), prim_interp_max) if comp_prim_dep_var and (prim_interp_min is not None) else (max(glob_prim_dep_var) if comp_prim_dep_var else None)
			# Secondary axis
			glob_sec_dep_var = numpy.unique(numpy.concatenate([series_obj.dep_var  for series_obj in self.series if series_obj.secondary_axis])) if comp_sec_dep_var else None
			sec_interp_min = min([min(series_obj.dep_var) for series_obj in self.series if series_obj.secondary_axis and (series_obj.interp_dep_var is not None)]).tolist() if panel_has_secondary_interp_series else None
			sec_interp_max = max([max(series_obj.dep_var) for series_obj in self.series if series_obj.secondary_axis and (series_obj.interp_dep_var is not None)]).tolist() if panel_has_secondary_interp_series else None
			secondary_min = min(min(glob_sec_dep_var), sec_interp_min) if comp_sec_dep_var and (sec_interp_min is not None) else (min(glob_sec_dep_var) if comp_sec_dep_var else None)
			secondary_max = max(max(glob_sec_dep_var), sec_interp_max) if comp_sec_dep_var and (sec_interp_max is not None) else (max(glob_sec_dep_var) if comp_sec_dep_var else None)
			# Global (for logarithmic dependent axis)
			glob_panel_dep_var = None if not self.log_dep_axis else numpy.unique(numpy.concatenate([series_obj.dep_var for series_obj in self.series]))
			panel_min = min(min(glob_panel_dep_var), prim_interp_min) if self.log_dep_axis and panel_has_primary_interp_series else (min(glob_panel_dep_var) if self.log_dep_axis else None)
			panel_max = max(max(glob_panel_dep_var), prim_interp_max) if self.log_dep_axis and panel_has_primary_interp_series else (max(glob_panel_dep_var) if self.log_dep_axis else None)
			panel_min = min(min(glob_panel_dep_var), sec_interp_min) if self.log_dep_axis and panel_has_secondary_interp_series else (min(glob_panel_dep_var) if self.log_dep_axis else None)
			panel_max = max(max(glob_panel_dep_var), sec_interp_max) if self.log_dep_axis and panel_has_secondary_interp_series else (max(glob_panel_dep_var) if self.log_dep_axis else None)
			# Get axis tick marks locations
			if comp_prim_dep_var:
				self._primary_dep_var_locs, self._primary_dep_var_labels, self._primary_dep_var_min, self._primary_dep_var_max, self._primary_dep_var_div, self._primary_dep_var_unit_scale = \
					_intelligent_ticks(glob_prim_dep_var, primary_min, primary_max, tight=False, log_axis=self.log_dep_axis)
			if comp_sec_dep_var:
				self._secondary_dep_var_locs, self._secondary_dep_var_labels, self._secondary_dep_var_min, self._secondary_dep_var_max, self._secondary_dep_var_div, self._secondary_dep_var_unit_scale = \
					_intelligent_ticks(glob_sec_dep_var, secondary_min, secondary_max, tight=False, log_axis=self.log_dep_axis)
			if self.log_dep_axis and self._panel_has_primary_axis:
				self._primary_dep_var_locs, self._primary_dep_var_labels, self._primary_dep_var_min, self._primary_dep_var_max, self._primary_dep_var_div, self._primary_dep_var_unit_scale = \
					_intelligent_ticks(glob_panel_dep_var, panel_min, panel_max, tight=False, log_axis=self.log_dep_axis)
			if self.log_dep_axis and self._panel_has_secondary_axis:
				self._secondary_dep_var_locs, self._secondary_dep_var_labels, self._secondary_dep_var_min, self._secondary_dep_var_max, self._secondary_dep_var_div, self._secondary_dep_var_unit_scale = \
					_intelligent_ticks(glob_panel_dep_var, panel_min, panel_max, tight=False, log_axis=self.log_dep_axis)
			# Equalize number of ticks on primary and secondary axis so that ticks are in the same percentage place within the dependent variable plotting interval (for non-logarithmic panels)
			if (not self.log_dep_axis) and self._panel_has_primary_axis and self._panel_has_secondary_axis:
				max_ticks = max(len(self._primary_dep_var_locs), len(self._secondary_dep_var_locs))-1
				primary_delta = (self._primary_dep_var_locs[-1]-self._primary_dep_var_locs[0])/float(max_ticks)
				secondary_delta = (self._secondary_dep_var_locs[-1]-self._secondary_dep_var_locs[0])/float(max_ticks)
				self._primary_dep_var_locs = [self._primary_dep_var_locs[0]+(num*primary_delta) for num in range(max_ticks+1)]
				self._secondary_dep_var_locs = [self._secondary_dep_var_locs[0]+(num*secondary_delta) for num in range(max_ticks+1)]
				self._primary_dep_var_locs, self._primary_dep_var_labels = _uniquify_tick_labels(self._primary_dep_var_locs, self._primary_dep_var_locs[0], self._primary_dep_var_locs[-1])
				self._secondary_dep_var_locs, self._secondary_dep_var_labels = _uniquify_tick_labels(self._secondary_dep_var_locs, self._secondary_dep_var_locs[0], self._secondary_dep_var_locs[-1])
			# Scale panel
			self._scale_dep_var(self._primary_dep_var_div, self._secondary_dep_var_div)

	def _get_primary_axis_label(self):	#pylint: disable=C0111
		return self._primary_axis_label

	@putil.pcontracts.contract(primary_axis_label='None|str')
	def _set_primary_axis_label(self, primary_axis_label):	#pylint: disable=C0111
		self._primary_axis_label = primary_axis_label

	def _get_primary_axis_units(self):	#pylint: disable=C0111
		return self._primary_axis_units

	@putil.pcontracts.contract(primary_axis_units='None|str')
	def _set_primary_axis_units(self, primary_axis_units):	#pylint: disable=C0111
		self._primary_axis_units = primary_axis_units

	def _get_secondary_axis_label(self):	#pylint: disable=C0111
		return self._secondary_axis_label

	@putil.pcontracts.contract(secondary_axis_label='None|str')
	def _set_secondary_axis_label(self, secondary_axis_label):	#pylint: disable=C0111
		self._secondary_axis_label = secondary_axis_label

	def _get_secondary_axis_units(self):	#pylint: disable=C0111
		return self._secondary_axis_units

	@putil.pcontracts.contract(secondary_axis_units='None|str')
	def _set_secondary_axis_units(self, secondary_axis_units):	#pylint: disable=C0111
		self._secondary_axis_units = secondary_axis_units

	def _get_log_dep_axis(self):	#pylint: disable=C0111
		return self._log_dep_axis

	@putil.pcontracts.contract(log_dep_axis='None|bool')
	def _set_log_dep_axis(self, log_dep_axis):	#pylint: disable=C0111
		self._recalculate_series = self.log_dep_axis != log_dep_axis
		self._log_dep_axis = log_dep_axis
		if self._recalculate_series:
			self._set_series(self._series)

	def _get_show_indep_axis(self):	#pylint: disable=C0111
		return self._show_indep_axis

	@putil.pcontracts.contract(show_indep_axis='None|bool')
	def _set_show_indep_axis(self, show_indep_axis):	#pylint: disable=C0111
		self._show_indep_axis = show_indep_axis

	def _get_legend_props(self):	#pylint: disable=C0111
		return self._legend_props

	@putil.pcontracts.contract(legend_props='None|dict')
	def _set_legend_props(self, legend_props):	#pylint: disable=C0111
		self._exh.add_exception(exname='invalid_legend_prop', extype=ValueError, exmsg='Illegal legend property `*[prop_name]*`')
		self._exh.add_exception(exname='illegal_legend_prop', extype=TypeError, exmsg="Legend property `pos` is not one of ['BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER LEFT', 'CENTER RIGHT',"+\
						  " 'LOWER CENTER', 'UPPER CENTER', 'CENTER'] (case insensitive)")
		self._exh.add_exception(exname='invalid_legend_cols', extype=RuntimeError, exmsg='Legend property `cols` is not valid')
		self._legend_props = legend_props if legend_props is not None else {'pos':'BEST', 'cols':1}
		if self.legend_props is not None:
			self._legend_props.setdefault('pos', 'BEST')
			self._legend_props.setdefault('cols', 1)
			for key, value in self.legend_props.iteritems():
				self._exh.raise_exception_if(exname='invalid_legend_prop', condition=key not in self._legend_props_list, edata={'field':'prop_name', 'value':key})
				self._exh.raise_exception_if(exname='illegal_legend_prop', condition=(key == 'pos') and _legend_position_validation(self.legend_props['pos']))
				self._exh.raise_exception_if(exname='invalid_legend_cols', condition=((key == 'cols') and (not isinstance(value, int))) or ((key == 'cols') and (isinstance(value, int) is True) and (value < 0)))
			self._legend_props['pos'] = self._legend_props['pos'].upper()

	def __str__(self):
		"""
		Print panel information
		"""
		ret = ''
		if (self.series is None) or (len(self.series) == 0):
			ret += 'Series: None\n'
		else:
			for num, element in enumerate(self.series):
				ret += 'Series {0}:\n'.format(num)
				temp = str(element).split('\n')
				temp = [3*' '+line for line in temp]
				ret += '\n'.join(temp)
				ret += '\n'
		ret += 'Primary axis label: {0}\n'.format(self.primary_axis_label if self.primary_axis_label not in ['', None] else 'not specified')
		ret += 'Primary axis units: {0}\n'.format(self.primary_axis_units if self.primary_axis_units not in ['', None] else 'not specified')
		ret += 'Secondary axis label: {0}\n'.format(self.secondary_axis_label if self.secondary_axis_label not in ['', None] else 'not specified')
		ret += 'Secondary axis units: {0}\n'.format(self.secondary_axis_units if self.secondary_axis_units not in ['', None] else 'not specified')
		ret += 'Logarithmic dependent axis: {0}\n'.format(self.log_dep_axis)
		ret += 'Show independent axis: {0}\n'.format(self.show_indep_axis)
		ret += 'Legend properties:\n'
		for num, (key, value) in enumerate(self.legend_props.iteritems()):
			ret += '   {0}: {1}{2}'.format(key, value, '\n' if num+1 < len(self.legend_props) else '')
		return ret

	def _validate_series(self):
		""" Verifies that elements of series list are of the right type and fully specified """
		self._exh.add_exception(exname='invalid_series', extype=RuntimeError, exmsg='Argument `series` is not valid')
		self._exh.add_exception(exname='incomplete_series', extype=RuntimeError, exmsg='Series item *[number]* is not fully specified')
		self._exh.add_exception(exname='no_log', extype=ValueError, exmsg='Series item *[number]* cannot be plotted in a logarithmic axis because it contains negative data points')
		for num, obj in enumerate(self.series):
			self._exh.raise_exception_if(exname='invalid_series', condition=type(obj) is not Series)
			self._exh.raise_exception_if(exname='incomplete_series', condition=not obj._complete(), edata={'field':'number', 'value':num})	#pylint: disable=W0212
			self._exh.raise_exception_if(exname='no_log', condition=bool((min(obj.dep_var) <= 0) and self.log_dep_axis), edata={'field':'number', 'value':num})

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

	def _setup_axis(self, axis_type, axis_obj, dep_min, dep_max, tick_locs, tick_labels, axis_label, axis_units, axis_scale):	#pylint: disable=R0201,R0913,R0914
		""" Configure dependent axis """
		# Set function pointers
		xflist = [axis_obj.xaxis.grid, axis_obj.set_xlim, axis_obj.xaxis.set_ticks, axis_obj.xaxis.set_ticklabels, axis_obj.xaxis.set_label_text]
		yflist = [axis_obj.yaxis.grid, axis_obj.set_ylim, axis_obj.yaxis.set_ticks, axis_obj.yaxis.set_ticklabels, axis_obj.yaxis.set_label_text]
		fgrid, flim, fticks, fticklabels, fset_label_text = xflist if axis_type.upper() == 'INDEP' else yflist
		# Process
		fgrid(True, 'both')
		flim((dep_min, dep_max), emit=True, auto=False)
		fticks(tick_locs)
		axis_obj.tick_params(axis='x' if axis_type.upper() == 'INDEP' else 'y', which='major', labelsize=AXIS_TICKS_FONT_SIZE)
		if tick_labels is not None:
			fticklabels(tick_labels)
		if (axis_label not in [None, '']) or (axis_units not in [None, '']):
			axis_label = '' if axis_label is None else axis_label.strip()
			unit_scale = '' if axis_scale is None else axis_scale.strip()
			fset_label_text(axis_label + ('' if (unit_scale == '') and (axis_units == '') else (' ['+unit_scale+('-' if axis_units == '' else axis_units)+']')), fontdict={'fontsize':AXIS_LABEL_FONT_SIZE})

	def _draw_panel(self, axarr_prim, indep_axis_dict, print_indep_axis):	#pylint: disable=R0912,R0914,R0915
		""" Draw panel series """
		axarr_sec = axarr_prim.twinx() if self._panel_has_secondary_axis else None
		# Place data series in their appropriate axis (primary or secondary)
		for series_obj in self.series:
			series_obj._draw_series(axarr_prim if not series_obj.secondary_axis else axarr_sec, indep_axis_dict['log_indep'], self.log_dep_axis)	#pylint: disable=W0212
		# Set up tick labels and axis labels
		if self._panel_has_primary_axis:
			self._setup_axis('DEP', axarr_prim, self._primary_dep_var_min, self._primary_dep_var_max, self._primary_dep_var_locs, self._primary_dep_var_labels,
						self.primary_axis_label, self.primary_axis_units, self._primary_dep_var_unit_scale)
		if self._panel_has_secondary_axis:
			self._setup_axis('DEP', axarr_sec, self._secondary_dep_var_min, self._secondary_dep_var_max, self._secondary_dep_var_locs, self._secondary_dep_var_labels,
						self.secondary_axis_label, self.secondary_axis_units, self._secondary_dep_var_unit_scale)
		if (not self._panel_has_primary_axis) and self._panel_has_secondary_axis:
			axarr_prim.yaxis.set_visible(False)
		# Print legend
		if (len(self.series) > 1) and (len(self.legend_props) > 0):
			_, primary_labels = axarr_prim.get_legend_handles_labels() if self._panel_has_primary_axis else (None, list()) #pylint: disable=W0612
			_, secondary_labels = axarr_sec.get_legend_handles_labels() if self._panel_has_secondary_axis else (None, list()) #pylint: disable=W0612
			labels = [r'$\Leftarrow$'+label for label in primary_labels]+ [label+r'$\Rightarrow$' for label in secondary_labels] if (len(primary_labels) > 0) and (len(secondary_labels) > 0) else primary_labels+secondary_labels
			if any([True if (label is not None) and (label != '') else False for label in labels]):
				leg_artist = [series_obj._legend_artist(LEGEND_SCALE) for series_obj in self.series]	#pylint: disable=W0212
				legend_axis = axarr_prim if self._panel_has_primary_axis else axarr_sec
				legend_axis.legend(leg_artist, labels, ncol=self.legend_props['cols'] if 'cols' in self.legend_props else len(labels),
					loc=self._legend_pos_list[self._legend_pos_list.index(self.legend_props['pos'].lower() if 'pos' in self.legend_props else 'lower left')], numpoints=1, fontsize=AXIS_LABEL_FONT_SIZE/LEGEND_SCALE)
				# Fix Matplotlib issue where when there is primary and secondary axis the legend box of one axis is transparent for the axis/series of the other
				# From: http://stackoverflow.com/questions/17158469/legend-transparency-when-using-secondary-axis
				if self._panel_has_primary_axis and self._panel_has_secondary_axis:
					axarr_prim.set_zorder(1)
					axarr_prim.set_frame_on(False)
					axarr_sec.set_frame_on(True)
		#  Print independent axis tick marks and label
		indep_var_min, indep_var_max, indep_var_locs = indep_axis_dict['indep_var_min'], indep_axis_dict['indep_var_max'], indep_axis_dict['indep_var_locs']
		indep_var_labels = indep_axis_dict['indep_var_labels'] if ('indep_var_labels' in indep_axis_dict) and (indep_axis_dict['indep_var_labels'] is not None) else None
		indep_axis_label = '' if indep_axis_dict['indep_axis_label'] is None or not print_indep_axis else indep_axis_dict['indep_axis_label'].strip()
		indep_axis_units = '' if indep_axis_dict['indep_axis_units'] is None else indep_axis_dict['indep_axis_units'].strip()
		indep_axis_unit_scale = '' if indep_axis_dict['indep_axis_unit_scale'] is None else indep_axis_dict['indep_axis_unit_scale'].strip()
		self._setup_axis('INDEP', axarr_prim, indep_var_min, indep_var_max, indep_var_locs, indep_var_labels, indep_axis_label, indep_axis_units, indep_axis_unit_scale)
		plt.setp(axarr_prim.get_xticklabels(), visible=print_indep_axis)
		return {'primary':None if not self._panel_has_primary_axis else axarr_prim, 'secondary':None if not self._panel_has_secondary_axis else axarr_sec}

	series = property(_get_series, _set_series, doc='Panel series')
	"""
	Panel series

	:type:	:py:class:`putil.plot.Series()` object or list of :py:class:`putil.plot.Series()` objects

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc(exclude=['putil.eng'])) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Panel.series

	:raises: (when assigned)

	 * RuntimeError (Argument `series` is not valid)

	 * RuntimeError (Series item *[number]* is not fully specified)

	 * ValueError (Series item *[number]* cannot be plotted in a logarithmic axis because it contains negative data points)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	primary_axis_label = property(_get_primary_axis_label, _set_primary_axis_label, doc='Panel primary axis label')
	"""
	Panel primary axis label

	:type:	string default is *''*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Panel.primary_axis_label

	:raises: (when assigned) RuntimeError (Argument `primary_axis_label` is not valid)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	secondary_axis_label = property(_get_secondary_axis_label, _set_secondary_axis_label, doc='Panel secondary axis label')
	"""
	Panel secondary axis label

	:type:	string, default is *''*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Panel.secondary_axis_label

	:raises: (when assigned) RuntimeError (Argument `secondary_axis_label` is not valid)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	primary_axis_units = property(_get_primary_axis_units, _set_primary_axis_units, doc='Panel primary axis units')
	"""
	Panel primary axis units

	:type:	string, default is *''*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Panel.primary_axis_units

	:raises: (when assigned) RuntimeError (Argument `primary_axis_units` is not valid)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	secondary_axis_units = property(_get_secondary_axis_units, _set_secondary_axis_units, doc='Panel secondary axis units')
	"""
	Panel secondary axis units

	:type:	string, default is *''*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Panel.secondary_axis_units

	:raises: (when assigned) RuntimeError (Argument `secondary_axis_units` is not valid)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	log_dep_axis = property(_get_log_dep_axis, _set_log_dep_axis, doc='Panel logarithmic dependent axis flag')
	"""
	Panel logarithmic dependent (primary and/or secondary) axis flag. Any plotted axis (primary, secondary or both) uses a logarithmic scale when this flag is *True*.

	:type:	boolean, default is *False*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Panel.log_dep_axis

	:raises: (when assigned) RuntimeError (Argument `log_dep_axis` is not valid)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	legend_props = property(_get_legend_props, _set_legend_props, doc='Panel legend box properties')
	"""
	Panel legend box properties. A dictionary that has properties (dictionary key) and their associated values (dictionary values). Currently supported properties are:

	* **pos** (*string*) -- legend box position, one of 'BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER' or 'CENTER' (case insensitive).

	* **cols** (integer) -- number of columns of the legend box

	.. note:: No legend is shown if a panel has only one series in it

	:type:	dictionary, default is *{'pos':'BEST', 'cols':1}*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Panel.legend_props

	:raises: (when assigned)

	 * RuntimeError (Argument `legend_props` is not valid)

	 * RuntimeError (Legend property `cols` is not valid)

	 * TypeError (Legend property `pos` is not one of ['BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER'] (case insensitive))

	 * ValueError (Illegal legend property `*[prop_name]*`)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	show_indep_axis = property(_get_show_indep_axis, _set_show_indep_axis, doc='Show independent axis flag')
	"""
	Show independent axis flag.

	:type:	boolean, default is *False*

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.Panel.show_indep_axis

	:raises: (when assigned) RuntimeError (Argument `show_indep_axis` is not valid)

	.. [[[end]]]
	"""	#pylint: disable=W0105


class Figure(object):	#pylint: disable=R0902
	"""
	Automagically generate presentation-quality plots

	:param	panels:				one or more data panels
	:type	panels:				:py:class:`putil.plot.Panel()` object or list of :py:class:`putil.plot.Panel()` objects
	:param	indep_var_label:	independent variable label
	:type	indep_var_label:	string
	:param	indep_var_units:	independent variable units
	:type	indep_var_units:	string
	:param	fig_width:			hard copy plot width
	:type	fig_width:			positive number
	:param	fig_height:			hard copy plot height
	:type	fig_height:			positive number
	:param	title:				plot title
	:type	title:				string
	:param	log_indep:			logarithmic independent axis flag
	:type	log_indep:			boolean
	:raises:
	 * Same as :py:attr:`putil.plot.Figure.panels`

	 * Same as :py:attr:`putil.plot.Figure.indep_var_label`

	 * Same as :py:attr:`putil.plot.Figure.indep_var_units`

	 * Same as :py:attr:`putil.plot.Figure.title`

	 * Same as :py:attr:`putil.plot.Figure.log_indep_axis`

	 * Same as :py:attr:`putil.plot.Figure.fig_width`

	 * Same as :py:attr:`putil.plot.Figure.fig_height`

	 * RuntimeError (Figure size is too small: minimum width = *[min_width]*, minimum height *[min_height]*)

	.. note:: The appropriate figure dimensions so that no labels are obstructed are calculated and used if **fig_width** and/or **fig_height** are not specified. The calculated figure width and/or height can be retrieved using \
	:py:attr:`putil.plot.Figure.fig_width` and/or :py:attr:`putil.plot.Figure.fig_height` attributes.
	"""
	def __init__(self, panels=None, indep_var_label='', indep_var_units='', fig_width=None, fig_height=None, title='', log_indep_axis=False):	#pylint: disable=R0913
		# Public attributes
		self._fig, self._panels, self._indep_var_label, self._indep_var_units, self._title, self._log_indep_axis, self._fig_width, self._fig_height, self._axes_list = None, None, None, None, None, None, None, None, list()
		# Assignment of arguments to attributes
		self._set_indep_var_label(indep_var_label)
		self._set_indep_var_units(indep_var_units)
		self._set_title(title)
		self._set_log_indep_axis(log_indep_axis)
		self._set_fig_width(fig_width)
		self._set_fig_height(fig_height)
		self._set_panels(panels)

	def _get_indep_var_label(self):	#pylint: disable=C0111
		return self._indep_var_label

	@putil.check.check_argument(putil.check.PolymorphicType([None, str]))
	def _set_indep_var_label(self, indep_var_label):	#pylint: disable=C0111
		self._indep_var_label = indep_var_label
		self._draw(force_redraw=True)

	def _get_indep_var_units(self):	#pylint: disable=C0111
		return self._indep_var_units

	@putil.check.check_argument(putil.check.PolymorphicType([None, str]))
	def _set_indep_var_units(self, indep_var_units):	#pylint: disable=C0111
		self._indep_var_units = indep_var_units
		self._draw(force_redraw=True)

	def _get_title(self):	#pylint: disable=C0111
		return self._title

	@putil.check.check_argument(putil.check.PolymorphicType([None, str]))
	def _set_title(self, title):	#pylint: disable=C0111
		self._title = title
		self._draw(force_redraw=True)

	def _get_log_indep_axis(self):	#pylint: disable=C0111
		return self._log_indep_axis

	@putil.check.check_argument(putil.check.PolymorphicType([None, bool]))
	def _set_log_indep_axis(self, log_indep_axis):	#pylint: disable=C0111
		self._log_indep_axis = log_indep_axis
		self._draw(force_redraw=True)

	def _get_fig_width(self):	#pylint: disable=C0111
		return self._fig_width

	@putil.check.check_argument(putil.check.PolymorphicType([None, putil.check.PositiveReal()]))
	def _set_fig_width(self, fig_width):	#pylint: disable=C0111
		self._fig_width = fig_width

	def _get_fig_height(self):	#pylint: disable=C0111
		return self._fig_height

	@putil.check.check_argument(putil.check.PolymorphicType([None, putil.check.PositiveReal()]))
	def _set_fig_height(self, fig_height):	#pylint: disable=C0111
		self._fig_height = fig_height

	def _get_panels(self):	#pylint: disable=C0111
		return self._panels

	def _set_panels(self, panels):	#pylint: disable=C0111
		self._panels = (panels if isinstance(panels, list) else [panels]) if panels is not None else panels
		if self.panels is not None:
			self._validate_panels()
		self._draw(force_redraw=True)

	def _validate_panels(self):
		""" Verifies that elements of panel list are of the right type and fully specified """
		for num, obj in enumerate(self.panels):
			if type(obj) is not Panel:
				raise TypeError('Argument `panels` is of the wrong type')
			if not obj._complete():	#pylint: disable=W0212
				raise RuntimeError('Panel {0} is not fully specified'.format(num))

	def _get_fig(self):	#pylint: disable=C0111
		return self._fig

	def _get_axes_list(self):	#pylint: disable=C0111
		return self._axes_list

	def _complete(self):
		""" Returns True if figure is fully specified, otherwise returns False """
		return (self.panels is not None) and (len(self.panels) > 0)

	def _draw(self, force_redraw=False, raise_exception=False):	#pylint: disable=C0111,R0914
		if (self._complete()) and force_redraw:
			num_panels = len(self.panels)
			plt.close('all')
			# Create required number of panels
			self._fig, axes = plt.subplots(num_panels, sharex=True)	#pylint: disable=W0612
			axes = axes if isinstance(axes, type(numpy.array([]))) else [axes]
			glob_indep_var = list()
			# Find union of the independent variable data set of all panels
			for panel_num, panel_obj in enumerate(self.panels):
				for series_num, series_obj in enumerate(panel_obj.series):
					if (self.log_indep_axis is not None) and self.log_indep_axis and (min(series_obj.indep_var) < 0):
						raise ValueError('Figure cannot cannot be plotted with a logarithmic independent axis because panel {0}, series {1} contains negative independent data points'.format(panel_num, series_num))
					glob_indep_var = numpy.unique(numpy.append(glob_indep_var, numpy.array([putil.misc.smart_round(element, 10) for element in series_obj.indep_var])))
			indep_var_locs, indep_var_labels, indep_var_min, indep_var_max, indep_var_div, indep_var_unit_scale = \
				_intelligent_ticks(glob_indep_var, min(glob_indep_var), max(glob_indep_var), tight=True, log_axis=self.log_indep_axis)
			# Scale all panel series
			for panel_obj in self.panels:
				panel_obj._scale_indep_var(indep_var_div)	#pylint: disable=W0212
			# Draw panels
			indep_axis_dict = {'indep_var_min':indep_var_min, 'indep_var_max':indep_var_max, 'indep_var_locs':indep_var_locs,
						 'indep_var_labels':None, 'indep_axis_label':None, 'indep_axis_units':None, 'indep_axis_unit_scale':None}
			indep_axis_dict = {'log_indep':self.log_indep_axis, 'indep_var_min':indep_var_min, 'indep_var_max':indep_var_max, 'indep_var_locs':indep_var_locs,
						 'indep_var_labels':indep_var_labels, 'indep_axis_label':self.indep_var_label, 'indep_axis_units':self.indep_var_units, 'indep_axis_unit_scale':indep_var_unit_scale}
			panels_with_indep_axis_list = [num for num, panel_obj in enumerate(self.panels) if panel_obj.show_indep_axis is True]
			panels_with_indep_axis_list = [num_panels-1] if len(panels_with_indep_axis_list) == 0 else panels_with_indep_axis_list
			for num, (panel_obj, axarr) in enumerate(zip(self.panels, axes)):
				panel_dict = panel_obj._draw_panel(axarr, indep_axis_dict, num in panels_with_indep_axis_list)	#pylint: disable=C0326,W0212
				self._axes_list.append({'number':num, 'primary':panel_dict['primary'], 'secondary':panel_dict['secondary']})
			if self.title not in [None, '']:
				axes[0].set_title(self.title, horizontalalignment='center', verticalalignment='bottom', multialignment='center', fontsize=TITLE_FONT_SIZE)
			#self._fig.canvas.draw()
			FigureCanvasAgg(self._fig).draw()	# Draw figure otherwise some bounding boxes return NaN
			self._calculate_figure_size()
		elif (not self._complete()) and (raise_exception):
			raise RuntimeError('Figure object is not fully specified')

	def _calculate_figure_size(self):	#pylint: disable=R0201,R0914
		""" Calculates minimum panel and figure size """
		title_height = title_width = 0
		title = self._fig.axes[0].get_title()
		if (title is not None) and (title.strip() != ''):
			title_obj = self._fig.axes[0].title
			title_height = _get_text_prop(self._fig, title_obj)['height']
			title_width = _get_text_prop(self._fig, title_obj)['width']
		xaxis_dims = [_get_xaxis_size(self._fig, axis_obj.xaxis.get_ticklabels(), axis_obj.xaxis.get_label()) for axis_obj in self._fig.axes]
		yaxis_dims = [_get_yaxis_size(self._fig, axis_obj.yaxis.get_ticklabels(), axis_obj.yaxis.get_label()) for axis_obj in self._fig.axes]
		panel_dims = [(yaxis_height+xaxis_height, yaxis_width+xaxis_width) for (yaxis_height, yaxis_width), (xaxis_height, xaxis_width) in zip(yaxis_dims, xaxis_dims)]
		min_fig_width = round((max(title_width, max([panel_width for _, panel_width in panel_dims])))/float(self._fig.dpi), 2)
		min_fig_height = round((((len(self._axes_list)*max([panel_height for panel_height, _ in panel_dims]))+title_height)/float(self._fig.dpi)), 2)
		if ((self.fig_width is not None) and (self.fig_width < min_fig_width)) or ((self.fig_height is not None) and (self.fig_height < min_fig_height)):
			raise RuntimeError('Figure size is too small: minimum width = {0}, minimum height {1}'.format(min_fig_width, min_fig_height))
		self.fig_width = min_fig_width if self.fig_width is None else self.fig_width
		self.fig_height = min_fig_height if self.fig_height is None else self.fig_height

	def show(self):	#pylint: disable=R0201
		"""
		Displays figure

		:raises:
		 * RuntimeError (Figure object is not fully specified)

		 * Same as :py:attr:`putil.plot.Figure.panels`
		"""
		self._draw(force_redraw=self._fig is None, raise_exception=True)
		plt.show()

	@putil.check.check_argument(putil.check.File())
	def save(self, file_name):
		"""
		Saves figure in PNG format to a file

		:param	file_name:	File name
		:type	file_name:	string
		:raises:
		 * TypeError (Argument `file_name` is of the wrong type)

		 * Same as :py:meth:`putil.plot.Figure.show()`
		"""
		if not self._complete():
			raise RuntimeError('Figure object is not fully specified')
		self._draw(force_redraw=self._fig is None, raise_exception=True)
		self.fig.set_size_inches(self.fig_width, self.fig_height)
		file_name = os.path.expanduser(file_name)	# Matplotlib seems to have a problem with ~/, expand it to $HOME
		putil.misc.make_dir(file_name)
		self._fig.savefig(file_name, bbox_inches='tight', dpi=self._fig.dpi)
		plt.close('all')

	def __str__(self):
		"""
		Print figure information
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
		ret += 'Independent variable label: {0}\n'.format(self.indep_var_label if self.indep_var_label not in ['', None] else 'not specified')
		ret += 'Independent variable units: {0}\n'.format(self.indep_var_units if self.indep_var_units not in ['', None] else 'not specified')
		ret += 'Logarithmic independent axis: {0}\n'.format(self.log_indep_axis)
		ret += 'Title: {0}\n'.format(self.title if self.title not in ['', None] else 'not specified')
		ret += 'Figure width: {0}\n'.format(self.fig_width)
		ret += 'Figure height: {0}\n'.format(self.fig_height)
		return ret

	indep_var_label = property(_get_indep_var_label, _set_indep_var_label, doc='Figure independent axis label')
	"""
	Figure independent variable label

	:type:		string or None, default is *''*
	:raises:
	 * TypeError (Argument `indep_var_label` is of the wrong type)

	 * Same as :py:attr:`putil.plot.Figure.panels`
	"""	#pylint: disable=W0105

	indep_var_units = property(_get_indep_var_units, _set_indep_var_units, doc='Figure independent axis units')
	"""
	Figure independent variable units

	:type:		string or None, default is *''*
	:raises:
	 * TypeError (Argument `indep_var_units` is of the wrong type)

	 * Same as :py:attr:`putil.plot.Figure.panels`
	"""	#pylint: disable=W0105

	title = property(_get_title, _set_title, doc='Figure title')
	"""
	Figure title

	:type:		string or None, default is *''*
	:raises:
	 * TypeError (Argument `title` is of the wrong type)

	 * Same as :py:attr:`putil.plot.Figure.panels`
	"""	#pylint: disable=W0105

	log_indep_axis = property(_get_log_indep_axis, _set_log_indep_axis, doc='Figure log_indep_axis')
	"""
	Figure logarithmic independent axis flag

	:type:		boolean, default is *False*
	:raises:
	 * TypeError (Argument `log_indep_axis` is of the wrong type)

	 * Same as :py:attr:`putil.plot.Figure.panels`
	"""	#pylint: disable=W0105

	fig_width = property(_get_fig_width, _set_fig_width, doc='Width of the hard copy plot')
	"""
	Width of the hard copy plot

	:type:		positive number, float or integer
	:raises:
	 * TypeError (Argument `fig_width` is of the wrong type)

	 * ValueError (Argument `fig_width` is not positive number)
	"""	#pylint: disable=W0105

	fig_height = property(_get_fig_height, _set_fig_height, doc='height of the hard copy plot')
	"""
	Height of the hard copy plot

	:type:		positive number, float or integer
	:raises:
	 * TypeError (Argument `fig_height` is of the wrong type)

	 * ValueError (Argument `fig_height` is not positive number)
	"""	#pylint: disable=W0105

	panels = property(_get_panels, _set_panels, doc='Figure panel(s)')
	"""
	Figure panel(s)

	:type:	:py:class:`putil.plot.Panel()` object or list of :py:class:`putil.plot.panel()` objects
	:raises:
	 * TypeError (Argument `panels` is of the wrong type)

	 * RuntimeError (Panel *[number]* is not fully specified)

	 * ValueError(Figure cannot cannot be plotted with a logarithmic independent axis because panel *[panel_num]*, series *[series_num]* contains negative independent data points)
	"""	#pylint: disable=W0105

	fig = property(_get_fig, doc='Figure handle')
	"""
	Matplotlib figure handle. Useful if annotations or further customizations to the figure are needed.

	:type:		Matplotlib figure handle if figure is fully specified, otherwise None
	"""	#pylint: disable=W0105

	axes_list = property(_get_axes_list, doc='Matplotlib figure axes handle list')
	"""
	Matplotlib figure axes handle list. Useful if annotations or further customizations to the panel(s) are needed. Each panel has an entry in the list, which is sorted in the order the panels are
	plotted (top to bottom). Each panel entry is a dictionary containing the following keys:

	* **number** (*integer*) -- panel number, panel 0 is the top-most panel

	* **primary** (*Matplotlib axis object*) -- axis handle for the primary axis, *None* if the figure has not primary axis

	* **secondary** (*Matplotlib axis object*) -- axis handle for the secondary axis, *None* if the figure has not secondary axis

	:type: list
	""" #pylint: disable=W0105

def _first_label(label_list):
	""" Find first non-blank label """
	for label_index, label_obj in enumerate(label_list):
		if (label_obj.get_text() is not None) and (label_obj.get_text().strip() != ''):
			return label_index
	return None

def _get_yaxis_size(fig_obj, tick_labels, axis_label):
	""" Compute Y axis height and width """
	# Minimum of one line spacing between vertical ticks
	axis_height = axis_width = 0
	if (tick_labels is not None) and (len(tick_labels) > 0):
		label_index = _first_label(tick_labels)
		if label_index is not None:
			label_height = _get_text_prop(fig_obj, tick_labels[label_index])['height']
			axis_height = (2*len(tick_labels)-1)*label_height
			axis_width = max([num for num in [_get_text_prop(fig_obj, tick)['width'] for tick in tick_labels] if isinstance(num, int) or isinstance(num, float)])
	if axis_label is not None:
		axis_height = max(axis_height, _get_text_prop(fig_obj, axis_label)['height'])
		axis_width = axis_width+(1.5*_get_text_prop(fig_obj, axis_label)['width'])
	return axis_height, axis_width

def _get_xaxis_size(fig_obj, tick_labels, axis_label):
	""" Compute Y axis height and width """
	# Minimum of one smallest label separation between horizontal ticks
	axis_height = axis_width = 0
	if (tick_labels is not None) and (len(tick_labels) > 0):
		min_label_width = min([num for num in [_get_text_prop(fig_obj, tick)['width'] for tick in tick_labels] if isinstance(num, int) or isinstance(num, float)])
		axis_width = ((len(tick_labels)-1)*min_label_width)+sum([num for num in [_get_text_prop(fig_obj, tick)['width'] for tick in tick_labels] if isinstance(num, int) or isinstance(num, float)])
	if axis_label is not None:
		axis_height = (axis_height+(1.5*_get_text_prop(fig_obj, axis_label)['height']))
		axis_width = max(axis_width, _get_text_prop(fig_obj, axis_label)['width'])
	return axis_height, axis_width

def _process_ticks(locs, min_lim, max_lim, mant):
	"""
	Returns pretty-printed tick locations that are within the given bound
	"""
	locs = [float(loc) for loc in locs]
	bounded_locs = [loc for loc in locs if ((loc >= min_lim) or (abs(loc-min_lim) <= 1e-14)) and ((loc <= max_lim) or (abs(loc-max_lim) <= 1e-14))]
	raw_labels = [putil.eng.peng(float(loc), mant, rjust=False) if ((abs(loc) >= 1) or (loc == 0)) else str(putil.misc.smart_round(loc, mant)) for loc in bounded_locs]
	return (bounded_locs, [label.replace('u', '$\\mu$') for label in raw_labels])

def _intelligent_ticks(series, series_min, series_max, tight=True, log_axis=False):	#pylint: disable=R0912,R0914,R0915
	""" Calculates ticks 'intelligently', trying to calculate sane tick spacing """
	# Handle 1-point series
	if len(series) == 1:
		series_min = series_max = series[0]
		tick_spacing = putil.misc.smart_round(0.1*series[0], PRECISION)
		tick_list = numpy.array([series[0]-tick_spacing, series[0], series[0]+tick_spacing])
		tick_spacing = putil.misc.smart_round(0.1*series[0], PRECISION)
		tight = tight_left = tight_right = log_axis = False
	else:
		if log_axis:
			dec_start = int(math.log10(min(series)))
			dec_stop = int(math.ceil(math.log10(max(series))))
			tick_list = [10**num for num in range(dec_start, dec_stop+1)]
			tight_left = False if (not tight) and (tick_list[0] >= min(series)) else True
			tight_right = False if (not tight) and (tick_list[-1] <= max(series)) else True
			tick_list = numpy.array(tick_list)
		else:
			# Try to find the tick spacing that will have the most number of data points on grid. Otherwise, place max_ticks uniformely distributed across the data rage
			series_delta = putil.misc.smart_round(max(series)-min(series), PRECISION)
			working_series = series[:].tolist()
			tick_list = list()
			num_ticks = SUGGESTED_MAX_TICKS
			while (num_ticks >= MIN_TICKS) and (len(working_series) > 1):
				data_spacing = [putil.misc.smart_round(element, PRECISION) for element in numpy.diff(working_series)]
				tick_spacing = putil.misc.gcd(data_spacing)
				num_ticks = (series_delta/tick_spacing)+1
				if (num_ticks >= MIN_TICKS) and (num_ticks <= SUGGESTED_MAX_TICKS):
					tick_list = numpy.linspace(putil.misc.smart_round(min(series), PRECISION), putil.misc.smart_round(max(series), PRECISION), num_ticks).tolist()	#pylint: disable=E1103
					break
				# Remove elements that cause minimum spacing, to see if with those elements removed the number of tick marks can be withing the acceptable range
				min_data_spacing = min(data_spacing)
				# Account for fact that if minimum spacing is between last two elements, the last element cannot be removed (it is the end of the range), but rather the next-to-last has to be removed
				if (data_spacing[-1] == min_data_spacing) and (len(working_series) > 2):
					working_series = working_series[:-2]+[working_series[-1]]
					data_spacing = [putil.misc.smart_round(element, PRECISION) for element in numpy.diff(working_series)]
				working_series = [working_series[0]]+[element for element, spacing in zip(working_series[1:], data_spacing) if spacing != min_data_spacing]
			tick_list = tick_list if len(tick_list) > 0 else numpy.linspace(min(series), max(series), SUGGESTED_MAX_TICKS).tolist()	#pylint: disable=E1103
			tick_spacing = putil.misc.smart_round(tick_list[1]-tick_list[0], PRECISION)
			# Account for interpolations, whose curves might have values above or below the data points. Only add an extra tick, otherwise let curve go above/below panel
			tight_left = False if (not tight) and (tick_list[0] >= series_min) else tight
			tight_right = False if (not tight) and (tick_list[-1] <= series_max) else tight
			tick_list = numpy.array(tick_list if tight else ([tick_list[0]-tick_spacing] if not tight_left else [])+tick_list+([tick_list[-1]+tick_spacing] if not tight_right else []))
	# Scale series with minimum, maximum and delta as reference, pick scaling option that has the most compact representation
	opt_min = _scale_ticks(tick_list, 'MIN')
	opt_max = _scale_ticks(tick_list, 'MAX')
	opt_delta = _scale_ticks(tick_list, 'DELTA')
	opt = opt_min if (opt_min['count'] <= opt_max['count']) and (opt_min['count'] <= opt_delta['count']) else (opt_max if (opt_max['count'] <= opt_min['count']) and (opt_max['count'] <= opt_delta['count']) else opt_delta)
	# Add extra room in logarithmic axis if Tight is True, but do not label marks (aesthetic decision)
	if log_axis and not tight:
		if not tight_left:
			opt['min'] = putil.misc.smart_round(0.9*opt['loc'][0], PRECISION)
			opt['loc'].insert(0, opt['min'])
			opt['labels'].insert(0, '')
		if not tight_right:
			opt['max'] = putil.misc.smart_round(1.1*opt['loc'][-1], PRECISION)
			opt['loc'].append(opt['max'])
			opt['labels'].append('')
	return (opt['loc'], opt['labels'], opt['min'], opt['max'], opt['scale'], opt['unit'])

def _scale_ticks(tick_list, mode):
	""" Scale series taking the reference to be the series start, stop or delta """
	mode = mode.strip().upper()
	tick_min = tick_list[0]
	tick_max = tick_list[-1]
	tick_delta = tick_max-tick_min
	tick_ref = tick_min if mode == 'MIN' else (tick_max if mode == 'MAX' else tick_delta)
	(unit, scale) = putil.eng.peng_power(putil.eng.peng(tick_ref, 3))
	# Move one engineering unit back if there are more ticks below 1.0 than above it
	rollback = (sum((tick_list/scale) >= 1000) > sum((tick_list/scale) < 1000)) and (tick_list[-1]/scale < 10000)
	scale = 1 if rollback else scale
	unit = putil.eng.peng_suffix_math(unit, +1) if rollback else unit
	tick_list = numpy.array([putil.misc.smart_round(element/scale, PRECISION) for element in tick_list])
	tick_min = putil.misc.smart_round(tick_min/scale, PRECISION)
	tick_max = putil.misc.smart_round(tick_max/scale, PRECISION)
	loc, labels = _uniquify_tick_labels(tick_list, tick_min, tick_max)
	count = len(''.join(labels))
	return {'loc':loc, 'labels':labels, 'unit':unit, 'scale':scale, 'min':tick_min, 'max':tick_max, 'count':count}

def _mantissa_digits(num):
	""" Get number of digits in the mantissa """
	snum = str(num)
	return 0 if (snum.find('.') == -1) or str(float(int(num))) == snum else len(snum)-snum.find('.')-1

def _uniquify_tick_labels(tick_list, tmin, tmax):
	""" Calculate minimum tick mantissa given tick spacing """
	# If minimum or maximum has a mantissa, at least preserve one digit
	mant_min = 1 if max(_mantissa_digits(tick_list[0]), _mantissa_digits(tick_list[-1])) > 0 else 0
	# Step 1: Look at two contiguous ticks and lower mantissa digits till they are no more right zeros
	mant = 10
	for mant in range(10, mant_min-1, -1):
		if (str(putil.eng.peng_frac(putil.eng.peng(tick_list[-1], mant)))[-1] != '0') or (str(putil.eng.peng_frac(putil.eng.peng(tick_list[-2], mant)))[-1] != '0'):
			break
	# Step 2: Confirm labels are unique
	unique_mant_found = False
	while mant >= mant_min:
		loc, labels = _process_ticks(tick_list, tmin, tmax, mant)
		if (sum([1 if labels[index] != labels[index+1] else 0 for index in range(0, len(labels[:-1]))]) == len(labels)-1) and \
				(sum([1 if (putil.eng.peng_float(label) != 0) or ((putil.eng.peng_float(label) == 0) and (num == 0)) else 0 for num, label in zip(tick_list, labels)]) == len(labels)):
			unique_mant_found = True
			mant -= 1
		else:
			mant += 1
			if unique_mant_found:
				loc, labels = _process_ticks(tick_list, tmin, tmax, mant)
				break
	return [putil.misc.smart_round(element, PRECISION) for element in loc], labels

def _get_text_prop(fig, text_obj):
	""" Return length of text in pixels """
	renderer = fig.canvas.get_renderer()
	bbox = text_obj.get_window_extent(renderer=renderer).transformed(fig.dpi_scale_trans.inverted())
	return {'width':bbox.width*fig.dpi, 'height':bbox.height*fig.dpi}

def _get_panel_prop(fig, axarr):
	""" Return height of (sub)panel in pixels """
	renderer = fig.canvas.get_renderer()
	bbox = axarr.get_window_extent(renderer=renderer).transformed(fig.dpi_scale_trans.inverted())
	return {'width':bbox.width*fig.dpi, 'height':bbox.height*fig.dpi}

_COLOR_SPACE_NAME_LIST = ['binary', 'Blues', 'BuGn', 'BuPu', 'gist_yarg', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']
@putil.check.check_arguments({'param_list':putil.check.ArbitraryLengthList(putil.check.Number()), 'offset':putil.check.NumberRange(0, 1), 'color_space':putil.check.OneOf(_COLOR_SPACE_NAME_LIST)})
def parameterized_color_space(param_list, offset=0, color_space='binary'):
	"""
	Computes a color space where lighter colors correspond to lower parameter values

	:param	param_list:		parameter list
	:type	param_list:		list of numbers (parameter values)
	:param	offset:			offset of the first (lightest) color
	:type	offset:			float between 0 and 1
	:param	color_space:	`color pallete <http://arnaud.ensae.net/Rressources/RColorBrewer.pdf>`_. One of 'binary', 'Blues', 'BuGn', 'BuPu', 'gist_yarg', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', \
	'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr' or 'YlOrRd' (case sensitive).
	:type	color_space:	string
	:rtype:					Matplotlib color
	:raises:
	 * TypeError (Argument `param_list` is of the wrong type)

	 * ValueError (Argument `param_list` is empty)

	 * TypeError (Argument `offset` is of the wrong type)

	 * ValueError (Argument `offset` is not in the range [0.0, 1.0])

	 * ValueError (Argument `color_space` is of the wrong type')

	 * ValueError (Argument `color_space` is not one of ['binary', 'Blues', 'BuGn', 'BuPu', 'gist_yarg', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', \
	 'YlOrBr', 'YlOrRd'] (case insensitive))
	"""
	if len(param_list) == 0:
		raise TypeError('Argument `param_list` is empty')
	color_pallete_list = [plt.cm.binary, plt.cm.Blues, plt.cm.BuGn, plt.cm.BuPu, plt.cm.gist_yarg, plt.cm.GnBu, plt.cm.Greens, plt.cm.Greys, plt.cm.Oranges, plt.cm.OrRd, plt.cm.PuBu,	#pylint: disable=E1101
					   plt.cm.PuBuGn, plt.cm.PuRd, plt.cm.Purples, plt.cm.RdPu, plt.cm.Reds, plt.cm.YlGn, plt.cm.YlGnBu, plt.cm.YlOrBr, plt.cm.YlOrRd]	#pylint: disable=E1101
	color_dict = dict(zip(_COLOR_SPACE_NAME_LIST, color_pallete_list))
	return [color_dict[color_space](putil.misc.normalize(value, param_list, offset)) for value in param_list]	#pylint: disable=E1101
