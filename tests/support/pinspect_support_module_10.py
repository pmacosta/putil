# pinspect_support_module_10.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0903,W0212,W0612

class AClass(object):
    """
    Class to test function closing and then indentation past previous
    indent but not in function
    """
    # pylint: disable=C0103,E0602
    def method1(self):
        """ A method """
        x = 5
        def func1(x):
            """ A function """
            return x+10
        # A comment
        for item in [1, 2]:
            class SubClass(object):
                """ This class does not belong in func1 """
                def __init__(self):
                    self.data = 0
            y = x+item

    def method2(self):
        """ Another method """
        pass
