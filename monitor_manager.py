'''
Created on Jun 12, 2013

@author: developer
'''

class monitor:
    pass

class MonitorManager:
    def __init__(self):
        self.mons_by_id = {}
        self.mons_by_ip = {}
        
    def register(self, ip, mon_id):
        new_mon = monitor()
        new_mon.ip = ip
        new_mon.id = mon_id
        if self.is_registered(mon_id):
            return ('Monitor: '+mon_id+' already registered', 404)
    
        self.mons_by_id[mon_id] = new_mon
        self.mons_by_ip[ip] = new_mon
        return "OK"
    
    def unregister(self, mon_id):
        if not self.is_registered(mon_id):
            return ('Monitor: '+mon_id+' not registered', 404)
    
        mon = self.mons_by_id.pop(mon_id)
        self.mons_by_ip.pop(mon.ip)
        return "OK"
    
    def is_registered(self, mon_id):
        return mon_id in self.mons_by_id
    
    def find_by_ip(self):
        pass
    