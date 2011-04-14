#!/usr/bin/env python

from distutils.core import setup

setup(name='tractor-glue',
      version='1.0',
      description='Glue to attach Maya/Nuke to tractor',
      author='Andrew Bunday',
      author_email='andrew.bunday@baseblack.com',
      url='http://svn/repos/tech/pipeline/renderfarm/tractor-glue/trunk/',
      packages=['tractor','tractor.glue'],
      #test_suite='nose.collector'
     )
