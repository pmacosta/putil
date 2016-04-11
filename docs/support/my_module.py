# my_module.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0903,W0105

###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
sys.path.append(os.environ['TRACER_DIR'])
import trace_my_module_1
exobj = trace_my_module_1.trace_module(no_print=True)
]]]
[[[end]]]
"""

import putil.exh

def func(name):
    r"""
    Prints your name

    :param   name: Name to print
    :type name: string

    .. [[[cog cog.out(exobj.get_sphinx_autodoc(width=69))]]]
    .. [[[end]]]

    """
    # Raise condition evaluated in same call as exception addition
    putil.exh.addex(
        TypeError, 'Argument `name` is not valid', not isinstance(name, str)
    )
    return 'My name is {0}'.format(name)

class MyClass(object):
    """ Stores a value """
    def __init__(self, value=None):
        self._value = None if not value else value

    def _get_value(self):
        # Raise condition not evaluated in same call as
        # exception additions
        exobj = putil.exh.addex(RuntimeError, 'Attribute `value` not set')
        exobj(not self._value)
        return self._value

    def _set_value(self, value):
        exobj = putil.exh.addex(RuntimeError, 'Argument `value` is not valid')
        exobj(not isinstance(value, int))
        self._value = value

    value = property(_get_value, _set_value)
    r"""
    Sets or returns a value

    :type:  integer
    :rtype: integer or None

    .. [[[cog cog.out(exobj.get_sphinx_autodoc(width=69))]]]
    .. [[[end]]]
    """
