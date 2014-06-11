# misc_test.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.misc unit tests
"""

import putil.misc

def test_pgcd():
	""" Test if the custom greatest common divisor function works """
	test_list = list()
	test_list.append(putil.misc.pgcd(48, 18) == 6)
	test_list.append(putil.misc.pgcd(2.7, 107.3) == 0.1)
	test_list.append(putil.misc.pgcd(3, 4) == 1)
	test_list.append(putil.misc.pgcd(0.05, 0.02) == 0.01)
	assert test_list == [True]*4
