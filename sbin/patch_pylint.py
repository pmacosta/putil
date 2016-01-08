#!/usr/bin/env python
# patch_pylint.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import os
import sys


###
# Functions
###
def main(pkg_dir):
    """ Processing """
    fname = os.path.join(pkg_dir, 'astroid', 'brain', 'pysix_moves.py')
    ret = []
    with open(fname, 'r') as fobj:
        lines = fobj.readlines()
    for num, line in enumerate([item.rstrip() for item in lines]):
        if num == 241:
            ret.append('    {0}')
        else:
            ret.append(line)
    with open(fname, 'w') as fobj:
        fobj.write(os.linesep.join(ret))


if __name__ == '__main__':
    main(sys.argv[1])
