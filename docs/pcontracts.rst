.. pcontracts.rst
.. Copyright (c) 2013-2016 Pablo Acosta-Serafini
.. See LICENSE for details
.. py:module:: putil.pcontracts

#################
pcontracts module
#################

This module is a thin wrapper around the
`PyContracts <https://andreacensi.github.io/contracts/>`_ library that enables
customization of the exception type raised and limited customization of the
exception message. Additionally, custom contracts specified via
:py:func:`putil.pcontracts.new_contract` and enforced via
:py:func:`putil.pcontracts.contract` register exceptions using the
:py:mod:`putil.exh` module, which means that the exceptions raised by these
contracts can be automatically documented using the :py:mod:`putil.exdoc`
module.

The way a contract is specified is identical to the decorator way of specifying
a contract with the `PyContracts <https://andreacensi.github.io/contracts/>`_
library. By default a :code:`RuntimeError` exception with the message
:code:`'Argument \`*[argument_name]*\` is not valid'` is raised unless a
custom contract specifies a different exception (the token
:code:`*[argument_name]*` is replaced by the argument name the contract is
attached to). For example, the definitions of the custom contracts
:py:func:`putil.ptypes.file_name` and
:py:func:`putil.ptypes.file_name_exists` are:


.. literalinclude:: ./support/ptypes.py
    :language: python
    :tab-width: 4
    :lines: 395-423

.. literalinclude:: ./support/ptypes.py
    :language: python
    :tab-width: 4
    :lines: 426-465

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
>>> fname = os.path.join('..', 'docs', 'pcontracts.rst') #doctest: +ELLIPSIS
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
OSError: File /dev/null/some_file.txt could not be found

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

.. function:: putil.pcontracts.contract(\*\*contract_args)

    Wraps PyContracts `contract() <http://andreacensi.github.io/contracts/
    api_reference.html#module-contracts>`_ decorator (only the decorator
    way of specifying a contract is supported and tested). A
    :code:`RuntimeError` exception with the message
    :code:`'Argument \`*[argument_name]*\` is not valid'` is raised when a
    contract is breached (:code:`'*[argument_name]*'` is replaced by the
    argument name the contract is attached to) unless the contract is
    custom and specified with the :py:func:`putil.pcontracts.new_contract`
    decorator. In this case the exception type and message are controlled
    by the custom contract specification.

.. function:: putil.pcontracts.new_contract(\*args, \*\*kwargs)

    Defines a new (custom) contract with custom exceptions.

    :raises:
     * RuntimeError (Attempt to redefine custom contract
       \`*[contract_name]*\`)

     * TypeError (Argument \`contract_exceptions\` is of the wrong type)

     * TypeError (Argument \`contract_name\` is of the wrong type)

     * TypeError (Contract exception definition is of the wrong type)

     * TypeError (Illegal custom contract exception definition)

     * ValueError (Empty custom contract exception message)

     * ValueError (Contract exception messages are not unique)

     * ValueError (Contract exception names are not unique)

     * ValueError (Multiple replacement fields to be substituted by
       argument value)

    The decorator argument(s) is(are) the exception(s) that can be raised
    by the contract. The most general way to define an exception is using a
    2-item tuple with the following members:

     * **exception type** *(type)* -- Either a built-in exception or
       sub-classed from Exception. Default is ``RuntimeError``

     * **exception message** *(string)* -- Default is
       ``'Argument `*[argument_name]*` is not valid'``, where the token
       :code:`*[argument_name]*` is replaced by the argument name the
       contract is attached to

    The order of the tuple elements is not important, i.e. the following
    are valid exception specifications and define the same exception:

    .. [[[cog
    .. import docs.support.incfile
    .. docs.support.incfile.incfile('pcontracts_example_3.py', cog.out, '9-17')
    .. ]]]
    .. code-block:: python

        @putil.pcontracts.new_contract(ex1=(RuntimeError, 'Invalid name'))
        def custom_contract1(arg):
            if not arg:
                raise ValueError(putil.pcontracts.get_exdesc())

        @putil.pcontracts.new_contract(ex1=('Invalid name', RuntimeError))
        def custom_contract2(arg):
            if not arg:
                raise ValueError(putil.pcontracts.get_exdesc())

    .. [[[end]]]

    The exception definition simplifies to just one of the exception
    definition tuple items if the other exception definition tuple item
    takes its default value. For example, the same exception is defined in
    these two contracts:

    .. [[[cog
    .. from docs.support.incfile import incfile
    .. incfile('pcontracts_example_3.py', cog.out, '19-30')
    .. ]]]
    .. code-block:: python

        @putil.pcontracts.new_contract(ex1=ValueError)
        def custom_contract3(arg):
            if not arg:
                raise ValueError(putil.pcontracts.get_exdesc())

        @putil.pcontracts.new_contract(ex1=(
            ValueError,
            'Argument `*[argument_name]*` is not valid'
        ))
        def custom_contract4(arg):
            if not arg:
                raise ValueError(putil.pcontracts.get_exdesc())

    .. [[[end]]]

    and these contracts also define the same exception (but different from
    that of the previous example):

    .. [[[cog
    .. from docs.support.incfile import incfile
    .. incfile('pcontracts_example_3.py', cog.out, '32-40')
    .. ]]]
    .. code-block:: python

        @putil.pcontracts.new_contract(ex1='Invalid name')
        def custom_contract5(arg):
            if not arg:
                raise ValueError(putil.pcontracts.get_exdesc())

        @putil.pcontracts.new_contract(ex1=('Invalid name', RuntimeError))
        def custom_contract6(arg):
            if not arg:
                raise ValueError(putil.pcontracts.get_exdesc())

    .. [[[end]]]

    In fact the exception need not be specified by keyword if the contract
    only uses one exception. All of the following are valid one-exception
    contract specifications:

    .. [[[cog
    .. from docs.support.incfile import incfile
    .. incfile('pcontracts_example_3.py', cog.out, '42-57')
    .. ]]]
    .. code-block:: python

        @putil.pcontracts.new_contract(
            (OSError, 'File could not be opened')
        )
        def custom_contract7(arg):
            if not arg:
                raise ValueError(putil.pcontracts.get_exdesc())

        @putil.pcontracts.new_contract('Invalid name')
        def custom_contract8(arg):
            if not arg:
                raise ValueError(putil.pcontracts.get_exdesc())

        @putil.pcontracts.new_contract(TypeError)
        def custom_contract9(arg):
            if not arg:
                raise ValueError(putil.pcontracts.get_exdesc())

    .. [[[end]]]

    No arguments are needed if a contract only needs a single exception and
    the default exception type and message suffice:

    .. [[[cog
    .. from docs.support.incfile import incfile
    .. incfile('pcontracts_example_3.py', cog.out, '59-62')
    .. ]]]
    .. code-block:: python

        @putil.pcontracts.new_contract()
        def custom_contract10(arg):
            if not arg:
                raise ValueError(putil.pcontracts.get_exdesc())

    .. [[[end]]]

    For code conciseness and correctness the exception message(s) should be
    retrieved via the :py:func:`putil.pcontracts.get_exdesc` function.

    A `PyContracts new contract <http://andreacensi.github.io/contracts/
    new_contract.html#new-contract>`_ can return False or raise a
    :code:`ValueError` exception to indicate a contract breach, however a
    new contract specified via the :py:func:`putil.pcontracts.new_contract`
    decorator *has* to raise a :code:`ValueError` exception to indicate a
    contract breach.

    The exception message can have substitution "tokens" of the form
    :code:`*[token_name]*`. The token :code:`*[argument_name]*` is
    substituted with the argument name the contract it is attached to.
    For example:

    .. [[[cog
    .. from docs.support.incfile import incfile
    .. incfile('pcontracts_example_3.py', cog.out, '64-74')
    .. ]]]
    .. code-block:: python

        @putil.pcontracts.new_contract((
            TypeError,
            'Argument `*[argument_name]*` has to be a string'
        ))
        def custom_contract11(city):
            if not isinstance(city, str):
                raise ValueError(putil.pcontracts.get_exdesc())

        @putil.pcontracts.contract(city_name='custom_contract11')
        def print_city_name(city_name):
            return 'City: {0}'.format(city_name)

    .. [[[end]]]

    .. code-block:: python

        >>> from __future__ import print_function
        >>> from docs.support.pcontracts_example_3 import print_city_name
        >>> print(print_city_name('Omaha'))
        City: Omaha
        >>> print(print_city_name(5))   #doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Argument `city_name` has to be a string

    Any other token is substituted with the argument *value*. For example:

    .. [[[cog
    .. import docs.support.incfile
    .. docs.support.incfile.incfile('pcontracts_example_3.py', cog.out, '76-')
    .. ]]]
    .. code-block:: python

        @putil.pcontracts.new_contract((
            OSError, 'File `*[fname]*` not found'
        ))
        def custom_contract12(fname):
            if not os.path.exists(fname):
                raise ValueError(putil.pcontracts.get_exdesc())

        @putil.pcontracts.contract(fname='custom_contract12')
        def print_fname(fname):
            print('File name to find: {0}'.format(fname))

    .. [[[end]]]

    .. code-block:: python

        >>> from __future__ import print_function
        >>> import os
        >>> from docs.support.pcontracts_example_3 import print_fname
        >>> fname = os.path.join(os.sep, 'dev', 'null', '_not_a_file_')
        >>> print(print_fname(fname))   #doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        OSError: File `..._not_a_file_` not found
