# pcontracts_example_1.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0702

from __future__ import print_function
import putil.ptypes

@putil.pcontracts.contract(name='file_name')
def print_if_fname_valid(name):
    """ Sample function 1 """
    print('Valid file name: {0}'.format(name))

@putil.pcontracts.contract(num=int, name='file_name_exists')
def print_if_fname_exists(num, name):
    """ Sample function 2 """
    print('Valid file name: [{0}] {1}'.format(num, name))
