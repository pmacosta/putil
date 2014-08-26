# trace_ex_pcsv		pylint: disable=C0111
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

import putil.exh
import putil.pcsv

_EXH = putil.exh.ExHandle()

def main():
	""" Main loop """
	obj = putil.pcsv.CsvFile('test.csv')
	obj.add_dfilter({'Result':20})

if __name__ == '__main__':
	main()
	print str(_EXH)
