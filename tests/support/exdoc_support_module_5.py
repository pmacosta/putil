# exdoc_support_module_5.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0903,W0613

import putil.exh


###
# Module functions
###
def float_func(arg):
    """
    Internal argument validation, have exceptions defined after a
    chain of function calls
    """
    exobj = putil.exh.get_or_create_exh_obj()
    exobj.add_exception(
        exname='illegal_argument',
        extype=TypeError,
        exmsg='Argument `arg` is not valid'
    )
    exobj.add_exception(
        exname='illegal_value',
        extype=ValueError,
        exmsg='Argument `arg` is illegal'
    )

    exobj.raise_exception_if('illegal_argument', not isinstance(arg, float))
    exobj.raise_exception_if('illegal_value', arg < 0)
