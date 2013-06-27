'''
Created on Jun 27, 2013

@author: developer
'''
from fm_services import app
import fm_services.db.client

class clientDb(fm_services.db.client.clientDb):
    
    def __init__(self):
        self.clients = set()
    
    def register(self, mac):
        self.clients.add(mac)
        return True
    
    def unregister(self, mac):
        if mac in self.clients:
            self.clients.remove(mac)
            return True
        return False
    
    def is_registered(self, mac):
        if mac in self.clients:
            return True
        else:
            return False
    
    def dump(self):
        ret = 'Registered clients: '
        for clt in self.clients:
            ret += clt + " "
        return ret
    
app.db['client'] = clientDb()