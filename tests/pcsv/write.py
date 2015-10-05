# write.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,F0401,R0201,R0915,W0232

import os
import pytest
import sys
import tempfile
if sys.version_info.major == 2:
    import mock
else:
    import unittest.mock as mock

import putil.pcsv
import putil.test
if sys.version_info.major == 2:
    from putil.compat2 import _read
else:
    from putil.compat3 import _read


###
# Test functions
###
@pytest.mark.write
def test_write_function_exceptions():
    """
    Test if write() function raises the right exceptions when its arguments
    are of the wrong type or are badly specified
    """
    some_fname = os.path.join(os.path.abspath(os.sep), 'some', 'file')
    def mock_make_dir_io(fname):
        raise IOError(
            'File {0} could not be created'.format(fname),
            'Permission denied'
        )
    def mock_make_dir_os(fname):
        raise OSError(
            'File {0} could not be created'.format(fname),
            'Permission denied'
        )
    some_fname = os.path.join(os.path.abspath(os.sep), 'some', 'file')
    putil.test.assert_exception(
        putil.pcsv.write,
        {'fname':5, 'data':[['Col1', 'Col2'], [1, 2]]},
        RuntimeError,
        'Argument `fname` is not valid'
    )
    putil.test.assert_exception(
        putil.pcsv.write,
        {
            'fname':some_fname,
            'data':[['Col1', 'Col2'], [1, 2]],
            'append':'a'
        },
        RuntimeError,
        'Argument `append` is not valid'
    )
    with mock.patch('putil.misc.make_dir', side_effect=mock_make_dir_io):
        putil.test.assert_exception(
            putil.pcsv.write,
            {'fname':some_fname, 'data':[['Col1', 'Col2'], [1, 2]]},
            OSError,
            'File {0} could not be created: Permission denied'.format(
                some_fname
            )
        )
    with mock.patch('putil.misc.make_dir', side_effect=mock_make_dir_os):
        putil.test.assert_exception(
            putil.pcsv.write,
            {'fname':some_fname, 'data':[['Col1', 'Col2'], [1, 2]]},
            OSError,
            'File {0} could not be created: Permission denied'.format(
                some_fname
            )
        )
    putil.test.assert_exception(
        putil.pcsv.write,
        {'fname':'test.csv', 'data':[True, False]},
        RuntimeError,
        'Argument `data` is not valid'
    )
    putil.test.assert_exception(
        putil.pcsv.write,
        {'fname':'test.csv', 'data':[[]]},
        ValueError,
        'There is no data to save to file'
    )


def test_write_function_works():
    """ Test if write() method behaves properly """
    with tempfile.NamedTemporaryFile() as fwobj:
        fname = fwobj.name
        putil.pcsv.write(
            fname,
            [['Input', 'Output'], [1, 2], [3, 4]],
            append=False
        )
        written_data = _read(fname)
    assert written_data == 'Input,Output\r\n1,2\r\n3,4\r\n'
    with tempfile.NamedTemporaryFile() as fwobj:
        fname = fwobj.name
        putil.pcsv.write(
            fname,
            [['Input', 'Output'], [1, 2], [3, 4]],
            append=False
        )
        putil.pcsv.write(fname, [[5.0, 10]], append=True)
        written_data = _read(fname)
    assert written_data == 'Input,Output\r\n1,2\r\n3,4\r\n5.0,10\r\n'
