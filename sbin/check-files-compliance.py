#!/usr/bin/env python
# check-files-compliance.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0914

from __future__ import print_function
import glob
import os
import re
import sys


def pkg_files(extensions):
    """ Returns package files of a given extension """
    pkgdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define directories to look files in
    fdirs = [
        '',
        'sbin',
        'putil',
        os.path.join('putil', 'pcsv'),
        os.path.join('putil', 'plot'),
        'tests',
        os.path.join('tests', 'pcsv'),
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
    for fdir in fdirs:
        fdir = os.path.join(pkgdir, fdir)
        for item in glob.glob(os.path.join(fdir, '*')):
            if ((os.path.splitext(item)[1] in extensions) and
               (not os.path.isdir(item)) and (item not in efiles)):
                yield item


def content_lines(fname):
    """ Returns non-empty lines of a package """
    skip_lines = [
        '#!/bin/bash',
        '#!/usr/bin/env python',
    ]
    encoding_dribble = '\xef\xbb\xbf'
    encoded = False
    with open(fname, 'r') as fobj:
        for num, line in enumerate(fobj):
            line = line.rstrip()
            if (not num) and line.startswith(encoding_dribble):
                line = line[len(encoding_dribble):]
            coding_line = (num == 0) and (line == '# -*- coding: utf-8 -*-')
            encoded = coding_line if not encoded else encoded
            shebang_line = (num == int(encoded)) and (line in skip_lines)
            if line and (not coding_line) and (not shebang_line):
                yield line


def check_header(args=None):
    """ Check that all files have header line and copyright notice """
    editor = args[0] if args else None
    # Processing
    fdict = {
        '.py': '#',
        '.rst': '..',
        '.yml': '#',
        '.ini': '#',
        '.in': '#',
        '.sh': '#',
        '': '#',
    }
    olist = []
    errors = False
    for fname in pkg_files(list(fdict.keys())):
        basename = os.path.basename(fname)
        extension = os.path.splitext(fname)[1]
        comment = fdict[extension]
        header_lines = [
            '{0} {1}'.format(comment, basename),
            '{} Copyright (c) 2013-2015 Pablo Acosta-Serafini'.format(comment),
            '{} See LICENSE for details'.format(comment)
        ]
        iobj = enumerate(zip(content_lines(fname), header_lines))
        for num, (line, ref) in iobj:
            if line != ref:
                msg = (
                    'File {} does not have a standard header'
                    if num == 0 else
                    'File {} does not have a standard copyright notice'
                )
                olist.append(fname)
                print(msg.format(fname))
                errors = True
    if not errors:
        print('All files header compliant')
    if editor and olist:
        if editor:
            olist = sorted(list(set(olist)))
            print('\n{0} {1} &'.format(editor, ' '.join(olist)))
        sys.exit(1)


def check_pylint():
    """ Check that there are no repeated Pylint codes per file """
    rec = re.compile
    soline = rec(r'^\s*#\s*pylint\s*:\s*disable\s*=\s*([\w|\s|,]+)')
    token_regexp = rec(r'(.*)#\s*pylint\s*:\s*disable\s*=\s*([\w|\s|,]+)')
    errors = False
    for fname in pkg_files('.py'):
        with open(fname, 'r') as fobj:
            header = False
            output_lines = []
            file_tokens = []
            for num, input_line in enumerate(fobj):
                line_match = soline.match(input_line)
                token_match = token_regexp.match(input_line)
                if token_match and (not line_match):
                    if not header:
                        print('File {}'.format(fname))
                    header = errors = True
                    print('   Line {} (EOL)'.format(num+1))
                if token_match:
                    indent = token_match.groups()[0]
                    tokens = sorted(
                        token_match.groups()[1].rstrip().split(',')
                    )
                    if any([item in file_tokens for item in tokens]):
                        if not header:
                            print('File {}'.format(fname))
                        print('   Line {} (repeated)'.format(num+1))
                        header = errors = True
                    file_tokens.extend(tokens)
                    output_lines.append(
                        '{0}# pylint: disable={1}\n'.format(
                            indent, ','.join(tokens)
                        )
                    )
                else:
                    output_lines.append(input_line)
        with open(fname, 'w') as fobj:
            for output_line in output_lines:
                fobj.write(output_line)
    if not errors:
        print('All files Pylint compliant')


if __name__ == "__main__":
    check_header(sys.argv[1:] if sys.argv[1:] else None)
    check_pylint()
