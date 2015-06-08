.. ptypes.rst
.. Copyright (c) 2013-2015 Pablo Acosta-Serafini
.. See LICENSE for details
.. _ptypes-module:

#############
ptypes module
#############

This module provides several pseudo-type definitions which can be enforced
and/or validated with custom contracts defined using the pcontracts module

************
Pseudo-types
************

.. _ColorSpaceOption:

ColorSpaceOption
----------------
String representing a Matplotlib color space, one :code:`'binary'`,
:code:`'Blues'`, :code:`'BuGn'`, :code:`'BuPu'`, :code:`'GnBu'`,
:code:`'Greens'`, :code:`'Greys'`, :code:`'Oranges'`, :code:`'OrRd'`,
:code:`'PuBu'`, :code:`'PuBuGn'`, :code:`'PuRd'`, :code:`'Purples'`,
:code:`'RdPu'`, :code:`'Reds'`, :code:`'YlGn'`, :code:`'YlGnBu'`,
:code:`'YlOrBr`', :code:`'YlOrRd'` or :code:`None`

.. _CsvDataFilter:

CsvDataFilter
-------------

The comma-separated values (CSV) data filter is a dictionary whose elements
are sub-filters with the following structure:

* **column name** *(string)* -- Dictionary key. Column to filter (as it appears
  in the comma-separated values file header)

* **value** *(list of strings or numbers, or string or number)* -- Dictionary
  value. Column value to filter if a string or number, column values to filter
  if a list of strings or numbers

If a data filter sub-filter is a column value all rows which contain the
specified value in the specified column are kept for that particular
individual filter. The overall data set is the intersection of all the data
sets specified by each individual filter. For example, if the file to be
processed is:

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
|    3 |   5 |     50 |
+------+-----+--------+

Then the filter specification ``dfilter = {'Ctrl':2, 'Ref':5}`` would result
in the following filtered data set:

+------+-----+--------+
| Ctrl | Ref | Result |
+======+=====+========+
|    2 |   5 |     40 |
+------+-----+--------+

However, the filter specification ``dfilter = {'Ctrl':2, 'Ref':3}`` would
result in an empty list because the data set specified by the `Ctrl`
individual filter does not overlap with the data set specified by the `Ref`
individual filter.

If a data filter sub-filter is a list, the items of the list represent all
the values to be kept for a particular column (strings or numbers). So for
example ``dfilter = {'Ctrl':[2, 3], 'Ref':5}`` would result in the following
filtered data set:

+------+-----+--------+
| Ctrl | Ref | Result |
+======+=====+========+
|    2 |   5 |     40 |
+------+-----+--------+
|    3 |   5 |     50 |
+------+-----+--------+

.. _EngineeringNotationNumber:

EngineeringNotationNumber
-------------------------

String with a number represented in engineering notation. Optional leading
whitespace can precede the mantissa; optional whitespace can also follow the
engineering suffix. An optional sign (+ or -) can precede the mantissa after
the leading whitespace. The suffix must be one of :code:`'y'`, :code:`'z'`,
:code:`'a'`, :code:`'f'`, :code:`'p'`, :code:`'n'`, :code:`'u'`, :code:`'m'`,
:code:`' '` (space), :code:`'k'`, :code:`'M'`, :code:`'G'`, :code:`'T'`,
:code:`'P'`, :code:`'E'`, :code:`'Z'` or :code:`'Y'`.  The correspondence
between suffix and floating point exponent is:

+----------+-------+--------+
| Exponent | Name  | Suffix |
+==========+=======+========+
| 1E-24    | yocto | y      |
+----------+-------+--------+
| 1E-21    | zepto | z      |
+----------+-------+--------+
| 1E-18    | atto  | a      |
+----------+-------+--------+
| 1E-15    | femto | f      |
+----------+-------+--------+
| 1E-12    | pico  | p      |
+----------+-------+--------+
| 1E-9     | nano  | n      |
+----------+-------+--------+
| 1E-6     | micro | u      |
+----------+-------+--------+
| 1E-3     | milli | m      |
+----------+-------+--------+
| 1E+0     |       |        |
+----------+-------+--------+
| 1E+3     | kilo  | k      |
+----------+-------+--------+
| 1E+6     | mega  | M      |
+----------+-------+--------+
| 1E+9     | giga  | G      |
+----------+-------+--------+
| 1E+12    | tera  | T      |
+----------+-------+--------+
| 1E+15    | peta  | P      |
+----------+-------+--------+
| 1E+18    | exa   | E      |
+----------+-------+--------+
| 1E+21    | zetta | Z      |
+----------+-------+--------+
| 1E+24    | yotta | Y      |
+----------+-------+--------+

.. _EngineeringNotationSuffix:

EngineeringNotationSuffix
-------------------------

A single character string, one  of :code:`'y'`, :code:`'z'`, :code:`'a'`,
:code:`'f'`, :code:`'p'`, :code:`'n'`, :code:`'u'`, :code:`'m'`,
:code:`' '` (space), :code:`'k'`, :code:`'M'`, :code:`'G'`, :code:`'T'`,
:code:`'P'`, :code:`'E'`, :code:`'Z'` or :code:`'Y'`.
:ref:`EngineeringNotationNumber` lists the correspondence between
suffix and floating point exponent.

.. _FileName:

FileName
--------

Valid file name

.. _FileNameExists:

FileNameExists
--------------

File name that exists in the file system

.. _Function:

Function
--------
Callable pointer or :code:`None`

.. _IncreasingRealNumpyVector:

IncreasingRealNumpyVector
-------------------------
Numpy vector in which all elements are real (integers and/or floats) and
monotonically increasing (each element is strictly greater than the
preceeding one)

.. _InterpolationOption:

InterpolationOption
-------------------
String representing an interpolation type, one of :code:`'STRAIGHT'`,
:code:`'STEP'`, :code:`'CUBIC'`, :code:`'LINREG'` or :code:`None`

.. _LineStyleOption:

LineStyleOption
---------------
String representing a Matplotlib line style, one of :code:`'-'`,
:code:`'--'`, :code:`'-.'`, :code:`':'` or :code:`None`

.. _NodeName:

NodeName
--------

A tree node name is a string where hierarchy levels are denoted by node
separator characters (:code:`'.'` by default). Node names cannot contain
spaces, empty hierarchy levels, start or end with a node separator character.

For this example tree::

	root
	├branch1
	│├leaf1
	│└leaf2
	└branch2

The node names are ``'root'``, ``'root.branch1'``, ``'root.branch1.leaf1'``,
``'root.branch1.leaf2'`` and ``'root.branch2'``.

.. _NodesWithData:

NodesWithData
-------------

Dictionary or list of dictionaries. Each dictionary must contain exactly two
keys:

* **name** (*NodeName*) Node name. See `NodeName`_ pseudo-type specification

* **data** (*any*) node data

The node data should be an empty list to create a node without data, for
example: :code:`{'name':'a.b.c', 'data':list()}`

.. _NonNegativeInteger:

NonNegativeInteger
------------------
Integer greater or equal to zero

.. _OffsetRange:

OffsetRange
-----------
Number in the [0, 1] range

.. _PositiveRealNum:

PositiveRealNum
---------------
Integer or float greater than zero or :code:`None`

.. _RealNum:

RealNum
-------
Integer, float or :code:`None`

.. _RealNumpyVector:

RealNumpyVector
---------------
Numpy vector in which all elements are real (integers and/or floats)

*********
Contracts
*********

.. autofunction:: putil.ptypes.color_space_option
.. autofunction:: putil.ptypes.csv_data_filter
.. autofunction:: putil.ptypes.engineering_notation_number
.. autofunction:: putil.ptypes.engineering_notation_suffix
.. autofunction:: putil.ptypes.non_negative_integer
.. autofunction:: putil.ptypes.file_name
.. autofunction:: putil.ptypes.file_name_exists
.. autofunction:: putil.ptypes.function
.. autofunction:: putil.ptypes.increasing_real_numpy_vector
.. autofunction:: putil.ptypes.interpolation_option
.. autofunction:: putil.ptypes.line_style_option
.. autofunction:: putil.ptypes.offset_range
.. autofunction:: putil.ptypes.positive_real_num
.. autofunction:: putil.ptypes.real_num
.. autofunction:: putil.ptypes.real_numpy_vector
