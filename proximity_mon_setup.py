'''
Created on Jun 20, 2013

@author: developer
'''
from setuptools import setup

setup(
    name='Sensus Proximity Monitor',
    version='0.1',
    long_description=__doc__,
    packages=['proximity_mon'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['pyzmq']
)