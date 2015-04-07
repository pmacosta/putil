.. _pinspect-module:

###############
pinspect module
###############




This module supplements the excellent Python introspection capabilities. The class :py:class:`putil.pinspect.Callables` "traces" modules and produces a database of callables (functions, classes, methods and class properties) 
and their attributes (callable type, file name, starting line number). Enclosed functions and classes are supported. For example:

.. literalinclude:: ./support/pinspect_example_1.py
    :language: python
    :linenos:
    :tab-width: 3

with

.. literalinclude:: ./support/python2_module.py
    :language: python
    :linenos:
    :tab-width: 3
    :lines: 1,5-

and 

.. literalinclude:: ./support/python3_module.py
    :language: python
    :linenos:
    :tab-width: 3
    :lines: 1,5-

gives:

.. code-block:: python

	>>> import pinspect_example_1, putil.pinspect, sys
	>>> cobj = putil.pinspect.Callables([sys.modules['pinspect_example_1'].__file__])
	>>> print str(cobj)
	Modules:
	   pinspect_example_1
	Classes:
	   pinspect_example_1.my_func.MyClass
	pinspect_example_1.my_func: func (6-19)
	pinspect_example_1.my_func.MyClass: class (8-19)
	pinspect_example_1.my_func.MyClass.__init__: meth (14-15)
	pinspect_example_1.my_func.MyClass._get_value: meth (16-17)
	pinspect_example_1.my_func.MyClass.value: prop (18)
	pinspect_example_1.print_name: func (20-21)


The numbers in parenthesis indicates the line number in which the callable starts and ends within the file it is defined in.

***************************************
Application programming interface (API)
***************************************

Functions
=========

.. autofunction:: putil.pinspect.get_function_args
.. autofunction:: putil.pinspect.get_module_name
.. autofunction:: putil.pinspect.get_package_name
.. autofunction:: putil.pinspect.is_object_module
.. autofunction:: putil.pinspect.is_special_method
.. autofunction:: putil.pinspect.loaded_package_modules

Classes
=======

.. autoclass:: putil.pinspect.Callables
	:members: trace, callables_db, reverse_callables_db, __add__, __copy__, __eq__, __iadd__, __repr__, __str__
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
