# exh_support_module_2.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0903,W0212,W0611,W0612

import putil.exh


class MyClass(object):
    """ Enclosed class """
    def __init__(self, exhobj, value=0):
        self._exhobj = exhobj
        self._value = None
        self.value = value

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._exhobj.add_exception(
            'wrong_value', TypeError, 'Illegal value'
        )
        self._value = value

    value = property(_get_value, _set_value, doc='Value property')
