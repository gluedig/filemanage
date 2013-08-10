'''
Created on Jun 17, 2013

@author: developer
'''
from fm_services import app
from flask import session

class ClientManager:
    def __init__(self, app):
        self.app = app
        self.db = app.db['client']
    
    #web methods
    def register(self, mac, session):
        #if mac in self.clients:
        #    return (str.format('Client {0} already seen\n', mac), 404)
        session.clear()
        session['mac'] = mac
        if self.db.register(mac):
            self.app.signals['client-register'].send(self.app, mac=mac)
            return True
        else:
            return False
    
    def unregister(self, session):
        if 'mac' in session:
            mac = session.pop('mac')
            session.clear()
            if self.db.unregister(mac):
                self.app.signals['client-unregister'].send(self.app, mac=mac)
            else:
                self.app.logger.debug(str.format("Client MAC: {0} found in session but not in db\n", mac))
            return True
        else:
            return False
    
    def dump(self):
        return self.db.dump()
    
    #interface methods
    def is_registered(self, mac):
        return self.db.is_registered(mac)

    def get_mac(self, session):
        if 'mac' not in session:
            return False
        else:
            return session['mac']


app.services['client_manager'] = ClientManager(app)
this_service = app.services['client_manager']

#===============================================================================
# client i/f
#===============================================================================
@app.route('/client/register/<mac>')
def client_register_route(mac):
    if this_service.register(mac, session):
        return 'OK'
    else:
        return ('Client registration failed\n', 404)
@app.route('/client/unregister')
def client_unregister_route():
    if this_service.unregister(session):
        return 'OK'
    else:
        return ('No MAC in session\n', 404)
        
@app.route('/client/mac')
def client_mac_route():
    mac = this_service.get_mac(session)
    if not mac:
            return ('No MAC in session\n', 404)
    else:
        return mac

@app.route('/client/dump')
def client_dump_route():
    return this_service.dump()
