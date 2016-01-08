# pinspect_support_module_9.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0201,R0903,W0212,W0621


def simple_property_generator():
    """
    Function to test if properties done via enclosed functions are
    properly detected
    """
    def fget(self):
        """ Actual getter function """
        return self._value
    return property(fget)
