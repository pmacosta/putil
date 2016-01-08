#!/usr/bin/env python
# format_commit_msg.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E1101,E1103,F0401,W0212

# Standard library imports
from __future__ import print_function
import re
import sys
import textwrap


###
# Global variables
###
LINE_WIDTH = 72


###
# Functions
###
def format_msg():
    """ Wrap commit message in 72-character lines """
    msg = sys.stdin.read()
    bullet_regexp = re.compile(r'^(\s*[\*|\+]\s+)\W*')
    if len(msg) > 0:
        lines = msg.split('\n')
        olines = []
        stack = [0]
        for line in [item.rstrip() for item in lines]:
            if not line:
                olines.append(line)
            else:
                robj = bullet_regexp.match(line)
                if robj:
                    indent = len(robj.group(1))
                    while indent <= stack[-1]:
                        stack.pop()
                    stack.append(indent)
                    wobj = textwrap.wrap(
                        line,
                        width=LINE_WIDTH,
                        subsequent_indent=' '*indent
                    )
                else:
                    stack = [0]
                    wobj = textwrap.wrap(
                        line,
                        width=LINE_WIDTH,
                    )
                for item in wobj:
                    olines.append(item)
        ret = '\n'.join(olines)
        print(ret)


if __name__ == '__main__':
    format_msg()
