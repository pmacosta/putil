# functions.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,F0401,R0914,W0105,W0212,W0611

import math
import numpy
import matplotlib.pyplot as plt
import sys

import putil.eng
import putil.misc
import putil.pcontracts
from .constants import PRECISION, MIN_TICKS, SUGGESTED_MAX_TICKS
if sys.version_info.major == 2: # pragma: no cover
    from .datasource2 import DataSource
else:   # pragma: no cover
    from .datasource3 import DataSource


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
if sys.version_info.major == 2:
    import __builtin__
else:
    import builtins as __builtin__
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_plot_functions
exobj_plot = trace_ex_plot_functions.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
def _process_ticks(locs, min_lim, max_lim, mant):
    """
    Returns pretty-printed tick locations that are within the given bound
    """
    locs = [float(loc) for loc in locs]
    bounded_locs = [
        loc
        for loc in locs
        if ((loc >= min_lim) or (abs(loc-min_lim) <= 1e-14)) and
           ((loc <= max_lim) or (abs(loc-max_lim) <= 1e-14))
    ]
    raw_labels = [
        putil.eng.peng(float(loc), mant, rjust=False)
        if ((abs(loc) >= 1) or (loc == 0)) else
        str(putil.eng.round_mantissa(loc, mant))
        for loc in bounded_locs
    ]
    return (
        bounded_locs,
        [label.replace('u', '$\\mu$') for label in raw_labels]
    )


def _intelligent_ticks(series, series_min, series_max,
                       tight=True, log_axis=False, tick_list=None):
    """
    Calculates ticks 'intelligently', trying to calculate sane tick spacing
    """
    # pylint: disable=E1103,R0912,R0913,R0915
    if tick_list is not None:
        tick_list = (
            numpy.array(tick_list)
            if isinstance(tick_list, list) else
            tick_list
        )
        tick_list = numpy.sort(tick_list)
    elif (not tick_list) and (len(series) == 1):
        # Handle 1-point series
        series_min = series_max = series[0]
        tick_spacing = putil.eng.round_mantissa(0.1*series[0], PRECISION)
        tick_list = numpy.array([
            series[0]-tick_spacing, series[0], series[0]+tick_spacing
        ])
        tick_spacing = putil.eng.round_mantissa(0.1*series[0], PRECISION)
        tight = tight_left = tight_right = log_axis = False
    elif not tick_list:
        if log_axis:
            dec_start = int(math.log10(min(series)))
            dec_stop = int(math.ceil(math.log10(max(series))))
            tick_list = [10**num for num in range(dec_start, dec_stop+1)]
            tight_left = not ((not tight) and (tick_list[0] >= min(series)))
            tight_right = not ((not tight) and (tick_list[-1] <= max(series)))
            tick_list = numpy.array(tick_list)
        else:
            # Try to find the tick spacing that will have the most number of
            # data points on grid. Otherwise, place max_ticks uniformly
            # distributed across the data rage
            series_delta = putil.eng.round_mantissa(
                max(series)-min(series), PRECISION\
            )
            working_series = series[:].tolist()
            tick_list = list()
            num_ticks = SUGGESTED_MAX_TICKS
            while (num_ticks >= MIN_TICKS) and (len(working_series) > 1):
                data_spacing = [
                    putil.eng.round_mantissa(element, PRECISION)
                    for element in numpy.diff(working_series)
                ]
                tick_spacing = putil.misc.gcd(data_spacing)
                num_ticks = (
                    (series_delta/tick_spacing)+1
                    if tick_spacing else
                    MIN_TICKS
                )
                if ((num_ticks >= MIN_TICKS) and
                   (num_ticks <= SUGGESTED_MAX_TICKS)):
                    tick_list = numpy.linspace(
                        putil.eng.round_mantissa(min(series), PRECISION),
                        putil.eng.round_mantissa(max(series), PRECISION),
                        num_ticks
                    ).tolist()
                    break
                # Remove elements that cause minimum spacing, to see if with
                # those elements removed the number of tick marks can be
                # withing the acceptable range
                min_data_spacing = min(data_spacing)
                # Account for fact that if minimum spacing is between last two
                # elements, the last element cannot be removed (it is the end
                # of the range), but rather the next-to-last has to be removed
                if ((data_spacing[-1] == min_data_spacing) and
                   (len(working_series) > 2)):
                    working_series = working_series[:-2]+[working_series[-1]]
                    data_spacing = [
                        putil.eng.round_mantissa(element, PRECISION)
                        for element in numpy.diff(working_series)
                    ]
                working_series = [working_series[0]]+[
                    element
                    for element, spacing in zip(working_series[1:], data_spacing)
                    if spacing != min_data_spacing
                ]
            tick_list = (tick_list
                        if len(tick_list) > 0 else
                        numpy.linspace(
                            min(series),
                            max(series),
                            SUGGESTED_MAX_TICKS
                        ).tolist())
            tick_spacing = putil.eng.round_mantissa(
                tick_list[1]-tick_list[0],
                PRECISION
            )
            # Account for interpolations, whose curves might have values above
            # or below the data points. Only add an extra tick, otherwise let
            # curve go above/below panel
            tight_left = (False
                         if (not tight) and (tick_list[0] >= series_min) else
                         tight)
            tight_right = (False
                          if (not tight) and (tick_list[-1] <= series_max) else
                          tight)
            tick_list = (numpy.array(
                tick_list
                if tight else
                ([tick_list[0]-tick_spacing] if not tight_left else [])+
                tick_list+
                ([tick_list[-1]+tick_spacing] if not tight_right else [])
            ))
    # Scale series with minimum, maximum and delta as reference, pick
    # scaling option that has the most compact representation
    opt_min = _scale_ticks(tick_list, 'MIN')
    opt_max = _scale_ticks(tick_list, 'MAX')
    opt_delta = _scale_ticks(tick_list, 'DELTA')
    opt = (opt_min
          if (opt_min['count'] <= opt_max['count']) and
             (opt_min['count'] <= opt_delta['count']) else
          (
              opt_max
              if (opt_max['count'] <= opt_min['count']) and
                 (opt_max['count'] <= opt_delta['count']) else
              opt_delta
    ))
    # Add extra room in logarithmic axis if Tight is True, but do not
    # label marks (aesthetic decision)
    if log_axis and not tight:
        if not tight_left:
            opt['min'] = putil.eng.round_mantissa(
                0.9*opt['loc'][0], PRECISION
            )
            opt['loc'].insert(0, opt['min'])
            opt['labels'].insert(0, '')
        if not tight_right:
            opt['max'] = putil.eng.round_mantissa(
                1.1*opt['loc'][-1], PRECISION
            )
            opt['loc'].append(opt['max'])
            opt['labels'].append('')
    return (
        opt['loc'],
        opt['labels'],
        opt['min'],
        opt['max'],
        opt['scale'],
        opt['unit'].replace('u', '$\\mu$')
    )


def _scale_ticks(tick_list, mode):
    """
    Scale series taking the reference to be the series start, stop or delta
    """
    mode = mode.strip().upper()
    tick_min = tick_list[0]
    tick_max = tick_list[-1]
    tick_delta = tick_max-tick_min
    tick_ref = (tick_min
               if mode == 'MIN' else
               (tick_max if mode == 'MAX' else tick_delta))
    (unit, scale) = putil.eng.peng_power(putil.eng.peng(tick_ref, 3))
    # Move one engineering unit back if there are more ticks
    # below 1.0 than above it
    above_1k_sum = sum((tick_list/scale) >= 1000)
    below_1k_sum = sum((tick_list/scale) < 1000)
    last_tick_below_10k = tick_list[-1]/scale < 10000
    rollback = (above_1k_sum > below_1k_sum) and last_tick_below_10k
    scale = 1 if rollback else scale
    unit = putil.eng.peng_suffix_math(unit, +1) if rollback else unit
    tick_list = numpy.array([
        putil.eng.round_mantissa(element/scale, PRECISION)
        for element in tick_list
    ])
    tick_min = putil.eng.round_mantissa(tick_min/scale, PRECISION)
    tick_max = putil.eng.round_mantissa(tick_max/scale, PRECISION)
    loc, labels = _uniquify_tick_labels(tick_list, tick_min, tick_max)
    count = len(''.join(labels))
    return {
        'loc':loc,
        'labels':labels,
        'unit':unit,
        'scale':scale,
        'min':tick_min,
        'max':tick_max,
        'count':count
    }


def _uniquify_tick_labels(tick_list, tmin, tmax):
    """ Calculate minimum tick mantissa given tick spacing """
    # If minimum or maximum has a mantissa, at least preserve one digit
    mant_min = (1
               if any([
                       float(item) != float(int(item)) for item in tick_list
               ]) else
               0)
    # Step 1: Look at two contiguous ticks and lower mantissa digits till
    # they are no more right zeros
    mant = 10
    for mant in range(10, mant_min-1, -1):
        ldig = str(putil.eng.peng_frac(putil.eng.peng(tick_list[-1], mant)))[-1]
        nldig = str(putil.eng.peng_frac(putil.eng.peng(tick_list[-2], mant)))[-1]
        if (ldig != '0') or (nldig != '0'):
            break
    # Step 2: Confirm labels are unique
    #unique_mant_found = False
    while mant >= mant_min:
        loc, labels = _process_ticks(tick_list, tmin, tmax, mant)
        if ((sum([
                1
                if labels[index] != labels[index+1] else
                0
                for index in range(0, len(labels[:-1]))]) == len(labels)-1
            ) and
            (sum([
                1 if (putil.eng.peng_float(label) != 0) or
                     ((putil.eng.peng_float(label) == 0) and (num == 0)) else
                0
                for num, label in zip(tick_list, labels)]) == len(labels))):
            #unique_mant_found = True
            mant -= 1
        else:
            mant += 1
            #if unique_mant_found:
            loc, labels = _process_ticks(tick_list, tmin, tmax, mant)
            break
    return (
        [putil.eng.round_mantissa(element, PRECISION) for element in loc],
        labels
    )


@putil.pcontracts.contract(
    param_list='list(int|float)',
    offset='offset_range',
    color_space='color_space_option'
)
def parameterized_color_space(param_list, offset=0, color_space='binary'):
    r"""
    Computes a color space where lighter colors correspond to lower
    parameter values

    :param  param_list:     parameter values
    :type   param_list:     list
    :param  offset:         offset of the first (lightest) color
    :type   offset:         :ref:`OffsetRange`
    :param  color_space:    color palette (case sensitive)
    :type   color_space:    :ref:`ColorSpaceOption`
    :rtype:                 Matplotlib color

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.functions.parameterized_color_space

    :raises:
     * RuntimeError (Argument \`color_space\` is not valid)

     * RuntimeError (Argument \`offset\` is not valid)

     * RuntimeError (Argument \`param_list\` is not valid)

     * TypeError (Argument \`param_list\` is empty)

     * ValueError (Argument \`color_space\` is not one of 'binary', 'Blues',
       'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu',
       'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu',
       'YlOrBr' or 'YlOrRd' (case insensitive))

    .. [[[end]]]
    """
    # pylint: disable=E1101
    color_space_name_list = [
        'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys',
        'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu',
        'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd'
    ]
    _exh = putil.exh.get_or_create_exh_obj()
    _exh.add_exception(
        exname='par_list_empty',
        extype=TypeError,
        exmsg='Argument `param_list` is empty'
    )
    _exh.raise_exception_if(
        exname='par_list_empty',
        condition=len(param_list) == 0
    )
    color_pallette_list = [
        plt.cm.binary, plt.cm.Blues, plt.cm.BuGn, plt.cm.BuPu, plt.cm.GnBu,
        plt.cm.Greens, plt.cm.Greys, plt.cm.Oranges, plt.cm.OrRd, plt.cm.PuBu,
        plt.cm.PuBuGn, plt.cm.PuRd, plt.cm.Purples, plt.cm.RdPu, plt.cm.Reds,
        plt.cm.YlGn, plt.cm.YlGnBu, plt.cm.YlOrBr, plt.cm.YlOrRd
    ]
    color_dict = dict(zip(color_space_name_list, color_pallette_list))
    return [
        color_dict[color_space](putil.misc.normalize(value, param_list, offset))
        for value in param_list
    ]


def _check_real_numpy_vector(obj):
    if ((type(obj) == numpy.ndarray) and
       (len(obj.shape) == 1) and (obj.shape[0] > 0) and
       ((obj.dtype.type == numpy.array([0]).dtype.type) or
       (obj.dtype.type == numpy.array([0.0]).dtype.type))):
        return False
    return True


def _check_increasing_real_numpy_vector(obj):
    # pylint: disable=C0103
    if ((type(obj) != numpy.ndarray) or ((type(obj) == numpy.ndarray) and
       ((len(obj.shape) > 1) or ((len(obj.shape) == 1) and
       (obj.shape[0] == 0))))):
        return True
    if (((obj.dtype.type == numpy.array([0]).dtype.type) or
       (obj.dtype.type == numpy.array([0.0]).dtype.type)) and
       ((obj.shape[0] == 1) or ((obj.shape[0] > 1) and
       (not min(numpy.diff(obj)) <= 0)))):
        return False
    return True
