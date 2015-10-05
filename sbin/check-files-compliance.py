#!/usr/bin/env python
# check-files-compliance.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0914

from __future__ import print_function
import argparse
import glob
import os
import re
import subprocess
import sys


###
# Functions
###
def which(name):
    """ Search PATH for executable files with the given name """
    # Inspired by https://twistedmatrix.com/trac/browser/tags/releases/
    # twisted-8.2.0/twisted/python/procutils.py
    # pylint: disable=W0141
    result = []
    path = os.environ.get('PATH', None)
    if path is None:
        return []
    for pdir in os.environ.get('PATH', '').split(os.pathsep):
        fname = os.path.join(pdir, name)
        if os.path.isfile(fname) and os.access(fname, os.X_OK):
            result.append(fname)
    return result[0]


def load_excluded_words():
    """ Load words that are excluded from Aspell output """
    pkgdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    efile = os.path.join(pkgdir, 'exclude.aspell')
    with open(efile, 'r') as fobj:
        words = fobj.readlines()
    words = [item.strip() for item in words if item.strip()]
    return sorted(list(set(words)))


def pkg_files(files, extensions):
    """ Returns package files of a given extension """
    pkgdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = [os.path.join(pkgdir, item) for item in files]
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
                if (not files) or (files and (item in files)):
                    yield item


def content_lines(fname, comment='#'):
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
            coding_line = (
                (num == 0)
                and
                (line == '{} -*- coding: utf-8 -*-'.format(comment))
            )
            encoded = coding_line if not encoded else encoded
            shebang_line = (num == int(encoded)) and (line in skip_lines)
            if line and (not coding_line) and (not shebang_line):
                yield line


def check_header(files, no_print=False):
    """ Check that all files have header line and copyright notice """
    # Processing
    fdict = {
        '.py': '#',
        '.rst': '..',
        '.yml': '#',
        '.ini': '#',
        '.in': '#',
        '.sh': '#',
        '.cfg': '#',
        '': '#',
    }
    olist = []
    errors = False
    for fname in pkg_files(files, list(fdict.keys())):
        basename = os.path.basename(fname)
        extension = os.path.splitext(fname)[1]
        comment = fdict[extension]
        header_lines = [
            '{0} {1}'.format(comment, basename),
            '{} Copyright (c) 2013-2015 Pablo Acosta-Serafini'.format(comment),
            '{} See LICENSE for details'.format(comment)
        ]
        iobj = enumerate(zip(content_lines(fname, comment), header_lines))
        for num, (line, ref) in iobj:
            if line != ref:
                msg = (
                    'File {} does not have a standard header'
                    if num == 0 else
                    'File {} does not have a standard copyright notice'
                )
                olist.append(fname)
                errors = True
                if not no_print:
                    print(msg.format(fname))
    if (not errors) and (not no_print):
        print('All files header compliant')
    return errors


def check_pylint(files, no_print=False):
    """ Check that there are no repeated Pylint codes per file """
    rec = re.compile
    soline = rec(r'^\s*#\s*pylint\s*:\s*disable\s*=\s*([\w|\s|,]+)')
    token_regexp = rec(r'(.*)#\s*pylint\s*:\s*disable\s*=\s*([\w|\s|,]+)')
    errors = False
    for fname in pkg_files(files, '.py'):
        with open(fname, 'r') as fobj:
            header = False
            output_lines = []
            file_tokens = []
            for num, input_line in enumerate(fobj):
                line_match = soline.match(input_line)
                token_match = token_regexp.match(input_line)
                if token_match and (not line_match):
                    if (not header) and (not no_print):
                        print('File {}'.format(fname))
                    header = errors = True
                    if not no_print:
                        print('   Line {} (EOL)'.format(num+1))
                if token_match:
                    indent = token_match.groups()[0]
                    tokens = sorted(
                        token_match.groups()[1].rstrip().split(',')
                    )
                    if any([item in file_tokens for item in tokens]):
                        if (not header) and (not no_print):
                            print('File {}'.format(fname))
                        if not no_print:
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
    if (not errors) and (not no_print):
        print('All files Pylint compliant')
    return errors


def check_aspell(files, no_print=False):
    """ Check files word spelling """
    excluded_words = load_excluded_words()
    errors = False
    for fname in pkg_files(files, ['.py', '.rst']):
        lines = subprocess.check_output(['cat', fname])
        pobj = subprocess.Popen(
            ['aspell', '--lang=en', 'list'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        raw_words, _ = pobj.communicate(lines)
        raw_words = sorted(list(set(raw_words.split('\n'))))
        raw_words = [item.strip() for item in raw_words]
        words = [
            item
            for item in raw_words
            if item and (item not in excluded_words)
        ]
        if words:
            errors = True
            if not no_print:
                print('File {}'.format(fname))
                print('\n'.join(words))
    if (not errors) and (not no_print):
        print('All files free of typos')
    return errors


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description='Perform various checks on package files'
    )
    PARSER.add_argument(
        '--aspell', help='Check files spelling', action="store_true"
    )
    PARSER.add_argument(
        '--header', help='Check files headers', action="store_true"
    )
    PARSER.add_argument(
        '--pylint', help='Check files PyLint lines', action="store_true"
    )
    PARSER.add_argument(
        '--quiet', help='Suppress messages', action="store_true"
    )
    PARSER.add_argument('files', help='Files to check', nargs='*')
    ARGS = PARSER.parse_args()
    TERRORS = False
    if ARGS.aspell:
        TERRORS = TERRORS or check_aspell(ARGS.files, ARGS.quiet)
    if ARGS.header:
        TERRORS = TERRORS or check_header(ARGS.files, ARGS.quiet)
    if ARGS.pylint:
        TERRORS = TERRORS or check_pylint(ARGS.files, ARGS.quiet)
    if TERRORS:
        sys.exit(1)
