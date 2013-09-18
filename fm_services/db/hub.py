'''
Created on Sep 10, 2013

@author: gluedig
'''
from abc import ABCMeta, abstractmethod
import json

class hubDb():
    __metaclass__ = ABCMeta

    class Hub(json.JSONEncoder):
        def json(self):
            return {'id':self.hub_id,
                    'description':self.description,
                    }
        def __str__(self):
            return json.dumps(self.json())

        def default(self, obj):
            if isinstance(obj, hubDb.Hub):
                return obj.json()
            else:
                return json.JSONEncoder.default(self, obj)
            
    @abstractmethod
    def get_hub(self, hub_id):
        return NotImplemented
    
    @abstractmethod
    def create_hub(self, description):
        return NotImplemented
    
    @abstractmethod
    def find_hubs(self, user_id):
        return NotImplemented
    
    @abstractmethod
    def associate(self, hub_id, user_id, only=False):
        return NotImplemented
    
    @abstractmethod
    def get_users(self, hub_id):
        return NotImplemented
    
    