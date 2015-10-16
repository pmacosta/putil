#!/usr/bin/env python
# build_wheel_cache.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

from __future__ import print_function
import os
import subprocess


###
# Functions
###
# This is a sub-set of the putil.misc.pcolor function, repeated here because
# this script may be run right after cloning and putil module may not be in
# the Python search path
def _pcolor(text, color, indent=0):
    esc_dict = {
        'black':30, 'red':31, 'green':32, 'yellow':33, 'blue':34, 'magenta':35,
        'cyan':36, 'white':37, 'none':-1
    }
    if esc_dict[color] != -1:
        return (
            '\033[{color_code}m{indent}{text}\033[0m'.format(
                color_code=esc_dict[color],
                indent=' '*indent,
                text=text
            )
        )
    return '{indent}{text}'.format(indent=' '*indent, text=text)


def build_wheel_cache():
    """ Build pip wheel cache """
    pkg_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    fname = os.path.join(pkg_dir, 'requirements.txt')
    with open(fname, 'r') as fobj:
        lines = sorted(
            [
                item.strip() for item in fobj.readlines()
                if not item.startswith('#')
            ]
        )
    lines.append('pylint>=1.3,<1.4')
    lines.append('pylint>=1.4')
    lines.append('sphinx>=1.2.3')
    lines.append('sphinxcontrib-inlinesyntaxhighlight>=0.2')
    for line in lines:
        print(_pcolor('Building {0} wheel cache'.format(line), 'cyan'))
        pobj = subprocess.Popen(
            ['pip', 'wheel', line],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, _ = pobj.communicate()
        print(stdout)


if __name__ == '__main__':
    build_wheel_cache()
