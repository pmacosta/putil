# exdoc_support_module_4.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0105,W0212

"""
[[[cog
import trace_my_module_2
exobj_my_module = trace_my_module_2.trace_module()
]]]
[[[end]]]
"""

import putil.exh

def func(name):
    """
    Prints your name

    :param   name: Name to print
    :type name: string

    .. [[[cog cog.out(exobj_my_module.get_sphinx_autodoc()) ]]]
    .. [[[end]]]

    """
    exhobj = putil.exh.get_or_create_exh_obj()
    exhobj.add_exception(
        exname='illegal_name',
        extype=TypeError,
        exmsg='Argument `name` is not valid'
    )
    exhobj.raise_exception_if(
        exname='illegal_name',
        condition=not isinstance(name, str)
    )
