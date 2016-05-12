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

*********
Contracts
*********

.. autofunction:: putil.ptypes.color_space_option
.. autofunction:: putil.ptypes.csv_col_filter
.. autofunction:: putil.ptypes.csv_col_sort
.. autofunction:: putil.ptypes.csv_data_filter
.. autofunction:: putil.ptypes.csv_filtered
.. autofunction:: putil.ptypes.csv_row_filter
.. autofunction:: putil.ptypes.interpolation_option
.. autofunction:: putil.ptypes.line_style_option
