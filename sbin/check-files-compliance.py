#!/usr/bin/env python
# check-files-compliance.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0103,R0914

import glob, os, sys


def main(args=None):
	""" Processing """
	editor = args[0] if args else None
	pkgdir = os.path.dirname(os.path.dirname(__file__))
	# Define comment marker for all file extensions that need to be checked
	fdict = {
		'.py': '#',
		'.rst': '..',
		'.yml': '#',
		'.ini': '#',
		'.in': '#',
		'.sh': '#',
		'': '#',
	}
	# Define directories to look files in
	fdirs = [
		'',
		'sbin',
		'putil',
		os.path.join('putil', 'plot'),
		'tests',
		os.path.join('tests', 'plot'),
		os.path.join('tests', 'support'),
		'docs',
		os.path.join('docs', 'support')
	]
	# Defines files to be excluded from check
	efiles = [
		os.path.join(pkgdir, 'tags'),
		os.path.join(pkgdir, 'LICENSE'),
		os.path.join(pkgdir, 'docs', 'conf.py'),
		os.path.join(pkgdir, 'docs', 'Makefile'),
	]
	# Processing
	olist = []
	errors = False
	for fdir in fdirs:
		flist = [
			item
			for item in glob.glob(os.path.join(pkgdir, fdir, '*'))
			if os.path.splitext(item)[1] in fdict and
			   (not os.path.isdir(item)) and (item not in efiles)
		]
		for fname in flist:
			# Read lines
			with open(fname, 'r') as fobj:
				flines = fobj.readlines()
			flines = [item.rstrip() for item in flines]
			if flines and (flines != ['']):
				ext = os.path.splitext(fname)[1]
				name_line = '{0} {1}'.format(fdict[ext], os.path.basename(fname))
				# Remove shebang line (if needed)
				if ((ext in ['', '.sh']) and
				   (flines[0] in ['#!/bin/bash', '\xef\xbb\xbf#!/bin/bash'])):
					flines = flines[1:]
				elif ((ext in ['.py']) and
					 (flines[0] in [
						 '#!/usr/bin/env python',
						 '\xef\xbb\xbf#!/usr/bin/env python'])):
					flines = flines[1:]
				# Remove coding line (if needed)
				if (ext in ['.py']) and (flines[0] == '# -*- coding: utf-8 -*-'):
					flines = flines[1:]
				if ((flines[0] != name_line) and
				   (flines[0] != '\xef\xbb\xbf{0}'.format(name_line))):
					olist.append(fname)
					print 'File {0} does not have a standard header'.format(fname)
					errors = True
				copyright_lines = [
					'{0} Copyright (c) 2013-2015 '
					'Pablo Acosta-Serafini'.format(fdict[ext]),
					'{0} See LICENSE for details'.format(fdict[ext])
				]
				if flines[1:3] != copyright_lines:
					olist.append(fname)
					print ('File {0} does not have a standard '
						  'copyright notice'.format(fname))
					errors = True
	if not errors:
		print 'All files compliant'
	if editor and olist:
		if editor:
			olist = sorted(list(set(olist)))
			print '\n{0} {1} &'.format(editor, ' '.join(olist))
		sys.exit(1)


if __name__ == "__main__":
	main(sys.argv[1:] if sys.argv[1:] else None)
