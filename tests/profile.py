"""
Module to profile plot generation time
Run with: python -m cProfile -s cumulative profile.py
"""

import gen_ref_images


if __name__ == '__main__':
	gen_ref_images.unittest_series_images(mode='test', test_dir='./profile', _timeit=True)
