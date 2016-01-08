#!/bin/bash
# zip-artifacts.sh
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details

source $(dirname "${BASH_SOURCE[0]}")/functions.sh

pkg_dir=$(dirname $(current_dir "${BASH_SOURCE[0]}"))

interp=$1
tar_file="${pkg_dir}"/artifacts_${interp}.tar.gz
artifacts_dir="${pkg_dir}"/artifacts
if [ -d "${artifacts_dir}" ]; then
	echo "Zipping artifacts in ${artifacts_dir} to ${tar_file}"
	rm -rf "${tar_file}"
	cd "${artifacts_dir}"
	tar -zcvf "${tar_file}" *
else
	echo "Directory ${artifacts_dir} does not exist"
fi
