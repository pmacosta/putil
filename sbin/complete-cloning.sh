#!/bin/bash
# complete-cloning.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

source $(dirname "${BASH_SOURCE[0]}")/functions.sh

pkg_dir=$(dirname $(current_dir "${BASH_SOURCE[0]}"))
bin_dir=${pkg_dir}/sbin
cpwd=${PWD}

# Set up pre-commit Git hooks
source ${bin_dir}/setup-git-hooks.sh

# Build documentation
source ${bin_dir}/build-docs.sh
