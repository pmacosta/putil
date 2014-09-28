#!/bin/bash

modules=(check pcsv tree)
for module in ${modules[@]}; do
	py.test -v -x $module"_test.py"
	if [ $? == 1 ]; then
		exit 1
	fi
done
