import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kdl import parse

def test_from_file():
	os.chdir(os.path.dirname(__file__))
	with open('complex.kdl', 'r') as fp:
		doc = parse(fp)
	if sys.version_info.major == 3:
		with open('complex_formatted.kdl', 'r', encoding='utf-8') as fp:
			assert fp.read() == str(doc)
	else:
		with open('complex_formatted.kdl', 'r') as fp:
			assert fp.read().decode('utf-8') == str(doc)
