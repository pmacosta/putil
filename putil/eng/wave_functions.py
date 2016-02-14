# wave_functions.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

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
    Returns the ceiling of the waveform's dependent variable vector

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
    Returns the cosine of the waveform's dependent variable vector

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
    Returns the hyperbolic cosine of the waveform's dependent variable vector

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
    Returns the waveform's dependent variable vector expressed in decibels

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
    # pylint: disable=C0103
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
def to_complex(wave):
    r"""
    Converts the waveform's dependent variable vector to complex

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.to_complex

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    ret._dep_vector = ret._dep_vector.astype(numpy.complex)
    return ret


@putil.pcontracts.contract(wave=Waveform)
def to_float(wave):
    r"""
    Converts the waveform's dependent variable vector to float

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.to_float

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
def to_int(wave):
    r"""
    Converts the waveform's dependent variable vector to integer

    :param wave: Waveform
    :type  wave: :py:class:`putil.eng.Waveform`

    :rtype: :py:class:`putil.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.wave_functions.to_int

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
