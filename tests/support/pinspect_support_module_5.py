# pinspect_support_module_5.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,F0401,W0125,W0212,W0611


import math
if True:
    import os
else:
    import module_not_found


def namespace_test_enclosing_function():
    """ Enclosing function to test namespace resolution """
    # pylint: disable=C0103,R0903,W0612
    class NamespaceTestClass(object):
        """ Enclosed class to test namespace resolution """
        def __init__(self):
            self._data = None

        def _get_data(self):
            return self._data

        def _set_data(self, data):
            self._data = data

        data = property(_get_data, _set_data, None, 'Data property')
