#!/bin/bash
# spellcheck-file.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

source $(dirname "${BASH_SOURCE[0]}")/functions.sh

pkg_dir=$(dirname $(current_dir "${BASH_SOURCE[0]}"))

for file in "$@"; do
	bfn=$(basename ${file})
	ext="${filename##*.}"
	if [ ! -d "${file}" ] && [ "${ext}" != "spell" ]; then
		tmpfile_1=$(tempfile)
		cat ${file} | aspell --lang=en list > ${tmpfile_1}
		tmpfile_2=${file}.spell
		sort ${tmpfile_1} | uniq > ${tmpfile_2}
		rm -rf ${tmpfile_1}
		echo "Spell-check results in ${tmpfile_2}"
	fi
done
