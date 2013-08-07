'''
Created on Aug 6, 2013

@author: gluedig
'''
from abc import ABCMeta, abstractmethod
import json
import datetime
import hashlib

class userDb():
    __metaclass__ = ABCMeta

    class User:
        def __init__(self):
            self.user_id = None
            self.firstname = "None"
            self.lastname = "None"
            self.email = None
            self.password = None
            self.image = None

            now = datetime.datetime.now()
            self.created = now
            self.modified = now
            self.seen = now

            self.device = []
        def json(self):
            return json.dumps([{'id':self.user_id,
                                'email':self.email,
                                'image':self.image,
                                'firstname':self.firstname,
                                'lastname':self.lastname,
                                'created':self.created.isoformat(sep=' '),
                                'modified':self.modified.isoformat(sep=' '),
                                'seen':self.seen.isoformat(sep=' ')
                                }])
        def __str__(self):
            return self.json()

        def check_password(self, password):
            if hashlib.sha512(password).hexdigest() == self.password:
                return True
            else:
                return False

        def set_password(self, password):
            self.password = hashlib.sha512(password).hexdigest()
        
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
    def add(self, email, passwd, image, device):
        return NotImplemented
    
    @abstractmethod
    def login(self, user_id):
        return NotImplemented
    
    @abstractmethod
    def associate_device(self, user_id, device):
        return NotImplemented