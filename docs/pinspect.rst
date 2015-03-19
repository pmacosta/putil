.. _pinspect-module:

###############
pinspect module
###############


..  can lead to erroneous results linking class properties and the modules of the propety actions (getter, deleter and/or setter). For example:

This module supplements the excellent Python introspection capabilities. The class :py:class:`putil.pinspect.Callables` "traces" modules and produces a database of callables (functions, classes, methods and class properties) 
and their attributes (callable type, file name, starting line number). Enclosed functions are supported, enclosed classes are also supported with the caveat that dynamic importing within enclosures is not supported. For example,
the following module

.. literalinclude:: ./support/pinspect_example_1.py
    :language: python
    :linenos:
    :tab-width: 3
    :lines: 1,3-

with

.. literalinclude:: ./support/python2_module.py
    :language: python
    :linenos:
    :tab-width: 3
    :lines: 1,3-

and 

.. literalinclude:: ./support/python3_module.py
    :language: python
    :linenos:
    :tab-width: 3
    :lines: 1,3-

produces an error when traced:

.. code-block:: python

	>>> import pinspect_example_1, putil.pinspect, sys
	>>> cobj = putil.pinspect.Callables(sys.modules['pinspect_example_1'])
	...
	NameError: name 'version' is not defined

Static imports in enclosures are supported:

.. literalinclude:: ./support/pinspect_example_2.py
    :language: python
    :linenos:
    :tab-width: 3

.. code-block:: python

	>>> import pinspect_example_2, putil.pinspect, sys
	>>> cobj = putil.pinspect.Callables(sys.modules['pinspect_example_2'])
	>>> print cobj
	Modules:
	   pinspect_example_2
	   python2_module
	Classes:
	   pinspect_example_2.my_func.MyClass
	pinspect_example_2.my_func: func (4)
	pinspect_example_2.my_func.MyClass: class (6)
	pinspect_example_2.my_func.MyClass.__init__: meth (9)
	pinspect_example_2.my_func.MyClass._get_value: meth (11)
	   fget of: pinspect_example_2.my_func.MyClass.value
	pinspect_example_2.my_func.MyClass.value: prop (13)
	   fset: python2_module._set_value
	   fget: pinspect_example_2.my_func.MyClass._get_value
	pinspect_example_2.print_name: func (15)
	python2_module._set_value: func (3)
	   fset of: pinspect_example_2.my_func.MyClass.value

The number in parenthesis indicates the line number in which the callable starts within the file it is defined in. Dynamic importing at the module level are also supported:

.. literalinclude:: ./support/pinspect_example_3.py
    :language: python
    :linenos:
    :tab-width: 3

.. code-block:: python

	>>> import pinspect_example_3, putil.pinspect, sys
	>>> cobj = putil.pinspect.Callables(sys.modules['pinspect_example_3'])
	>>> print cobj
	Modules:
	   pinspect_example_3
	   python2_module
	Classes:
	   pinspect_example_3.my_func.MyClass
	pinspect_example_3.my_func: func (9)
	pinspect_example_3.my_func.MyClass: class (12)
	pinspect_example_3.my_func.MyClass.__init__: meth (14)
	pinspect_example_3.my_func.MyClass._get_value: meth (17)
	   fget of: pinspect_example_3.my_func.MyClass.value
	pinspect_example_3.my_func.MyClass.value: prop (19)
	   fset: python2_module._set_value
	   fget: pinspect_example_3.my_func.MyClass._get_value
	pinspect_example_3.print_name: func (21)
	python2_module._set_value: func (3)
	   fset of: pinspect_example_3.my_func.MyClass.value

***********
Interpreter
***********

The module has been developed using Python 2.7, but it *should* also work with Python 3.x

************
Dependencies
************

None

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
	:members: trace, callables_db, reverse_callables_db

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
