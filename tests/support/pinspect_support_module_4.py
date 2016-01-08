# pinspect_support_module_4.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

USAGE1 = """\
    This is a test\
    of a multi-line string """

USAGE2 = r"""
    This is a test
    of a raw multi-line string """

USAGE3 = r""" This is a test of a single-line string """

def another_property_action_enclosing_function():
    """
    Generator function to test namespace support for enclosed class properties
    """
    # pylint: disable=C0103,E0602
    def fget(self):
        """ Actual getter function """
        return math.sqrt(self._value)
    return property(fget)
