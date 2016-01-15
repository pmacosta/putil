#!/usr/bin/env python
# compare_images.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

from __future__ import print_function
import argparse
import os
import sys
import numpy
import scipy
import scipy.misc


###
# Global variables
###
IMGTOL = 1e-3

###
# Functions
###
def compare_images(image_file_name1, image_file_name2, no_print=True):
    """ Compare two images by calculating Manhattan and Zero norms """
    # Source: http://stackoverflow.com/questions/189943/
    # how-can-i-quantify-difference-between-two-images
    img1 = scipy.misc.imread(image_file_name1).astype(float)
    img2 = scipy.misc.imread(image_file_name2).astype(float)
    if img1.size != img2.size:
        m_norm, z_norm = 2*[2*IMGTOL]
    else:
        # Element-wise for Scipy arrays
        diff = img1-img2
        # Manhattan norm
        m_norm = scipy.sum(numpy.abs(diff))
        # Zero norm
        z_norm = scipy.linalg.norm(diff.ravel(), 0)
    result = bool((m_norm < IMGTOL) and (z_norm < IMGTOL))
    if not no_print:
        print(
            'Image 1: {0}, Image 2: {1} -> ({2}, {3}) [{4}]'.format(
                image_file_name1, image_file_name2, m_norm, z_norm, result
            )
        )
    return (m_norm, z_norm)


def main(no_print, img1, img2):
    """ Compare two images """
    if not os.path.exists(img1):
        raise IOError('File {0} could not be found'.format(img1))
    if not os.path.exists(img2):
        raise IOError('File {0} could not be found'.format(img2))
    img1 = os.path.abspath(img1)
    img2 = os.path.abspath(img2)
    metrics = compare_images(img1, img2)
    result = (metrics[0] < IMGTOL) and (metrics[1] < IMGTOL)
    msg = (
        'Image 1: {0}\n'
        'Image 2: {1}\n'
        'Images are {2}'.format(
            img1, img2, 'identical' if result else 'different'
        )
    )
    if not no_print:
        print(msg)
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
