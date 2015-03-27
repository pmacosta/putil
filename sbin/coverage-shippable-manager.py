#!/usr/bin/env python
# coverage-shippable-manager.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0103

import os, sys


def main(site_pkg_dir):
	""" Processing """
	debug = False
	pkg_dir = os.environ['SHIPPABLE_REPO_DIR']
	output_file_name = os.path.join(pkg_dir, '.coveragerc_shippable')
	lines = []
	lines.append('# .coveragerc_shippable to control coverage.py during Shippable CI runs')
	lines.append('[run]')
	lines.append('branch = True')
	start_flag = True
	for file_name in os.listdir(os.path.join(pkg_dir, 'putil')):
		if file_name.endswith('.py') and (file_name != '__init__.py'):
			if start_flag:
				lines.append('include = {0}'.format(os.path.join(site_pkg_dir, 'putil', file_name)))
				start_flag = False
			else:
				lines.append('          {0}'.format(os.path.join(site_pkg_dir, 'putil', file_name)))
	lines.append('[xml]')
	lines.append('output = shippable/codecoverage/coverage.xml')
	with open(output_file_name, 'w') as fobj:
		fobj.write('\n'.join(lines))
	if debug:
		with open(output_file_name, 'r') as fobj:
			print ''.join(fobj.readlines())


if __name__ == '__main__':
	main(sys.argv[1])
