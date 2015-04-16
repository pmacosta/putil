#!/bin/bash
# complete-cloning.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

# Find directory where script is (from http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in)
source="${BASH_SOURCE[0]}"
while [ -h "${source}" ]; do # resolve $source until the file is no longer a symlink
	dir="$( cd -P "$( dirname "${source}" )" && pwd )"
	source="$(readlink "${source}")"
	[[ ${source} != /* ]] && source="$dir/$source" # if $source was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
dir="$( cd -P "$( dirname "${source}" )" && pwd )"
pkg_dir=$(dirname ${dir})
bin_dir=${pkg_dir}/sbin
cpwd=${PWD}

# Set up pre-commit Git hooks
source ${bin_dir}/setup-git-hooks.sh

# Build documentation
source ${bin_dir}/build-docs.sh
