# pinspect_support_module_6.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212


def namespace_test_enclosing_error_function():
    """
    Enclosing function to test namespace resolution when non-import errors
    are encountered
    """
    # pylint: disable=C0103,R0903,W0612
    class NamespaceTestClass(object):
        """ Enclosed class to test namespace resolution error handling """
        import math
        value = math.sqrt(-1)

        def __init__(self):
            self._data = None

        def _get_data(self):
            return self._data

        def _set_data(self, data):
            self._data = data

        data = property(_get_data, _set_data, None, 'Data property')
