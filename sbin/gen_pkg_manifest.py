#!/usr/bin/env python
# gen_pkg_manifest.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

from __future__ import print_function
import sys

import sbin.functions


if __name__ == '__main__':
    print('Generating MANIFEST.in file')
    sbin.functions.gen_manifest('wheel' in sys.argv)
