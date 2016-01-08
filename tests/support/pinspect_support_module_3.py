# pinspect_support_module_3.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

from __future__ import print_function


def deleter(self):
    """
    Getter function to test if enclosed class detection works with property
    action functions in different files
    """
    # pylint: disable=W0613
    print('Deleter action')


def another_class_enclosing_func():
    """
    Test function to see if classes within enclosures are detected, in this
    case with property actions imported via 'from *'
    """
    from tests.support.pinspect_support_module_9 import (
        simple_property_generator
    )
    class FromImportClosureClass(object):
        """ Actual class """
        # pylint: disable=R0903
        def __init__(self, value):
            self._value = value

        encprop = simple_property_generator()

    return FromImportClosureClass


def another_property_action_enclosing_function():
    """
    Generator function to test namespace support for enclosed
    class properties
    """
    # pylint: disable=C0103,E0602
    def fget(self):
        """ Actual getter function """
        return math.sqrt(self._value)
    return property(fget)
