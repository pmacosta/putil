.. exh.rst
.. Copyright (c) 2013-2015 Pablo Acosta-Serafini
.. See LICENSE for details
.. _exh-module:

##########
exh module
##########

This module can be used to register exceptions and then raise them if a given
condition is true. For example:

.. literalinclude:: ./support/exh_example.py
    :language: python
    :tab-width: 4
    :lines: 1,6-

.. code-block:: python

	>>> import docs.support.exh_example
	>>> docs.support.exh_example.my_func('Tom')
	My name is Tom
	>>> docs.support.exh_example.my_func(5)	#doctest: +ELLIPSIS
	Traceback (most recent call last):
	    ...
	TypeError: Argument `name` is not valid

When :code:`my_func()` gets called with anything but a string as an argument
a :code:`TypeError` exception is raised with the message
:code:`'Argument \`name\` is not valid'`. While adding/registering
an exception with :py:meth:`putil.exh.ExHandle.add_exception` and
conditionally raising it with :py:meth:`putil.exh.ExHandle.raise_exception_if`
takes the same number of lines of code as an exception raised inside an
:code:`if` block and incurs a slight performance penalty, using the
:ref:`exh-module` allows for automatic documentation of the exceptions raised
by any function, method or class property with the help of the
:ref:`exdoc-module`.

*********
Functions
*********

.. autofunction:: putil.exh.get_exh_obj
.. autofunction:: putil.exh.get_or_create_exh_obj
.. autofunction:: putil.exh.del_exh_obj
.. autofunction:: putil.exh.set_exh_obj

*******
Classes
*******

.. autoclass:: putil.exh.ExHandle
	:members: add_exception, callables_db, callables_separator, exceptions_db,
			  raise_exception_if, __add__, __copy__, __eq__, __iadd__,
			  __nonzero__, __str__
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
