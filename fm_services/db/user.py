'''
Created on Aug 6, 2013

@author: gluedig
'''
from abc import ABCMeta, abstractmethod
import json
import hashlib

class userDb():
    __metaclass__ = ABCMeta

    class User(json.JSONEncoder):
        def json(self):
            return {'id':self.user_id,
                    'email':self.email,
                    'image':self.image,
                    'firstname':self.firstname,
                    'lastname':self.lastname,
                    'created':self.created.isoformat(sep=' '),
                    'modified':self.modified.isoformat(sep=' '),
                    'seen':self.seen.isoformat(sep=' ')
                    }
        def __str__(self):
            return json.dumps(self.json())

        def default(self, obj):
            if isinstance(obj, userDb.User):
                return obj.json()
            else:
                return json.JSONEncoder.default(self, obj)

        def check_password(self, password):
            if hashlib.sha512(password).hexdigest() == self.password:
                return True
            else:
                return False

        def set_password(self, password):
            self.password = hashlib.sha512(password).hexdigest()
    @abstractmethod
    def get_contacts(self, user_id):
        return NotImplemented

    @abstractmethod
    def add_contact(self, user_id, contact):
        return NotImplemented

    @abstractmethod
    def remove_contact(self, user_id, contact):
        return NotImplemented

    @abstractmethod
    def find_by_id(self, user_id):
        return NotImplemented
    
    @abstractmethod
    def find_by_name(self, user_name):
        return NotImplemented

    @abstractmethod
    def find(self, search_term):
        return NotImplemented

    @abstractmethod
    def add(self, email, passwd, image):
        return NotImplemented
    
    @abstractmethod
    def login(self, user_id):
        return NotImplemented
    
    