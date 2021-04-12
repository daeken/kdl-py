import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kdl import parse

def test_from_file():
	with open('complex.kdl', 'r') as fp:
		doc = parse(fp)
	print str(doc)
	with open('complex_formatted.kdl', 'r') as fp:
		assert fp.read().decode('utf-8') == str(doc)
