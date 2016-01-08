#!/bin/bash
# set-matplotlib-backend.sh
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details

echo -e '# matplotlibrc\n'\
'# Copyright (c) 2013-2016 Pablo Acosta-Serafini\n'\
'# See LICENSE for details\n'\
'backend : Agg' > $1/matplotlibrc
