import sys

from distutils.core import setup

requirements = ['boto',
                'celery[redis]',
                'Flask',
                'gunicorn',
                'pyrpm-02strich',
                'requests',
                'simpleflock',
                'xmltodict']
test_requirements = []

setup(
    name='slingrpm',
    version='1.0.0b2',
    license='MIT',
    author="Ernest W. Durbin III",
    author_email='ewdurbin@gmail.com',
    description='a lightweight manager for pushing, removing, and promoting rpms in a remote yum repository',
    url='https://github.com/ewdurbin/slingrpm',
    packages=['slingrpm',
              'slingrpm.utils',
              'slingrpm.server',
              'slingrpm.tasks'],
    scripts=['scripts/slingrpm'],
    test_suite='tests',
    install_requires=requirements,
    tests_require=test_requirements,
)
