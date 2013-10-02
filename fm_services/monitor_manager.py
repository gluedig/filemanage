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
        self.watched_macs = set()
        self.last_rssi = {}
        app.signals['user-device-associate'].connect(self.user_assoc)

    def user_assoc(self, sender, **args):
        if 'mac' in args:
            mac = args['mac']
            if mac not in self.watched_macs:
                app.logger.debug("New watched MAC: <%s>", mac)
                self.watched_macs.add(mac)

            mon_ids = self.find_client(None, mac)
            if mon_ids:
                for mon in mon_ids:
                    if mon in self.mons_by_id:
                        rssi = 0
                        if mac in self.last_rssi:
                            rssi = self.last_rssi[mac]
                        self._proximity_enter(self.mons_by_id[mon], mac, rssi)
    
    #web methods 
    def register(self, ip, mon_id):
        new_mon = MonitorManager.monitor()
        new_mon.ip = ip
        new_mon.id = mon_id
        if self.is_registered(mon_id):
            return (str.format('Monitor: {0} already registered', mon_id), 200)
    
        self.mons_by_id[mon_id] = new_mon
        if ip not in self.mons_by_ip:
            self.mons_by_ip[ip] = []
        self.mons_by_ip[ip].append(new_mon)
        
        return "OK"
    
    def unregister(self, mon_id):
        if not self.is_registered(mon_id):
            return (str.format('Monitor: {0} not registered', mon_id), 200)
    
        mon = self.mons_by_id.pop(mon_id)
        mons =  self.mons_by_ip[mon.ip]
        for tmon in mons:
            if tmon.id == mon.id:
                mons.remove(tmon) 
        
        return "OK\n"
    
    def dump(self):
        ret = ''
        if len(self.watched_macs):
            ret += str.format("Watched MACs: {0}\n", self.watched_macs)
        for mon in self.mons_by_id.values():
            ret += str.format("Monitor ID: {0} IP: {1} Known clients: {2}\n", mon.id, mon.ip, mon.clients)
        return ret

    def _proximity_enter(self, monitor, mac, rssi):
        if mac not in monitor.clients:
            monitor.clients.add(mac)
        self.last_rssi[mac] = rssi
        if mac in self.watched_macs:
            app.logger.debug(str.format("MAC <{0}> entered proximity of monitor {1}", mac, monitor.id))
            self.app.signals['proximity-entered'].send(self, mon_id=monitor.id, mac=mac, rssi=rssi)

    def _proximity_leave(self, monitor, mac, rssi):
        if mac in monitor.clients:
            monitor.clients.remove(mac)
        self.last_rssi[mac] = rssi
        if mac in self.watched_macs:
            app.logger.debug(str.format("MAC <{0}> left proximity of monitor {1}", mac, monitor.id))
            self.app.signals['proximity-left'].send(self, mon_id=monitor.id, mac=mac, rssi=rssi)

    def _proximity_change(self, monitor, mac, rssi):
        self.last_rssi[mac] = rssi
        if mac in self.watched_macs:
            app.logger.debug(str.format("MAC <{0}> changed proximity to monitor {1}", mac, monitor.id))
            self.app.signals['proximity-change'].send(self, mon_id=monitor.id, mac=mac, rssi=rssi)

    def client_event(self, mon_id, request):
        if not self.is_registered(mon_id):
            self.register(request.remote_addr, mon_id)

        monitor = self.mons_by_id[mon_id]
        #self.app.logger.debug(request.get_data(as_text=True))
        try:
            msg_json = json.loads(request.get_data(as_text=True))[0]
        except (ValueError):
            self.app.logger.error("Cannot decode message: "+request.data)
            return ("Cannot decode message", 500)

        #client add
        mac = msg_json['mac']
        event_type = msg_json['event_type']
        rssi = msg_json['rssi']
        if event_type == 0:
            self._proximity_enter(monitor, mac, rssi)
            msg = str.format("Monitor {0} registered new MAC <{1}>", mon_id, mac)
            #app.logger.debug(msg)
            return msg
        #client remove
        elif event_type == 1:
            self._proximity_leave(monitor, mac, rssi)
            msg = str.format("Monitor {0} unregistered MAC <{1}>", mon_id, mac)
            #app.logger.debug(msg)
            return msg
        #change
        elif event_type == 2:
            if mac in monitor.clients:
                if rssi != msg_json['prev_rssi']:
                    msg = str.format("Monitor {0} MAC <{1}> prev rssi {2} new rssi {3}", mon_id, mac, msg_json['prev_rssi'], rssi)
                    #app.logger.debug(msg)
                    self._proximity_change(monitor, mac, rssi)
                    return msg
            else:
                self._proximity_enter(monitor, mac, rssi)
                msg = str.format("Monitor {0} registered new MAC <{1}>", mon_id, mac)
                #app.logger.debug(msg)
                return msg
#        else:
#            error = str.format("Unknown event: {0}", msg_json['event_type'])
#            self.app.logger.error(error)
#            self.app.logger.debug(msg_json)
#            return (error, 404)

        return 'OK'
    
    #interface methods
    def is_registered(self, mon_id):
        return mon_id in self.mons_by_id
    
    def find_monitor_by_ip(self, ip):
        if ip and ip in self.mons_by_ip:
            return self.mons_by_ip[ip]
        else:
            return None
        
    def find_client(self, ip, mac):
        monitors = self.find_monitor_by_ip(ip)
        if not monitors:
            monitors=self.mons_by_id.values()
        
        mon_ids = []
        for monitor in monitors:
            if mac in monitor.clients:
                mon_ids.append(monitor.id)
        
        if len(mon_ids):
            return mon_ids
        else:
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

@app.route('/monitor/unregister/<int:mon_id>')
def mon_unregister_route(mon_id):
    return this_service.unregister(mon_id)

@app.route('/monitor/event/<int:mon_id>', methods=["POST"])
def mon_event_route(mon_id):
    return this_service.client_event(mon_id, request)

@app.route('/monitor/find/<mac>')
def mon_find_route(mac):
    ip = request.remote_addr
    monitors = this_service.find_client(ip, mac)
    if monitors:
        return str.format("{0}\n", [ int(mon) for mon in monitors])
    else:
        return ("Not found", 404)    

@app.route('/monitor/dump')
def mon_dump_route():
    return this_service.dump()
