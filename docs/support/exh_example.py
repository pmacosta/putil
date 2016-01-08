# exh_example.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,W0212,W0640

from __future__ import print_function
import putil.exh

EXHOBJ = putil.exh.ExHandle()

def my_func(name):
    """ Sample function """
    EXHOBJ.add_exception(
        exname='illegal_name',
        extype=TypeError,
        exmsg='Argument `name` is not valid'
    )
    EXHOBJ.raise_exception_if(
        exname='illegal_name',
        condition=not isinstance(name, str)
    )
    print('My name is {0}'.format(name))
