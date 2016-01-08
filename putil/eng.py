# eng.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0105,W0611

# Standard library imports
import collections
import math
import textwrap
import decimal
from decimal import Decimal
# PyPI imports
import numpy
# Putil imports
import putil.exh
from putil.ptypes import (
    engineering_notation_number,
    engineering_notation_suffix,
    non_negative_integer
)


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
import trace_ex_eng
exobj_eng = trace_ex_eng.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Global variables
###
_POWER_TO_SUFFIX_DICT = dict(
    (exp, prf) for exp, prf in zip(range(-24, 27, 3), 'yzafpnum kMGTPEZY')
)
_SUFFIX_TO_POWER_DICT = dict(
    (value, key) for key, value in _POWER_TO_SUFFIX_DICT.items()
)
_SUFFIX_POWER_DICT = dict(
    (key, float(10**value)) for key, value in _SUFFIX_TO_POWER_DICT.items()
)

ENGPOWER = collections.namedtuple('EngPower', ['suffix', 'exp'])
"""
Constructor for engineering notation suffix
"""

NUMCOMP = collections.namedtuple('NumComp', ['mant', 'exp'])
"""
Constructor for number components representation
"""


###
# Functions
###
def _split_every(text, sep, count, lstrip=False, rstrip=False):
    """
    Returns a list of the words in the string, using a count of a separator as
    the delimiter

    :param text: String to split
    :type  text: string

    :param sep: Separator
    :type  sep: string

    :param count: Number of separators to use as delimiter
    :type  count: integer

    :param lstrip: Flag that indicates whether whitespace is removed
                   from the beginning of each list item (True) or not
                   (False)
    :type  lstrip: boolean

    :param rstrip: Flag that indicates whether whitespace is removed
                   from the end of each list item (True) or not (False)
    :type  rstrip: boolean

    :rtype: list
    """
    tlist = text.split(sep)
    lines = (
        sep.join(tlist[num:num+count]) for num in range(0, len(tlist), count)
    )
    ltr = '_rl '[2*lstrip+rstrip].strip()
    return [
        getattr(line, ltr+'strip')() if ltr != '_' else line for line in lines
    ]


def _to_eng_tuple(number):
    """
    Returns a tuple where the first item is the mantissa and the second
    item is the exponent when the number is formatted in engineering
    notation
    """
    # Convert number to scientific notation, a "constant" format
    mant, exp = to_scientific_tuple(number)
    # At most the integer part of the mantissa can have 3 digits in
    # engineering notation, so some numbers might need to have trailing
    # zeros added
    mant = '{mant}00'.format(mant=mant).replace('.', '')
    new_exp = exp-(exp%3)
    new_ppos = 1+exp-new_exp+(mant[0] == '-')
    # .rstrip('.0') does not work because in cases like '100.0' it will
    # return '1', as it takes both zeros and periods;
    # .rstrip('0').rstrip('.') _first_ removes trailing zeros and _then_
    # removes the period if the fractional part of the mantissa was null
    new_mant = '{int_part}.{frac_part}'.format(
        int_part=mant[:new_ppos],
        frac_part=mant[new_ppos:]
    ).rstrip('0').rstrip('.')
    return NUMCOMP(new_mant, new_exp)


def _to_sci_string(number):
    """
    Returns a string with the number formatted in scientific notation. This
    function does not have all the configurability of the public function
    to_scientific_string, this is a convenience function to test _to_eng_tuple
    """
    mant, exp = _to_eng_tuple(number)
    return '{mant}E{exp_sign}{exp}'.format(
        mant=mant,
        exp_sign='-' if exp < 0 else '+',
        exp=abs(exp)
    )


@putil.pcontracts.contract(number='number')
def no_exp(number):
    r"""
    Converts a number to a string guaranteeing that the result is not
    expressed in scientific notation

    :param number: Number to convert
    :type  number: integer or float

    :rtype: string

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for putil.eng.no_exp

    :raises: RuntimeError (Argument \`number\` is not valid)

    .. [[[end]]]
    """
    mant, exp = to_scientific_tuple(number)
    if exp == 0:
        return str(number)
    elif exp < 0:
        return '0.{zeros}{fpart}'.format(
            zeros='0'*(abs(exp)-1),
            fpart=mant.replace('.', '')
        )
    else:
        if '.' not in mant:
            return mant+('0'*exp)+('.0' if isinstance(number, float) else '')
        else:
            lfpart = len(mant)-2
            if lfpart < exp:
                return '{fpart}{zeros}'.format(
                    fpart=mant.replace('.', ''),
                    zeros='0'*(exp-lfpart)
                ).rstrip('.')
            else:
                mant = mant.replace('.', '')
                return (mant[:lfpart+1]+'.'+mant[lfpart+1:]).rstrip('.')


@putil.pcontracts.contract(
    number='int|float',
    frac_length='non_negative_integer',
    rjust=bool
)
def peng(number, frac_length, rjust=True):
    r"""
    Converts a number to engineering notation. The absolute value of the
    number (if it is not exactly zero) is bounded to the interval
    [1E-24, 1E+24)

    :param number: Number to convert
    :type  number: integer or float

    :param frac_length: Number of digits of fractional part
    :type  frac_length: :ref:`NonNegativeInteger`

    :param rjust: Flag that indicates whether the number is
                  right-justified (True) or not (False)
    :type  rjust: boolean

    :rtype: string

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for putil.eng.peng

    :raises:
     * RuntimeError (Argument \`frac_length\` is not valid)

     * RuntimeError (Argument \`number\` is not valid)

     * RuntimeError (Argument \`rjust\` is not valid)

    .. [[[end]]]

    The supported engineering suffixes are:

    +----------+-------+--------+
    | Exponent | Name  | Suffix |
    +==========+=======+========+
    | 1E-24    | yocto | y      |
    +----------+-------+--------+
    | 1E-21    | zepto | z      |
    +----------+-------+--------+
    | 1E-18    | atto  | a      |
    +----------+-------+--------+
    | 1E-15    | femto | f      |
    +----------+-------+--------+
    | 1E-12    | pico  | p      |
    +----------+-------+--------+
    | 1E-9     | nano  | n      |
    +----------+-------+--------+
    | 1E-6     | micro | u      |
    +----------+-------+--------+
    | 1E-3     | milli | m      |
    +----------+-------+--------+
    | 1E+0     |       |        |
    +----------+-------+--------+
    | 1E+3     | kilo  | k      |
    +----------+-------+--------+
    | 1E+6     | mega  | M      |
    +----------+-------+--------+
    | 1E+9     | giga  | G      |
    +----------+-------+--------+
    | 1E+12    | tera  | T      |
    +----------+-------+--------+
    | 1E+15    | peta  | P      |
    +----------+-------+--------+
    | 1E+18    | exa   | E      |
    +----------+-------+--------+
    | 1E+21    | zetta | Z      |
    +----------+-------+--------+
    | 1E+24    | yotta | Y      |
    +----------+-------+--------+

    For example:

        >>> import putil.eng
        >>> putil.eng.peng(1235.6789E3, 3, False)
        '1.236M'
    """
    # The decimal module has a to_eng_string() function, but it does not seem
    # to work well in all cases. For example:
    # >>> decimal.Decimal('34.5712233E8').to_eng_string()
    # '3.45712233E+9'
    # >>> decimal.Decimal('34.57122334E8').to_eng_string()
    # '3457122334'
    # It seems that the conversion function does not work in all cases
    #
    # Return formatted zero if number is zero, easier to not deal with this
    # special case through the rest of the algorithm
    if number == 0:
        number = '0.{zrs}'.format(zrs='0'*frac_length) if frac_length else '0'
        # Engineering notation numbers can have a sign, a 3-digit integer part,
        # a period, and a fractional part of length frac_length, so the
        # length of the number to the left of, and including, the period is 5
        return (
            '{num} '.format(num=number.rjust(5+frac_length))
            if rjust else
            number
        )
    # Low-bound number
    sign = +1 if number >= 0 else -1
    ssign = '-' if sign == -1 else ''
    anumber = abs(number)
    if anumber < 1e-24:
        anumber = 1e-24
        number = sign*1e-24
    # Round fractional part if requested frac_length is less than length
    # of fractional part. Rounding method is to add a '5' at the decimal
    # position just after the end of frac_length digits
    exp = 3.0*math.floor(math.floor(math.log10(anumber))/3.0)
    mant = number/10**(exp)
    # Because exponent is a float, mantissa is a float and its string
    # representation always includes a period
    smant = str(mant)
    ppos = smant.find('.')
    if len(smant)-ppos-1 > frac_length:
        mant += sign*5*10**(-frac_length-1)
        if abs(mant) >= 1000:
            exp += 3
            mant = mant/1E3
        smant = str(mant)
        ppos = smant.find('.')
    # Make fractional part have frac_length digits
    bfrac_length = bool(frac_length)
    flength = ppos-(not bfrac_length)+frac_length+1
    new_mant = smant[:flength].ljust(flength, '0')
    # Upper-bound number
    if exp > 24:
        new_mant, exp = (
            '{sign}999.{frac}'.format(sign=ssign, frac='9'*frac_length), 24
        )
    # Right-justify number, engineering notation numbers can have a sign,
    # a 3-digit integer part and a period, and a fractional part of length
    # frac_length, so the length of the number to the left of the
    # period is 4
    new_mant = new_mant.rjust(rjust*(4+bfrac_length+frac_length))
    # Format number
    num = '{mant}{suffix}'.format(
        mant=new_mant,
        suffix=_POWER_TO_SUFFIX_DICT[exp] if exp else ' '*bool(rjust)
    )
    return num


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_float(snum):
    r"""
    Returns the floating point equivalent of a number represented
    in engineering notation

    :param snum: Number
    :type  snum: :ref:`EngineeringNotationNumber`

    :rtype: string

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for putil.eng.peng_float

    :raises: RuntimeError (Argument \`snum\` is not valid)

    .. [[[end]]]

    For example:

        >>> import putil.eng
        >>> putil.eng.peng_float(putil.eng.peng(1235.6789E3, 3, False))
        1236000.0
    """
    # This can be coded as peng_mant(snum)*(peng_power(snum)[1]), but the
    # "function unrolling" is about 4x faster
    snum = snum.rstrip()
    power = _SUFFIX_POWER_DICT[' ' if snum[-1].isdigit() else snum[-1]]
    return float(snum if snum[-1].isdigit() else snum[:-1])*power


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_frac(snum):
    r"""
    Returns the fractional part of a number represented in engineering notation

    :param snum: Number
    :type  snum: :ref:`EngineeringNotationNumber`

    :rtype: integer

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for putil.eng.peng_frac

    :raises: RuntimeError (Argument \`snum\` is not valid)

    .. [[[end]]]

    For example:

        >>> import putil.eng
        >>> putil.eng.peng_frac(putil.eng.peng(1235.6789E3, 3, False))
        236
    """
    snum = snum.rstrip()
    pindex = snum.find('.')
    if pindex == -1:
        return 0
    else:
        return (
            int(snum[pindex+1:] if snum[-1].isdigit() else snum[pindex+1:-1])
        )


def peng_int(snum):
    r"""
    Returns the integer part of a number represented in engineering notation

    :param snum: Number
    :type  snum: :ref:`EngineeringNotationNumber`

    :rtype: integer

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for putil.eng.peng_int

    :raises: RuntimeError (Argument \`snum\` is not valid)

    .. [[[end]]]

    For example:

        >>> import putil.eng
        >>> putil.eng.peng_int(putil.eng.peng(1235.6789E3, 3, False))
        1
    """
    return int(peng_mant(snum))


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_mant(snum):
    r"""
    Returns the mantissa of a number represented in engineering notation

    :param snum: Number
    :type  snum: :ref:`EngineeringNotationNumber`

    :rtype: float

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for putil.eng.peng_mant

    :raises: RuntimeError (Argument \`snum\` is not valid)

    .. [[[end]]]

    For example:

        >>> import putil.eng
        >>> putil.eng.peng_mant(putil.eng.peng(1235.6789E3, 3, False))
        1.236
    """
    snum = snum.rstrip()
    return float(snum if snum[-1].isdigit() else snum[:-1])


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_power(snum):
    r"""
    Returns  engineering suffix and floating point equivalent of the
    suffix when a number is represented in engineering notation.
    :py:func:`putil.eng.peng` lists the correspondence between suffix and
    floating point exponent.

    :param snum: Number
    :type  snum: :ref:`EngineeringNotationNumber`

    :rtype: named tuple in which the first item is the engineering suffix and
            the second item is the floating point equivalent of the suffix
            when the number is represented in engineering notation.


    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for putil.eng.peng_power

    :raises: RuntimeError (Argument \`snum\` is not valid)

    .. [[[end]]]

    For example:

        >>> import putil.eng
        >>> putil.eng.peng_power(putil.eng.peng(1235.6789E3, 3, False))
        EngPower(suffix='M', exp=1000000.0)
    """
    suffix = ' ' if snum[-1].isdigit() else snum[-1]
    return ENGPOWER(suffix, _SUFFIX_POWER_DICT[suffix])


@putil.pcontracts.contract(snum='engineering_notation_number')
def peng_suffix(snum):
    r"""
    Returns the suffix of a number represented in engineering notation

    :param snum: Number
    :type  snum: :ref:`EngineeringNotationNumber`

    :rtype: string

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for putil.eng.peng_suffix

    :raises: RuntimeError (Argument \`snum\` is not valid)

    .. [[[end]]]

    For example:

        >>> import putil.eng
        >>> putil.eng.peng_suffix(putil.eng.peng(1235.6789E3, 3, False))
        'M'
    """
    snum = snum.rstrip()
    return ' ' if snum[-1].isdigit() else snum[-1]


@putil.pcontracts.contract(suffix='engineering_notation_suffix', offset=int)
def peng_suffix_math(suffix, offset):
    r"""
    Returns an engineering suffix based on a starting suffix and an offset of
    number of suffixes

    :param suffix: Engineering suffix
    :type  suffix: :ref:`EngineeringNotationSuffix`

    :param offset: Engineering suffix offset
    :type  offset: integer

    :rtype: string

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.eng.peng_suffix_math

    :raises:
     * RuntimeError (Argument \`offset\` is not valid)

     * RuntimeError (Argument \`suffix\` is not valid)

     * ValueError (Argument \`offset\` is not valid)

    .. [[[end]]]

    For example:

        >>> import putil.eng
        >>> putil.eng.peng_suffix_math('u', 6)
        'T'
    """
    # pylint: disable=W0212,W0631
    exhobj = putil.exh.get_or_create_exh_obj()
    exhobj.add_exception(
        exname='invalid_offset',
        extype=ValueError,
        exmsg='Argument `offset` is not valid'
    )
    try:
        return _POWER_TO_SUFFIX_DICT[_SUFFIX_TO_POWER_DICT[suffix]+3*offset]
    except KeyError:
        exhobj.raise_exception_if(exname='invalid_offset', condition=True)


def round_mantissa(arg, decimals=0):
    """
    Rounds the fractional part of a floating point number mantissa or Numpy
    vector of floating point numbers to a given number of digits. Integers are
    not altered. The mantissa used is that of the floating point number(s)
    when expressed in `normalized scientific notation
    <https://en.wikipedia.org/wiki/Scientific_notation#Normalized_notation>`_

    :param arg: Input data
    :type  arg: integer, float, Numpy vector of integers or floats, or None

    :param decimals: Number of digits to round the fractional part of the
                     mantissa to.
    :type  decimals: integer

    :rtype: same as **arg**

    For example::

        >>> import putil.eng
        >>> putil.eng.round_mantissa(012345678E-6, 3)
        12.35
        >>> putil.eng.round_mantissa(5, 3)
        5
    """
    if arg is None:
        return arg
    if isinstance(arg, numpy.ndarray):
        foi = [isinstance(item, int) for item in arg]
        return numpy.array(
            [
                item
                if isint else
                float(to_scientific_string(item, decimals))
                for isint, item in zip(foi, arg)
            ]
        )
    if isinstance(arg, int):
        return arg
    return float(to_scientific_string(arg, decimals))


def pprint_vector(vector, limit=False, width=None, indent=0,
                  eng=False, frac_length=3):
    r"""
    Formats a list of numbers (vector) or a Numpy vector for printing. If the
    argument **vector** is :code:`None` the string :code:`'None'` is returned

    :param vector: Vector to pretty print or None
    :type  vector: list of integers or floats, Numpy vector or None

    :param limit: Flag that indicates whether at most 6 vector items are
                  printed (all vector items if its length is equal or less
                  than 6, first and last 3 vector items if it is not) (True),
                  or the entire vector is printed (False)
    :type  limit: boolean

    :param width: Number of available characters per line. If None the vector
                  is printed in one line
    :type  width: integer or None

    :param indent: Flag that indicates whether all subsequent lines after the
                   first one are indented (True) or not (False). Only relevant
                   if **width** is not None
    :type  indent: boolean

    :param eng: Flag that indicates whether engineering notation is used
                (True) or not (False)
    :type  eng: boolean

    :param frac_length: Number of digits of fractional part (only applicable
                        if **eng** is True)
    :type  frac_length: integer

    :raises: ValueError (Argument \`width\` is too small)

    :rtype: string

    For example:

        >>> from __future__ import print_function
        >>> import putil.eng
        >>> header = 'Vector: '
        >>> data = [1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 8, 9]
        >>> print(
        ...     header+putil.eng.pprint_vector(
        ...         data,
        ...         width=30,
        ...         eng=True,
        ...         frac_length=1,
        ...         limit=True,
        ...         indent=len(header)
        ...     )
        ... )
        Vector: [    1.0m,   20.0u,  300.0M,
                             ...
                   700.0 ,    8.0 ,    9.0  ]
        >>> print(
        ...     header+putil.eng.pprint_vector(
        ...         data,
        ...         width=30,
        ...         eng=True,
        ...         frac_length=0,
        ...         indent=len(header)
        ...     )
        ... )
        Vector: [    1m,   20u,  300M,    4p,
                     5k,   -6n,  700 ,    8 ,
                     9  ]
        >>> print(putil.eng.pprint_vector(data, eng=True, frac_length=0))
        [    1m,   20u,  300M,    4p,    5k,   -6n,  700 ,    8 ,    9  ]
        >>> print(putil.eng.pprint_vector(data, limit=True))
        [ 0.001, 2e-05, 300000000.0, ..., 700, 8, 9 ]
    """
    # pylint: disable=R0912,R0913,R0914
    def _str(*args):
        """
        Converts numbers to string, optionally represented
        in engineering notation
        """
        ret = [
            str(element)
            if not eng else
            putil.eng.peng(element, frac_length, True)
            for element in args
        ]
        return ret[0] if len(ret) == 1 else ret
    if vector is None:
        return 'None'
    if (not limit) or (limit and (len(vector) < 7)):
        uret = '[ {0} ]'.format(', '.join(_str(*vector)))
    else:
        uret = '[ {0}, ..., {1} ]'.format(
            ', '.join(_str(*vector[:3])), ', '.join(_str(*vector[-3:])),
        )
    if (width is None) or (len(uret) < width):
        return uret
    # Figure out how long the first line needs to be
    wobj = textwrap.TextWrapper(
        initial_indent='[ ',
        width=width,
        subsequent_indent=' '*(indent+2)
    )
    # uret[2:] -> do not include initial '[ ' as this is specified as
    # the initial indent to the text wrapper
    rlist = wobj.wrap(uret[2:])
    first_line = rlist[0]
    elements_per_row = first_line.count(',')
    if elements_per_row == 0:
        raise ValueError('Argument `width` is too small')
    # "Manually" format limit output so that it is either 3 lines, first and
    # last line with 3 elements and the middle with '...' or 7 lines, each with
    # 1 element and the middle with '...'
    # If numbers are not to be aligned at commas (variable width) then use the
    # existing results of the wrap() function
    if limit:
        if elements_per_row < 3:
            rlist = [
                '[ {0},'.format(_str(vector[0])),
                _str(vector[1]),
                _str(vector[2]),
                '...',
                _str(vector[-3]),
                _str(vector[-2]),
                '{0} ]'.format(_str(vector[-1]))
            ]
            elements_per_row = 1
        else:
            rlist = [
                '[ {0},'.format(', '.join(_str(*vector[:3]))),
                '...',
                '{0} ]'.format(', '.join(_str(*vector[-3:]))),
            ]
        first_line = rlist[0]
    if not eng:
        return '\n'.join(rlist)
    # Align elements across multiple lines
    if limit:
        remainder_list = [line.lstrip() for line in rlist[1:]]
    else:
        remainder_list = _split_every(
            text=uret[len(first_line):],
            sep=',',
            count=elements_per_row,
            lstrip=True
        )
    first_comma_index = first_line.find(',')
    actual_width = len(first_line)-2
    new_wrapped_lines_list = [first_line]
    for line in remainder_list[:-1]:
        new_wrapped_lines_list.append(
            '{0},'.format(line).rjust(actual_width)
            if line != '...' else
            line.center(actual_width).rstrip()
        )
    # Align last line on fist comma (if it exists) or
    # on length of field if does not
    if remainder_list[-1].find(',') == -1:
        marker = len(remainder_list[-1])-2
    else:
        marker = remainder_list[-1].find(',')
    new_wrapped_lines_list.append(
        '{0}{1}'.format(
            (first_comma_index-marker-2)*' ',
            remainder_list[-1]
        )
    )
    return '\n'.join(
        [
            '{spaces}{line}'.format(spaces=' '*(indent+2), line=line)
            if num > 0 else
            line
            for num, line in enumerate(new_wrapped_lines_list)
        ]
    )


def to_scientific_string(
        number,
        frac_length=None,
        exp_length=None,
        sign_always=False
    ):
    """
    Converts a number or a string representing a number to a string with the
    number expressed in scientific notation. Full precision is maintained if
    the number is represented as a string

    :param number: Number to convert
    :type  number: number or string

    :param frac_length: Number of digits of fractional part, None indicates
                        that the fractional part of the number should not be
                        limited
    :type  frac_length: integer or None

    :param exp_length: Number of digits of the exponent; the actual length of
                       the exponent takes precedence if it is longer
    :type  exp_length: integer or None

    :param sign_always: Flag that indicates whether the sign always
                        precedes the number for both non-negative and negative
                        numbers (True) or only for negative numbers (False)
    :type  sign_always: boolean

    :rtype: string

    For example:

        >>> import putil.eng
        >>> putil.eng.to_scientific_string(333)
        '3.33E+2'
        >>> putil.eng.to_scientific_string(0.00101)
        '1.01E-3'
        >>> putil.eng.to_scientific_string(99.999, 1, 2, True)
        '+1.0E+02'
    """
    exp_length = 0 if not exp_length else exp_length
    mant, exp = to_scientific_tuple(number)
    fmant = float(mant)
    if (not frac_length) or (fmant == int(fmant)):
        return '{sign}{mant}{period}{zeros}E{exp_sign}{exp}'.format(
            sign='+' if sign_always and (fmant >= 0) else '',
            mant=mant,
            period='.' if frac_length else '',
            zeros='0'*frac_length if frac_length else '',
            exp_sign='-' if exp < 0 else '+',
            exp=str(abs(exp)).rjust(exp_length, '0')
        )
    rounded_mant = round(fmant, frac_length)
    # Avoid infinite recursion when rounded mantissa is _exactly_ 10
    if abs(rounded_mant) == 10:
        rounded_mant = fmant = -1.0 if number < 0 else 1.0
        frac_length = 1
        exp = exp+1
    zeros = 2+(1 if (fmant < 0) else 0)+frac_length-len(str(rounded_mant))
    return '{sign}{mant}{zeros}E{exp_sign}{exp}'.format(
        sign='+' if sign_always and (fmant >= 0) else '',
        mant=rounded_mant,
        zeros='0'*zeros,
        exp_sign='-' if exp < 0 else '+',
        exp=str(abs(exp)).rjust(exp_length, '0')
    )


def to_scientific_tuple(number):
    """
    Returns mantissa and exponent of a number when expressed in
    scientific notation. Full precision is maintained if the number is
    represented as a string

    :param number: Number
    :type  number: integer, float or string

    :rtype: named tuple in which the first item is the mantissa (*string*)
            and the second item is the exponent (*integer*) of the number
            when expressed in scientific notation

    For example:

        >>> import putil.eng
        >>> putil.eng.to_scientific_tuple('135.56E-8')
        NumComp(mant='1.3556', exp=-6)
        >>> putil.eng.to_scientific_tuple(0.0000013556)
        NumComp(mant='1.3556', exp=-6)
    """
    # pylint: disable=W0632
    convert = not isinstance(number, str)
    # Detect zero and return, simplifies subsequent algorithm
    if ((convert and (number == 0)) or
       ((not convert) and (not number.strip('0').strip('.')))):
        return ('0', 0)
    # Break down number into its components, use Decimal type to
    # preserve resolution:
    # sign  : 0 -> +, 1 -> -
    # digits: tuple with digits of number
    # exp   : exponent that gives null fractional part
    sign, digits, exp = Decimal(str(number) if convert else number).as_tuple()
    mant = '{sign}{itg}{frac}'.format(
        sign='-' if sign else '',
        itg=digits[0],
        frac=(
            '.{frac}'.format(frac=''.join([str(num) for num in digits[1:]]))
            if len(digits) > 1 else
            ''
        )
    ).rstrip('0').rstrip('.')
    exp += len(digits)-1
    return NUMCOMP(mant, exp)
