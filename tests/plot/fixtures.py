# fixtures.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E0611,W0621

# Standard library imports
from __future__ import print_function
import os
import shutil
import subprocess
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
def compare_images(image_file_name1, image_file_name2, no_print=True):
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
    result = bool((m_norm < IMGTOL) and (z_norm < IMGTOL))
    if not no_print:
        print(
            'Image 1: {0}, Image 2: {1} -> ({2}, {3}) [{4}]'.format(
                image_file_name1, image_file_name2, m_norm, z_norm, result
            )
        )
    return result


def compare_image_set(tmpdir, images_dict_list, section):
    """ Compare image sets """
    subdir = 'test_images_{0}'.format(section)
    tmpdir.mkdir(subdir)
    global_result = True
    for images_dict in images_dict_list:
        ref_file_name_list = images_dict['ref_fname']
        test_file_name = images_dict['test_fname']
        print('Reference images:')
        for ref_file_name in ref_file_name_list:
            print('   file://{0}'.format(
                    os.path.realpath(ref_file_name)
                )
            )
        print('Actual image:')
        print('   file://{0}'.format(
                os.path.realpath(test_file_name)
            )
        )
        partial_result = []
        for ref_file_name in ref_file_name_list:
            partial_result.append(
                compare_images(ref_file_name, test_file_name)
            )
        result = any(partial_result)
        global_result = global_result and partial_result
        if not result:
            print('Images do not match')
            export_image(test_file_name)
        print('')
    if global_result:
        try:
            tmpdir.remove(subdir)
        except OSError: # pragma: no cover
            pass
    return global_result


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


def export_image(fname, method=True):
    tdir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
    artifact_dir = os.path.join(tdir, 'artifacts')
    if not os.path.exists(artifact_dir):
        os.makedirs(artifact_dir)
    if method:
        src = fname
        dst = os.path.join(artifact_dir, os.path.basename(fname))
        shutil.copyfile(src, dst)
    else:
        if os.environ.get('APPVEYOR', None):
            proc = subprocess.Popen(
                ['appveyor', 'PushArtifact', os.path.realpath(fname)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            proc.communicate()
        elif os.environ.get('TRAVIS', None):
            # If only a few binary files need to be exported a hex dump works,
            # otherwise the log can grow past 4MB and the process is terminated
            # by Travis
            proc = subprocess.Popen(
                [
                    os.path.join(tdir, 'sbin', 'png-to-console.sh'),
                    os.path.realpath(fname)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            stdout, _ = proc.communicate()
            print(stdout)
