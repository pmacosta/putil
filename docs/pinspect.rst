###############
pinspect module
###############



This module can be used to aid introspection

***********
Interpreter
***********

The module has been developed using Python 2.7, but it *should* also work with Python 3.x

******************
External libraries
******************

* Standard Python library and other Putil library modules

***************************************
Application programming interface (API)
***************************************

Functions
=========

.. autofunction:: putil.pinspect.is_magic_method
.. autofunction:: putil.pinspect.is_object_module
.. autofunction:: putil.pinspect.get_module_name
.. autofunction:: putil.pinspect.get_package_name
.. autofunction:: putil.pinspect.loaded_package_modules

Classes
=======

.. autoclass:: putil.pinspect.Callables
	:members: trace, callables_db

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
