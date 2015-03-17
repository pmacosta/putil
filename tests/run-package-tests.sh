#!/bin/bash

modules=(eng exdoc exh misc pinspect pcontracts pcsv plot "test" tree)
for module in ${modules[@]}; do
	if ! py.test -s -vv -x test_$module.py; then
		exit 1
	fi
done
