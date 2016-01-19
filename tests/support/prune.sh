#!/bin/bash
# prune.sh
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details

dest_dir=
files=(
)
src_dir=ref_tmp
echo "Prunning ${dest_dir}"
mv "${dest_dir}" "${src_dir}"
mkdir -p "${dest_dir}"
for file in "${files[@]}"; do
	mv "${src_dir}"/"${file}" "${dest_dir}"/.
done
rm -rf "${src_dir}"
