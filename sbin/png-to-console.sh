#!/bin/bash
# png-to-console.sh
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details

file=$1
if [ -f ${file}  ]; then
	convert $1 png - | xxd
else
	echo "File ${file} could not be found" >&2
fi
