# trace_ex_pcsv		pylint: disable=C0111
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

import putil.exh
import putil.tree
import putil.pcsv

_EXH = putil.exh.ExHandle('putil.pcsv.CsvFile')

def main():
	""" Main loop """
	print 'Tracing'
	obj = putil.pcsv.CsvFile('test.csv', dfilter={'Result':20})
	obj.add_dfilter({'Result':20})
	obj.dfilter = {'Result':20}
	obj.data()
	_EXH.build_ex_tree()
	_EXH.print_ex_tree()
	_EXH.print_ex_table()

if __name__ == '__main__':
	main()
