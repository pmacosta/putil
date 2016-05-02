.. ptypes.rst
.. Copyright (c) 2013-2016 Pablo Acosta-Serafini
.. See LICENSE for details
.. py:module:: putil.ptypes

#############
ptypes module
#############

This module provides several pseudo-type definitions which can be enforced
and/or validated with custom contracts defined using the
:py:mod:`putil.pcontracts` module

************
Pseudo-types
************

.. _ColorSpaceOption:

ColorSpaceOption
----------------
String representing a `Matplotlib <http://matplotlib.org/>`_ color space, one
:code:`'binary'`, :code:`'Blues'`, :code:`'BuGn'`, :code:`'BuPu'`,
:code:`'GnBu'`, :code:`'Greens'`, :code:`'Greys'`, :code:`'Oranges'`,
:code:`'OrRd'`, :code:`'PuBu'`, :code:`'PuBuGn'`, :code:`'PuRd'`,
:code:`'Purples'`, :code:`'RdPu'`, :code:`'Reds'`, :code:`'YlGn'`,
:code:`'YlGnBu'`, :code:`'YlOrBr`', :code:`'YlOrRd'` or :code:`None`

.. _CsvColFilter:

CsvColFilter
------------

String, integer, a list of strings or a list of integers that identify a column
or columns within a comma-separated values (CSV) file.

Integers identify a column by position (column 0 is the leftmost column)
whereas strings identify the column by name. Columns can be identified either
by position or by name when the file has a header (first row of file
containing column labels) but only by position when the file does not have a
header.

:code:`None` indicates that no column filtering should be done

.. _CsvColSort:

CsvColSort
----------

Integer, string, dictionary or list of integers, strings or dictionaries that
specify the sort direction of a column or columns in a comma-separated values
(CSV) file.

The sort direction can be either ascending, specified by the string
:code:`'A'`, or descending, specified by the string :code:`'B'` (case
insensitive). The default sort direction is ascending.

The column can be specified numerically or with labels depending on whether the
CSV file was loaded with or without a header.

The full specification is a dictionary (or list of dictionaries if multiple
columns are to be used for sorting) where the key is the column and the value
is the sort order, thus valid examples are :code:`{'MyCol':'A'}` and
:code:`[{'MyCol':'A'}, {3:'d'}]`.

When the default direction suffices it can be omitted; for example in
:code:`[{'MyCol':'D'}, 3]`, the data is sorted first by MyCol in descending
order and then by the 4th column (column 0 is the leftmost column in a CSV
file) in ascending order

.. _CsvDataFilter:

CsvDataFilter
-------------

In its most general form a two-item tuple, where one item is of `CsvColFilter`_
pseudo-type and the other item is of `CsvRowFilter`_ pseudo-type (the order of
the items is not mandated, i.e.  the first item could be of pseudo-type
CsvRowFilter and the second item could be of pseudo-type CsvColFilter or
vice-versa).

The two-item tuple can be reduced to a one-item tuple when only a row or column
filter needs to be specified, or simply to an object of either CsvRowFilter
or CsvColFilter pseudo-type.

For example, all of the following are valid CsvDataFilter objects:
:code:`('MyCol', {'MyCol':2.5})`, :code:`({'MyCol':2.5}, 'MyCol')` (filter in
the column labeled MyCol and rows where the column labeled MyCol has the value
2.5), :code:`('MyCol', )` (filter in column labeled MyCol and all rows) and
:code:`{'MyCol':2.5}` (filter in all columns and only rows where the column
labeled MyCol has the values 2.5)

:code:`None`, :code:`(None, )` or :code:`(None, None)` indicate that no row or
column filtering should be done

.. _CsvFiltered:

CsvFiltered
-----------

String or a boolean that indicates what type of row and column filtering is to
be performed in a comma-separated values (CSV) file. If :code:`True`,
:code:`'B'` or :code:`'b'` it indicates that both row- and column-filtering are
to be performed; if :code:`False`, :code:`'N'` or :code:`'n'` no filtering is
to be performed, if :code:`'R'` or :code:`'r'` only row-filtering is to be
performed, if :code:`'C'` or :code:`'c'` only column-filtering is to be
performed

.. _CsvRowFilter:

CsvRowFilter
------------

Dictionary whose elements are sub-filters with the following structure:

* **column identifier** *(CsvColFilter)* -- Dictionary key. Column to filter
  (as it appears in the comma-separated values file header when a string is
  given) or column number (when an integer is given, column zero is the
  leftmost column)

* **value** *(list of strings or numbers, or string or number)* -- Dictionary
  value. Column value to filter if a string or number, column values to filter
  if a list of strings or numbers

If a row filter sub-filter is a column value all rows which contain the
specified value in the specified column are kept for that particular
individual filter. The overall data set is the intersection of all the data
sets specified by each individual sub-filter. For example, if the file to be
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

Then the filter specification ``rfilter = {'Ctrl':2, 'Ref':5}`` would result
in the following filtered data set:

+------+-----+--------+
| Ctrl | Ref | Result |
+======+=====+========+
|    2 |   5 |     40 |
+------+-----+--------+

However, the filter specification ``rfilter = {'Ctrl':2, 'Ref':3}`` would
result in an empty list because the data set specified by the `Ctrl`
individual sub-filter does not overlap with the data set specified by the
`Ref` individual sub-filter.

If a row sub-filter is a list, the items of the list represent all
the values to be kept for a particular column (strings or numbers). So for
example ``rfilter = {'Ctrl':[2, 3], 'Ref':5}`` would result in the following
filtered data set:

+------+-----+--------+
| Ctrl | Ref | Result |
+======+=====+========+
|    2 |   5 |     40 |
+------+-----+--------+
|    3 |   5 |     50 |
+------+-----+--------+

:code:`None` indicates that no row filtering should be done

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
suffix and floating point exponent

.. _IncreasingRealNumpyVector:

IncreasingRealNumpyVector
-------------------------
Numpy vector in which all elements are real (integers and/or floats) and
monotonically increasing (each element is strictly greater than the
preceding one)

.. _InterpolationOption:

InterpolationOption
-------------------
String representing an interpolation type, one of :code:`'STRAIGHT'`,
:code:`'STEP'`, :code:`'CUBIC'`, :code:`'LINREG'` (case insensitive)
or :code:`None`

.. _LineStyleOption:

LineStyleOption
---------------
String representing a `Matplotlib`_ line style, one of :code:`'-'`,
:code:`'--'`, :code:`'-.'`, :code:`':'` or :code:`None`

.. _NumberNumpyVector:

NumberNumpyVector
-----------------
Numpy vector in which all elements are integers and/or floats and/or complex

.. _RealNumpyVector:

RealNumpyVector
---------------
Numpy vector in which all elements are real (integers and/or floats)

.. _TouchstoneData:

TouchstoneData
--------------

A dictionary with the following structure:

* **points** (*integer*) -- Number of data points

* **freq** (:ref:`IncreasingRealNumpyVector`) -- Frequency vector

* **data** (:ref:`NumberNumpyVector`) -- Parameter data, its size is equal to
  :code:`nports` x :code:`nports` x :code:`points` where :code:`nports`
  represents the number of ports in the file

The dictionary keys are case sensitive

.. _TouchstoneNoiseData:

TouchstoneNoiseData
-------------------

A dictionary with the following structure:

* **points** (*integer*) -- Number of data points

* **freq** (:ref:`IncreasingRealNumpyVector`) -- Frequency vector

* **nf** (:ref:`RealNumpyVector`) -- Minimum noise figure vector in decibels

* **rc** (:ref:`NumberNumpyVector`) -- Source source reflection coefficient to
  realize minimum noise figure

* **res** (:ref:`RealNumpyVector`) -- Normalized effective noise resistance

The dictionary keys are case sensitive

.. _TouchstoneOptions:

TouchstoneOptions
-----------------

A dictionary with the following structure:

* **units** (*string*) -- Frequency units, one of :code:`'GHz'`, :code:`'MHz'`,
  :code:`'KHz'` or :code:`'Hz'` (case insensitive, default :code:`'GHz'`)

* **ptype** (*string*) -- Parameter type, one of :code:`'S'`, :code:`'Y'`,
  :code:`'Z'`, :code:`'H'` or :code:`'G'` (case insensitive, default
  :code:`'S'`)

* **pformat** (*string*) -- Data point format type, one of :code:`'DB'`
  (decibels), :code:`'MA'` (magnitude and angle), or :code:`'RI'` (real and
  imaginary) (case insensitive, default :code:`'MA'`)

* **z0** (float) -- Reference resistance in Ohms, default 50 Ohms

The dictionary keys are case sensitive

.. _WaveInterpOption:

WaveInterpOption
----------------
String representing a waveform interpolation type, one of :code:`'CONTINUOUS'`
or :code:`'STAIRCASE'` (case insensitive)

.. _WaveScaleOption:

WaveScaleOption
---------------
String representing a waveform scale type, one of :code:`'LINEAR'`
or :code:`'LOG'` (case insensitive)

.. _WaveVectors:

WaveVectors
-----------
Non-empty list of tuples in which each tuple is a waveform point. The first
item of a point tuple is its independent variable and the second item of a
point tuple is its dependent variable. The vector formed by the first item
of the point tuples is of :ref:`IncreasingRealNumpyVector` pseudo-type; the
vector formed by the second item of the point tuples is of
:ref:`RealNumpyVector` pseudo-type

*********
Contracts
*********

.. autofunction:: putil.ptypes.color_space_option
.. autofunction:: putil.ptypes.csv_col_filter
.. autofunction:: putil.ptypes.csv_col_sort
.. autofunction:: putil.ptypes.csv_data_filter
.. autofunction:: putil.ptypes.csv_filtered
.. autofunction:: putil.ptypes.csv_row_filter
.. autofunction:: putil.ptypes.engineering_notation_number
.. autofunction:: putil.ptypes.engineering_notation_suffix
.. autofunction:: putil.ptypes.increasing_real_numpy_vector
.. autofunction:: putil.ptypes.interpolation_option
.. autofunction:: putil.ptypes.line_style_option
.. autofunction:: putil.ptypes.number_numpy_vector
.. autofunction:: putil.ptypes.real_numpy_vector
.. autofunction:: putil.ptypes.wave_interp_option
.. autofunction:: putil.ptypes.wave_scale_option
.. autofunction:: putil.ptypes.wave_vectors
