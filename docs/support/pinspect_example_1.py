# pinspect_example_1.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0903,W0212,W0611,W0612

from __future__ import print_function
import math

def my_func(version):
    """ Enclosing function """
    class MyClass(object):
        """ Enclosed class """
        if version == 2:
            import docs.support.python2_module as pm
        else:
            import docs.support.python3_module as pm

        def __init__(self, value):
            self._value = value

        def _get_value(self):
            return self._value

        value = property(_get_value, pm._set_value, None, 'Value property')

def print_name(name):
    print('My name is {0}, and sqrt(2) = {1}'.format(name, math.sqrt(2)))
