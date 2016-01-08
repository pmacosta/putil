# pinspect_support_module_8.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,F0401,R0903,W0212,W0612

class BaseClass(object):
    """ Master class from which test enclosed class is going to be derived """
    def __init__(self):
        self.value = None

def test_enclosure_derived_class():
    import math
    class SubClassA(object):
        def __init__(self):
            import re
            self.co_filename = ''
    import copy
    class SubClassB(BaseClass):
        def __init__(self):
            super(SubClassB, self).__init__()
            self.f_code = SubClassA()
        def sub_enclosure_method(self):
            """ Test enclosed classes on enclosed classes """
            import os
            import _not_a_module_
            class SubClassC(object):
                """ Actual sub-closure class """
                def __init__(self):
                    """ Constructor method """
                    self.subobj = None
            return SubClassC

    class SubClassD(object):
        def __init__(self):
            self.value = None
