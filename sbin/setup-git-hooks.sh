#!/bin/bash
# setup-git-hooks.sh
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details

source $(dirname "${BASH_SOURCE[0]}")/functions.sh

pkg_dir=$(dirname $(current_dir "${BASH_SOURCE[0]}"))
source ${pkg_dir}/.hooks/setup-git-hooks.sh
