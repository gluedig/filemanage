'''
Created on Sep 11, 2013

@author: gluedig
'''
from fm_services import app
from flask import session, request, make_response, Config
from fm_services.decorators import xsite_enabled, user_loggedin
import json

class HubManager:
    def __init__(self, app):
        self.app = app
        self.db = app.db['hubs']
        self.user_db = app.db['users']
        config = Config(app.root_path)
        self.hub_monitor_map = {}
        if config.from_pyfile(app.config['MONITOR_HUB_MAP'], silent=True) and 'MAP' in config:
            self.hub_monitor_map.update(config['MAP'])
            app.logger.debug(str.format("Loaded Monitor -> Hub mapping:\n{0}", self.hub_monitor_map))
        app.signals['proximity-entered'].connect(self._prox_enter)
        app.signals['proximity-left'].connect(self._prox_leave)
        app.signals['proximity-change'].connect(self._prox_change)

    def _prox_enter(self, sender, mon_id, mac, rssi, **args):
        mon_id = int(mon_id)
        if mon_id not in self.hub_monitor_map:
            return
        hub = self.db.get_hub(self.hub_monitor_map[mon_id])
        device = self.user_db.find_device_by_mac(mac)
        if hub and device and device.user_id:
            user_id = device.user_id
            app.logger.debug(str.format("User: {0} (MAC: <{1}>) entered proximity of Hub: {2} (Monitor: {3})", user_id, mac, hub.hub_id, mon_id))
            if self.db.associate(hub.hub_id, user_id):
                self.app.signals['hub-associate'].send(self, user_id=user_id, hub_id=hub.hub_id)
            else:
                app.logger.error('Cannot associate user %d to hub %d', user_id, hub.hub_id)

    def _prox_leave(self, sender, mon_id, mac, rssi, **args):
        mon_id = int(mon_id)
        if mon_id not in self.hub_monitor_map:
            return
        hub = self.db.get_hub(self.hub_monitor_map[mon_id])
        device = self.user_db.find_device_by_mac(mac)
        if hub and device and device.user_id:
            user_id = device.user_id
            app.logger.debug(str.format("User: {0} (MAC: <{1}>) left proximity of Hub: {2} (Monitor: {3})", user_id, mac, hub.hub_id, mon_id))
            if self.db.unassociate(hub.hub_id, user_id):
                self.app.signals['hub-unassociate'].send(self, user_id=user_id, hub_id=hub.hub_id)
            else:
                app.logger.error('Cannot unassociate user %d from hub %d', user_id, hub.hub_id)

    def _prox_change(self, sender, mon_id, mac, rssi, **args):
        mon_id = int(mon_id)
        if mon_id not in self.hub_monitor_map:
            return

    def create(self, request):
        if 'description' not in request.form:
            description = ''
        else:
            description = request.form['description']
        
        hub = self.db.create_hub(description)

        if hub:
            resp = make_response(json.dumps(hub.json()), 200)
            resp.mimetype = 'application/json'
            return resp
        else:
            return make_response("Hub creation failed", 400)
        
    def get(self, hub_id):
        hub = self.db.get_hub(hub_id)
        if hub:
            resp = make_response(json.dumps(hub.json()), 200)
            resp.mimetype = 'application/json'
            return resp
        else:
            return make_response("Hub not found", 404)
    
    def get_users(self, hub_id):
        users = self.db.get_users(hub_id)
        if users:
            resp = make_response(json.dumps([user.json() for user in users]), 200)
            resp.mimetype = 'application/json'
            return resp
        else:
            return make_response("No users not found", 404)
        
    @user_loggedin
    def find(self, session):
        user_id = int(session.get_user_id())
        hubs = self.db.find_hubs(user_id)
        resp = make_response(json.dumps([hub.json() for hub in hubs]), 200)
        resp.mimetype = 'application/json'
        return resp
    
    @user_loggedin
    def associate(self, hub_id, session, request):
        user_id = int(session.get_user_id())
        if 'only' in request.args:
            only = True
        else:
            only = False
        
        if self.db.associate(hub_id, user_id, only=only):
            self.app.signals['hub-associate'].send(self, user_id=user_id, hub_id=hub_id)
            return make_response('OK', 200)
        else:
            return make_response('NOK', 500)

    @user_loggedin
    def unassociate(self, hub_id, session, request):
        user_id = int(session.get_user_id())
        if self.db.unassociate(hub_id, user_id):
            self.app.signals['hub-unassociate'].send(self, user_id=user_id, hub_id=hub_id)
            return make_response('OK', 200)
        else:
            return make_response('NOK', 500)
        
app.services['hub_manager'] = HubManager(app)
this_service = app.services['hub_manager']

#===============================================================================
# client i/f
#===============================================================================
@app.route('/bbs/hub', methods=["POST"])
def hub_create():
    return this_service.create(request)

@app.route('/bbs/hub/<hub_id>')
@xsite_enabled
def hub_get(hub_id):
    return this_service.get(hub_id)
        
@app.route('/bbs/hub/find')
@xsite_enabled
def hub_find():
    return this_service.find(session)

@app.route('/bbs/hub/<hub_id>/associate')
@xsite_enabled
def hub_associate(hub_id):
    return this_service.associate(hub_id, session, request)

@app.route('/bbs/hub/<hub_id>/unassociate')
@xsite_enabled
def hub_unassociate(hub_id):
    return this_service.unassociate(hub_id, session, request)

@app.route('/bbs/hub/<hub_id>/users')
@xsite_enabled
def hub_users(hub_id):
    return this_service.get_users(hub_id)