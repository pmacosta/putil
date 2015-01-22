###########
pcsv module
###########



This module can be used to process information in comma-separated values (CSV) files

***********
Interpreter
***********

The module has been developed using Python 2.7, but it *should* also work with Python 3.x

******************
External libraries
******************

Standard Python library and other Putil library modules

***************************************
Application programming interface (API)
***************************************

Pseudo-types
============

DataFilter
----------

The data filter is a *dictionary* whose elements are sub-filters with the following structure:

* **column name** *(string)* -- Dictionary key. Column to filter (as it appears in the comma-separated values file header)

* **value** *(list of strings or numbers, or string or number)* -- Dictionary value. Column value to filter if a string or number, column values to filter if a list of strings or numbers

If a data filter sub-filter is a column value all rows which contain the specified value in the specified column are kept for that particular individual filter. \
The overall data set is the intersection of all the data sets specified by each individual filter. For example, if the file to be processed is:

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

Then the filter specification ``dfilter = {'Ctrl':2, 'Ref':5}`` would result in the following filtered data set:

+------+-----+--------+
| Ctrl | Ref | Result |
+======+=====+========+
|    2 |   5 |     40 |
+------+-----+--------+

However, the filter specification ``dfilter = {'Ctrl':2, 'Ref':3}`` would result in an empty list because the data set specified by the `Ctrl` individual filter does not overlap with the data set \
specified by the `Ref` individual filter.

If a data filter sub-filter is a list, the items of the list represent all the values to be kept for a particular column (strings or numbers). So for example ``dfilter = {'Ctrl':[2, 3], 'Ref':5}`` \
would result in the following filtered data set:

+------+-----+--------+
| Ctrl | Ref | Result |
+======+=====+========+
|    2 |   5 |     40 |
+------+-----+--------+
|    3 |   5 |     50 |
+------+-----+--------+

Contracts
=========

.. autofunction:: putil.pcsv.csv_data_filter

Functions
=========

.. autofunction:: putil.pcsv.write

Classes
=======

.. automodule:: putil.pcsv
    :members: CsvFile
    :undoc-members:
    :show-inheritance:

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
