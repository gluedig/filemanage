'''
Created on Jun 17, 2013

@author: developer
'''


class ClientManager:
    def __init__(self):
        self.clients = set()
    
    #web methods
    def register(self, mac, session):
        if mac in self.clients:
            return (str.format('Client {0} already seen\n', mac), 404)
        session.clear()
        session['mac'] = mac
        
        self.clients.add(mac)
        return str.format("Registered client MAC: {0}\n", mac)
    
    def unregister(self, session):
        if 'mac' in session:
            mac = session.pop('mac')
            session.clear()
            if mac in self.clients:
                self.clients.remove(mac)
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