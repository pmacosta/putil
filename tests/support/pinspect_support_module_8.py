# pinspect_support_module_7.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

class BaseClass(object):	#pylint: disable=R0903
	""" Master class from which test enclosed class is going to be derived """
	def __init__(self):
		self.value = None

def test_enclosure_derived_class():
	import math	#pylint: disable=W0612
	class SubClassA(object):	#pylint: disable=R0903,C0111,W0612
		def __init__(self):
			import re	#pylint: disable=W0612
			self.co_filename = ''
	import copy	#pylint: disable=W0612
	class SubClassB(BaseClass):	#pylint: disable=R0903,C0111,W0612
		def __init__(self):
			super(SubClassB, self).__init__()
			self.f_code = SubClassA()
		def sub_enclosure_method(self):
			""" Test enclosed classes on enclosed classes """
			import os	#pylint: disable=W0612
			import _not_a_module_	#pylint: disable=F0401,W0612
			class SubClassC(object):	# pylint: disable=R0903,W0612
				""" Actual sub-closure class """
				def __init__(self):
					""" Constructor method """
					self.subobj = None
			return SubClassC

	class SubClassD(object):	#pylint: disable=R0903,C0111,W0612
		def __init__(self):
			self.value = None
