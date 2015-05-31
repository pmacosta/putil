.. pcontracts.rst
.. Copyright (c) 2013-2015 Pablo Acosta-Serafini
.. See LICENSE for details
.. _pcontracts-module:

#################
pcontracts module
#################

This module is a thin wrapper around the
`PyContracts <https://andreacensi.github.io/contracts/>`_ library that enables
customization of the exception type raised and limited customization of the
exception message. Additionally, custom contracts specified via
:py:func:`putil.pcontracts.new_contract` and enforced via
:py:func:`putil.pcontracts.contract` register exceptions using the
:ref:`exh-module` , which means that the exceptions raised by these contracts
can be automatically documented using the :ref:`exdoc-module`.

The way a contract is specified is identical to the decorator way of specifying
a contract with the `PyContracts <https://andreacensi.github.io/contracts/>`_
library. By default a :code:`RuntimeError` exception with the message
:code:`'Argument \`*[argument_name]*\` is not valid'` is raised unless a
custom contract specifies a different exception (the token
:code:`*[argument_name]*` is replaced by the argument name the contract is
attached to). For example, the definitions of the custom contracts
:py:func:`putil.ptypes.file_name` and
:py:func:`putil.ptypes.file_name_exists` are:


.. literalinclude:: ../putil/ptypes.py
    :language: python
    :tab-width: 4
    :lines: 385-410

.. literalinclude:: ../putil/ptypes.py
    :language: python
    :tab-width: 4
    :lines: 413-452

This is nearly identical to the way custom contracts are defined using the
`PyContracts <https://andreacensi.github.io/contracts/>`_ library with two
exceptions:

1. To avoid repetition and errors, the exception messages defined in the
   :py:func:`putil.pcontracts.new_contract` decorator are available in the
   contract definition function via :py:func:`putil.pcontracts.get_exdesc`.

2. A `PyContracts new contract <http://andreacensi.github.io/contracts/
   new_contract.html#new-contract>`_ can return False or raise a
   :code:`ValueError` exception to indicate a contract breach, however a new
   contract specified via the :py:func:`putil.pcontracts.new_contract`
   decorator *has* to raise a :code:`ValueError` exception to indicate
   a contract breach.

Exceptions can be specified in a variety of ways and verbosity is minimized by
having reasonable defaults (see :py:func:`putil.pcontracts.new_contract` for a
full description). What follows is a simple usage example of the two
contracts shown above and the exceptions they produce:

.. literalinclude:: ./support/pcontracts_example_1.py
    :language: python
    :tab-width: 4
    :lines: 1,6-

>>> import os
>>> from docs.support.pcontracts_example_1 import *
>>> print_if_fname_valid('some_file.txt')
Valid file name: some_file.txt
>>> print_if_fname_valid('invalid_fname.txt\0')
Traceback (most recent call last):
    ...
RuntimeError: Argument `name` is not valid
>>> fname = os.path.join('..', 'docs', 'pcontracts.rst')	#doctest: +ELLIPSIS
>>> print_if_fname_exists(10, fname)
Valid file name: [10] ...pcontracts.rst
>>> print_if_fname_exists('hello', fname)
Traceback (most recent call last):
    ...
RuntimeError: Argument `num` is not valid
>>> print_if_fname_exists(5, 'another_invalid_fname.txt\0')
Traceback (most recent call last):
    ...
RuntimeError: Argument `name` is not valid
>>> print_if_fname_exists(5, '/dev/null/some_file.txt')
Traceback (most recent call last):
    ...
IOError: File `/dev/null/some_file.txt` could not be found

*********
Functions
*********

.. autofunction:: putil.pcontracts.all_disabled
.. autofunction:: putil.pcontracts.disable_all
.. autofunction:: putil.pcontracts.enable_all
.. autofunction:: putil.pcontracts.get_exdesc

**********
Decorators
**********

.. autofunction:: putil.pcontracts.contract
.. autofunction:: putil.pcontracts.new_contract

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
