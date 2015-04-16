#!/usr/bin/env python
# pylint-cleaner.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0103

import fnmatch
import os
import re

def main():
	""" Processing """
	# pylint: disable=R0914
	source_files = []
	for sdir in ['putil', 'docs', 'tests']:
		for root, _, filenames in os.walk(sdir):
			for filename in fnmatch.filter(filenames, '*.py'):
				source_files.append(os.path.join(root, filename))
	soline = re.compile(r'^\s*#\s*pylint\s*:\s*disable\s*=\s*([\w|\s|,]+)')
	token_regexp = re.compile(r'(.*)#\s*pylint\s*:\s*disable\s*=\s*([\w|\s|,]+)')
	for source_file in source_files:
		with open(source_file, 'r') as fname:
			input_lines = fname.readlines()
		header = False
		output_lines = []
		file_tokens = []
		for num, input_line in enumerate(input_lines):
			line_match = soline.match(input_line)
			token_match = token_regexp.match(input_line)
			if token_match and (not line_match):
				if not header:
					header = True
					print 'File {0}'.format(source_file)
				print '   Line {0} (EOL)'.format(num+1)
			if token_match:
				indent = token_match.groups()[0]
				tokens = sorted(token_match.groups()[1].rstrip().split(','))
				if any([item in file_tokens for item in tokens]):
					if not header:
						header = True
						print 'File {0}'.format(source_file)
					print '   Line {0} (repeated)'.format(num+1)
				file_tokens.extend(tokens)
				output_lines.append(
					'{0}# pylint: disable={1}\n'.format(indent, ','.join(tokens))
				)
			else:
				output_lines.append(input_line)
		with open(source_file, 'w') as fname:
			for output_line in output_lines:
				fname.write(output_line)

if __name__ == '__main__':
	main()
