from setuptools import setup
import os.path, sys

here = os.path.dirname(os.path.abspath(__file__))

README = open(os.path.join(here, 'README.md'), 'r').read()
if sys.version_info.major == 2:
	README = README.decode('utf-8')

# This call to setup() does all the work
setup(
	name='kdl-py',
	version='0.1.0',
	description='A Python library for the KDL Document Language.',
	long_description=README,
	long_description_content_type='text/markdown',
	url='https://github.com/daeken/kdl-py',
	author='Sera Brocious',
	author_email='sera.brocious@gmail.com',
	license='MIT',
	classifiers=[
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 2.7',
	],
	packages=['kdl'],
	include_package_data=True,
	install_requires=['TatSu >= 4.4.0', 'regex >= 2021.4.4'],
)