# exh_example.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,W0212,W0640

from __future__ import print_function
from putil.exh import addex

def my_func(name):
    """ Sample function """
    # Add exception
    exobj = addex(TypeError, 'Argument `name` is not valid')
    # Conditionally raise exception
    exobj(not isinstance(name, str))
    print('My name is {0}'.format(name))
