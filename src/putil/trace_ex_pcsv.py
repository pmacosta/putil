# trace_ex_pcsv		pylint: disable=C0111
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

import putil.exh
import putil.tree
import putil.pcsv

_EXH = putil.exh.ExHandle()

def main():
	""" Main loop """
	obj = putil.pcsv.CsvFile('test.csv')
	obj.add_dfilter({'Result':20})
	print _EXH
	tree_data = _EXH.tree_data()
	tobjs = putil.tree.build_tree(tree_data)
	tobjs = tobjs if isinstance(tobjs, list) else [tobjs]
	for tobj in tobjs:
		tobj.collapse()
		print tobj.ppstr
	print putil.tree.search_for_node(tobjs[0], 'putil.pcsv.CsvFile.__init__').data
	print obj.data()

if __name__ == '__main__':
	main()
