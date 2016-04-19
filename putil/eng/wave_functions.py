# wave_functions.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,W0105,W0212

# Standard library imports
import copy
# PyPI imports
import numpy
# Putil imports
import putil.exh
import putil.pcontracts
from .functions import remove_extra_delims
from .constants import FP_ATOL, FP_RTOL
from .wave_core import _interp_dep_vector, Waveform


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
if sys.hexversion < 0x03000000:
    import __builtin__
else:
    import builtins as __builtin__
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_eng_wave_functions
exobj_eng = trace_ex_eng_wave_functions.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
def _bound_waveform(wave, indep_min, indep_max):
    """ Add independent variable vector bounds if they are not in vector """
    indep_min, indep_max = _validate_min_max(wave, indep_min, indep_max)
    indep_vector = copy.copy(wave._indep_vector)
    if ((isinstance(indep_min, float) or isinstance(indep_max, float)) and
        indep_vector.dtype.name.startswith('int')):
        indep_vector = indep_vector.astype(float)
    min_pos = numpy.searchsorted(indep_vector, indep_min)
    if not numpy.isclose(indep_min, indep_vector[min_pos], FP_RTOL, FP_ATOL):
        indep_vector = numpy.insert(indep_vector, min_pos, indep_min)
    max_pos = numpy.searchsorted(indep_vector, indep_max)
    if not numpy.isclose(indep_max, indep_vector[max_pos], FP_RTOL, FP_ATOL):
        indep_vector = numpy.insert(indep_vector, max_pos, indep_max)
    dep_vector = _interp_dep_vector(wave, indep_vector)
    wave._indep_vector = indep_vector[min_pos:max_pos+1]
    wave._dep_vector = dep_vector[min_pos:max_pos+1]


def _build_units(indep_units, dep_units, op):
    """ Build unit math operations """
    if (not dep_units) and (not indep_units):
        return ''
    if dep_units and (not indep_units):
        return dep_units
    if (not dep_units) and indep_units:
        return (
            remove_extra_delims('1{0}({1})'.format(op, indep_units))
            if op == '/' else
            remove_extra_delims('({0})'.format(indep_units))
        )
    return remove_extra_delims(
        '({0}){1}({2})'.format(dep_units, op, indep_units)
    )


def _operation(wave, desc, units, fpointer):
    """ Generic operation on a waveform object """
    ret = copy.copy(wave)
    ret.dep_units = units
    ret.indep_name = '{0}({1})'.format(desc, ret.indep_name)
    ret._dep_vector = fpointer(ret._dep_vector)
    return ret


def _running_area(indep_vector, dep_vector):
    """ Calculate running area under curve """
    rect_height = numpy.minimum(dep_vector[:-1], dep_vector[1:])
    rect_base = numpy.diff(indep_vector)
    rect_area = numpy.multiply(rect_height, rect_base)
    triang_height = numpy.abs(numpy.diff(dep_vector))
    triang_area = 0.5*numpy.multiply(triang_height, rect_base)
    return numpy.cumsum(
        numpy.concatenate((numpy.array([0.0]), triang_area+rect_area))
    )


def _validate_min_max(wave, indep_min, indep_max):
    """
    Validate that minimum and maximum bounds are within the waveform's
    independent variable vector
    """
    imin, imax = False, False
    if indep_min is None:
        indep_min = wave._indep_vector[0]
        imin = True
    if indep_max is None:
        indep_max = wave._indep_vector[-1]
        imax = True
    if imin and imax:
        return indep_min, indep_max
    exminmax = putil.exh.addex(
        RuntimeError, 'Incongruent `indep_min` and `indep_max` arguments'
    )
    exmin = putil.exh.addai('indep_min')
    exmax = putil.exh.addai('indep_max')
    exminmax(bool(indep_min >= indep_max))
    exmin(
        bool(
            (indep_min < wave._indep_vector[0]) and
            (
                not numpy.isclose(
                    indep_min, wave._indep_vector[0], FP_RTOL, FP_ATOL
                )
            )
        )
    )
    exmax(
        bool(
            (indep_max > wave._indep_vector[-1]) and
            (
                not numpy.isclose(
                    indep_max, wave._indep_vector[-1], FP_RTOL, FP_ATOL
                )
            )
        )
    )
    return indep_min, indep_max


@putil.pcontracts.contract(wave=Waveform)
def acos(wave):
    r"""
    Returns the arc cosine of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.acos

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    putil.exh.addex(
        ValueError, 'Math domain error', bool(
            (min(wave._dep_vector) < -1) or (max(wave._dep_vector) > 1)
        )
    )
    return _operation(wave, 'acos', 'rad', numpy.arccos)


@putil.pcontracts.contract(wave=Waveform)
def acosh(wave):
    r"""
    Returns the hyperbolic arc cosine of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.acosh

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    putil.exh.addex(
        ValueError, 'Math domain error', bool(min(wave._dep_vector) < 1)
    )
    return _operation(wave, 'acosh', '', numpy.arccosh)


@putil.pcontracts.contract(wave=Waveform)
def asin(wave):
    r"""
    Returns the arc sine of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.asin

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    putil.exh.addex(
        ValueError, 'Math domain error', bool(
            (min(wave._dep_vector) < -1) or (max(wave._dep_vector) > 1)
        )
    )
    return _operation(wave, 'asin', 'rad', numpy.arcsin)


@putil.pcontracts.contract(wave=Waveform)
def asinh(wave):
    r"""
    Returns the hyperbolic arc sine of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.asinh

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'asinh', '', numpy.arcsinh)


@putil.pcontracts.contract(wave=Waveform)
def atan(wave):
    r"""
    Returns the arc tangent of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.atan

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'atan', 'rad', numpy.arctan)


@putil.pcontracts.contract(wave=Waveform)
def atanh(wave):
    r"""
    Returns the hyperbolic arc tangent of a waveform's dependent variable
    vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.atanh

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    putil.exh.addex(
        ValueError, 'Math domain error', bool(
            (min(wave._dep_vector) < -1) or (max(wave._dep_vector) > 1)
        )
    )
    return _operation(wave, 'atanh', '', numpy.arctanh)


@putil.pcontracts.contract(
    wave=Waveform, indep_min='None|number', indep_max='None|number'
)
def average(wave, indep_min=None, indep_max=None):
    r"""
    Returns the running average of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.average

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    area = _running_area(ret._indep_vector, ret._dep_vector)
    area[0] = ret._dep_vector[0]
    deltas = ret._indep_vector-ret._indep_vector[0]
    deltas[0] = 1.0
    ret._dep_vector = numpy.divide(area, deltas)
    ret.indep_name = 'average({0})'.format(ret._indep_name)
    return ret


@putil.pcontracts.contract(wave=Waveform)
def ceil(wave):
    r"""
    Returns the ceiling of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.ceil

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'ceil', wave.dep_units, numpy.ceil)


@putil.pcontracts.contract(wave=Waveform)
def cos(wave):
    r"""
    Returns the cosine of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.cos

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'cos', '', numpy.cos)


@putil.pcontracts.contract(wave=Waveform)
def cosh(wave):
    r"""
    Returns the hyperbolic cosine of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.cosh

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'cosh', '', numpy.cosh)


@putil.pcontracts.contract(wave=Waveform)
def db(wave):
    r"""
    Returns a waveform's dependent variable vector expressed in decibels

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.db

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    putil.exh.addex(
        ValueError, 'Math domain error', bool((min(wave._dep_vector) <= 0))
    )
    ret = copy.copy(wave)
    ret.dep_units = 'dB'
    ret.indep_name = 'db({0})'.format(ret.indep_name)
    ret._dep_vector = 20.0*numpy.log10(ret._dep_vector)
    return ret


@putil.pcontracts.contract(
    wave=Waveform, indep_min='None|number', indep_max='None|number'
)
def derivative(wave, indep_min=None, indep_max=None):
    r"""
    Returns the numerical derivative of a waveform's dependent variable vector
    using
    `backwards differences <https://en.wikipedia.org/wiki/
    Finite_difference#Forward.2C_backward.2C_and_central_differences>`_

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: float

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.derivative

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    delta_indep = numpy.diff(ret._indep_vector)
    delta_dep = numpy.diff(ret._dep_vector)
    delta_indep = numpy.concatenate(
        (numpy.array([delta_indep[0]]), delta_indep)
    )
    delta_dep = numpy.concatenate(
        (numpy.array([delta_dep[0]]), delta_dep)
    )
    ret._dep_vector = numpy.divide(delta_dep, delta_indep)
    ret.indep_name = 'derivative({0})'.format(ret._indep_name)
    ret.dep_units = _build_units(ret.indep_units, ret.dep_units, '/')
    return ret


@putil.pcontracts.contract(wave=Waveform)
def exp(wave):
    r"""
    Returns the natural exponent of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.exp

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'exp', '', numpy.exp)


@putil.pcontracts.contract(wave=Waveform)
def floor(wave):
    r"""
    Returns the floor of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.floor

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'floor', wave.dep_units, numpy.floor)


@putil.pcontracts.contract(wave=Waveform)
def imag(wave):
    r"""
    Returns the imaginary part of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.imag

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'imag', wave.dep_units, numpy.imag)


@putil.pcontracts.contract(
    wave=Waveform, indep_min='None|number', indep_max='None|number'
)
def integral(wave, indep_min=None, indep_max=None):
    r"""
    Returns the running integral of a waveform's dependent variable vector
    using the
    `trapezoidal method <https://en.wikipedia.org/wiki/Trapezoidal_rule>`_

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.integral

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    ret._dep_vector = _running_area(ret._indep_vector, ret._dep_vector)
    ret.indep_name = 'integral({0})'.format(ret._indep_name)
    ret.dep_units = _build_units(ret.indep_units, ret.dep_units, '*')
    return ret


@putil.pcontracts.contract(wave=Waveform)
def log(wave):
    r"""
    Returns the natural logarithm of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.log

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    putil.exh.addex(
        ValueError, 'Math domain error', bool((min(wave._dep_vector) <= 0))
    )
    return _operation(wave, 'log', '', numpy.log)


@putil.pcontracts.contract(wave=Waveform)
def log10(wave):
    r"""
    Returns the base 10 logarithm of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.log10

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    putil.exh.addex(
        ValueError, 'Math domain error', bool((min(wave._dep_vector) <= 0))
    )
    return _operation(wave, 'log10', '', numpy.log10)


@putil.pcontracts.contract(
    wave=Waveform, indep_min='None|number', indep_max='None|number'
)
def naverage(wave, indep_min=None, indep_max=None):
    r"""
    Returns the numerical average of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.naverage

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    delta_x = ret._indep_vector[-1]-ret._indep_vector[0]
    return numpy.trapz(ret._dep_vector, x=ret._indep_vector)/delta_x


@putil.pcontracts.contract(
    wave=Waveform, indep_min='None|number', indep_max='None|number'
)
def nintegral(wave, indep_min=None, indep_max=None):
    r"""
    Returns the numerical integral of a waveform's dependent variable vector
    using the
    `trapezoidal method <https://en.wikipedia.org/wiki/Trapezoidal_rule>`_

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: float

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.nintegral

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    return numpy.trapz(ret._dep_vector, ret._indep_vector)


@putil.pcontracts.contract(
    wave=Waveform, indep_min='None|number', indep_max='None|number'
)
def nmax(wave, indep_min=None, indep_max=None):
    r"""
    Returns the maximum of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: float

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.nmax

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    return numpy.max(ret._dep_vector)


@putil.pcontracts.contract(
    wave=Waveform, indep_min='None|number', indep_max='None|number'
)
def nmin(wave, indep_min=None, indep_max=None):
    r"""
    Returns the minimum of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: float

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.nmin

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    return numpy.min(ret._dep_vector)


@putil.pcontracts.contract(wave=Waveform, unwrap=bool, rad=bool)
def phase(wave, unwrap=True, rad=True):
    r"""
    Returns the phase of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :param unwrap: Flag that indicates whether phase should change phase shifts
                   to their :code:`2*pi` complement (True) or not (False)
    :type  unwrap: boolean

    :param rad: Flag that indicates whether phase should be returned in radians
                (True) or degrees (False)
    :type  rad: boolean

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.phase

    :raises:
     * RuntimeError (Argument \`rad\` is not valid)

     * RuntimeError (Argument \`unwrap\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    ret.dep_units = 'rad' if rad else 'deg'
    ret.indep_name = 'phase({0})'.format(ret.indep_name)
    ret._dep_vector = (
        numpy.unwrap(numpy.angle(ret._dep_vector))
        if unwrap else
        numpy.angle(ret._dep_vector)
    )
    if not rad:
        ret._dep_vector = numpy.rad2deg(ret._dep_vector)
    return ret


@putil.pcontracts.contract(wave=Waveform)
def real(wave):
    r"""
    Returns the real part of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.real

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'real', wave.dep_units, numpy.real)



@putil.pcontracts.contract(wave=Waveform, decimals='int,>=0')
def round(wave, decimals=0):
    r"""
    Rounds a waveform's dependent variable vector to a given number of decimal
    places

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :param decimals: Number of decimals to round to
    :type  decimals: integer

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.round

    :raises:
     * RuntimeError (Argument \`decimals\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    # pylint: disable=W0622
    putil.exh.addex(
        TypeError,
        'Cannot convert complex to integer',
        wave._dep_vector.dtype.name.startswith('complex')
    )
    ret = copy.copy(wave)
    ret.indep_name = 'round({0}, {1})'.format(ret.indep_name, decimals)
    ret._dep_vector = numpy.round(wave._dep_vector, decimals)
    return ret


@putil.pcontracts.contract(wave=Waveform)
def sin(wave):
    r"""
    Returns the sine of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.sin

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'sin', '', numpy.sin)


@putil.pcontracts.contract(wave=Waveform)
def sinh(wave):
    r"""
    Returns the hyperbolic sine of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.sinh

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'sinh', '', numpy.sinh)


@putil.pcontracts.contract(wave=Waveform)
def sqrt(wave):
    r"""
    Returns the square root of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.sqrt

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    dep_units = '{0}**0.5'.format(wave.dep_units)
    return _operation(wave, 'sqrt', dep_units, numpy.sqrt)


@putil.pcontracts.contract(wave=Waveform)
def tan(wave):
    r"""
    Returns the tangent of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.tan

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'tan', '', numpy.tan)


@putil.pcontracts.contract(wave=Waveform)
def tanh(wave):
    r"""
    Returns the hyperbolic tangent of a waveform's dependent variable vector

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.tanh

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, 'tanh', '', numpy.tanh)


@putil.pcontracts.contract(wave=Waveform)
def wcomplex(wave):
    r"""
    Converts a waveform's dependent variable vector to complex

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.wcomplex

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    ret._dep_vector = ret._dep_vector.astype(numpy.complex)
    return ret


@putil.pcontracts.contract(wave=Waveform)
def wfloat(wave):
    r"""
    Converts a waveform's dependent variable vector to float

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.wfloat

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * TypeError (Cannot convert complex to float)

    .. [[[end]]]
    """
    putil.exh.addex(
        TypeError,
        'Cannot convert complex to float',
        wave._dep_vector.dtype.name.startswith('complex')
    )
    ret = copy.copy(wave)
    ret._dep_vector = ret._dep_vector.astype(numpy.float)
    return ret


@putil.pcontracts.contract(wave=Waveform)
def wint(wave):
    r"""
    Converts a waveform's dependent variable vector to integer

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.wint

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * TypeError (Cannot convert complex to integer)

    .. [[[end]]]
    """
    putil.exh.addex(
        TypeError,
        'Cannot convert complex to integer',
        wave._dep_vector.dtype.name.startswith('complex')
    )
    ret = copy.copy(wave)
    ret._dep_vector = ret._dep_vector.astype(numpy.int)
    return ret


@putil.pcontracts.contract(wave=Waveform, indep_var='number')
def wvalue(wave, indep_var):
    r"""
    Returns the dependent variable value at a given independent variable point.
    If the independent variable point is not in the independent variable vector
    the dependent variable value is obtained by linear interpolation

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :param indep_var: Independent variable point for which the dependent
                      variable is to be obtained
    :type  indep_var: integer or float

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.wvalue

    :raises:
     * RuntimeError (Argument \`indep_var\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Argument \`indep_var\` is not in the independent
       variable vector range)

    .. [[[end]]]
    """
    close_min = numpy.isclose(
        indep_var, wave._indep_vector[0], FP_RTOL, FP_ATOL
    )
    close_max = numpy.isclose(
        indep_var, wave._indep_vector[-1], FP_RTOL, FP_ATOL
    )
    putil.exh.addex(
        ValueError,
        'Argument `indep_var` is not in the independent variable vector range',
        bool(((indep_var < wave._indep_vector[0]) and (not close_min))
        or
        ((indep_var > wave._indep_vector[-1]) and (not close_max)))
    )
    if close_min:
        return wave._dep_vector[0]
    if close_max:
        return wave._dep_vector[-1]
    idx = numpy.searchsorted(wave._indep_vector, indep_var)
    xdelta = wave._indep_vector[idx]-wave._indep_vector[idx-1]
    ydelta = wave._dep_vector[idx]-wave._dep_vector[idx-1]
    slope = ydelta/float(xdelta)
    return wave._dep_vector[idx-1]+slope*(indep_var-wave._indep_vector[idx-1])
