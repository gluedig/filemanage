'''
Created on Sep 11, 2013

@author: gluedig
'''
from fm_services import app
from flask import session, request, make_response
from fm_services.decorators import xsite_enabled, user_loggedin
import json

class HubManager:
    def __init__(self, app):
        self.app = app
        self.db = app.db['hubs']
        
    def create(self, request):
        if 'description' not in request.form:
            description = ''
        else:
            description = request.form['description']
        
        hub = self.db.create_hub(description)

        if hub:
            resp = make_response(json.dumps([hub.json()]), 200)
            resp.mimetype = 'application/json'
            return resp
        else:
            return make_response("Hub creation failed", 400)
        
    def get(self, hub_id):
        hub = self.db.get_hub(hub_id)
        if hub:
            resp = make_response(json.dumps([hub.json()]), 200)
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
        user_id = int(session['user_id'])
        hubs = self.db.find_hubs(user_id)
        
        hubb = []
        for hub in hubs:
            hubb.append(hub.json())
            
        resp = make_response(json.dumps(hubb), 200)
        resp.mimetype = 'application/json'
        return resp
    
    @user_loggedin
    def associate(self, hub_id, session, request):
        user_id = int(session['user_id'])
        if 'only' in request.args:
            only = True
        else:
            only = False
        
        if self.db.associate(hub_id, user_id, only=only):
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

@app.route('/bbs/hub/<hub_id>/users')
@xsite_enabled
def hub_users(hub_id):
    return this_service.get_users(hub_id)