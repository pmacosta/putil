# pinspect_support_module_2.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212


def setter_enclosing_func(offset):
    """ Test function to see if property enclosures are detected """
    def setter_closure_func(self, num):
        """ Actual closure function """
        self._clsvar = offset+num
    return setter_closure_func


class SimpleClass(object):
    """ Simple class with property for mocking purposes """
    def __init__(self):
        """ Constructor method """
        self.mobj = None

    def get_mobj(self):
        """ Getter method """
        return self.mobj

    def set_mobj(self, mobj):
        """ Setter method """
        self.mobj = mobj

    mobj = property(get_mobj, set_mobj)


def getter_func_for_closure_class(self):
    """
    Getter function to test if enclosed class detection works with property
    action functions in different files
    """
    return self.mobj
