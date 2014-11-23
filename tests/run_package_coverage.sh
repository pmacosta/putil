#!/bin/bash

modules=(pcontracts pcsv tree)
cd ../putil
for module in ${modules[@]}; do
	py.test --cov "putil."$module --cov-report term-missing "../tests/test_"$module".py"
	if [ $? != 0 ]; then
		exit 1
	fi
done
