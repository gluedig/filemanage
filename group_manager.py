'''
Created on Jun 18, 2013

@author: developer
'''

class GroupManager(object):
    '''
    classdocs
    '''
    class group:
        def __init__(self, grp_id):
            self.id = grp_id
            self.clients = set()

    def __init__(self, clt_mgr, mon_mgr):
        '''
        Constructor
        '''
        self.clt_mgr = clt_mgr
        self.mon_mgr = mon_mgr
        self.groups = {}
        
        
    def join(self, ip, session):
        if 'mac' not in session:
            return ('No MAC in session', 404)
        mac = session['mac']
        
        if not self.clt_mgr.is_registered(mac):
            return (str.format('Client MAC: {0} not registered', mac), 404)
        
        mon_id = self.mon_mgr.find_client(ip, mac)
        if not mon_id:
            return (str.format('Cannot find client MAC: {0} through any monitor', mac), 404)
        
        grp_id = "group-"+mon_id
        if grp_id not in self.groups:
            new_grp = GroupManager.group(grp_id)
            self.groups[grp_id] = new_grp
        self.groups[grp_id].clients.add(mac)
        
        session['group'] = grp_id
        return str.format("Registered client MAC: {0} in group:{1}", mac, grp_id)
    
    def leave(self, session):
        if 'group' not in session:
            return ("Client does not belong to any group", 404)
        
        grp_id = session['group']
        if grp_id not in self.groups:
            return (str.format("Group: {0} not longer valid", grp_id), 404)
        
        self.groups[grp_id].clients.remove(session['mac'])
        session.pop('group')
        return "OK"
    
    def members(self, session):
        if 'group' not in session:
            return ("Client does not belong to any group", 404)
        
        grp_id = session['group']
        if grp_id not in self.groups:
            return (str.format("Group: {0} not longer valid", grp_id), 404)
        
        group = self.groups[grp_id]
        
        return "\n".join(group.clients)
    
    def dump(self):
        ret = ""
        for group in self.groups.values():
            ret += str.format("Group: {0} Members:{1}\n", group.id, group.clients)
        
        return ret
    
    
        