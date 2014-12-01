# test_pinspect.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.pintrospect unit tests
"""

import sys

import putil.exh
import putil.test
import putil.pinspect

def test_package_modules():
	""" Test package_modules() function """
	test_list = list()
	test_list.append(putil.test.trigger_exception(putil.pinspect.package_modules, {'module_obj':5}, AttributeError, 'Argument `module_obj` does not have the attribute __name__'))
	tmp = putil.exh.ExHandle()
	tmp.__name__ = 5
	test_list.append(putil.test.trigger_exception(putil.pinspect.package_modules, {'module_obj':tmp}, AttributeError, 'Argument `module_obj` does not have the attribute __name__'))
	tmp.__name__ = '_not_a_valid_module_name_'
	test_list.append(putil.test.trigger_exception(putil.pinspect.package_modules, {'module_obj':tmp}, RuntimeError, 'Package object `_not_a_valid_module_name_` could not be found'))
	module_obj_list = [sys.modules['putil.pcontracts'], sys.modules['putil.eng'], sys.modules['putil.misc'], sys.modules['putil.tree'], sys.modules['putil.check'], \
					sys.modules['putil.pinspect'], sys.modules['putil.test'], sys.modules['putil.eng'], sys.modules['putil.exh']]
	test_list.append(set(putil.pinspect.package_modules(sys.modules['putil.eng'])) == set(module_obj_list))
	assert test_list == [True]*len(test_list)

def test_object_is_module():
	""" Test object_is_module() function """
	test_list = list()
	test_list.append(putil.pinspect.is_object_module(5) == False)
	test_list.append(putil.pinspect.is_object_module(sys.modules['putil.eng']) == True)
	assert test_list == [True]*len(test_list)

