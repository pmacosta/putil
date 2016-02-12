.. eng.rst
.. Copyright (c) 2013-2016 Pablo Acosta-Serafini
.. See LICENSE for details
.. py:module:: putil.eng

##########
eng module
##########

This module provides engineering-related classes and functions.

The functions include:

* Handling numbers represented in engineering notation, obtaining
  their constituent components and converting to and from regular
  floats. For example:

    .. code-block:: python


		>>> import putil.eng
		>>> x = putil.eng.peng(1346, 2, True)
		>>> x
		'   1.35k'
		>>> putil.eng.peng_float(x)
		1350.0
		>>> putil.eng.peng_int(x)
		1
		>>> putil.eng.peng_frac(x)
		35
		>>> str(putil.eng.peng_mant(x))
		'1.35'
		>>> putil.eng.peng_power(x)
		EngPower(suffix='k', exp=1000.0)
		>>> putil.eng.peng_suffix(x)
		'k'

* Pretty printing Numpy vectors. For example:

    .. code-block:: python

		>>> from __future__ import print_function
		>>> import putil.eng
		>>> header = 'Vector: '
		>>> data = [1e-3, 20e-6, 30e+6, 4e-12, 5.25e3, -6e-9, 70, 8, 9]
		>>> print(
		...     header+putil.eng.pprint_vector(
		...         data,
		...         width=30,
		...         eng=True,
		...         frac_length=1,
		...         limit=True,
		...         indent=len(header)
		...     )
		... )
		Vector: [    1.0m,   20.0u,   30.0M,
		                     ...
		            70.0 ,    8.0 ,    9.0  ]

* Formatting numbers represented in scientific notation with a greater
  degree of control and options than standard Python string formatting.
  For example:

    .. code-block:: python

		>>> import putil.eng
		>>> putil.eng.to_scientific_string(
		...     number=99.999,
		...     frac_length=1,
		...     exp_length=2,
		...     sign_always=True
		... )
		'+1.0E+02'

The classes include:

* A waveform class that is a first-class object. For example:

	.. doctest::

		>>> import copy, numpy, putil.eng
		>>> obj_a=putil.eng.Waveform(
		...     indep_vector=numpy.array([1, 2, 3]),
                ...     dep_vector=numpy.array([10, 20, 30]),
                ...     indep_name='obj_a'
		... )
                >>> obj_b = obj_a*2
                >>> print(obj_b)
                Waveform: obj_a*2
                Independent variable: [ 1, 2, 3 ]
                Dependent variable: [ 20, 40, 60 ]
                Independent variable scale: LINEAR
                Dependent variable scale: LINEAR
                Independent variable units: (None)
                Dependent variable units: (None)
                Interpolating function: CONTINUOUS
                >>> obj_c = copy.copy(obj_b)
                >>> obj_a == obj_b
                False
                >>> obj_b == obj_c
                True

****************
Global variables
****************

.. autodata:: putil.eng.FP_ATOL
.. autodata:: putil.eng.FP_RTOL

************
Named tuples
************

.. autofunction:: putil.eng.EngPower
.. autofunction:: putil.eng.NumComp
.. autofunction:: putil.eng.Point

*********
Functions
*********

.. autofunction:: putil.eng.no_exp
.. autofunction:: putil.eng.peng
.. autofunction:: putil.eng.peng_float
.. autofunction:: putil.eng.peng_frac
.. autofunction:: putil.eng.peng_int
.. autofunction:: putil.eng.peng_mant
.. autofunction:: putil.eng.peng_power
.. autofunction:: putil.eng.peng_suffix
.. autofunction:: putil.eng.peng_suffix_math
.. autofunction:: putil.eng.pprint_vector
.. autofunction:: putil.eng.remove_extra_delims
.. autofunction:: putil.eng.round_mantissa
.. autofunction:: putil.eng.to_scientific_string
.. autofunction:: putil.eng.to_scientific_tuple


*******
Classes
*******

 .. autoclass:: putil.eng.Waveform
	:members: __add__,
                  __and__,
                  __bool__,
                  __copy__,
                  __delitem__,
                  __div__,
                  __eq__,
                  __floordiv__,
                  __ge__,
                  __getitem__,
                  __gt__,
                  __invert__,
                  __iter__,
                  __le__,
                  __len__,
                  __lshift__,
                  __lt__,
                  __mod__,
                  __mul__,
                  __ne__,
                  __neg__,
                  __nonzero__,
                  __or__,
                  __pos__,
                  __pow__,
                  __sub__,
                  __radd__,
                  __rand__,
                  __repr__,
                  __rfloordiv__,
                  __rlshift__,
                  __rmod__,
                  __rmul__,
                  __ror__,
                  __rpow__,
                  __rrshift__,
                  __rshift__,
                  __rsub__,
                  __rtruediv__,
                  __rxor__,
                  __setitem__,
                  __str__,
                  __truediv__,
                  __xor__,
                  vectors,
                  dep_scale,
                  dep_units,
                  dep_vector,
                  indep_scale,
                  indep_units,
                  indep_vector,
                  interp
	:show-inheritance:
