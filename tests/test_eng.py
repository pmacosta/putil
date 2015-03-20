﻿# test_eng.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0302,W0212

"""
putil.eng unit tests
"""

import putil.test, putil.eng

###
# Functions
###
def test_to_eng_string():	#pylint: disable=R0915
	""" Test _to_eng_string() function """
	# Positive
	assert putil.eng._to_eng_string(0.000000000000000000000001001234567890) == '1.00123456789E-24'
	assert putil.eng._to_eng_string(0.000000000000000000000001) == '1E-24'
	assert putil.eng._to_eng_string(0.00000000000000000000001001234567890) == '10.0123456789E-24'
	assert putil.eng._to_eng_string(0.00000000000000000000001) == '10E-24'
	assert putil.eng._to_eng_string(0.0000000000000000000001001234567890) == '100.123456789E-24'
	assert putil.eng._to_eng_string(0.0000000000000000000001) == '100E-24'
	assert putil.eng._to_eng_string(0.000000000000000000001001234567890) == '1.00123456789E-21'
	assert putil.eng._to_eng_string(0.000000000000000000001) == '1E-21'
	assert putil.eng._to_eng_string(0.00000000000000000001001234567890) == '10.0123456789E-21'
	assert putil.eng._to_eng_string(0.00000000000000000001) == '10E-21'
	assert putil.eng._to_eng_string(0.0000000000000000001001234567890) == '100.123456789E-21'
	assert putil.eng._to_eng_string(0.0000000000000000001) == '100E-21'
	assert putil.eng._to_eng_string(0.000000000000000001001234567890) == '1.00123456789E-18'
	assert putil.eng._to_eng_string(0.000000000000000001) == '1E-18'
	assert putil.eng._to_eng_string(0.00000000000000001001234567890) == '10.0123456789E-18'
	assert putil.eng._to_eng_string(0.00000000000000001) == '10E-18'
	assert putil.eng._to_eng_string(0.0000000000000001001234567890) == '100.123456789E-18'
	assert putil.eng._to_eng_string(0.0000000000000001) == '100E-18'
	assert putil.eng._to_eng_string(0.000000000000001001234567890) == '1.00123456789E-15'
	assert putil.eng._to_eng_string(0.000000000000001) == '1E-15'
	assert putil.eng._to_eng_string(0.00000000000001001234567890) == '10.0123456789E-15'
	assert putil.eng._to_eng_string(0.00000000000001) == '10E-15'
	assert putil.eng._to_eng_string(0.0000000000001001234567890) == '100.123456789E-15'
	assert putil.eng._to_eng_string(0.0000000000001) == '100E-15'
	assert putil.eng._to_eng_string(0.000000000001001234567890) == '1.00123456789E-12'
	assert putil.eng._to_eng_string(0.000000000001) == '1E-12'
	assert putil.eng._to_eng_string(0.00000000001001234567890) == '10.0123456789E-12'
	assert putil.eng._to_eng_string(0.00000000001) == '10E-12'
	assert putil.eng._to_eng_string(0.0000000001001234567890) == '100.123456789E-12'
	assert putil.eng._to_eng_string(0.0000000001) == '100E-12'
	assert putil.eng._to_eng_string(0.000000001001234567890) == '1.00123456789E-9'
	assert putil.eng._to_eng_string(0.000000001) == '1E-9'
	assert putil.eng._to_eng_string(0.00000001001234567890) == '10.0123456789E-9'
	assert putil.eng._to_eng_string(0.00000001) == '10E-9'
	assert putil.eng._to_eng_string(0.0000001001234567890) == '100.123456789E-9'
	assert putil.eng._to_eng_string(0.0000001) == '100E-9'
	assert putil.eng._to_eng_string(0.000001001234567890) == '1.00123456789E-6'
	assert putil.eng._to_eng_string(0.000001) == '1E-6'
	assert putil.eng._to_eng_string(0.00001001234567890) == '10.0123456789E-6'
	assert putil.eng._to_eng_string(0.00001) == '10E-6'
	assert putil.eng._to_eng_string(0.0001001234567890) == '100.123456789E-6'
	assert putil.eng._to_eng_string(0.0001) == '100E-6'
	assert putil.eng._to_eng_string(0.001001234567890) == '1.00123456789E-3'
	assert putil.eng._to_eng_string(0.001) == '1E-3'
	assert putil.eng._to_eng_string(0.01001234567890) == '10.0123456789E-3'
	assert putil.eng._to_eng_string(0.01) == '10E-3'
	assert putil.eng._to_eng_string(0.1001234567890) == '100.123456789E-3'
	assert putil.eng._to_eng_string(0.1) == '100E-3'
	assert putil.eng._to_eng_string(0) == '0E+0'
	assert putil.eng._to_eng_string(1) == '1E+0'
	assert putil.eng._to_eng_string(1.1234567890) == '1.123456789E+0'
	assert putil.eng._to_eng_string(10) == '10E+0'
	assert putil.eng._to_eng_string(10.1234567890) == '10.123456789E+0'
	assert putil.eng._to_eng_string(100) == '100E+0'
	assert putil.eng._to_eng_string(100.1234567890) == '100.123456789E+0'
	assert putil.eng._to_eng_string(1000) == '1E+3'
	assert putil.eng._to_eng_string(1000.1234567890) == '1.00012345679E+3'
	assert putil.eng._to_eng_string(10000) == '10E+3'
	assert putil.eng._to_eng_string(10000.1234567890) == '10.0001234568E+3'
	assert putil.eng._to_eng_string(100000) == '100E+3'
	assert putil.eng._to_eng_string(100000.1234567890) == '100.000123457E+3'
	assert putil.eng._to_eng_string(1000000) == '1E+6'
	assert putil.eng._to_eng_string(1000000.1234567890) == '1.00000012346E+6'
	assert putil.eng._to_eng_string(10000000) == '10E+6'
	assert putil.eng._to_eng_string(10000000.1234567890) == '10.0000001235E+6'
	assert putil.eng._to_eng_string(100000000) == '100E+6'
	assert putil.eng._to_eng_string(100000000.1234567890) == '100.000000123E+6'
	assert putil.eng._to_eng_string(1000000000) == '1E+9'
	assert putil.eng._to_eng_string(1000000000.1234567890) == '1.00000000012E+9'
	assert putil.eng._to_eng_string(10000000000) == '10E+9'
	assert putil.eng._to_eng_string(10000000000.1234567890) == '10.0000000001E+9'
	assert putil.eng._to_eng_string(100000000000) == '100E+9'
	assert putil.eng._to_eng_string(100000000000.1234567890) == '100E+9'
	assert putil.eng._to_eng_string(1000000000000) == '1E+12'
	assert putil.eng._to_eng_string(1000000000000.1234567890) == '1E+12'
	assert putil.eng._to_eng_string(10000000000000) == '10E+12'
	assert putil.eng._to_eng_string(10000000000000.1234567890) == '10E+12'
	assert putil.eng._to_eng_string(100000000000000) == '100E+12'
	assert putil.eng._to_eng_string(100000000000000.1234567890) == '100E+12'
	assert putil.eng._to_eng_string(1000000000000000) == '1E+15'
	assert putil.eng._to_eng_string(1000000000000000.1234567890) == '1E+15'
	assert putil.eng._to_eng_string(10000000000000000) == '10E+15'
	assert putil.eng._to_eng_string(10000000000000000.1234567890) == '10E+15'
	assert putil.eng._to_eng_string(100000000000000000) == '100E+15'
	assert putil.eng._to_eng_string(100000000000000000.1234567890) == '100E+15'
	assert putil.eng._to_eng_string(1000000000000000000) == '1E+18'
	assert putil.eng._to_eng_string(1000000000000000000.1234567890) == '1E+18'
	assert putil.eng._to_eng_string(10000000000000000000) == '10E+18'
	assert putil.eng._to_eng_string(10000000000000000000.1234567890) == '10E+18'
	assert putil.eng._to_eng_string(100000000000000000000) == '100E+18'
	assert putil.eng._to_eng_string(100000000000000000000.1234567890) == '100E+18'
	assert putil.eng._to_eng_string(1000000000000000000000) == '1E+21'
	assert putil.eng._to_eng_string(1000000000000000000000.1234567890) == '1E+21'
	assert putil.eng._to_eng_string(10000000000000000000000) == '10E+21'
	assert putil.eng._to_eng_string(10000000000000000000000.1234567890) == '10E+21'
	assert putil.eng._to_eng_string(100000000000000000000000) == '100E+21'
	assert putil.eng._to_eng_string(100000000000000000000000.1234567890) == '100E+21'
	assert putil.eng._to_eng_string(1000000000000000000000000) == '1E+24'
	assert putil.eng._to_eng_string(1000000000000000000000000.1234567890) == '1E+24'
	assert putil.eng._to_eng_string(10000000000000000000000000) == '10E+24'
	assert putil.eng._to_eng_string(10000000000000000000000000.1234567890) == '10E+24'
	assert putil.eng._to_eng_string(100000000000000000000000000) == '100E+24'
	assert putil.eng._to_eng_string(100000000000000000000000000.1234567890) == '100E+24'
	# Negative
	assert putil.eng._to_eng_string(-0.000000000000000000000001001234567890) == '-1.00123456789E-24'
	assert putil.eng._to_eng_string(-0.000000000000000000000001) == '-1E-24'
	assert putil.eng._to_eng_string(-0.00000000000000000000001001234567890) == '-10.0123456789E-24'
	assert putil.eng._to_eng_string(-0.00000000000000000000001) == '-10E-24'
	assert putil.eng._to_eng_string(-0.0000000000000000000001001234567890) == '-100.123456789E-24'
	assert putil.eng._to_eng_string(-0.0000000000000000000001) == '-100E-24'
	assert putil.eng._to_eng_string(-0.000000000000000000001001234567890) == '-1.00123456789E-21'
	assert putil.eng._to_eng_string(-0.000000000000000000001) == '-1E-21'
	assert putil.eng._to_eng_string(-0.00000000000000000001001234567890) == '-10.0123456789E-21'
	assert putil.eng._to_eng_string(-0.00000000000000000001) == '-10E-21'
	assert putil.eng._to_eng_string(-0.0000000000000000001001234567890) == '-100.123456789E-21'
	assert putil.eng._to_eng_string(-0.0000000000000000001) == '-100E-21'
	assert putil.eng._to_eng_string(-0.000000000000000001001234567890) == '-1.00123456789E-18'
	assert putil.eng._to_eng_string(-0.000000000000000001) == '-1E-18'
	assert putil.eng._to_eng_string(-0.00000000000000001001234567890) == '-10.0123456789E-18'
	assert putil.eng._to_eng_string(-0.00000000000000001) == '-10E-18'
	assert putil.eng._to_eng_string(-0.0000000000000001001234567890) == '-100.123456789E-18'
	assert putil.eng._to_eng_string(-0.0000000000000001) == '-100E-18'
	assert putil.eng._to_eng_string(-0.000000000000001001234567890) == '-1.00123456789E-15'
	assert putil.eng._to_eng_string(-0.000000000000001) == '-1E-15'
	assert putil.eng._to_eng_string(-0.00000000000001001234567890) == '-10.0123456789E-15'
	assert putil.eng._to_eng_string(-0.00000000000001) == '-10E-15'
	assert putil.eng._to_eng_string(-0.0000000000001001234567890) == '-100.123456789E-15'
	assert putil.eng._to_eng_string(-0.0000000000001) == '-100E-15'
	assert putil.eng._to_eng_string(-0.000000000001001234567890) == '-1.00123456789E-12'
	assert putil.eng._to_eng_string(-0.000000000001) == '-1E-12'
	assert putil.eng._to_eng_string(-0.00000000001001234567890) == '-10.0123456789E-12'
	assert putil.eng._to_eng_string(-0.00000000001) == '-10E-12'
	assert putil.eng._to_eng_string(-0.0000000001001234567890) == '-100.123456789E-12'
	assert putil.eng._to_eng_string(-0.0000000001) == '-100E-12'
	assert putil.eng._to_eng_string(-0.000000001001234567890) == '-1.00123456789E-9'
	assert putil.eng._to_eng_string(-0.000000001) == '-1E-9'
	assert putil.eng._to_eng_string(-0.00000001001234567890) == '-10.0123456789E-9'
	assert putil.eng._to_eng_string(-0.00000001) == '-10E-9'
	assert putil.eng._to_eng_string(-0.0000001001234567890) == '-100.123456789E-9'
	assert putil.eng._to_eng_string(-0.0000001) == '-100E-9'
	assert putil.eng._to_eng_string(-0.000001001234567890) == '-1.00123456789E-6'
	assert putil.eng._to_eng_string(-0.000001) == '-1E-6'
	assert putil.eng._to_eng_string(-0.00001001234567890) == '-10.0123456789E-6'
	assert putil.eng._to_eng_string(-0.00001) == '-10E-6'
	assert putil.eng._to_eng_string(-0.0001001234567890) == '-100.123456789E-6'
	assert putil.eng._to_eng_string(-0.0001) == '-100E-6'
	assert putil.eng._to_eng_string(-0.001001234567890) == '-1.00123456789E-3'
	assert putil.eng._to_eng_string(-0.001) == '-1E-3'
	assert putil.eng._to_eng_string(-0.01001234567890) == '-10.0123456789E-3'
	assert putil.eng._to_eng_string(-0.01) == '-10E-3'
	assert putil.eng._to_eng_string(-0.1001234567890) == '-100.123456789E-3'
	assert putil.eng._to_eng_string(-0.1) == '-100E-3'
	assert putil.eng._to_eng_string(-1) == '-1E+0'
	assert putil.eng._to_eng_string(-1.1234567890) == '-1.123456789E+0'
	assert putil.eng._to_eng_string(-10) == '-10E+0'
	assert putil.eng._to_eng_string(-10.1234567890) == '-10.123456789E+0'
	assert putil.eng._to_eng_string(-100) == '-100E+0'
	assert putil.eng._to_eng_string(-100.1234567890) == '-100.123456789E+0'
	assert putil.eng._to_eng_string(-1000) == '-1E+3'
	assert putil.eng._to_eng_string(-1000.1234567890) == '-1.00012345679E+3'
	assert putil.eng._to_eng_string(-10000) == '-10E+3'
	assert putil.eng._to_eng_string(-10000.1234567890) == '-10.0001234568E+3'
	assert putil.eng._to_eng_string(-100000) == '-100E+3'
	assert putil.eng._to_eng_string(-100000.1234567890) == '-100.000123457E+3'
	assert putil.eng._to_eng_string(-1000000) == '-1E+6'
	assert putil.eng._to_eng_string(-1000000.1234567890) == '-1.00000012346E+6'
	assert putil.eng._to_eng_string(-10000000) == '-10E+6'
	assert putil.eng._to_eng_string(-10000000.1234567890) == '-10.0000001235E+6'
	assert putil.eng._to_eng_string(-100000000) == '-100E+6'
	assert putil.eng._to_eng_string(-100000000.1234567890) == '-100.000000123E+6'
	assert putil.eng._to_eng_string(-1000000000) == '-1E+9'
	assert putil.eng._to_eng_string(-1000000000.1234567890) == '-1.00000000012E+9'
	assert putil.eng._to_eng_string(-10000000000) == '-10E+9'
	assert putil.eng._to_eng_string(-10000000000.1234567890) == '-10.0000000001E+9'
	assert putil.eng._to_eng_string(-100000000000) == '-100E+9'
	assert putil.eng._to_eng_string(-100000000000.1234567890) == '-100E+9'
	assert putil.eng._to_eng_string(-1000000000000) == '-1E+12'
	assert putil.eng._to_eng_string(-1000000000000.1234567890) == '-1E+12'
	assert putil.eng._to_eng_string(-10000000000000) == '-10E+12'
	assert putil.eng._to_eng_string(-10000000000000.1234567890) == '-10E+12'
	assert putil.eng._to_eng_string(-100000000000000) == '-100E+12'
	assert putil.eng._to_eng_string(-100000000000000.1234567890) == '-100E+12'
	assert putil.eng._to_eng_string(-1000000000000000) == '-1E+15'
	assert putil.eng._to_eng_string(-1000000000000000.1234567890) == '-1E+15'
	assert putil.eng._to_eng_string(-10000000000000000) == '-10E+15'
	assert putil.eng._to_eng_string(-10000000000000000.1234567890) == '-10E+15'
	assert putil.eng._to_eng_string(-100000000000000000) == '-100E+15'
	assert putil.eng._to_eng_string(-100000000000000000.1234567890) == '-100E+15'
	assert putil.eng._to_eng_string(-1000000000000000000) == '-1E+18'
	assert putil.eng._to_eng_string(-1000000000000000000.1234567890) == '-1E+18'
	assert putil.eng._to_eng_string(-10000000000000000000) == '-10E+18'
	assert putil.eng._to_eng_string(-10000000000000000000.1234567890) == '-10E+18'
	assert putil.eng._to_eng_string(-100000000000000000000) == '-100E+18'
	assert putil.eng._to_eng_string(-100000000000000000000.1234567890) == '-100E+18'
	assert putil.eng._to_eng_string(-1000000000000000000000) == '-1E+21'
	assert putil.eng._to_eng_string(-1000000000000000000000.1234567890) == '-1E+21'
	assert putil.eng._to_eng_string(-10000000000000000000000) == '-10E+21'
	assert putil.eng._to_eng_string(-10000000000000000000000.1234567890) == '-10E+21'
	assert putil.eng._to_eng_string(-100000000000000000000000) == '-100E+21'
	assert putil.eng._to_eng_string(-100000000000000000000000.1234567890) == '-100E+21'
	assert putil.eng._to_eng_string(-1000000000000000000000000) == '-1E+24'
	assert putil.eng._to_eng_string(-1000000000000000000000000.1234567890) == '-1E+24'
	assert putil.eng._to_eng_string(-10000000000000000000000000) == '-10E+24'
	assert putil.eng._to_eng_string(-10000000000000000000000000.1234567890) == '-10E+24'
	assert putil.eng._to_eng_string(-100000000000000000000000000) == '-100E+24'
	assert putil.eng._to_eng_string(-100000000000000000000000000.1234567890) == '-100E+24'
	# Full precision is retained if number is expressed a string
	assert putil.eng._to_eng_string('100000.1234567890') == '100.000123456789E+3'
	assert putil.eng._to_eng_string('-100000.1234567890') == '-100.000123456789E+3'


def test_peng():	#pylint: disable=R0915
	""" Test peng() function """
	putil.test.assert_exception(putil.eng.peng, {'number':['5'], 'frac_length':3, 'rjust':True}, RuntimeError, 'Argument `number` is not valid')
	putil.test.assert_exception(putil.eng.peng, {'number':5, 'frac_length':3.5, 'rjust':True}, RuntimeError, 'Argument `frac_length` is not valid')
	putil.test.assert_exception(putil.eng.peng, {'number':5, 'frac_length':3, 'rjust':'hello'}, RuntimeError, 'Argument `rjust` is not valid')
	assert putil.eng.peng(3.0333333333, 1, False) == '3.0'
	assert putil.eng.peng(0, 3, True) == '   0.000 '
	assert putil.eng.peng(0, 3, False) == '0.000'
	# Positive
	assert putil.eng.peng(1e-25, 3, True) == '   1.000y'
	assert putil.eng.peng(1e-24, 3, True) == '   1.000y'
	assert putil.eng.peng(1e-23, 3, True) == '  10.000y'
	assert putil.eng.peng(1e-22, 3, True) == ' 100.000y'
	assert putil.eng.peng(1e-21, 3, True) == '   1.000z'
	assert putil.eng.peng(1e-20, 3, True) == '  10.000z'
	assert putil.eng.peng(1e-19, 3, True) == ' 100.000z'
	assert putil.eng.peng(1e-18, 3, True) == '   1.000a'
	assert putil.eng.peng(1e-17, 3, True) == '  10.000a'
	assert putil.eng.peng(1e-16, 3, True) == ' 100.000a'
	assert putil.eng.peng(1e-15, 3, True) == '   1.000f'
	assert putil.eng.peng(1e-14, 3, True) == '  10.000f'
	assert putil.eng.peng(1e-13, 3, True) == ' 100.000f'
	assert putil.eng.peng(1e-12, 3, True) == '   1.000p'
	assert putil.eng.peng(1e-11, 3, True) == '  10.000p'
	assert putil.eng.peng(1e-10, 3, True) == ' 100.000p'
	assert putil.eng.peng(1e-9, 3, True) == '   1.000n'
	assert putil.eng.peng(1e-8, 3, True) == '  10.000n'
	assert putil.eng.peng(1e-7, 3, True) == ' 100.000n'
	assert putil.eng.peng(1e-6, 3, True) == '   1.000u'
	assert putil.eng.peng(1e-5, 3, True) == '  10.000u'
	assert putil.eng.peng(1e-4, 3, True) == ' 100.000u'
	assert putil.eng.peng(1e-3, 3, True) == '   1.000m'
	assert putil.eng.peng(1e-2, 3, True) == '  10.000m'
	assert putil.eng.peng(1e-1, 3, True) == ' 100.000m'
	assert putil.eng.peng(1e-0, 3, True) == '   1.000 '
	assert putil.eng.peng(1e+1, 3, True) == '  10.000 '
	assert putil.eng.peng(1e+2, 3, True) == ' 100.000 '
	assert putil.eng.peng(1e+3, 3, True) == '   1.000k'
	assert putil.eng.peng(1e+4, 3, True) == '  10.000k'
	assert putil.eng.peng(1e+5, 3, True) == ' 100.000k'
	assert putil.eng.peng(1e+6, 3, True) == '   1.000M'
	assert putil.eng.peng(1e+7, 3, True) == '  10.000M'
	assert putil.eng.peng(1e+8, 3, True) == ' 100.000M'
	assert putil.eng.peng(1e+9, 3, True) == '   1.000G'
	assert putil.eng.peng(1e+10, 3, True) == '  10.000G'
	assert putil.eng.peng(1e+11, 3, True) == ' 100.000G'
	assert putil.eng.peng(1e+12, 3, True) == '   1.000T'
	assert putil.eng.peng(1e+13, 3, True) == '  10.000T'
	assert putil.eng.peng(1e+14, 3, True) == ' 100.000T'
	assert putil.eng.peng(1e+15, 3, True) == '   1.000P'
	assert putil.eng.peng(1e+16, 3, True) == '  10.000P'
	assert putil.eng.peng(1e+17, 3, True) == ' 100.000P'
	assert putil.eng.peng(1e+18, 3, True) == '   1.000E'
	assert putil.eng.peng(1e+19, 3, True) == '  10.000E'
	assert putil.eng.peng(1e+20, 3, True) == ' 100.000E'
	assert putil.eng.peng(1e+21, 3, True) == '   1.000Z'
	assert putil.eng.peng(1e+22, 3, True) == '  10.000Z'
	assert putil.eng.peng(1e+23, 3, True) == ' 100.000Z'
	assert putil.eng.peng(1e+24, 3, True) == '   1.000Y'
	assert putil.eng.peng(1e+25, 3, True) == '  10.000Y'
	assert putil.eng.peng(1e+26, 3, True) == ' 100.000Y'
	assert putil.eng.peng(1e+27, 3, True) == ' 999.999Y'
	assert putil.eng.peng(12.45, 1, True) == '  12.5 '
	assert putil.eng.peng(998.999e3, 1, True) == ' 999.0k'
	assert putil.eng.peng(998.999e3, 1, False) == '999.0k'
	assert putil.eng.peng(999.999e3, 1, True) == '   1.0M'
	assert putil.eng.peng(999.999e3, 1) == '   1.0M'
	assert putil.eng.peng(999.999e3, 1, False) == '1.0M'
	assert putil.eng.peng(0.995, 0, False) == '995m'
	assert putil.eng.peng(0.9999, 0, False) == '1'
	assert putil.eng.peng(1.9999, 0, False) == '2'
	assert putil.eng.peng(999.99, 0, False) == '1k'
	assert putil.eng.peng(9.99, 1, False) == '10.0'
	assert putil.eng.peng(5.25e3, 1, True) == '   5.3k'
	assert putil.eng.peng(1.05e3, 0, True) == '   1k'
	# Negative
	assert putil.eng.peng(-1e-25, 3, True) == '  -1.000y'
	assert putil.eng.peng(-1e-24, 3, True) == '  -1.000y'
	assert putil.eng.peng(-1e-23, 3, True) == ' -10.000y'
	assert putil.eng.peng(-1e-22, 3, True) == '-100.000y'
	assert putil.eng.peng(-1e-21, 3, True) == '  -1.000z'
	assert putil.eng.peng(-1e-20, 3, True) == ' -10.000z'
	assert putil.eng.peng(-1e-19, 3, True) == '-100.000z'
	assert putil.eng.peng(-1e-18, 3, True) == '  -1.000a'
	assert putil.eng.peng(-1e-17, 3, True) == ' -10.000a'
	assert putil.eng.peng(-1e-16, 3, True) == '-100.000a'
	assert putil.eng.peng(-1e-15, 3, True) == '  -1.000f'
	assert putil.eng.peng(-1e-14, 3, True) == ' -10.000f'
	assert putil.eng.peng(-1e-13, 3, True) == '-100.000f'
	assert putil.eng.peng(-1e-12, 3, True) == '  -1.000p'
	assert putil.eng.peng(-1e-11, 3, True) == ' -10.000p'
	assert putil.eng.peng(-1e-10, 3, True) == '-100.000p'
	assert putil.eng.peng(-1e-9, 3, True) == '  -1.000n'
	assert putil.eng.peng(-1e-8, 3, True) == ' -10.000n'
	assert putil.eng.peng(-1e-7, 3, True) == '-100.000n'
	assert putil.eng.peng(-1e-6, 3, True) == '  -1.000u'
	assert putil.eng.peng(-1e-5, 3, True) == ' -10.000u'
	assert putil.eng.peng(-1e-4, 3, True) == '-100.000u'
	assert putil.eng.peng(-1e-3, 3, True) == '  -1.000m'
	assert putil.eng.peng(-1e-2, 3, True) == ' -10.000m'
	assert putil.eng.peng(-1e-1, 3, True) == '-100.000m'
	assert putil.eng.peng(-1e-0, 3, True) == '  -1.000 '
	assert putil.eng.peng(-1e+1, 3, True) == ' -10.000 '
	assert putil.eng.peng(-1e+2, 3, True) == '-100.000 '
	assert putil.eng.peng(-1e+3, 3, True) == '  -1.000k'
	assert putil.eng.peng(-1e+4, 3, True) == ' -10.000k'
	assert putil.eng.peng(-1e+5, 3, True) == '-100.000k'
	assert putil.eng.peng(-1e+6, 3, True) == '  -1.000M'
	assert putil.eng.peng(-1e+7, 3, True) == ' -10.000M'
	assert putil.eng.peng(-1e+8, 3, True) == '-100.000M'
	assert putil.eng.peng(-1e+9, 3, True) == '  -1.000G'
	assert putil.eng.peng(-1e+10, 3, True) == ' -10.000G'
	assert putil.eng.peng(-1e+11, 3, True) == '-100.000G'
	assert putil.eng.peng(-1e+12, 3, True) == '  -1.000T'
	assert putil.eng.peng(-1e+13, 3, True) == ' -10.000T'
	assert putil.eng.peng(-1e+14, 3, True) == '-100.000T'
	assert putil.eng.peng(-1e+15, 3, True) == '  -1.000P'
	assert putil.eng.peng(-1e+16, 3, True) == ' -10.000P'
	assert putil.eng.peng(-1e+17, 3, True) == '-100.000P'
	assert putil.eng.peng(-1e+18, 3, True) == '  -1.000E'
	assert putil.eng.peng(-1e+19, 3, True) == ' -10.000E'
	assert putil.eng.peng(-1e+20, 3, True) == '-100.000E'
	assert putil.eng.peng(-1e+21, 3, True) == '  -1.000Z'
	assert putil.eng.peng(-1e+22, 3, True) == ' -10.000Z'
	assert putil.eng.peng(-1e+23, 3, True) == '-100.000Z'
	assert putil.eng.peng(-1e+24, 3, True) == '  -1.000Y'
	assert putil.eng.peng(-1e+25, 3, True) == ' -10.000Y'
	assert putil.eng.peng(-1e+26, 3, True) == '-100.000Y'
	assert putil.eng.peng(-1e+27, 3, True) == '-999.999Y'
	assert putil.eng.peng(-12.45, 1, True) == ' -12.5 '
	assert putil.eng.peng(-998.999e3, 1, True) == '-999.0k'
	assert putil.eng.peng(-998.999e3, 1, False) == '-999.0k'
	assert putil.eng.peng(-999.999e3, 1, True) == '  -1.0M'
	assert putil.eng.peng(-999.999e3, 1) == '  -1.0M'
	assert putil.eng.peng(-999.999e3, 1, False) == '-1.0M'
	assert putil.eng.peng(-0.995, 0, False) == '-995m'
	assert putil.eng.peng(-0.9999, 0, False) == '-1'
	assert putil.eng.peng(-1.9999, 0, False) == '-2'
	assert putil.eng.peng(-999.99, 0, False) == '-1k'
	assert putil.eng.peng(-9.99, 1, False) == '-10.0'
	assert putil.eng.peng(-5.25e3, 1, True) == '  -5.3k'
	assert putil.eng.peng(-1.05e3, 0, True) == '  -1k'


def test_peng_suffix():
	""" Test peng_suffix() function """
	putil.test.assert_exception(putil.eng.peng_suffix, {'snum':None}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_suffix, {'snum':''}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_suffix, {'snum':' 5x'}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_suffix, {'snum':'a5M'}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_suffix, {'snum':'- - a5M'}, RuntimeError, 'Argument `snum` is not valid')
	assert putil.eng.peng_suffix(putil.eng.peng(1, 3, True)) == ' '
	assert putil.eng.peng_suffix(putil.eng.peng(-10.5e-6, 3, False)) == 'u'


def test_peng_suffix_math():
	""" Test peng_suffix_math() function """
	putil.test.assert_exception(putil.eng.peng_suffix_math, {'suffix':'X', 'offset':-1}, RuntimeError, 'Argument `suffix` is not valid')
	putil.test.assert_exception(putil.eng.peng_suffix_math, {'suffix':'M', 'offset':'a'}, RuntimeError, 'Argument `offset` is not valid')
	putil.test.assert_exception(putil.eng.peng_suffix_math, {'suffix':'M', 'offset':20}, ValueError, 'Argument `offset` is not valid')
	assert putil.eng.peng_suffix_math(' ', 3) == 'G'
	assert putil.eng.peng_suffix_math('u', -2) == 'p'


def test_peng_power():
	""" Test peng_power() function """
	putil.test.assert_exception(putil.eng.peng_power, {'snum':None}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_power, {'snum':''}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_power, {'snum':' 5x'}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_power, {'snum':'a5M'}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_power, {'snum':'- - a5M'}, RuntimeError, 'Argument `snum` is not valid')
	tup = putil.eng.peng_power(putil.eng.peng(1234.567, 3, True))
	assert tup == ('k', 1000.0)
	assert isinstance(tup[1], float)


def test_peng_int():
	""" Test peng_int() function """
	putil.test.assert_exception(putil.eng.peng_int, {'snum':None}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_int, {'snum':''}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_int, {'snum':' 5x'}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_int, {'snum':'a5M'}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_int, {'snum':'- - a5M'}, RuntimeError, 'Argument `snum` is not valid')
	assert putil.eng.peng_int(putil.eng.peng(5234.567, 6, True)) == 5


def test_peng_frac():
	""" Test peng_frac() function """
	putil.test.assert_exception(putil.eng.peng_frac, {'snum':None}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_frac, {'snum':''}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_frac, {'snum':' 5x'}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_frac, {'snum':'a5M'}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_frac, {'snum':'- - a5M'}, RuntimeError, 'Argument `snum` is not valid')
	assert putil.eng.peng_frac(putil.eng.peng(5234.567, 6, True)) == 234567


def test_peng_mant():
	""" Test peng_mant() function """
	putil.test.assert_exception(putil.eng.peng_mant, {'snum':None}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_mant, {'snum':''}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_mant, {'snum':' 5x'}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_mant, {'snum':'a5M'}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_mant, {'snum':'- - a5M'}, RuntimeError, 'Argument `snum` is not valid')
	assert putil.eng.peng_mant(putil.eng.peng(5234.567, 3, True)) == 5.235


def test_peng_float():
	""" Test peng_float() function """
	putil.test.assert_exception(putil.eng.peng_float, {'snum':None}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_float, {'snum':''}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_float, {'snum':' 5x'}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_float, {'snum':'a5M'}, RuntimeError, 'Argument `snum` is not valid')
	putil.test.assert_exception(putil.eng.peng_float, {'snum':'- - a5M'}, RuntimeError, 'Argument `snum` is not valid')
	assert putil.eng.peng_float(putil.eng.peng(5234.567, 3, True)) == 5.235e3
	assert putil.eng.peng_float('     5.235k    ') == 5.235e3
	assert putil.eng.peng_float('    -5.235k    ') == -5.235e3
