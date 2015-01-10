#!/bin/bash
sta=""
if [ "${2}" != "" ]; then
	sta="-k ${2}"
fi
py.test -s -vv -x ${sta} test_${1}.py
