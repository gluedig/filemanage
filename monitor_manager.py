'''
Created on Jun 12, 2013

@author: developer
'''

class monitor:
    def __init__(self):
        self.id = None
        self.ip = None
        self.clients = {}
        
class client:
    def __init__(self):
        self.mac = None

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
    
    def find_by_ip(self, ip):
        if ip in self.mons_by_ip:
            return self.mons_by_ip[ip]
        else:
            return None
        
    def client_event(self, mon_id, event, mac):
        if not self.is_registered(mon_id):
            return ('Monitor: '+mon_id+' not registered', 404)
        
        monitor = self.mons_by_id[mon_id]
        #client add
        if event == 0:
            if not mac in monitor.clients:
                new_client = client()
                new_client.mac = mac
                monitor.clients[mac] = new_client
        #client remove
        elif event == 1: 
            if mac in monitor.clients:
                client = monitor.clients.pop(mac)
        
        return "OK"
    