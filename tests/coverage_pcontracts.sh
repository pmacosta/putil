#!/bin/bash
cd ../putil
py.test --cov putil.pcontracts --cov-report term-missing ../tests/test_pcontracts.py
