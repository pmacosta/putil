#!/usr/bin/env python
# compare_images.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
from __future__ import print_function
import argparse
import os
import sys
# PyPI imports
import numpy
import scipy
import scipy.misc
# Putil imports
import sbin.functions


###
# Functions
###
def compare_images(fname1, fname2, no_print=True, imgtol=1e-3):
    """ Compare two images by calculating Manhattan and Zero norms """
    # Source: http://stackoverflow.com/questions/189943/
    # how-can-i-quantify-difference-between-two-images
    for item in (fname1, fname2):
        if not os.path.exists(item):
            return False
    img1 = scipy.misc.imread(fname1).astype(float)
    img2 = scipy.misc.imread(fname2).astype(float)
    if img1.size != img2.size:
        m_norm, z_norm = 2*[2*imgtol]
    else:
        # Element-wise for Scipy arrays
        diff = img1-img2
        # Manhattan norm
        m_norm = scipy.sum(numpy.abs(diff))
        # Zero norm
        z_norm = scipy.linalg.norm(diff.ravel(), 0)
    result = bool((m_norm < imgtol) and (z_norm < imgtol))
    if not no_print:
        print(
            'Image 1: {0}, Image 2: {1} -> ({2}, {3}) [{4}]'.format(
                fname1, fname2, m_norm, z_norm, result
            )
        )
    return result


def main(no_print, img1, img2):
    """ Compare two images """
    for item in [img1, img2]:
        if not os.path.exists(item):
            raise IOError('File {0} could not be found'.format(item))
    img1 = os.path.abspath(img1)
    img2 = os.path.abspath(img2)
    result = compare_images(img1, img2)
    if not no_print:
        msg = 'Images are {0}'.format('identical' if result else 'different')
        print('Image 1: {0}'.format(img1))
        print('Image 2: {0}'.format(img2))
        print(sbin.functions.pcolor(msg, 'green' if result else 'red'))
    sys.exit(1 if not result else 0)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='Compare images'
    )
    PARSER.add_argument(
        '-q', '--quiet',
        help='suppress messages',
        action="store_true",
        default=False
    )
    PARSER.add_argument('file1', help='File 1 to check', nargs=1)
    PARSER.add_argument('file2', help='File 2 to check', nargs=1)
    ARGS = PARSER.parse_args()
    main(ARGS.quiet, ARGS.file1[0], ARGS.file2[0])
