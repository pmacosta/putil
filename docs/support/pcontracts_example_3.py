# pcontracts_example_3.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0410,W0613,W0702

from __future__ import print_function
import os, putil.pcontracts

@putil.pcontracts.new_contract(ex1=(RuntimeError, 'Invalid name'))
def custom_contract1(arg):
    if not arg:
        raise ValueError(putil.pcontracts.get_exdesc())

@putil.pcontracts.new_contract(ex1=('Invalid name', RuntimeError))
def custom_contract2(arg):
    if not arg:
        raise ValueError(putil.pcontracts.get_exdesc())

@putil.pcontracts.new_contract(ex1=ValueError)
def custom_contract3(arg):
    if not arg:
        raise ValueError(putil.pcontracts.get_exdesc())

@putil.pcontracts.new_contract(ex1=(
    ValueError,
    'Argument `*[argument_name]*` is not valid'
))
def custom_contract4(arg):
    if not arg:
        raise ValueError(putil.pcontracts.get_exdesc())

@putil.pcontracts.new_contract(ex1='Invalid name')
def custom_contract5(arg):
    if not arg:
        raise ValueError(putil.pcontracts.get_exdesc())

@putil.pcontracts.new_contract(ex1=('Invalid name', RuntimeError))
def custom_contract6(arg):
    if not arg:
        raise ValueError(putil.pcontracts.get_exdesc())

@putil.pcontracts.new_contract(
    (OSError, 'File could not be opened')
)
def custom_contract7(arg):
    if not arg:
        raise ValueError(putil.pcontracts.get_exdesc())

@putil.pcontracts.new_contract('Invalid name')
def custom_contract8(arg):
    if not arg:
        raise ValueError(putil.pcontracts.get_exdesc())

@putil.pcontracts.new_contract(TypeError)
def custom_contract9(arg):
    if not arg:
        raise ValueError(putil.pcontracts.get_exdesc())

@putil.pcontracts.new_contract()
def custom_contract10(arg):
    if not arg:
        raise ValueError(putil.pcontracts.get_exdesc())

@putil.pcontracts.new_contract((
    TypeError,
    'Argument `*[argument_name]*` has to be a string'
))
def custom_contract11(city):
    if not isinstance(city, str):
        raise ValueError(putil.pcontracts.get_exdesc())

@putil.pcontracts.contract(city_name='custom_contract11')
def print_city_name(city_name):
    return 'City: {0}'.format(city_name)

@putil.pcontracts.new_contract((
    OSError, 'File `*[fname]*` not found'
))
def custom_contract12(fname):
    if not os.path.exists(fname):
        raise ValueError(putil.pcontracts.get_exdesc())

@putil.pcontracts.contract(fname='custom_contract12')
def print_fname(fname):
    print('File name to find: {0}'.format(fname))
