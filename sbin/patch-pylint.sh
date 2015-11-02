#!/bin/bash
# patch-pylint.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

sed -r -i '242s/\{\}/\{0\}/' $1/astroid/brain/pysix_moves.py
