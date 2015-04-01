# basic_source.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302

import numpy

import putil.exh, putil.pcontracts
from .constants import PRECISION


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_plot_basic_source
exobj_plot = trace_ex_plot_basic_source.trace_module(no_print=True)
]]]
[[[end]]]
"""	#pylint: disable=W0105


###
# Class
###
class BasicSource(object):	#pylint: disable=R0902,R0903
	r"""
	Objects of this class hold a given data set intended for plotting. It is a convenient way to plot manually-entered data or data coming from
	a source that does not export to a comma-separated values (CSV) file.

	:param	indep_var:			independent variable vector
	:type	indep_var:			increasing real Numpy vector
	:param	dep_var:			dependent variable vector
	:type	dep_var:			real Numpy vector
	:param	indep_min:			minimum independent variable value
	:type	indep_min:			number or None
	:param	indep_max:			maximum independent variable value
	:type	indep_max:			number or None
	:rtype:						:py:class:`putil.plot.BasicSource` object

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.basic_source.BasicSource.__init__

	:raises:
	 * RuntimeError (Argument \`dep_var\` is not valid)

	 * RuntimeError (Argument \`indep_max\` is not valid)

	 * RuntimeError (Argument \`indep_min\` is not valid)

	 * RuntimeError (Argument \`indep_var\` is not valid)

	 * ValueError (Argument \`indep_min\` is greater than argument \`indep_max\`)

	 * ValueError (Argument \`indep_var\` is empty after \`indep_min\`/\`indep_max\` range bounding)

	 * ValueError (Arguments \`indep_var\` and \`dep_var\` must have the same number of elements)

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
	r"""
	Gets or sets the minimum independent variable limit

	:type:		number or None, default is None

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.basic_source.BasicSource.indep_min

	:raises: (when assigned)

	 * RuntimeError (Argument \`indep_min\` is not valid)

	 * ValueError (Argument \`indep_min\` is greater than argument \`indep_max\`)

	 * ValueError (Argument \`indep_var\` is empty after \`indep_min\`/\`indep_max\` range bounding)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	indep_max = property(_get_indep_max, _set_indep_max, None, doc='Maximum of independent variable')
	r"""
	Gets or sets the maximum independent variable limit

	:type:		number or None, default is None

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.basic_source.BasicSource.indep_max

	:raises: (when assigned)

	 * RuntimeError (Argument \`indep_max\` is not valid)

	 * ValueError (Argument \`indep_min\` is greater than argument \`indep_max\`)

	 * ValueError (Argument \`indep_var\` is empty after \`indep_min\`/\`indep_max\` range bounding)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	indep_var = property(_get_indep_var, _set_indep_var, None, doc='Independent variable Numpy vector')
	r"""
	Gets or sets the independent variable data

	:type:		increasing real Numpy vector

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.basic_source.BasicSource.indep_var

	:raises: (when assigned)

	 * RuntimeError (Argument \`indep_var\` is not valid)

	 * ValueError (Argument \`indep_var\` is empty after \`indep_min\`/\`indep_max\` range bounding)

	 * ValueError (Arguments \`indep_var\` and \`dep_var\` must have the same number of elements)

	.. [[[end]]]
	"""	#pylint: disable=W0105

	dep_var = property(_get_dep_var, _set_dep_var, None, doc='Dependent variable Numpy vector')
	r"""
	Gets or sets the dependent variable data

	:type:		real Numpy vector

	.. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.plot.basic_source.BasicSource.dep_var

	:raises: (when assigned)

	 * RuntimeError (Argument \`dep_var\` is not valid)

	 * ValueError (Arguments \`indep_var\` and \`dep_var\` must have the same number of elements)

	.. [[[end]]]
	"""	#pylint: disable=W0105
