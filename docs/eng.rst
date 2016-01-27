.. eng.rst
.. Copyright (c) 2013-2016 Pablo Acosta-Serafini
.. See LICENSE for details
.. py:module:: putil.eng

##########
eng module
##########

This module provides engineering-related functions including:

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

************
Named tuples
************

.. autofunction:: putil.eng.ENGPOWER
.. autofunction:: putil.eng.NUMCOMP

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
.. autofunction:: putil.eng.round_mantissa
.. autofunction:: putil.eng.to_scientific_string
.. autofunction:: putil.eng.to_scientific_tuple
