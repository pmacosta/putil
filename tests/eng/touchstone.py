# touchstone.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0611

# Standard library imports
import itertools
import cmath
import os
import platform
import random
# PyPI imports
import numpy
import pytest
# Putil imports
import putil.eng
from putil.test import AE, AI


###
# Helper function
###
def write_file(fobj, opts=None, data=None, eopts=None):
    """ Write a sample Touchstone file """
    lines = []
    lines.append('! Sample file')
    if opts:
        lines.append('# '+' '.join(opts))
    if eopts:
        lines.append('# '+eopts)
    if not data:
        data = [[1, 1, 1]]
    for row in data:
        lines.append(' '.join([str(item) for item in row]))
    lines = [item+'\n' for item in lines]
    fobj.writelines(lines)


def all_options():
    """ Generate all possible option lines """
    units_opts = ['', 'GHz', 'MHz', 'KHz', 'Hz']
    type_opts = ['', 'S', 'Y', 'Z', 'H', 'G']
    format_opts = ['', 'DB', 'MA', 'RI']
    z0_opts = ['', 'R', 'R 75']
    return itertools.product(units_opts, type_opts, format_opts, z0_opts)

###
# Helper class
###
class TmpFile(object):
    # pylint: disable=R0903,W0702
    """ Create a temporary Touchstone file """
    def __init__(self, fname, opts=None, data=None, eopts=None):
        if platform.system().lower() == 'windows':  # pragma: no cover
            fname = fname.replace(os.sep, '/')
        self._fname = fname
        self._opts = opts or []
        self._data = data or [[1, 1, 1]]
        self._eopts = eopts

    def __enter__(self):
        with open(self._fname, 'w') as fobj:
            write_file(fobj, self._opts, self._data, self._eopts)

    def __exit__(self, exc_type, exc_value, exc_tb):
        try:
            os.remove(self._fname)
        except:
            pass
        if exc_type is not None:
            return False


###
# Test functions
###
def test_read_touchstone():
    """ Test read_touchstone function behavior """
    # pylint: disable=R0915
    obj = putil.eng.read_touchstone
    # Test parsing of options line
    fname = 'file.s4p'
    for units, ptype, pformat, res in all_options():
        opts = [units, ptype, pformat, res]
        if all([not item for item in opts]):
            opts = [' ']
        else:
            random.shuffle(opts)
        with TmpFile(fname, opts, [33*[1]]):
            ret = obj(fname)
            assert ret['nports'] == 4
            assert ret['opts'] == dict(
                units=units or 'GHz',
                ptype=ptype or 'S',
                pformat=pformat or 'MA',
                z0=75.0 if res == 'R 75' else 50.0
            )
    # Test multiple options line after first are ignored
    fname = 'file2.s8p'
    with TmpFile(fname, ['R 12', 'KHz'], [129*[1]], eopts='R 100 Z'):
        ret = obj(fname)
        assert ret['nports'] == 8
        assert ret['opts'] == dict(units='KHz', ptype='S', pformat='MA', z0=12)
    # Test 1-port data parsing (and end of line comments)
    fname = 'file.s1p'
    data = [
        [1, 2, 3],
        [4, 5, '6 ! this is an end of line comment'],
        [7, 8, 9]
    ]
    with TmpFile(fname, ['RI'], data):
        ret = obj(fname)
    assert ret['nports'] == 1
    assert ret['opts'] == dict(units='GHz', ptype='S', pformat='RI', z0=50)
    assert (ret['data']['freq'] == numpy.array([1.0, 4.0, 7.0])).all()
    ref = numpy.array([2+3j, 5+6j, 8+9j])
    assert (ret['data']['data'] == ref).all()
    assert ret['points'] == 3
    # Test 2-port data parsing
    # Real and imaginary format
    fname = 'file.s2p'
    data = [
        [1, 2, 3, 4, 5, 1.1, 7, 2.2, 3.3],
        [2, 8, 9, 10, 11, 12, 13, 14, 15]
    ]
    with TmpFile(fname, ['RI'], data):
        ret = obj(fname)
    assert ret['nports'] == 2
    assert ret['opts'] == dict(units='GHz', ptype='S', pformat='RI', z0=50)
    assert (ret['data']['freq'] == numpy.array([1.0, 2.0])).all()
    ref = numpy.array(
        [
            [
                [2+3j, 1.1+7j],
                [4+5j, 2.2+3.3j]
            ],
            [
                [8+9j, 12+13j],
                [10+11j, 14+15j]
            ]
        ]
    )
    assert (ret['data']['data'] == ref).all()
    assert ret['points'] == 2
    # Magnitude and angle
    with TmpFile(fname, ['MA'], data):
        ret = obj(fname)
    assert ret['nports'] == 2
    assert ret['opts'] == dict(units='GHz', ptype='S', pformat='MA', z0=50)
    assert (ret['data']['freq'] == numpy.array([1.0, 2.0])).all()
    ref = numpy.array(
        [
            [
                [2*cmath.exp(3j), 1.1*cmath.exp(7j)],
                [4*cmath.exp(5j), 2.2*cmath.exp(3.3j)]
            ],
            [
                [8*cmath.exp(9j), 12*cmath.exp(13j)],
                [10*cmath.exp(11j), 14*cmath.exp(15j)]
            ]
        ]
    )
    assert (ret['data']['data'] == ref).all()
    assert ret['points'] == 2
    # Decibel-angle
    with TmpFile(fname, ['DB'], data):
        ret = obj(fname)
    assert ret['nports'] == 2
    assert ret['opts'] == dict(units='GHz', ptype='S', pformat='DB', z0=50)
    assert (ret['data']['freq'] == numpy.array([1.0, 2.0])).all()
    idb = lambda x: 10**(x/20.0)
    ref = numpy.array(
        [
            [
                [idb(2)*cmath.exp(3j), idb(1.1)*cmath.exp(7j)],
                [idb(4)*cmath.exp(5j), idb(2.2)*cmath.exp(3.3j)]
            ],
            [
                [idb(8)*cmath.exp(9j), idb(12)*cmath.exp(13j)],
                [idb(10)*cmath.exp(11j), idb(14)*cmath.exp(15j)]
            ]
        ]
    )
    assert (ret['data']['data'] == ref).all()
    assert ret['points'] == 2
    # Test 3-port data parsing
    # Real and imaginary format
    fname = 'file.s3p'
    data = [
        [1, 2, 3, 4, 5, 1.1, 7],
        [2.2, 3.3, 10, 20, 5.5, 6.6],
        [2, 1, 4, 3, 1.5, 1.6],
        [2, 9, 0, 5, 4, 1, 3.3],
        [20, 30, 40, 50, 32.5, 56.7],
        [60, 70, 80, 90.5, 45, 55],
    ]
    with TmpFile(fname, ['RI'], data):
        ret = obj(fname)
    assert ret['nports'] == 3
    assert ret['opts'] == dict(units='GHz', ptype='S', pformat='RI', z0=50)
    assert (ret['data']['freq'] == numpy.array([1.0, 2.0])).all()
    ref = numpy.array(
        [
            [
                [2+3j, 4+5j, 1.1+7j],
                [2.2+3.3j, 10+20j, 5.5+6.6j],
                [2+1j, 4+3j, 1.5+1.6j],
            ],
            [
                [9+0j, 5+4j, 1+3.3j],
                [20+30j, 40+50j, 32.5+56.7j],
                [60+70j, 80+90.5j, 45+55j]
            ]
        ]
    )
    assert (ret['data']['data'] == ref).all()
    assert ret['points'] == 2



@pytest.mark.touchstone
def test_read_touchstone_exceptions():
    """ Test read function exceptions """
    obj = putil.eng.read_touchstone
    msg = 'File __not_a_file__ could not be found'
    AE(obj, OSError, msg, '__not_a_file__')
    msg = 'File {0} does not have a valid extension'
    items = ['file.zzz', 'file.s10a3p']
    for item in items:
        with TmpFile(item):
            AE(obj, RuntimeError, msg.format(item), item)
    msg = 'First non-comment line is not the option line'
    fname = 'file.s1p'
    with TmpFile(fname):
        AE(obj, RuntimeError, msg, fname)
    # Add an invalid option to options line
    for units, ptype, pformat, res in all_options():
        opts = [units, ptype, pformat, res, 'noopt']
        if all([not item for item in opts]):
            opts = [' ']
        else:
            random.shuffle(opts)
        with TmpFile(fname, opts):
            AE(obj, RuntimeError, 'Illegal option line', fname)
    # No data
    with TmpFile(fname, ['MA'], ['']):
        AE(obj, RuntimeError, 'File file.s1p has no data', fname)
    # Invalid data line
    with TmpFile(fname, ['MA'], [[1, 2, 3], [3.5, 'a', 7]]):
        AE(obj, RuntimeError, 'Illegal data in line 4', fname)
    # Frequency not increasing
    fname = 'file.s1p'
    with TmpFile(fname, ['MA'], [[1, 2, 3], [2, 3, 4], [2, 5, 6]]):
        AE(obj, RuntimeError, 'Frequency must increase', fname)
