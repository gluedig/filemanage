'''
Created on Aug 6, 2013

@author: gluedig
'''
from abc import ABCMeta, abstractmethod

class userDb():
    __metaclass__ = ABCMeta
        
    @abstractmethod
    def find_by_device(self, device):
        return NotImplemented
    
    @abstractmethod    
    def find_by_id(self, user_id):
        return NotImplemented
    
    @abstractmethod    
    def find_by_name(self, user_name):
        return NotImplemented
        
    @abstractmethod
    def add(self, email, image, device):
        return NotImplemented
    
    @abstractmethod
    def login(self, user_id):
        return NotImplemented
    
    @abstractmethod
    def associate_device(self, user_id, device):
        return NotImplemented