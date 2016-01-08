# pcontracts_example_2.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0702

import putil.pcontracts

@putil.pcontracts.new_contract('Only one exception')
def custom_contract_a(name):
    msg = putil.pcontracts.get_exdesc()
    if not name:
        raise ValueError(msg)

@putil.pcontracts.new_contract(ex1='Empty name', ex2='Invalid name')
def custom_contract_b(name):
    msg = putil.pcontracts.get_exdesc()
    if not name:
        raise ValueError(msg['ex1'])
    elif name.find('[') != -1:
        raise ValueError(msg['ex2'])
