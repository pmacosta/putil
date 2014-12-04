#################
pcontracts module
#################



This module is a thin wrapper around the `PyContracts <https://andreacensi.github.io/contracts/>`_ library that enables customization of the exception type raised and limited customization of the exception message.
Additionally, custom contracts specified via :py:func:`putil.pcontracts.new_contract` and enforced via :py:func:`putil.pcontracts.contract` register exceptions using the :ref:`exh-module` if an exception
handler object is detected. This also means that the exceptions raised by these contracts can be automatically documented using the :ref:`exdoc-module`.

The way a contract is specified is identical to decorator way of specifying a contract with the `PyContracts <https://andreacensi.github.io/contracts/>`_ library. By default :code:`RuntimeError('Argument \`*[argument_name]*\` is
not valid')` is raised unless a custom contract specifies a different exception (the token :code:`'*[argument_name]*'` is replaced by the argument name the contract is attached to). These are the definitions of the custom
contracts :py:func:`putil.pcontracts.file_name` and :py:func:`putil.pcontracts.file_name_exists`:


.. literalinclude:: ../putil/pcontracts.py
    :language: python
    :linenos:
    :tab-width: 3
    :lines: 382-415

This is nearly identical to the way custom contracts are defined using the `PyContracts <https://andreacensi.github.io/contracts/>`_ library with two exceptions:

1. To avoid repetition and errors, the exception messages defined with :py:func:`putil.pcontracts.new_contract` are available within the contract via the :py:func:`putil.pcontracts.get_exdesc()` function.
  
2. A `PyContracts new contract <http://andreacensi.github.io/contracts/new_contract.html#new-contract>`_ can return :code:`False` or raise a :code:`ValueError` exception to indicate a contract breach, however a new contract
   specified via the :py:func:`putil.pcontracts.new_contract` decorator *has* to raise a :code:`ValueError` exception to indicate a contract breach.

Exceptions can be specified in a variety of ways and verbosity is minimized by having reasonable defaults (see :py:func:`putil.pcontracts.new_contract` for a full description). What follows is a simple usage example of the two
contracts shown above and the exceptions they produce:

>>> import putil.pcontracts
>>> @putil.pcontracts.contract(name='file_name')
... def print_if_file_name_valid(name):
...    """ Sample function 1 """
...    print 'Valid file name: {0}'.format(name)
... 
>>> @putil.pcontracts.contract(num=int, name='file_name_exists')
... def print_if_file_name_exists(num, name):
...    """ Sample function 2 """
...    print 'Valid file name: [{0}] {1}'.format(num, name)
... 
>>> print_if_file_name_valid('some_file.txt')
Valid file name: some_file.txt
>>> print_if_file_name_valid('invalid_file_name.txt\0')
Traceback (most recent call last):
  ...
RuntimeError: Argument `name` is not valid
>>> print_if_file_name_exists(10,'pcontracts.py')
Valid file name: [10] pcontracts.py
>>> print_if_file_name_exists('hello','pcontracts.py')
Traceback (most recent call last):
  ...
RuntimeError: Argument `num` is not valid
>>> print_if_file_name_exists(5,'another_invalid_file_name.txt\0')
Traceback (most recent call last):
  ...
RuntimeError: Argument `name` is not valid
>>> print_if_file_name_exists(5,'/dev/null/some_file.txt')
Traceback (most recent call last):
  ...
IOError: File `/dev/null/some_file.txt` could not be found

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

.. autofunction:: putil.pcontracts.file_name
.. autofunction:: putil.pcontracts.file_name_exists

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
