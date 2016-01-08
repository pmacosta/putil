.. pinspect.rst
.. Copyright (c) 2013-2016 Pablo Acosta-Serafini
.. See LICENSE for details
.. py:module:: putil.pinspect

###############
pinspect module
###############

This module supplements Python's introspection capabilities. The
class :py:class:`putil.pinspect.Callables` "traces" modules and produces a
database of callables (functions, classes, methods and class properties)
and their attributes (callable type, file name, starting line number).
Enclosed functions and classes are supported. For example:

.. literalinclude:: ./support/pinspect_example_1.py
    :language: python
    :tab-width: 4
    :lines: 1,6-

with

.. literalinclude:: ./support/python2_module.py
    :language: python
    :tab-width: 4
    :lines: 1,6-

and

.. literalinclude:: ./support/python3_module.py
    :language: python
    :tab-width: 4
    :lines: 1,6-

gives:

.. code-block:: python

	>>> from __future__ import print_function
	>>> import docs.support.pinspect_example_1, putil.pinspect, sys
	>>> cobj = putil.pinspect.Callables(
	...     [sys.modules['docs.support.pinspect_example_1'].__file__]
	... )
	>>> print(cobj)
	Modules:
	   docs.support.pinspect_example_1
	Classes:
	   docs.support.pinspect_example_1.my_func.MyClass
	docs.support.pinspect_example_1.my_func: func (9-25)
	docs.support.pinspect_example_1.my_func.MyClass: class (11-25)
	docs.support.pinspect_example_1.my_func.MyClass.__init__: meth (18-20)
	docs.support.pinspect_example_1.my_func.MyClass._get_value: meth (21-23)
	docs.support.pinspect_example_1.my_func.MyClass.value: prop (24-25)
	docs.support.pinspect_example_1.print_name: func (26-27)

The numbers in parenthesis indicate the line number in which the callable
starts and ends within the file it is defined in.

*********
Functions
*********

.. autofunction:: putil.pinspect.get_function_args
.. autofunction:: putil.pinspect.get_module_name
.. autofunction:: putil.pinspect.is_object_module
.. autofunction:: putil.pinspect.is_special_method
.. autofunction:: putil.pinspect.private_props

*******
Classes
*******

.. autoclass:: putil.pinspect.Callables
	:members: load, refresh, save, trace, callables_db,
                  reverse_callables_db, __add__, __copy__,
                  __eq__, __iadd__, __nonzero__, __repr__, __str__
	:show-inheritance:
