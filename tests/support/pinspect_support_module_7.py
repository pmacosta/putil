# pinspect_support_module_7.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0111,R0903,W0212,W0612,W0613

def test_enclosure_class():
    class MockFCode(object):
        def __init__(self):
            self.co_filename = ''
    class MockGetFrame(object):
        def __init__(self):
            self.f_code = MockFCode()
        def sub_enclosure_method(self):
            """ Test enclosed classes on enclosed classes """
            class SubClosureClass(object):
                """ Actual sub-closure class """
                def __init__(self):
                    """ Constructor method """
                    self.subobj = None
            return SubClosureClass

    class FinalClass(object):
        def __init__(self):
            self.value = None

    def mock_getframe():
        return MockGetFrame()
