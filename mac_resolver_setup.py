'''
Created on Jun 20, 2013

@author: developer
'''
from setuptools import setup

setup(
    name='Sensus MAC resolver',
    version='0.1',
    long_description=__doc__,
    packages=['mac_resolver'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask']
)