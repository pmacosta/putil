# fixtures.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E0611,W0621

# PyPI imports
import numpy
import pytest
import scipy
from scipy.misc import imread
# Putil imports
import putil.plot


###
# Global variables
###
IMGTOL = 1e-3

###
# Fixtures
###
def compare_images(image_file_name1, image_file_name2):
    """ Compare two images by calculating Manhattan and Zero norms """
    # Source: http://stackoverflow.com/questions/189943/
    # how-can-i-quantify-difference-between-two-images
    img1 = imread(image_file_name1).astype(float)
    img2 = imread(image_file_name2).astype(float)
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


@pytest.fixture
def default_source():
    """
    Provides a default source to be used in testing the
    putil.plot.Series class
    """
    return putil.plot.BasicSource(
        indep_var=numpy.array([5, 6, 7, 8]),
        dep_var=numpy.array([0, -10, 5, 4])
    )


@pytest.fixture
def default_series(default_source):
    """
    Provides a default series object to be used in testing the
    putil.plot.Panel class
    """
    return putil.plot.Series(
        data_source=default_source,
        label='test series'
    )


@pytest.fixture
def default_panel(default_series):
    """
    Provides a default panel object to be used in testing the
    putil.plot.Figure class
    """
    return putil.plot.Panel(
        series=default_series,
        primary_axis_label='Primary axis',
        primary_axis_units='A',
        secondary_axis_label='Secondary axis',
        secondary_axis_units='B'
    )
