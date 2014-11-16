#!/bin/bash

modules=(check pcontracts pcsv tree)
for module in ${modules[@]}; do
	py.test -v -x "test_"$module".py"
	if [ $? != 0 ]; then
		exit 1
	fi
done
