#!/usr/bin/env python

from distutils.core import setup

setup(name='slingrpm',
      version='0.0.1',
      description='distributed publication of RPMS',
      author='Ernest W. Durbin III',
      author_email='ewdurbin@gmail.com',
      packages=['slingrpm'],
      scripts=['bin/slingrpmdaemon', 'bin/slinger'],
      requires=['pyzmq'],
     )
