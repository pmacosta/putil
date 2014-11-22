# test_exh.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212

"""
putil.exh unit tests
"""

import putil.exh

def test_get_exh_obj():
	""" Test get_txh_obj() function """
	putil.exh._set_exh_obj('Test global variable')
	test_list = list()
	test_list.append(putil.exh._get_exh_obj() == 'Test global variable')
	putil.exh._del_exh_obj()
	test_list.append(putil.exh._get_exh_obj() == None)
	assert test_list == len(test_list)*[True]


