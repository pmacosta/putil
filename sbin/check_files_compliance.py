#!/usr/bin/env python
# check_files_compliance.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0912,R0914

# Standard library imports
from __future__ import print_function
import argparse
import datetime
import glob
import os
import re
import subprocess
import sys
# Putil imports
if sys.hexversion < 0x03000000:
    from putil.compat2 import _readlines
else:
    from putil.compat3 import _readlines


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
    return result[0] if result else None


def load_aspell_whitelist():
    """ Load words that are excluded from Aspell output """
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    efile = os.path.join(pkg_dir, 'data', 'aspell-whitelist')
    words = [item.strip() for item in _readlines(efile) if item.strip()]
    return sorted(list(set(words)))


def pkg_files(sdir, mdir, files, extensions):
    """ Returns package files of a given extension """
    pkgdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = [os.path.join(pkgdir, item) for item in files]
    # Define directories to look files in
    fdirs = [
        os.path.join(mdir, ''),
        os.path.join(mdir, 'sbin'),
        os.path.join(sdir, 'putil'),
        os.path.join(sdir, 'putil', 'pcsv'),
        os.path.join(sdir, 'putil', 'plot'),
        os.path.join(mdir, 'tests'),
        os.path.join(mdir, 'tests', 'pcsv'),
        os.path.join(mdir, 'tests', 'plot'),
        os.path.join(mdir, 'tests', 'support'),
        os.path.join(mdir, 'docs'),
        os.path.join(mdir, 'docs', 'support')
    ]
    # Defines files to be excluded from check
    efiles = [
        os.path.join(mdir, 'tags'),
        os.path.join(mdir, 'LICENSE'),
        os.path.join(mdir, 'setup.cfg'),
        os.path.join(mdir, 'docs', 'conf.py'),
        os.path.join(mdir, 'docs', 'Makefile'),
        os.path.join(mdir, 'sbin', 'aspell-whitelist'),
        os.path.join(mdir, 'sbin', 'install.ps1'),
        os.path.join(mdir, 'sbin', 'run_with_env.cmd'),
        os.path.join(mdir, 'sbin', 'build_matplotlib_dep.cmd'),
        os.path.join(mdir, 'sbin', 'dropbox_uploader.sh'),
    ]
    # Processing
    for fdir in fdirs:
        for item in glob.glob(os.path.join(fdir, '*')):
            if ((os.path.splitext(item)[1] in extensions) and
               (not os.path.isdir(item)) and (item not in efiles)):
                if (not files) or (files and (item in files)):
                    yield item


def content_lines(fname, comment='#'):
    """ Returns non-empty lines of a package """
    skip_lines = [
        '#!/bin/bash',
        '#!/usr/bin/env bash',
        '#!/usr/bin/env python',
    ]
    encoding_dribble = '\xef\xbb\xbf'
    encoded = False
    cregexp = re.compile(r'.*{0} -\*- coding: utf-8 -\*-\s*'.format(comment))
    with open(fname, 'r') as fobj:
        for num, line in enumerate(fobj):
            line = line.rstrip()
            if (not num) and line.startswith(encoding_dribble):
                line = line[len(encoding_dribble):]
            coding_line = (num == 0) and (cregexp.match(line) is not None)
            encoded = coding_line if not encoded else encoded
            shebang_line = (num == int(encoded)) and (line in skip_lines)
            if line and (not coding_line) and (not shebang_line):
                yield line


def check_header(sdir, mdir, files, no_print=False):
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
    year = datetime.datetime.now().year
    for fname in pkg_files(sdir, mdir, files, list(fdict.keys())):
        basename = os.path.basename(fname)
        extension = os.path.splitext(fname)[1]
        comment = fdict[extension]
        header_lines = [
            '{0} {1}'.format(comment, basename),
            (
                '{0} Copyright (c) 2013-{1} '
                'Pablo Acosta-Serafini'.format(comment, year)
            ),
            '{0} See LICENSE for details'.format(comment)
        ]
        iobj = enumerate(zip(content_lines(fname, comment), header_lines))
        wheader = False
        for num, (line, ref) in iobj:
            if line != ref:
                print(line)
                print(ref)
                msg = (
                    'File {0} does not have a standard header'
                    if num == 0 else
                    'File {0} does not have a standard copyright notice'
                )
                errors = True
                if ((not no_print) and
                   ((num == 0) or ((num > 0) and (not wheader)))):
                    print(msg.format(fname))
                olist.append(fname)
                wheader = num > 0
    if (not errors) and (not no_print):
        print('All files header compliant')
    return errors


def check_pylint(sdir, mdir, files, no_print=False):
    """ Check that there are no repeated Pylint codes per file """
    rec = re.compile
    soline = rec(r'(^\s*)#\s*pylint\s*:\s*disable\s*=\s*([\w|\s|,]+)\s*')
    # Regular expression to get a Pylint disable directive but only
    # if it is not in a string
    template = r'#\s*pylint:\s*disable\s*=\s*([\w|\s|\s*,\s*]+)'
    quoted_eol = rec(r'(.*)(\'|")\s*'+template+r'\s*\2\s*')
    eol = rec(r'(.*)\s*'+template+r'\s*')
    errors = False
    for fname in pkg_files(sdir, mdir, files, '.py'):
        with open(fname, 'r') as fobj:
            header = False
            output_lines = []
            file_tokens = []
            for num, input_line in enumerate(fobj):
                line_match = soline.match(input_line)
                quoted_eol_match = quoted_eol.match(
                    input_line.replace('\\n', '\n').replace('\\r', '\r')
                )
                eol_match = eol.match(input_line)
                if eol_match and (not quoted_eol_match) and (not line_match):
                    if (not header) and (not no_print):
                        print('File {0}'.format(fname))
                    header = errors = True
                    if not no_print:
                        print('   Line {0} (EOL)'.format(num+1))
                if line_match:
                    indent = line_match.groups()[0]
                    tokens = sorted(
                        line_match.groups()[1].rstrip().split(',')
                    )
                    if any([item in file_tokens for item in tokens]):
                        if (not header) and (not no_print):
                            print('File {0}'.format(fname))
                        if not no_print:
                            print('   Line {0} (repeated)'.format(num+1))
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


def check_aspell(sdir, mdir, files, no_print=False):
    """ Check files word spelling """
    errors = False
    if which('aspell'):
        excluded_words = load_aspell_whitelist()
        for fname in pkg_files(sdir, mdir, files, ['.py', '.rst']):
            pobj = subprocess.Popen(
                ['cat', fname],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            lines, _ = pobj.communicate()
            pobj = subprocess.Popen(
                ['aspell', '--lang=en', 'list'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            raw_words, _ = pobj.communicate(lines)
            raw_words = [item for item in raw_words.decode().split('\n')]
            raw_words = sorted(list(set(raw_words)))
            raw_words = [item.strip() for item in raw_words]
            words = [
                item
                for item in raw_words
                if item and (item not in excluded_words)
            ]
            if words:
                errors = True
                if not no_print:
                    print('File {0}'.format(fname))
                    print('\n'.join(words))
        if (not errors) and (not no_print):
            print('All files free of typos')
    else:
        print('Files spell check omitted, aspell could not be found')
    return errors


if __name__ == "__main__":
    PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PARSER = argparse.ArgumentParser(
        description='Perform various checks on package files'
    )
    PARSER.add_argument(
        '-s', '--spell', help='check files spelling', action="store_true"
    )
    PARSER.add_argument(
        '-t', '--top', help='check files top (headers)', action="store_true"
    )
    PARSER.add_argument(
        '-p', '--pylint', help='check files PyLint lines', action="store_true"
    )
    PARSER.add_argument(
        '-q', '--quiet', help='suppress messages', action="store_true"
    )
    PARSER.add_argument(
        '-d', '--source-dir', help='source files directory (default ../putil)',
        nargs=1, default=PKG_DIR
    )
    PARSER.add_argument(
        '-m', '--misc-dir', help='miscellaneous files directory (default ../)',
        nargs=1, default=PKG_DIR
    )
    PARSER.add_argument('files', help='Files to check', nargs='*')
    ARGS = PARSER.parse_args()
    SOURCE_DIR = (
        ARGS.source_dir[0]
        if isinstance(ARGS.source_dir, list)
        else ARGS.source_dir
    )
    MISC_DIR = (
        ARGS.misc_dir[0]
        if isinstance(ARGS.misc_dir, list)
        else ARGS.misc_dir
    )
    TERRORS = False
    if not ARGS.quiet:
        print('Source directory: {0}'.format(SOURCE_DIR))
        print('Miscellaneous directory: {0}'.format(MISC_DIR))
    if ARGS.spell:
        TERRORS = TERRORS or check_aspell(
            SOURCE_DIR, MISC_DIR, ARGS.files, ARGS.quiet
        )
    if ARGS.top:
        TERRORS = TERRORS or check_header(
            SOURCE_DIR, MISC_DIR, ARGS.files, ARGS.quiet
        )
    if ARGS.pylint:
        TERRORS = TERRORS or check_pylint(
            SOURCE_DIR, MISC_DIR, ARGS.files, ARGS.quiet
        )
    if TERRORS:
        sys.exit(1)
