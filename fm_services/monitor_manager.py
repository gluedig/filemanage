'''
Created on Jun 12, 2013

@author: developer
'''
from fm_services import app
from flask import request
import json

class MonitorManager:
    class monitor:
        def __init__(self):
            self.id = None
            self.ip = None
            self.clients = set()
    
    def __init__(self, app):
        self.app = app
        self.mons_by_id = {}
        self.mons_by_ip = {}
    
    #web methods 
    def register(self, ip, mon_id):
        new_mon = MonitorManager.monitor()
        new_mon.ip = ip
        new_mon.id = mon_id
        if self.is_registered(mon_id):
            return ('Monitor: '+mon_id+' already registered\n', 404)
    
        self.mons_by_id[mon_id] = new_mon
        if ip not in self.mons_by_ip:
            self.mons_by_ip[ip] = []
        self.mons_by_ip[ip].append(new_mon)
        
        return "OK\n"
    
    def unregister(self, mon_id):
        if not self.is_registered(mon_id):
            return ('Monitor: '+mon_id+' not registered\n', 404)
    
        mon = self.mons_by_id.pop(mon_id)
        mons =  self.mons_by_ip[mon.ip]
        for tmon in mons:
            if tmon.id == mon.id:
                mons.remove(tmon) 
        
        return "OK\n"
    
    def dump(self):
        ret = ''
        for mon in self.mons_by_id.values():
            ret += str.format("Monitor ID: {0} IP: {1} Known clients: {2}\n", mon.id, mon.ip, mon.clients)
        return ret

    def _proximity_enter(self, monitor,  mac, rssi):
        monitor.clients.add(mac)
        self.app.signals['proximity-entered'].send(self.app, mon_id=monitor.id, mac=mac, rssi=rssi)

    def _proximity_leave(self, monitor, mac, rssi):
        monitor.clients.remove(mac)
        self.app.signals['proximity-left'].send(self.app, mon_id=monitor.id, mac=mac, rssi=rssi)

    def _proximity_change(self, monitor, mac, rssi):
        self.app.signals['proximity-change'].send(self.app, mon_id=monitor.id, mac=mac, rssi=rssi)

    def client_event(self, mon_id, request):
        if not self.is_registered(mon_id):
            return ('Monitor: '+mon_id+' not registered\n', 404)

        monitor = self.mons_by_id[mon_id]
        #self.app.logger.debug(request.get_data(as_text=True))
        try:
            msg_json = json.loads(request.data)[0]
        except (ValueError):
            self.app.logger.error("Cannot decode message: "+request.data)
            return ("Cannot decode message", 500)

        #client add
        mac = msg_json['mac']
        event_type = msg_json['event_type']
        rssi = msg_json['rssi']
        if event_type == 0:
            if not mac in monitor.clients:
                self._proximity_enter(monitor, mac, rssi)
                return str.format("Monitor {0} registered new client {1}\n", mon_id, mac)
        #client remove
        elif event_type == 1:
            if mac in monitor.clients:
                self._proximity_leave(monitor, mac, rssi)
                return str.format("Monitor {0} unregistered client {1}\n", mon_id, mac)
        #change
        elif event_type == 2:
            if mac in monitor.clients:
                if rssi != msg_json['prev_rssi']:
                    self.app.logger.info(str.format("MAC {0} prev rssi {1} new rssi {2}", mac, msg_json['prev_rssi'], rssi ))
                    self._proximity_change(monitor, mac, rssi)
                    return str.format("Monitor {0} client {1} RSSI changed\n", mon_id, mac)
            else:
                self._proximity_enter(monitor, mac, rssi)
                return str.format("Monitor {0} registered new client {1}\n", mon_id, mac)
        else:
            error = str.format("Unknown event: {0}\n", msg_json['event_type'])
            self.app.logger.error(error)
            self.app.logger.debug(msg_json)
            return (error, 404)

        return 'OK'
    
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


app.services['monitor_manager'] = MonitorManager(app)
this_service = app.services['monitor_manager']
#===============================================================================
# wifi monitor i/f
#===============================================================================
@app.route('/monitor/register/<mon_id>')
def mon_register_route(mon_id):
    ip = request.remote_addr
    return this_service.register(ip, mon_id)

@app.route('/monitor/unregister/<mon_id>')
def mon_unregister_route(mon_id):
    return this_service.unregister(mon_id)

@app.route('/monitor/event/<mon_id>', methods=["POST"])
def mon_event_route(mon_id):
    return this_service.client_event(mon_id, request)

@app.route('/monitor/find/<mac>')
def mon_find_route(mac):
    ip = request.remote_addr
    monitor = this_service.find_client(ip, mac)
    if monitor:
        return monitor+'\n'
    else:
        return ("Not found", 404)    

@app.route('/monitor/dump')
def mon_dump_route():
    return this_service.dump()
