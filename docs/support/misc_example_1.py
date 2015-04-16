# misc_example_1.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0702

import os, putil.misc

def ignored_example():
	file_name = 'somefile.tmp'
	open(file_name, 'w').close()
	print 'File {0} exists? {1}'.format(
		file_name, os.path.isfile(file_name)
	)
	with putil.misc.ignored(OSError):
		os.remove(file_name)
	print 'File {0} exists? {1}'.format(
		file_name, os.path.isfile(file_name)
	)
	with putil.misc.ignored(OSError):
		os.remove(file_name)
	print 'No exception trying to remove a file that does not exists'
	try:
		with putil.misc.ignored(RuntimeError):
			os.remove(file_name)
	except:
		print 'Got an exception'
