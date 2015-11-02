#!/bin/bash
# rtest.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

opath=${PATH}
export PATH=/home/pacosta/python/python2.6/bin:/home/pacosta/python/python2.7/bin:/home/pacosta/python/python3.3/bin:/home/pacosta/python/python3.4/bin:/home/pacosta/python/python3.5/bin:${PATH}
tox -- "$@"
export PATH=${opath}
