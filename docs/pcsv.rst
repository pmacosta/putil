.. pcsv.rst
.. Copyright (c) 2013-2016 Pablo Acosta-Serafini
.. See LICENSE for details
.. py:module:: putil.pcsv

###########
pcsv module
###########

This module can be used to handle comma-separated values (CSV) files and do
lightweight processing of their data with support for row and column
filtering. In addition to basic read, write and data replacement, files
can be concatenated, merged, and sorted

********
Examples
********

Read/write
==========

.. literalinclude:: ./support/pcsv_example_1.py
    :language: python
    :tab-width: 4
    :lines: 1,6-

Replace data
============

.. literalinclude:: ./support/pcsv_example_2.py
    :language: python
    :tab-width: 4
    :lines: 1,6-

Concatenate two files
=====================

.. literalinclude:: ./support/pcsv_example_3.py
    :language: python
    :tab-width: 4
    :lines: 1,6-

Merge two files
===============

.. literalinclude:: ./support/pcsv_example_4.py
    :language: python
    :tab-width: 4
    :lines: 1,6-

Sort a file
===========

.. literalinclude:: ./support/pcsv_example_5.py
    :language: python
    :tab-width: 4
    :lines: 1,6-

*******************************
Identifying (filtering) columns
*******************************

Several class methods and functions in this module allow column and row
filtering of the CSV file data. It is necessary to identify columns for both
of these operations and how these columns can be identified depends on whether
the file has or does not have a header as indicated by the **has_header**
boolean constructor argument:

* If **has_header** is :code:`True` the first line of the file is taken as the
  header.  Columns can be identified by name (a string that has to match a
  column value in the file header) or by number (an integer representing the
  column number with column zero being the leftmost column)

* If **has_header** is :code:`False` columns can only be identified by number
  (an integer representing the column number with column zero being the
  leftmost column)

For example, if a file ``myfile.csv`` has the following data:

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

Then when the file is loaded with
:code:`putil.pcsv.CsvFile('myfile.csv', has_header=True)` the columns can be
referred to as :code:`'Ctrl'` or :code:`0`, :code:`'Ref'` or :code:`1`, or
:code:`'Result'` or :code:`2`. However if the file is loaded with
:code:`putil.pcsv.CsvFile('myfile.csv', has_header=False)` the columns can
be referred only as :code:`0`, :code:`1` or :code:`2`.

**************
Filtering rows
**************

Several class methods and functions of this module allow row filtering of the
CSV file data. The row filter is described in the :ref:`CsvRowFilter`
pseudo-type

*****************************
Swapping or inserting columns
*****************************

The column filter not only filters columns *but also* determines the order in
which the columns are stored internally in an :py:class:`putil.pcsv.CsvFile`
object. This means that the column filter can be used to reorder and/or
duplicate columns. For example:

.. literalinclude:: ./support/pcsv_example_6.py
    :language: python
    :tab-width: 4
    :lines: 1,6-

*************
Empty columns
*************

When a file has empty columns they are read as :code:`None`. Conversely
any column value that is :code:`None` is written as an empty column.
Empty columns are ones that have either an empty string (:code:`''`)
or literally no information between the column delimiters (:code:`,`)

For example, if a file ``myfile2.csv`` has the following data:

+------+-----+--------+
| Ctrl | Ref | Result |
+======+=====+========+
|    1 |   4 |     20 |
+------+-----+--------+
|    2 |     |     30 |
+------+-----+--------+
|    2 |   5 |        |
+------+-----+--------+
|      |   5 |     50 |
+------+-----+--------+

The corresponding read array is:

.. code-block:: python

        [
            ['Ctrl', 'Ref', 'Result'],
            [1, 4, 20],
            [2, None, 30],
            [2, 5, None],
            [None, 5, 50]
        ]

*********
Functions
*********

.. autofunction:: putil.pcsv.concatenate
.. autofunction:: putil.pcsv.dsort
.. autofunction:: putil.pcsv.merge
.. autofunction:: putil.pcsv.replace
.. autofunction:: putil.pcsv.write

*******
Classes
*******

.. autoclass:: putil.pcsv.CsvFile
    :members: add_dfilter, cfilter, cols, data, dfilter, dsort, header, replace,
              reset_dfilter, rfilter, rows, write, __eq__, __repr__
    :show-inheritance:
