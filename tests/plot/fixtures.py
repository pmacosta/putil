# fixtures.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E0611,W0621

import numpy
import scipy
import pytest
from scipy.misc import imread

import putil.plot


IMGTOL = 1e-3
def compare_images(image_file_name1, image_file_name2):
    """ Compare two images by calculating Manhattan and Zero norms """
    # Source: http://stackoverflow.com/questions/189943/
    # how-can-i-quantify-difference-between-two-images
    img1 = imread(image_file_name1).astype(float)
    img2 = imread(image_file_name2).astype(float)
    if img1.size != img2.size:
        m_norm, z_norm = 2*[2*IMGTOL]
    else:
        diff = img1 - img2                              # element-wise for scipy arrays
        m_norm = scipy.sum(numpy.abs(diff))             # Manhattan norm
        z_norm = scipy.linalg.norm(diff.ravel(), 0)     # Zero norm
    return (m_norm, z_norm)


@pytest.fixture
def default_source():
    """
    Provides a default source to be used in testing the
    putil.plot.Series() class
    """
    return putil.plot.BasicSource(
        indep_var=numpy.array([5, 6, 7, 8]),
        dep_var=numpy.array([0, -10, 5, 4])
    )


@pytest.fixture
def default_series(default_source):
    """
    Provides a default series object to be used in testing the
    putil.plot.Panel() class
    """
    return putil.plot.Series(
        data_source=default_source,
        label='test series'
    )


@pytest.fixture
def default_panel(default_series):
    """
    Provides a default panel object to be used in testing the
    putil.plot.Figure() class
    """
    return putil.plot.Panel(
        series=default_series,
        primary_axis_label='Primary axis',
        primary_axis_units='A',
        secondary_axis_label='Secondary axis',
        secondary_axis_units='B'
    )
