# misc_example_2.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0702

import putil.misc

def timer(num_tries, fpointer):
	with putil.misc.Timer() as tobj:
		for _ in xrange(num_tries):
			fpointer()
	print 'Time per call: {0} seconds'.format(
		tobj.elapsed_time/(2.0*num_tries)
	)

def sample_func():
	count = 0
	for num in xrange(0, count):
		count += num
