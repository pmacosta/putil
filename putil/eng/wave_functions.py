# wave_functions.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,W0212

# Standard library imports
import copy
# PyPI imports
import numpy
# Putil imports
import putil.pcontracts
from .wave_core import Waveform


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
def _operation(wave, desc, units, fpointer):
    """ Generic operation on a waveform object """
    ret = copy.copy(wave)
    ret.dep_units = units
    ret.indep_name = '{0}({1})'.format(desc, ret.indep_name)
    ret._dep_vector = fpointer(ret._dep_vector)
    return ret


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
    exh = putil.exh.get_or_create_exh_obj()
    exh.add_exception(
        exname='domain_error',
        extype=ValueError,
        exmsg='Math domain error'
    )
    exh.raise_exception_if(
        exname='domain_error',
        condition=bool(
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
    exh = putil.exh.get_or_create_exh_obj()
    exh.add_exception(
        exname='domain_error',
        extype=ValueError,
        exmsg='Math domain error'
    )
    exh.raise_exception_if(
        exname='domain_error', condition=bool(min(wave._dep_vector) < 1)
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
    exh = putil.exh.get_or_create_exh_obj()
    exh.add_exception(
        exname='domain_error',
        extype=ValueError,
        exmsg='Math domain error'
    )
    exh.raise_exception_if(
        exname='domain_error',
        condition=bool(
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
    exh = putil.exh.get_or_create_exh_obj()
    exh.add_exception(
        exname='domain_error',
        extype=ValueError,
        exmsg='Math domain error'
    )
    exh.raise_exception_if(
        exname='domain_error',
        condition=bool(
            (min(wave._dep_vector) < -1) or (max(wave._dep_vector) > 1)
        )
    )
    return _operation(wave, 'atanh', '', numpy.arctanh)


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
    exh = putil.exh.get_or_create_exh_obj()
    exh.add_exception(
        exname='domain_error',
        extype=ValueError,
        exmsg='Math domain error'
    )
    exh.raise_exception_if(
        exname='domain_error',
        condition=bool((min(wave._dep_vector) <= 0))
    )
    ret = copy.copy(wave)
    ret.dep_units = 'dB'
    ret.indep_name = 'db({0})'.format(ret.indep_name)
    ret._dep_vector = 20.0*numpy.log10(ret._dep_vector)
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
    exh = putil.exh.get_or_create_exh_obj()
    exh.add_exception(
        exname='domain_error',
        extype=ValueError,
        exmsg='Math domain error'
    )
    exh.raise_exception_if(
        exname='domain_error',
        condition=bool((min(wave._dep_vector) <= 0))
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
    exh = putil.exh.get_or_create_exh_obj()
    exh.add_exception(
        exname='domain_error',
        extype=ValueError,
        exmsg='Math domain error'
    )
    exh.raise_exception_if(
        exname='domain_error',
        condition=bool((min(wave._dep_vector) <= 0))
    )
    return _operation(wave, 'log10', '', numpy.log10)


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
    exh = putil.exh.get_or_create_exh_obj()
    exh.add_exception(
        exname='complex_not_supported',
        extype=TypeError,
        exmsg='Cannot convert complex to float'
    )
    exh.raise_exception_if(
        exname='complex_not_supported',
        condition=wave._dep_vector.dtype.name.startswith('complex')
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
    exh = putil.exh.get_or_create_exh_obj()
    exh.add_exception(
        exname='complex_not_supported',
        extype=TypeError,
        exmsg='Cannot convert complex to integer'
    )
    exh.raise_exception_if(
        exname='complex_not_supported',
        condition=wave._dep_vector.dtype.name.startswith('complex')
    )
    ret = copy.copy(wave)
    ret._dep_vector = ret._dep_vector.astype(numpy.int)
    return ret

@putil.pcontracts.contract(wave=Waveform, decimals='int,>=0')
def wround(wave, decimals=0):
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
    .. putil.eng.wave_functions.wround

    :raises:
     * RuntimeError (Argument \`decimals\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    # pylint: disable=W0622
    exh = putil.exh.get_or_create_exh_obj()
    exh.add_exception(
        exname='complex_not_supported',
        extype=TypeError,
        exmsg='Cannot convert complex to integer'
    )
    exh.raise_exception_if(
        exname='complex_not_supported',
        condition=wave._dep_vector.dtype.name.startswith('complex')
    )
    ret = copy.copy(wave)
    ret.indep_name = 'round({0}, {1})'.format(ret.indep_name, decimals)
    ret._dep_vector = numpy.round(wave._dep_vector, decimals)
    return ret
