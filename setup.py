#!/usr/bin/env python

from distutils.core import setup
setup(name='tractor-api',
	version='3.0',
	description='Tractor script making api in python',
	author='Andrew Bunday',
	author_email='andrew.bunday@baseblack.com',
	maintainer_email='requests@baseblack.com',
	packages=['tractor', 'tractor.api'],
	package_dir={'tractor':'src/lib/tractor'},
	)