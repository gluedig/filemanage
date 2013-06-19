'''
Created on Jun 17, 2013

@author: developer
'''
from services import app
from flask import session

class ClientManager:
    def __init__(self, app):
        self.app = app
        self.clients = set()
    
    #web methods
    def register(self, mac, session):
        if mac in self.clients:
            return (str.format('Client {0} already seen\n', mac), 404)
        session.clear()
        session['mac'] = mac
        
        self.clients.add(mac)

        self.app.signals['client-register'].send(self.app, mac=mac)
        return str.format("Registered client MAC: {0}\n", mac)
    
    def unregister(self, session):
        if 'mac' in session:
            mac = session.pop('mac')
            session.clear()
            if mac in self.clients:
                self.clients.remove(mac)

                self.app.signals['client-unregister'].send(self.app, mac=mac)
                return str.format("Unregistered client MAC: {0}\n", mac)
            else:
                return (str.format("Client MAC: {0} found in session but not in db\n", mac))
        else:
            return ('No MAC in session\n', 404)
    
    def dump(self):
        ret = 'Registered clients: '
        for clt in self.clients:
            ret += clt + " "
        return ret
    
    #interface methods
    def is_registered(self, mac):
        if mac in self.clients:
            return True
        else:
            return False
        
        
app.services['client_manager'] = ClientManager(app)
this_service = app.services['client_manager']

#===============================================================================
# client i/f
#===============================================================================
@app.route('/client/register/<mac>')
def client_register_route(mac):
    return this_service.register(mac, session)

@app.route('/client/unregister')
def client_unregister_route():
    return this_service.unregister(session)

@app.route('/client/mac')
def client_mac_route():
    if 'mac' not in session:
            return ('No MAC in session\n', 404)

    return session['mac']

@app.route('/client/dump')
def client_dump_route():
    return this_service.dump()
