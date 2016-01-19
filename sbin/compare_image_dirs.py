#!/usr/bin/env python
# compare_image_dirs.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
from __future__ import print_function
import argparse
import glob
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


def main(no_print, dir1, dir2):
    """ Compare two images """
    # pylint: disable=R0912
    for item in [dir1, dir2]:
        if not os.path.exists(item):
            raise IOError('Directory {0} could not be found'.format(item))
    dir1_images = set(
        [
            os.path.basename(item)
            for item in glob.glob(os.path.join(dir1, '*.png'))
        ]
    )
    dir2_images = set(
        [
            os.path.basename(item)
            for item in glob.glob(os.path.join(dir2, '*.png'))
        ]
    )
    yes_list = []
    no_list = []
    dir1_list = sorted(list(dir1_images-dir2_images))
    dir2_list = sorted(list(dir2_images-dir1_images))
    global_result = bool((not dir1_list) and (not dir2_list))
    for image in sorted(list(dir1_images & dir2_images)):
        result = compare_images(
            os.path.join(dir1, image), os.path.join(dir2, image)
        )
        if (not result) and (not no_print):
            no_list.append(image)
            global_result = False
        elif not no_print:
            yes_list.append(image)
    print('Files only in {0}'.format(dir1))
    if dir1_list:
        for item in dir1_list:
            print('   {0}'.format(item))
    else:
        print('   None')
    print('Files only in {0}'.format(dir2))
    if dir2_list:
        for item in dir2_list:
            print('   {0}'.format(item))
    else:
        print('   None')
    print('Matching files')
    if yes_list:
        for item in yes_list:
            print('   {0}'.format(item))
    else:
        print('   None')
    print('Mismatched files')
    if no_list:
        for item in no_list:
            print('   {0}'.format(item))
    else:
        print('   None')
    if global_result and (not no_print):
        print(sbin.functions.pcolor('Directories ARE equal', 'green'))
    elif (not global_result) and (not no_print):
        print(sbin.functions.pcolor('Directories ARE NOT equal', 'red'))
    sys.exit(1 if not global_result else 0)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='Compare image directories'
    )
    PARSER.add_argument(
        '-q', '--quiet',
        help='suppress messages',
        action="store_true",
        default=False
    )
    PARSER.add_argument('dir1', help='First directory to compare', nargs=1)
    PARSER.add_argument('dir2', help='Second directory to compare', nargs=1)
    ARGS = PARSER.parse_args()
    main(ARGS.quiet, ARGS.dir1[0], ARGS.dir2[0])
