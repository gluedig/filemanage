'''
Created on Sep 11, 2013

@author: gluedig
'''
from abc import ABCMeta, abstractmethod
import json

class messageDb():
    __metaclass__ = ABCMeta

    class Message(json.JSONEncoder):
        def json(self):
            return {'id':self.msg_id,
                    'text':self.text,
                    'user':self.user_id,
                    'hub':self.hub_id,
                    'posted':self.posted,
                    }
        def __str__(self):
            return json.dumps(self.json())

        def default(self, obj):
            if isinstance(obj, messageDb.Message):
                return obj.json()
            else:
                return json.JSONEncoder.default(self, obj)
            
    @abstractmethod
    def get(self, msg_id):
        return NotImplemented
        
    @abstractmethod
    def post(self, user_id, hub_id, text):
        return NotImplemented
    
    @abstractmethod
    def update(self, msg_id, text):
        return NotImplemented
    
    @abstractmethod
    def remove(self, msg_id):
        return NotImplemented
    
    @abstractmethod
    def get_by_user(self, user_id, count=False, start=0, end=-1):
        return NotImplemented
    
    @abstractmethod
    def get_by_hub(self, hub_id, count=False, start=0, end=-1):
        return NotImplemented
    