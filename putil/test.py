# test.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E0611,F0401

# Standard library imports
import re
import sys
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
def assert_exception(obj, args, extype, exmsg):
    """
    Asserts an exception type and message within the Py.test environment. If
    the actual exception message and the expected exception message do not
    literally match then the expected exception message is treated as a
    regular expression and a match is sought with the actual exception message

    :param obj: Object to evaluate
    :type  obj: callable

    :param args: Keyword arguments to pass to object
    :type  args: dictionary

    :param extype: Expected exception type
    :type  extype: type

    :param exmsg: Expected exception message (can have regular expressions)
    :type  exmsg: string

    :rtype: None

    For example:

        >>> import putil.test, putil.eng
        >>> try:
        ...     putil.test.assert_exception(
        ...         putil.eng.peng,
        ...         {'number':5, 'frac_length':3, 'rjust':True},
        ...         RuntimeError,
        ...         'Argument `number` is not valid'
        ...     )   #doctest: +ELLIPSIS
        ... except AssertionError:
        ...     raise RuntimeError('Test failed')
        Traceback (most recent call last):
            ...
        RuntimeError: Test failed
    """
    # pylint: disable=W0703
    regexp = re.compile(exmsg)
    try:
        with pytest.raises(extype) as excinfo:
            obj(**args)
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


def comp_list_of_dicts(list1, list2):
    """ Compare list of dictionaries """
    return all([item in list1 for item in list2])


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


def get_exmsg(obj): # pragma: no cover
    """ Return exception message """
    return _get_ex_msg(obj)
