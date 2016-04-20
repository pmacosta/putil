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
    obj = putil.eng.read_touchstone
    # Test parsing of options line
    fname = 'file.s4p'
    for units, ptype, pformat, res in all_options():
        opts = [units, ptype, pformat, res]
        if all([not item for item in opts]):
            opts = [' ']
        else:
            random.shuffle(opts)
        with TmpFile(fname, opts, [9*[1]]):
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
    with TmpFile(fname, ['R 12', 'KHz'], [17*[1]], eopts='R 100 Z'):
        ret = obj(fname)
        assert ret['nports'] == 8
        assert ret['opts'] == dict(units='KHz', ptype='S', pformat='MA', z0=12)
    # Test data parsing
    # Real and imaginary format
    fname = 'file.s2p'
    with TmpFile(fname, ['RI'], [[1, 2, 3, 4, 5], [3.5, 1.1, 7, 2.2, 3.3]]):
        ret = obj(fname)
    assert ret['nports'] == 2
    assert ret['opts'] == dict(units='GHz', ptype='S', pformat='RI', z0=50)
    assert (ret['data']['freq'] == numpy.array([1.0, 3.5])).all()
    ref = numpy.array(
        [
            [2+3j, 4+5j],
            [1.1+7j, 2.2+3.3j]
        ]
    )
    assert (ret['data']['data'] == ref).all()
    assert ret['points'] == 2
    # Magnitude and angle
    with TmpFile(fname, ['MA'], [[1, 2, 3, 4, 5], [3.5, 1.1, 7, 2.2, 3.3]]):
        ret = obj(fname)
    assert ret['nports'] == 2
    assert ret['opts'] == dict(units='GHz', ptype='S', pformat='MA', z0=50)
    assert (ret['data']['freq'] == numpy.array([1.0, 3.5])).all()
    ref = numpy.array(
        [
            [2*cmath.exp(3j), 4*cmath.exp(5j)],
            [1.1*cmath.exp(7j), 2.2*cmath.exp(3.3j)]
        ]
    )
    assert (ret['data']['data'] == ref).all()
    assert ret['points'] == 2
    # Decibel-angle
    with TmpFile(fname, ['DB'], [[1, 2, 3, 4, 5], [3.5, 1.1, 7, 2.2, 3.3]]):
        ret = obj(fname)
    assert ret['nports'] == 2
    assert ret['opts'] == dict(units='GHz', ptype='S', pformat='DB', z0=50)
    assert (ret['data']['freq'] == numpy.array([1.0, 3.5])).all()
    ref = numpy.array(
        [
            [(10**(2/20.0))*cmath.exp(3j), (10**(4/20.0))*cmath.exp(5j)],
            [(10**(1.1/20.0))*cmath.exp(7j), (10**(2.2/20.0))*cmath.exp(3.3j)]
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
