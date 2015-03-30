.. _misc-module:

###########
misc module
###########



This module contains miscellaneous utility functions that can be applied in a variety of circumstances: there are context managers, membership functions (a certain argument is of a given type), numerical functions
and string functions

***************************************
Application programming interface (API)
***************************************

Context managers
================

.. autofunction:: putil.misc.ignored
.. autoclass:: putil.misc.Timer
	:members: elapsed_time
.. autoclass:: putil.misc.TmpFile

File
====

.. autofunction:: putil.misc.make_dir

Membership
==========

.. autofunction:: putil.misc.isalpha
.. autofunction:: putil.misc.isexception
.. autofunction:: putil.misc.ishex
.. autofunction:: putil.misc.isiterable
.. autofunction:: putil.misc.isnumber
.. autofunction:: putil.misc.isreal

Miscellaneous
=============

.. autofunction:: putil.misc.Bundle
.. autofunction:: putil.misc.flatten_list

Numbers
=======

.. autofunction:: putil.misc.gcd
.. autofunction:: putil.misc.normalize
.. autofunction:: putil.misc.per
.. autofunction:: putil.misc.pgcd
.. autofunction:: putil.misc.smart_round
.. autofunction:: putil.misc.to_scientific_tuple

String
======

.. autofunction:: putil.misc.binary_string_to_octal_string
.. autofunction:: putil.misc.char_to_decimal
.. autofunction:: putil.misc.elapsed_time_string
.. autofunction:: putil.misc.pcolor
.. autofunction:: putil.misc.pprint_vector
.. autofunction:: putil.misc.quote_str
.. autofunction:: putil.misc.split_every
.. autofunction:: putil.misc.strtype
.. autofunction:: putil.misc.strtype_item
.. autofunction:: putil.misc.strframe
.. autofunction:: putil.misc.to_scientific_string
