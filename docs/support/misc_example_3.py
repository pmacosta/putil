# misc_example_3.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0702

import putil.misc

def write_data(file_handle):
	file_handle.write('Hello world!')

def show_tmpfile():
	with putil.misc.TmpFile(write_data) as file_name:
		with open(file_name, 'r') as fobj:
			lines = fobj.readlines()
	print '\n'.join(lines)
