'''
Created on Jun 12, 2013

@author: developer
'''

class MonitorManager:
    class monitor:
        def __init__(self):
            self.id = None
            self.ip = None
            self.clients = set()
    
    def __init__(self):
        self.mons_by_id = {}
        self.mons_by_ip = {}
    
    #web methods 
    def register(self, ip, mon_id):
        new_mon = MonitorManager.monitor()
        new_mon.ip = ip
        new_mon.id = mon_id
        if self.is_registered(mon_id):
            return ('Monitor: '+mon_id+' already registered', 404)
    
        self.mons_by_id[mon_id] = new_mon
        if ip not in self.mons_by_ip:
            self.mons_by_ip[ip] = []
        self.mons_by_ip[ip].append(new_mon)
        
        return "OK"
    
    def unregister(self, mon_id):
        if not self.is_registered(mon_id):
            return ('Monitor: '+mon_id+' not registered', 404)
    
        mon = self.mons_by_id.pop(mon_id)
        mons =  self.mons_by_ip[mon.ip]
        for tmon in mons:
            if tmon.id == mon.id:
                mons.remove(tmon) 
        
        return "OK"
    
    def dump(self):
        ret = ''
        for mon in self.mons_by_id.values():
            ret += str.format("Monitor ID: {0} IP: {1}\nKnown clients:\n{2}\n", mon.id, mon.ip, mon.clients)
            
        return ret
        
    def client_event(self, mon_id, event, mac):
        if not self.is_registered(mon_id):
            return ('Monitor: '+mon_id+' not registered', 404)
        
        monitor = self.mons_by_id[mon_id]
        #client add
        if event == '0':
            if not mac in monitor.clients:
                monitor.clients.add(mac)
                return str.format("Monitor {0} registered new client {1}", mon_id, mac)
        #client remove
        elif event == '1': 
            if mac in monitor.clients:
                monitor.clients.remove(mac)
                return str.format("Monitor {0} unregistered client {1}", mon_id, mac)
        else:
            return ("Unknown event: "+event, 404)
        
        return "OK"
    
    
    #interface methods
    def is_registered(self, mon_id):
        return mon_id in self.mons_by_id
    
    def find_monitor_by_ip(self, ip):
        if ip in self.mons_by_ip:
            return self.mons_by_ip[ip]
        else:
            return None
        
    def find_client(self, ip, mac):
        monitors = self.find_monitor_by_ip(ip)
        if not monitors:
            return None
        
        for monitor in monitors:
            if mac in monitor.clients:
                return monitor.id
        
        return None
    
    
    