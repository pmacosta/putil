# touchstone.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0611

# Standard library imports
import copy
import os
import re
# PyPI imports
import numpy
# Putil imports
import putil.exh
import putil.pcontracts
from putil.ptypes import file_name_exists


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_eng_touchstone
exobj = trace_ex_eng_touchstone.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
@putil.pcontracts.contract(fname='file_name_exists')
def read_touchstone(fname):
    r"""
    Reads a `Touchstone <https://ibis.org/connector/touchstone_spec11.pdf>`_
    file. According to the specification a data line can have at most values
    for four complex parameters (plus potentially the frequency point), however
    this function is able to process malformed files as long as they have the
    correct number of data points. Per the Touchstone specification noise data
    is only supported for 2-port files

    :param fname: Touchstone file name
    :type  fname: ref:`FileNameExists`

    :rtype: dictionary with the following structure:

     * **nports** (*integer*) -- number of ports

     * **opts** (:ref:`TouchstoneOptions`) -- File options

     * **data** (:ref:`TouchstoneData`) -- Parameter data

     * **noise** (:ref:`TouchstoneNoiseData`) -- Noise data, per the Touchstone
       specification only supported in 2-port files

    .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.touchstone.read_touchstone

    :raises:
     * OSError (File *[fname]* could not be found)

     * RuntimeError (Argument \`fname\` is not valid)

     * RuntimeError (File *[fname]* does not have a valid extension)

     * RuntimeError (File *[fname]* has no data)

     * RuntimeError (First non-comment line is not the option line)

     * RuntimeError (Frequency must increase)

     * RuntimeError (Illegal data in line *[lineno]*)

     * RuntimeError (Illegal option line)

     * RuntimeError (Malformed data)

     * RuntimeError (Malformed noise data)

     * RuntimeError (Noise frequency must increase)

    .. [[[end]]]
    """
    # pylint: disable=R0912,R0914,R0915,W0702
    # Exceptions definitions
    exnports = putil.exh.addex(
        RuntimeError, 'File *[fname]* does not have a valid extension'
    )
    exnoopt = putil.exh.addex(
        RuntimeError, 'First non-comment line is not the option line'
    )
    exopt = putil.exh.addex(RuntimeError, 'Illegal option line')
    exline = putil.exh.addex(RuntimeError, 'Illegal data in line *[lineno]*')
    exnodata = putil.exh.addex(RuntimeError, 'File *[fname]* has no data')
    exdata = putil.exh.addex(RuntimeError, 'Malformed data')
    exndata = putil.exh.addex(RuntimeError, 'Malformed noise data')
    exfreq = putil.exh.addex(RuntimeError, 'Frequency must increase')
    exnfreq = putil.exh.addex(RuntimeError, 'Noise frequency must increase')
    # Verify that file has correct extension format
    _, ext = os.path.splitext(fname)
    ext = ext.lower()
    nports_regexp = re.compile(r'\.s(\d+)p')
    match = nports_regexp.match(ext)
    exnports(not match, edata={'field':'fname', 'value':fname})
    nports = int(match.groups()[0])
    opt_line = False
    units_dict = {'GHZ':'GHz', 'MHZ':'MHz', 'KHZ':'KHz', 'HZ':'Hz'}
    units_opts = ['GHZ', 'MHZ', 'KHZ', 'HZ']
    type_opts = ['S', 'Y', 'Z', 'H', 'G']
    format_opts = ['DB', 'MA', 'RI']
    opts = dict(units=None, ptype=None, pformat=None, z0=None)
    data = numpy.array([])
    with open(fname, 'r') as fobj:
        for num, line in enumerate(fobj):
            line = line.strip().upper()
            # Comment line
            if line.startswith('!'):
                continue
            # Options line
            if (not opt_line) and (not line.startswith('#')):
                exnoopt(True)
            if not opt_line:
                # Each Touchstone data file must contain an option line
                # (additional option lines after the first one will be ignored)
                opt_line = True
                tokens = line[1:].split()   # Remove initial hash
                if 'R' in tokens:
                    idx = tokens.index('R')
                    add = 1
                    if len(tokens) > idx+1:
                        try:
                            opts['z0'] = float(tokens[idx+1])
                            add = 2
                        except:
                            pass
                    tokens = tokens[:idx]+tokens[idx+add:]
                matches = 0
                for token in tokens:
                    if (token in format_opts) and (not opts['pformat']):
                        matches += 1
                        opts['pformat'] = token
                    elif (token in units_opts) and (not opts['units']):
                        matches += 1
                        opts['units'] = units_dict[token]
                    elif (token in type_opts) and (not opts['ptype']):
                        matches += 1
                        opts['ptype'] = token
                exopt(matches != len(tokens))
            if opt_line and line.startswith('#'):
                continue
            # Data lines
            try:
                if '!' in line:
                    idx = line.index('!')
                    line = line[:idx]
                tokens = [float(item) for item in line.split()]
                data = numpy.append(data, tokens)
            except:
                exline(True, edata={'field':'lineno', 'value':num+1})
    exnodata(not data.size, edata={'field':'fname', 'value':fname})
    # Set option defaults
    opts['units'] = opts['units'] or 'GHz'
    opts['ptype'] = opts['ptype'] or 'S'
    opts['pformat'] = opts['pformat'] or 'MA'
    opts['z0'] = opts['z0'] or 50
    # Format data
    data_dict = {}
    nums_per_freq = 1+(2*(nports**2))
    fslice = slice(0, data.size, nums_per_freq)
    freq = data[fslice]
    ndiff = numpy.diff(freq)
    ndict = {}
    if (nports == 2) and ndiff.size and (min(ndiff) <= 0):
        # Extract noise data
        npoints = numpy.where(ndiff <= 0)[0][0]+1
        freq = freq[:npoints]
        ndata = data[9*npoints:]
        nfpoints = int(ndata.size / 5.0)
        exndata(ndata.size % 5 != 0)
        data = data[:9*npoints]
        ndiff = 1
        nfslice = slice(0, ndata.size, 5)
        nfreq = ndata[nfslice]
        ndiff = numpy.diff(nfreq)
        exnfreq(bool(ndiff.size and (min(ndiff) <= 0)))
        nfig_slice = slice(1, ndata.size, 5)
        rlmag_slice = slice(2, ndata.size, 5)
        rlphase_slice = slice(3, ndata.size, 5)
        res_slice = slice(4, ndata.size, 5)
        ndict['freq'] = nfreq
        ndict['nf'] = ndata[nfig_slice]
        ndict['rc'] = ndata[rlmag_slice]*numpy.exp(1j*ndata[rlphase_slice])
        ndict['res'] = ndata[res_slice]
        ndict['points'] = nfpoints
    exdata(data.size % nums_per_freq != 0)
    npoints = int(data.size / nums_per_freq)
    exfreq(bool(ndiff.size and (min(ndiff) <= 0)))
    data_dict['freq'] = freq
    d1slice = slice(0, data.size, 2)
    d2slice = slice(1, data.size, 2)
    data = numpy.delete(data, fslice)
    if opts['pformat'] == 'MA':
        data = data[d1slice]*numpy.exp(1j*data[d2slice])
    elif opts['pformat'] == 'RI':
        data = data[d1slice]+(1j*data[d2slice])
    else: # if opts['pformat'] == 'DB':
        data = (10**(data[d1slice]/20.0))*numpy.exp(1j*data[d2slice])
    if nports > 1:
        data_dict['data'] = numpy.resize(data, (npoints, nports, nports))
    else:
        data_dict['data'] = copy.copy(data)
    del data
    data_dict['points'] = npoints
    if nports == 2:
        # The order of data for a two-port file is N11, N21, N12, N22 but for
        # m ports where m > 2, the order is N11, N12, N13, ..., N1m
        data_dict['data'] = numpy.transpose(data_dict['data'], (0, 2, 1))
    return dict(
        nports=nports, opts=opts, data=data_dict, noise=ndict
    )
