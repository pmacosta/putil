# compat2.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0122,W0613


def _rwtb(extype, exmsg, extb): # pragma: no cover
    """ Python 2 exception raising with traceback """
    exec('raise extype, exmsg, extb')


def _raise_exception(exception_object):
    """ Raise exception with short traceback """
    raise exception_object


def _read(fname):
    """ Read data from file """
    with open(fname, 'r') as frobj:
        return frobj.read()


def _write(fobj, data):
    """ Write data to file """
    fobj.write(data)


def _ex_type_str(exobj):
    """ Returns a string corresponding to the exception type """
    return str(exobj).split('.')[-1][:-2]


def _get_func_code(obj):
    """ Get funcion code """
    return obj.func_code


def _get_ex_msg(obj):
    """ Get exception message """
    return obj.value.message if hasattr(obj, 'value') else obj.message


def _unicode_char(char):
    """ Returns true if character is Unicode (non-ASCII) character """
    try:
        char.encode('ascii')
    except UnicodeDecodeError:
        return True
    return False
