.. misc.rst
.. Copyright (c) 2013-2016 Pablo Acosta-Serafini
.. See LICENSE for details
.. py:module:: putil.misc

###########
misc module
###########

This module contains miscellaneous utility functions that can be applied in a
variety of circumstances; there are context managers, membership functions
(test if an argument is of a given type), numerical functions and string
functions

****************
Context managers
****************

.. autofunction:: putil.misc.ignored
.. autoclass:: putil.misc.Timer
	:members: elapsed_time
	:show-inheritance:
.. autoclass:: putil.misc.TmpFile
	:show-inheritance:

****
File
****

.. autofunction:: putil.misc.make_dir
.. autofunction:: putil.misc.normalize_windows_fname

**********
Membership
**********

.. autofunction:: putil.misc.isalpha
.. autofunction:: putil.misc.ishex
.. autofunction:: putil.misc.isiterable
.. autofunction:: putil.misc.isnumber
.. autofunction:: putil.misc.isreal

*************
Miscellaneous
*************

.. autofunction:: putil.misc.flatten_list

*******
Numbers
*******

.. autofunction:: putil.misc.gcd
.. autofunction:: putil.misc.normalize
.. autofunction:: putil.misc.per
.. autofunction:: putil.misc.pgcd

******
String
******

.. autofunction:: putil.misc.binary_string_to_octal_string
.. autofunction:: putil.misc.char_to_decimal
.. autofunction:: putil.misc.elapsed_time_string
.. autofunction:: putil.misc.pcolor
.. autofunction:: putil.misc.quote_str
.. autofunction:: putil.misc.strframe
