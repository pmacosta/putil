#!/bin/bash
cd ../putil
py.test --cov putil.pcsv --cov-report term-missing ../tests/test_pcsv.py
