# test.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E0611,F0401,W0106,W0703

# Standard library imports
from __future__ import print_function
import re
import sys
try:    # pragma: no cover
    from inspect import signature
except ImportError: # pragma: no cover
    from funcsigs import signature
# PyPI imports
import pytest
# Putil imports
if sys.hexversion < 0x03000000: # pragma: no cover
    from putil.compat2 import _ex_type_str, _get_ex_msg
else:   # pragma: no cover
    from putil.compat3 import _ex_type_str, _get_ex_msg


###
# Functions
###
def _get_fargs(func, no_self=False, no_varargs=False): # pragma: no cover
    """ Same as putil.pinspect.get_function_args """
    is_parg = lambda x: (len(x) > 1) and (x[0] == '*') and (x[1] != '*')
    is_kwarg = lambda x: (len(x) > 2) and (x[:2] == '**')

    par_dict = signature(func).parameters
    # Mark positional and/or keyword arguments (if any)
    args = [
        '{prefix}{arg}'.format(
            prefix=(
                '*'
                if par_dict[par].kind == par_dict[par].VAR_POSITIONAL else
                (
                    '**'
                    if par_dict[par].kind == par_dict[par].VAR_KEYWORD else
                    ''
                )
            ),
            arg=par
        )
        for par in par_dict
    ]
    # Filter out 'self' from parameter list (optional)
    self_filtered_args = args if not args else (
        args[1 if (args[0] == 'self') and no_self else 0:]
    )
    # Filter out positional or keyword arguments (optional)
    varargs_filtered_args = tuple([
        arg
        for arg in self_filtered_args
        if ((not no_varargs) or
           (no_varargs and (not is_parg(arg)) and (not is_kwarg(arg))))
    ])
    return varargs_filtered_args


def assert_arg_invalid(fpointer, pname, *args, **kwargs):
    r"""
    Asserts whether a function raises a :code:`RuntimeError` exception with the
    message :code:`'Argument \`*pname*\` is not valid'`, where
    :code:`*pname*` is the value of the **pname** argument

    :param fpointer: Object to evaluate
    :type  fpointer: callable

    :param pname: Parameter name
    :type  pname: string

    :param args: Positional arguments to pass to object
    :type  args: tuple

    :param kwargs: Keyword arguments to pass to object
    :type  kwargs: dictionary

    :raises:
     * AssertionError (Did not raise)

     * RuntimeError (Illegal number of arguments)
    """
    assert_exception(
        fpointer,
        RuntimeError,
        'Argument `{0}` is not valid'.format(pname),
        *args,
        **kwargs
    )


def assert_exception(fpointer, extype, exmsg, *args, **kwargs):
    """
    Asserts an exception type and message within the Py.test environment. If
    the actual exception message and the expected exception message do not
    literally match then the expected exception message is treated as a
    regular expression and a match is sought with the actual exception message

    :param fpointer: Object to evaluate
    :type  fpointer: callable

    :param extype: Expected exception type
    :type  extype: type

    :param exmsg: Expected exception message (can have regular expressions)
    :type  exmsg: string

    :param args: Positional arguments to pass to object
    :type  args: tuple

    :param kwargs: Keyword arguments to pass to object
    :type  kwargs: dictionary

    For example:

        >>> import putil.test, putil.eng
        >>> try:
        ...     putil.test.assert_exception(
        ...         putil.eng.peng,
        ...         RuntimeError,
        ...         'Argument `number` is not valid',
        ...         {'number':5, 'frac_length':3, 'rjust':True}
        ...     )   #doctest: +ELLIPSIS
        ... except AssertionError:
        ...     raise RuntimeError('Test failed')
        Traceback (most recent call last):
            ...
        RuntimeError: Test failed

    :raises:
     * AssertionError (Did not raise)

     * RuntimeError (Illegal number of arguments)
    """
    # Collect function arguments
    arg_dict = {}
    if args:
        fargs = _get_fargs(fpointer, no_self=True)
        if len(args) > len(fargs):
            raise RuntimeError('Illegal number of arguments')
        arg_dict = dict(zip(fargs, args))
    arg_dict.update(kwargs)
    # Execute function and catch exception
    regexp = re.compile(exmsg)
    try:
        with pytest.raises(extype) as excinfo:
            fpointer(**arg_dict)
    except Exception as eobj:
        actmsg = get_exmsg(eobj)
        if actmsg == 'DID NOT RAISE':
            raise AssertionError('Did not raise')
        eobj_extype = repr(eobj)[:repr(eobj).find('(')]
        assert (
            '{0} ({1})'.format(
                eobj_extype,
                actmsg
            )
            ==
            '{0} ({1})'.format(exception_type_str(extype), exmsg)
        )
    actmsg = get_exmsg(excinfo)
    if ((exception_type_str(excinfo.type) == exception_type_str(extype)) and
       ((actmsg == exmsg) or regexp.match(actmsg))):
        assert True
    else:
        assert (
            '{0} ({1})'.format(
                exception_type_str(excinfo.type),
                actmsg
            )
            ==
            '{0} ({1})'.format(exception_type_str(extype), exmsg)
        )


def assert_ro_prop(cobj, prop_name):
    """
    Asserts that a class property cannot be deleted

    :param cobj: Class object
    :type  cobj: class object

    :param prop_name: Property name
    :type  prop_name: string
    """
    # pylint: disable=W0122,W0613
    try:
        with pytest.raises(AttributeError) as excinfo:
            exec('del cobj.'+prop_name, None, locals())
    except Exception as eobj:
        if get_exmsg(eobj) == 'DID NOT RAISE':
            raise AssertionError('Property can be deleted')
        raise
    assert get_exmsg(excinfo) == "can't delete attribute"


def comp_list_of_dicts(list1, list2):
    """ Compare list of dictionaries """
    for item in list1:
        if item not in list2:
            print('List1 item not in list2:')
            print(item)
            return False
    for item in list2:
        if item not in list1:
            print('List2 item not in list1:')
            print(item)
            return False
    return True


def exception_type_str(exobj):
    """
    Returns an exception type string

    :param exobj: Exception
    :type  exobj: type (Python 2) or class (Python 3)

    :rtype: string

    For example:

        >>> import putil.test
        >>> exception_type_str(RuntimeError)
        'RuntimeError'
    """
    return _ex_type_str(exobj)


def get_exmsg(exobj): # pragma: no cover
    """
    Returns exception message (Python interpreter version independent)

    :param exobj: Exception object
    :type  exobj: exception object

    :rtype: string
    """
    return _get_ex_msg(exobj)


###
# Global variables (shortcuts)
###
AE = assert_exception
AI = assert_arg_invalid
AROPROP = assert_ro_prop
CLDICTS = comp_list_of_dicts
GET_EXMSG = get_exmsg
RE = RuntimeError
