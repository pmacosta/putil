# __init__.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# PyPI imports
import matplotlib
# Default to non-interactive PNG to avoid any
# matplotlib back-end misconfiguration
matplotlib.rcParams['backend'] = 'Agg'
