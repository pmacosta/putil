.. _eng-module:

##########
eng module
##########



This module provides engineering-related functions, mainly handling numbers represented in engineering notation, obtaining their constituent components and converting to and from regular floats. For example:

	>>> import putil.eng
	>>> x = putil.eng.peng(1346, 2, False)
	>>> x
	'1.25k'
	>>> x = putil.eng.peng(1346, 2, True)
	'   1.25k'
	>>> putil.eng.peng_float(x)
	1250.0
	>>> putil.eng.peng_int(x)
	1
	>>> putil.eng.peng_frac(x)
	25
	>>> putil.eng.peng_mant(x)
	1.25
	>>> putil.eng.peng_power(x)
	('k', 1000.0)
	>>> putil.eng.peng_suffix(x)
	'k'

***************************************
Application programming interface (API)
***************************************

Pseudo-types
============

EngineeringNotationNumber
-------------------------

String with a number represented in engineering notation. Optional leading whitespace can precede the mantissa; optional whitespace can also follow the engineering suffix. An optional sign (+ or -) can precede the mantissa after
the leading whitespace. The suffix must be one of y, z, a, f, p, n, u, m, (space) , k, M, G, T, P, E, Z or Y. :py:func:`putil.eng.peng` lists the correspondence between suffix and floating point exponent.

EngineeringNotationSuffix
-------------------------

A single character string, one of y, z, a, f, p, n, u, m, (space) , k, M, G, T, P, E, Z, or Y. :py:func:`putil.eng.peng` lists the correspondence between suffix and floating point exponent.

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
