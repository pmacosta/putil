"""
Timing scratch module
"""

import putil.eng
import putil.misc

def main():
	""" Processing """
	num_tries = 1000
	with putil.misc.Timer() as tobj:
		for _ in xrange(num_tries):
			putil.eng.peng_mant('     5.245k   ')
			putil.eng.peng_mant('345')
	print 'Time per call: {0}'.format(tobj.elapsed_time/(2.0*num_tries))

if __name__ == '__main__':
	main()
