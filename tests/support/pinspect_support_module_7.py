# pinspect_support_module_7.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

def test_enclosure_class():
	class MockFCode(object):	#pylint: disable=R0903,C0111
		def __init__(self):
			self.co_filename = ''
	class MockGetFrame(object):	#pylint: disable=R0903,C0111
		def __init__(self):
			self.f_code = MockFCode()
		def sub_enclosure_method(self):
			""" Test enclosed classes on enclosed classes """
			import math	#pylint: disable=W0612
			class SubClosureClass(object):	# pylint: disable=R0903
				""" Actual sub-closure class """
				def __init__(self):
					""" Constructor method """
					self.subobj = None
			return SubClosureClass

	class FinalClass(object):	#pylint: disable=R0903,C0111,W0612
		def __init__(self):
			self.value = None

	def mock_getframe():	#pylint: disable=W0613,C0111,W0612
		return MockGetFrame()
