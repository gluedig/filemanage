'''
Created on Jun 27, 2013

@author: developer
'''
from abc import ABCMeta, abstractmethod

class clientDb():
    __metaclass__ = ABCMeta
   
    
    @abstractmethod
    def register(self, mac):
        return NotImplemented
    
    @abstractmethod
    def unregister(self, mac):
        return NotImplemented
    
    @abstractmethod
    def is_registered(self, mac):
        return NotImplemented
    
    @abstractmethod
    def dump(self):
        return NotImplemented
    
    