# pinspect_support_module_5.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212


import math	#pylint: disable=W0611
if True:
	import os	#pylint: disable=W0611
else:
	import module_not_found	#pylint: disable=F0401,W0611


def namespace_test_enclosing_function():	#pylint: disable=C0103
	""" Enclosing function to test namespace resolution """
	class NamespaceTestClass(object):	#pylint: disable=R0903,W0612
		""" Enclosed class to test namespace resolution """
		def __init__(self):
			self._data = None

		def _get_data(self):
			return self._data

		def _set_data(self, data):
			self._data = data

		data = property(_get_data, _set_data, None, 'Data property')
