#!/usr/bin/env python
# coveragerc-manager.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0103

import os, sys

SUBMODULES_LIST = ['plot']

def get_source_files(sdir):
	""" Get Python source files that are not __init__.py """
	return [
		file_name
		for file_name in os.listdir(sdir)
		if file_name.endswith('.py') and (file_name != '__init__.py')
	]


def main(argv):	# pylint: disable=R0912,R0914
	""" Processing """
	debug = True
	env = argv[0]
	# Unpack command line arguments
	if env == 'tox':
		if len(argv[1:]) == 3:
			mode_flag, pkg_dir, site_pkg_dir, submodules, module = (
				argv[1:]+[SUBMODULES_LIST, '']
			)
		else:
			mode_flag, pkg_dir, module = argv[1:]+['']
	elif env == 'shippable':
		mode_flag, pkg_dir, site_pkg_dir, submodules, module = (
			argv[1],
			os.environ['SHIPPABLE_REPO_DIR'],
			argv[2],
			SUBMODULES_LIST,
			''
		)
	elif env == 'local':
		if len(argv[1:]) == 3:
			mode_flag, pkg_dir, site_pkg_dir, submodules, module = (
				argv[1],
				argv[2],
				argv[2],
				[argv[3]],
				argv[3]
			)
		else:
			mode_flag, pkg_dir, site_pkg_dir, submodules, module = (
				argv[1],
				argv[2],
				argv[2],
				[''],
				''
			)
	# Generate .coveragerc file
	is_submodule = module in SUBMODULES_LIST
	output_file_name = os.path.join(pkg_dir, '.coveragerc_{0}'.format(env))
	if mode_flag == '1':
		lines = []
		lines.append(
			'# .coveragerc_{0} to control coverage.py during {1} runs'.format(
				env,
				env.capitalize()
			)
		)
		lines.append('[run]')
		lines.append('branch = True')
		lines.append('show_missing = True')
		start_flag = True
		# Include modules
		for file_name in [
				item
				for item in get_source_files(os.path.join(pkg_dir, 'putil'))
				if (env != 'local') or ((env == 'local') and
				   (not is_submodule) and (item == '{0}.py'.format(module)))]:
			start_flag, prefix = (
				(False, 'include = ')
				if start_flag else
				(False, 10*' ')
			)
			lines.append(
				'{0}{1}'.format(prefix, os.path.join(
					site_pkg_dir,
					'putil',
					file_name
			)))
		# Include sub-modules
		if (env != 'local') or ((env == 'local') and is_submodule):
			for submodule in submodules:
				for file_name in [
						item
						for item in get_source_files(os.path.join(
								pkg_dir,
								'putil',
								submodule))]:
					start_flag, prefix = (
						(False, 'include = ')
						if start_flag else
						(False, 10*' ')
					)
					lines.append('{0}{1}'.format(prefix, os.path.join(
						site_pkg_dir,
						'putil',
						submodule,
						file_name
					)))
		# Generate XML reports for continuous integration
		if env == 'shippable':
			lines.append('[xml]')
			lines.append('output = {0}'.format(os.path.join(
				pkg_dir,
				'shippable',
				'codecoverage',
				'coverage.xml'
			)))
		# Write file
		with open(output_file_name, 'w') as fobj:
			fobj.write('\n'.join(lines))
		# Echo file
		if debug:
			print 'File: {0}'.format(output_file_name)
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
