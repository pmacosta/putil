#################
pcontracts module
#################



This module is a thin wrapper around the `PyContracts <https://andreacensi.github.io/contracts/>`_ library that enables customization of the exception type raised and limited
customization of the exception message. Additionally, custom contracts specified by :py:func:`putil.pcontracts.new_contract` and contract enforcement via
:py:func:`putil.pcontracts.contract` register exceptions using the :py:mod:`putil.exh` module if an exception handler object is detected. This also means that the
exceptions raised by these contracts can be auto-documented using the :py:mod:`putil.exdoc` module

The way a contract is specified is identical to decorator way of specifying a contract with the `PyContracts <https://andreacensi.github.io/contracts/>`_ library. By default :code:`RuntimeError('Argument \`*[argument_name]*\` is not
valid')` is raised unless a custom contract specifies a different exception (the token :code:`'*[argument_name]*'` is replaced by the argument name the contract is attached to).

***********
Interpreter
***********

The module has been developed using Python 2.7, but it *should* also work with Python 3.x

******************
External libraries
******************

* Standard Python library

* Other Putil library modules

* `PyContracts <https://andreacensi.github.io/contracts/>`_

***************************************
Application programming interface (API)
***************************************

Pseudo-types
============

None

Functions
=========

.. autofunction:: putil.pcontracts.all_disabled
.. autofunction:: putil.pcontracts.disable_all
.. autofunction:: putil.pcontracts.enable_all
.. autofunction:: putil.pcontracts.get_exdesc

Decorators
==========

.. autofunction:: putil.pcontracts.contract
.. autofunction:: putil.pcontracts.new_contract

*******
License
*******

The MIT License (MIT)

Copyright (c) 2013-2014 Pablo Acosta-Serafini

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
