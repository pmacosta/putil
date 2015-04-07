﻿# exh_support_module_1.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111


###
# Module functions
###
def mydecorator(func):
	""" Dummy decorator """
	return func


@mydecorator
def func16(exobj):	#pylint: disable=C0111,W0612
	exobj.add_exception('total_exception_16', TypeError, 'Total exception #16')
