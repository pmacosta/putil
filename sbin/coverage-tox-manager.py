#!/usr/bin/env python
# coverage-tox-manager.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0103

import os, sys


def main(argv):
	""" Processing """
	debug = True
	if len(argv) == 3:
		mode_flag, pkg_dir, site_pkg_dir = argv
	else:
		mode_flag, pkg_dir = argv
	output_file_name = os.path.join(pkg_dir, '.coveragerc_tox')
	if mode_flag == '1':
		lines = []
		lines.append('# .coveragerc_tox to control coverage.py during tox runs')
		lines.append('[run]')
		start_flag = True
		for file_name in os.listdir(os.path.join(pkg_dir, 'putil')):
			if file_name.endswith('.py') and (file_name != '__init__.py'):
				if start_flag:
					lines.append('include = {0}'.format(os.path.join(site_pkg_dir, 'putil', file_name)))
					start_flag = False
				else:
					lines.append('          {0}'.format(os.path.join(site_pkg_dir, 'putil', file_name)))
		with open(output_file_name, 'w') as fobj:
			fobj.write('\n'.join(lines))
		if debug:
			with open(output_file_name, 'r') as fobj:
				print ''.join(fobj.readlines())
	else:
		try:
			os.remove(output_file_name)
			os.remove(os.path.join(pkg_dir, '.coverage'))
		except:	#pylint: disable=W0702
			pass


if __name__ == '__main__':
	main(sys.argv[1:])
