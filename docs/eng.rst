.. eng.rst
.. Copyright (c) 2013-2015 Pablo Acosta-Serafini
.. See LICENSE for details
.. _eng-module:

##########
eng module
##########

This module provides engineering-related functions including:

* Handling numbers represented in engineering notation, obtaining
  their constituent components and converting to and from regular
  floats. For example:

	.. doctest::

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
		>>> putil.eng.peng_mant(x)
		1.35
		>>> putil.eng.peng_power(x)
		('k', 1000.0)
		>>> putil.eng.peng_suffix(x)
		'k'

* Pretty printing Numpy vectors. For example:

	.. doctest::

		>>> import putil.eng
		>>> header = 'Vector: '
		>>> data = [1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 8, 9]
		>>> print header+putil.eng.pprint_vector(
		...     data,
		...     width=30,
		...     eng=True,
		...     frac_length=1,
		...     limit=True,
		...     indent=len(header)
		... )
		Vector: [    1.0m,   20.0u,  300.0M,
		                     ...
		           700.0 ,    8.0 ,    9.0  ]

* Formatting numbers represented in scientific notation with a greater
  degree of control and options than standard Python string formatting.
  For example:

	.. doctest::

		>>> import putil.eng
		>>> putil.eng.to_scientific_string(
		...     number=99.999,
		...     frac_length=1,
		...     exp_length=2,
		...     sign_always=True
		... )
		'+1.0E+02'

***************************************
Application programming interface (API)
***************************************

Pseudo-types
============

EngineeringNotationNumber
-------------------------

String with a number represented in engineering notation. Optional leading
whitespace can precede the mantissa; optional whitespace can also follow the
engineering suffix. An optional sign (+ or -) can precede the mantissa after
the leading whitespace. The suffix must be one of :code:`'y'`, :code:`'z'`,
:code:`'a'`, :code:`'f'`, :code:`'p'`, :code:`'n'`, :code:`'u'`, :code:`'m'`,
:code:`' '` (space), :code:`'k'`, :code:`'M'`, :code:`'G'`, :code:`'T'`,
:code:`'P'`, :code:`'E'`, :code:`'Z'` or :code:`'Y'`.
:py:func:`putil.eng.peng` lists the correspondence between suffix and floating
point exponent.

EngineeringNotationSuffix
-------------------------

A single character string, one  of :code:`'y'`, :code:`'z'`, :code:`'a'`,
:code:`'f'`, :code:`'p'`, :code:`'n'`, :code:`'u'`, :code:`'m'`,
:code:`' '` (space), :code:`'k'`, :code:`'M'`, :code:`'G'`, :code:`'T'`,
:code:`'P'`, :code:`'E'`, :code:`'Z'` or :code:`'Y'`. :py:func:`putil.eng.peng`
lists the correspondence between suffix and floating point exponent.

Contracts
=========

.. autofunction:: putil.eng.engineering_notation_number
.. autofunction:: putil.eng.engineering_notation_suffix
.. autofunction:: putil.eng.pos_integer

Functions
=========

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

*******
License
*******

The MIT License (MIT)

Copyright (c) 2013-2015 Pablo Acosta-Serafini

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
