'''
Created on Jun 20, 2013

@author: developer
'''
from setuptools import setup

setup(
    name='Sensus FM services',
    version='0.1',
    long_description=__doc__,
    packages=['fm_services'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'blinker'],
    package_data={'fm_services': ['static/*', 'templates/*']}
)