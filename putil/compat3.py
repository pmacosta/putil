# compat3.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0122,W0613


###
# Functions
###
def _read(fname):
    """ Read data from file """
    with open(fname, 'r', newline='\r\n') as frobj:
        return frobj.read()


def _readlines(fname, fpointer1=open, fpointer2=open):  # pragma: no cover
    """ Read all lines from file """
    # fpointer1, fpointer2 arguments to ease testing
    try:
        with fpointer1(fname, 'r') as fobj:
            return fobj.readlines()
    except UnicodeDecodeError: # pragma: no cover
        with fpointer2(fname, 'r', encoding='utf-8') as fobj:
            return fobj.readlines()
    except: # pragma: no cover
        raise


def _unicode_to_ascii(obj):  # pragma: no cover
    # pylint: disable=E0602
    return obj


def _write(fobj, data):
    """ Write data to file """
    fobj.write(data)
