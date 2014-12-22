#!/bin/bash

modules=(check pcontracts pcsv tree exh pinspect)
for module in ${modules[@]}; do
	if ! py.test -s -vv -x test_$module.py; then
		exit 1
	fi
done
