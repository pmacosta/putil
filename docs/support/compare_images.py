#!/usr/bin/env python
# compare_images.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

from __future__ import print_function
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
def compare_images(image_file_name1, image_file_name2):
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
    return (m_norm, z_norm)


def main(img1, img2):
    """ Compare two images """
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
    print(msg)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
