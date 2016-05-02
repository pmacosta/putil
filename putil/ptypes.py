# ptypes.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0916

# Standard library imports
import math
# PyPI imports
import numpy
import pexdoc.pcontracts


###
# Global variables
###
_SUFFIX_TUPLE = (
    'y', 'z', 'a', 'f', 'p', 'n', 'u', 'm',
    ' ',
    'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'
)


###
# Functions
###
def _check_csv_col_filter(obj):
    if (not isinstance(obj, bool)) and ((obj is None) or
       isinstance(obj, str) or isinstance(obj, int) or
       (isinstance(obj, list) and (len(obj) > 0) and
       all([(isinstance(item, str) or isinstance(item, int)) and
       (not isinstance(item, bool)) for item in obj]))):
        return False
    return True


def _check_csv_row_filter(obj):
    # pylint: disable=R0911
    if obj is None:
        return 0
    if not isinstance(obj, dict):
        return 1
    if not len(obj):
        return 2
    if any(
            [
                not (isinstance(col_name, str) or isinstance(col_name, int))
                for col_name in obj.keys()
            ]
    ):
        return 1
    for col_name, col_value in obj.items(): # pragma: no branch
        if ((not isinstance(obj[col_name], list)) and
           (not _isnumber(obj[col_name])) and
           (not isinstance(obj[col_name], str))):
            return 1
        if isinstance(col_value, list):
            for element in col_value:   # pragma: no branch
                if ((not _isnumber(element)) and
                   (not isinstance(element, str))):
                    return 1
    return 0


def _check_increasing_real_numpy_vector(obj):
    # pylint: disable=C0103
    if (isinstance(obj, numpy.ndarray) and
       (len(obj.shape) == 1) and (obj.shape[0] > 0)):
        otype = obj.dtype.name
        result = any(
            [otype.startswith(item) for item in ('int', 'float')]
        )
        return not (
            bool(result)
            and
            (
                (obj.shape[0] == 1)
                or
                ((obj.shape[0] > 1) and (min(numpy.diff(obj)) > 0))
            )
        )
    return True


def _check_number_numpy_vector(obj):
    if (isinstance(obj, numpy.ndarray) and
       (len(obj.shape) == 1) and (obj.shape[0] > 0)):
        otype = obj.dtype.name
        result = any(
            [otype.startswith(item) for item in ('int', 'float', 'complex')]
        )
        return not bool(result)
    return True


def _check_real_numpy_vector(obj):
    if (isinstance(obj, numpy.ndarray) and
       (len(obj.shape) == 1) and (obj.shape[0] > 0)):
        otype = obj.dtype.name
        result = any(
            [otype.startswith(item) for item in ('int', 'float')]
        )
        return not bool(result)
    return True


def _homogenize_data_filter(dfilter):
    """
    Make data filter definition consistent, create a
    tuple where first element is the row filter and
    the second element is the column filter
    """
    if (dfilter is None) or (dfilter == (None, None)) or (dfilter == (None, )):
        dfilter = (None, None)
    if (isinstance(dfilter, bool) or (not any(
            [
                isinstance(dfilter, item) for item in
                [tuple, dict, str, int, list]
            ]))):
        dfilter = (2.0, 2.0)
    if isinstance(dfilter, tuple) and (len(dfilter) == 1):
        dfilter = (dfilter[0], None)
    elif isinstance(dfilter, dict):
        dfilter = (dfilter, None)
    elif (isinstance(dfilter, str) or (isinstance(dfilter, int) and
         (not isinstance(dfilter, bool))) or isinstance(dfilter, list)):
        dfilter = (None, dfilter if isinstance(dfilter, list) else [dfilter])
    elif (isinstance(dfilter[0], dict) or ((dfilter[0] is None) and
         (not isinstance(dfilter[1], dict)))):
        pass
    else:
        dfilter = (dfilter[1], dfilter[0])
    return dfilter


def _isnumber(obj):
    """
    Function copied from pmisc module to avoid
    import loops
    """
    return (
        (((obj is not None) and
        (not isinstance(obj, bool)) and
        (isinstance(obj, int) or
        isinstance(obj, float) or
        isinstance(obj, complex))))
    )


@pexdoc.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    argument_bad_choice=(
        ValueError,
        (
            "Argument `*[argument_name]*` is not one of 'binary', 'Blues', "
            "'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', "
            "'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', "
            "'YlGnBu', 'YlOrBr' or 'YlOrRd' (case insensitive)"
        )
    )
)
def color_space_option(obj):
    r"""
    Validates if an object is a ColorSpaceOption pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the name of the argument the contract
       is attached to

     * RuntimeError (Argument \`*[argument_name]*\` is not one of 'binary',
       'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd',
       'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu',
       'YlOrBr' or 'YlOrRd). The token \*[argument_name]\* is replaced by the
       name of the argument the contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    if (obj is not None) and (not isinstance(obj, str)):
        raise ValueError(exdesc['argument_invalid'])
    if (obj is None) or (obj and any([
            item.lower() == obj.lower()
            for item in [
                    'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens',
                    'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd',
                    'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu',
                    'YlOrBr', 'YlOrRd'
            ]
    ])):
        return None
    raise ValueError(exdesc['argument_bad_choice'])


@pexdoc.pcontracts.new_contract()
def csv_col_filter(obj):
    r"""
    Validates if an object is a CsvColFilter pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the *name* of the argument the
       contract is attached to

    :rtype: None
    """
    if _check_csv_col_filter(obj):
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def csv_col_sort(obj):
    r"""
    Validates if an object is a CsvColSort pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the *name* of the argument the
       contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    obj = obj if isinstance(obj, list) else [obj]
    if len(obj) == 0:
        raise ValueError(exdesc)
    for item in obj:
        # Weed out items not having the right basic types
        if isinstance(item, bool) or ((not isinstance(item, str))
           and (not isinstance(item, int)) and (not isinstance(item, dict))):
            raise ValueError(exdesc)
        # If it is a dictionary, the key has to be a valid column name and the
        # sort order has to be either 'A' (for ascending) or 'D' (for
        # descending), case insensitive
        if isinstance(item, dict):
            keys = list(item.keys())
            if (len(keys) > 1) or ((len(keys) == 1) and
               ((not isinstance(keys[0], int)) and
               (not isinstance(keys[0], str)))):
                raise ValueError(exdesc)
            value = item[keys[0]]
            if value not in ['A', 'D', 'a', 'd']:
                raise ValueError(exdesc)


@pexdoc.pcontracts.new_contract()
def csv_data_filter(obj):
    r"""
    Validates if an object is a CsvDataFilter pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the *name* of the argument the
       contract is attached to

    :rtype: None
    """
    if isinstance(obj, tuple) and len(obj) > 2:
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    else:
        obj = _homogenize_data_filter(obj)
    row_value = _check_csv_row_filter(obj[0])
    col_value = _check_csv_col_filter(obj[1])
    if col_value or (row_value != 0):
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def csv_filtered(obj):
    r"""
    Validates if an object is a CsvFilter pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the *name* of the argument the
       contract is attached to

    :rtype: None
    """
    if obj in [True, False, 'B', 'b', 'C', 'c', 'R', 'r', 'N', 'n']:
        return None
    raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    argument_empty=(ValueError, 'Argument `*[argument_name]*` is empty')
)
def csv_row_filter(obj):
    r"""
    Validates if an object is a CsvRowFilter pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the *name* of the argument the
       contract is attached to

     * ValueError (Argument \`*[argument_name]*\` is empty). The token
       \*[argument_name]\* is replaced by the *name* of the argument the
       contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    ecode = _check_csv_row_filter(obj)
    if ecode == 1:
        raise ValueError(exdesc['argument_invalid'])
    elif ecode == 2:
        raise ValueError(exdesc['argument_empty'])


@pexdoc.pcontracts.new_contract()
def engineering_notation_number(obj):
    r"""
    Validates if an object is an EngineeringNotationNumber pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    try:
        obj = obj.rstrip()
        float(obj[:-1] if obj[-1] in _SUFFIX_TUPLE else obj)
        return None
    except (AttributeError, IndexError, ValueError):
        # AttributeError: obj.rstrip(), object could not be a string
        # IndexError: obj[-1], when an empty string
        # ValueError: float(), when not a string representing a number
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def engineering_notation_suffix(obj):
    r"""
    Validates if an object is an EngineeringNotationSuffix pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the *name* of the argument the
     contract is attached to

    :rtype: None
    """
    try:
        assert obj in _SUFFIX_TUPLE
    except AssertionError:
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def increasing_real_numpy_vector(obj):
    r"""
    Validates if an object is IncreasingRealNumpyVector pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if _check_increasing_real_numpy_vector(obj):
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    argument_bad_choice=(
        ValueError,
        (
            "Argument `*[argument_name]*` is not one of ['STRAIGHT', 'STEP', "
            "'CUBIC', 'LINREG'] (case insensitive)"
        )
    )
)
def interpolation_option(obj):
    r"""
    Validates if an object is an InterpolationOption pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the name of the argument the contract
       is attached to

     * RuntimeError (Argument \`*[argument_name]*\` is not one of ['STRAIGHT',
       'STEP', 'CUBIC', 'LINREG'] (case insensitive)). The token
       \*[argument_name]\* is replaced by the name of the argument
       the contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    if (obj is not None) and (not isinstance(obj, str)):
        raise ValueError(exdesc['argument_invalid'])
    if ((obj is None) or
       (obj and any([
           item.lower() == obj.lower()
           for item in ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']]))):
        return None
    raise ValueError(exdesc['argument_bad_choice'])


@pexdoc.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    argument_bad_choice=(
        ValueError,
        "Argument `*[argument_name]*` is not one of ['-', '--', '-.', ':']"
    )
)
def line_style_option(obj):
    r"""
    Validates if an object is a LineStyleOption pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the name of the argument the contract
       is attached to

     * RuntimeError (Argument \`*[argument_name]*\` is not one of ['-', '--',
       '-.', ':']). The token \*[argument_name]\* is replaced by the name of
       the argument the contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    if (obj is not None) and (not isinstance(obj, str)):
        raise ValueError(exdesc['argument_invalid'])
    if obj in [None, '-', '--', '-.', ':']:
        return None
    raise ValueError(exdesc['argument_bad_choice'])


@pexdoc.pcontracts.new_contract()
def number_numpy_vector(obj):
    r"""
    Validates if an object is a NumberNumpyVector pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if _check_number_numpy_vector(obj):
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def real_numpy_vector(obj):
    r"""
    Validates if an object is a RealNumpyVector pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if _check_real_numpy_vector(obj):
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def touchstone_data(obj):
    r"""
    Validates if an object is an TouchstoneData pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if ((not isinstance(obj, dict)) or (isinstance(obj, dict) and
       (sorted(obj.keys()) != sorted(['points', 'freq', 'data'])))):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if not (isinstance(obj['points'], int) and (obj['points'] > 0)):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if _check_increasing_real_numpy_vector(obj['freq']):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if not isinstance(obj['data'], numpy.ndarray):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    vdata = ['int', 'float', 'complex']
    if not any([obj['data'].dtype.name.startswith(item) for item in vdata]):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if obj['freq'].size != obj['points']:
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    nports = int(math.sqrt(obj['data'].size/obj['freq'].size))
    if obj['points']*(nports**2) != obj['data'].size:
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    return None


@pexdoc.pcontracts.new_contract()
def touchstone_noise_data(obj):
    r"""
    Validates if an object is an TouchstoneNoiseData pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if isinstance(obj, dict) and (not obj):
        return None
    if ((not isinstance(obj, dict)) or (isinstance(obj, dict) and
       (sorted(obj.keys()) != sorted(['points', 'freq', 'nf', 'rc', 'res'])))):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if not (isinstance(obj['points'], int) and (obj['points'] > 0)):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if _check_increasing_real_numpy_vector(obj['freq']):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if _check_real_numpy_vector(obj['nf']):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if _check_number_numpy_vector(obj['rc']):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if not (isinstance(obj['res'], numpy.ndarray) and
       (len(obj['res'].shape) == 1) and (obj['res'].shape[0] > 0) and
       numpy.all(obj['res'] >= 0)):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    sizes = [obj['freq'].size, obj['nf'].size, obj['rc'].size, obj['res'].size]
    if set(sizes) != set([obj['points']]):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    return None


@pexdoc.pcontracts.new_contract()
def touchstone_options(obj):
    r"""
    Validates if an object is an TouchstoneOptions pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if ((not isinstance(obj, dict)) or (isinstance(obj, dict) and
       (sorted(obj.keys()) != sorted(['units', 'ptype', 'pformat', 'z0'])))):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if not ((obj['units'].lower() in ['ghz', 'mhz', 'khz', 'hz']) and
       (obj['ptype'].lower() in ['s', 'y', 'z', 'h', 'g']) and
       (obj['pformat'].lower() in ['db', 'ma', 'ri']) and
       isinstance(obj['z0'], float) and (obj['z0'] >= 0)):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    return None


@pexdoc.pcontracts.new_contract()
def wave_interp_option(obj):
    r"""
    Validates if an object is a WaveInterpOption pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    if not isinstance(obj, str):
        raise ValueError(exdesc)
    if obj.upper() in ['CONTINUOUS', 'STAIRCASE']:
        return None
    raise ValueError(exdesc)


@pexdoc.pcontracts.new_contract()
def wave_scale_option(obj):
    r"""
    Validates if an object is a WaveScaleOption pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    if not isinstance(obj, str):
        raise ValueError(exdesc)
    if obj.upper() in ['LINEAR', 'LOG']:
        return None
    raise ValueError(exdesc)


@pexdoc.pcontracts.new_contract()
def wave_vectors(obj):
    r"""
    Validates if an object is a WaveVectors pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    if not isinstance(obj, list) or (isinstance(obj, list) and not len(obj)):
        raise ValueError(exdesc)
    if any([not (isinstance(item, tuple) and len(item) == 2) for item in obj]):
        raise ValueError(exdesc)
    indep_vector, dep_vector = zip(*obj)
    if _check_increasing_real_numpy_vector(numpy.array(indep_vector)):
        raise ValueError(exdesc)
    if _check_real_numpy_vector(numpy.array(dep_vector)):
        raise ValueError(exdesc)
