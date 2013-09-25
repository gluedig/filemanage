'''
Created on Sep 11, 2013

@author: gluedig
'''
from fm_services import app
from flask import session, request, make_response
from fm_services.decorators import xsite_enabled, user_loggedin, post_data
import json

class Bbs:
    def __init__(self, app):
        self.app = app
        self.db = app.db['messages']
    
    def get_msg(self, msg_id):
        msg_id = int(msg_id)
        msg = self.db.get(msg_id)
        if msg:
            resp = make_response(json.dumps([msg.json()]), 200)
            resp.mimetype = 'application/json'
            return resp
        else:
            return make_response("Message not found", 404)
    
    @user_loggedin
    def modify_msg(self, msg_id, session, request):
        msg = self.db.get(msg_id)
        if not msg:
            return make_response('Message not found', 404)

        if not int(msg.user) == int(session.get_user_id()):
            return make_response('Cannot modify other user', 403)

        new_data = request.get_json(silent=True)
        if not new_data:
            return make_response('Cannot parse user data JSON', 400)

        for key, value in new_data[0].iteritems():
            if hasattr(msg, key):
                setattr(msg, key, value)
        
        return self.get_msg(msg_id)
    
    @user_loggedin
    def delete_msg(self, msg_id, session, request):
        msg = self.db.get(msg_id)
        if not msg:
            return make_response('Message not found', 404)
        
        if int(msg.user) != int(session.get_user_id()):
            return make_response('Cannot modify other user', 403)
        
        if self.db.remove(msg_id):
            resp = make_response('OK', 200)
        else:
            resp = make_response('NOK', 500)
        return resp
        
    @user_loggedin
    def find_user_msg(self, session, request):
        user_id = int(session.get_user_id())
        count = False
        start = 0
        end = None
        
        if 'count' in request.args:
            count = True
        if 'start' in request.args:
            start = int(request.args['start'])
        if 'end' in request.args:
            end = int(request.args['end'])    
        
        msgs = self.db.get_by_user(user_id, count=count, start=start, end=end)
        if msgs != None:
            if count:
                resp = make_response(json.dumps([msgs]), 200)
                resp.mimetype = 'application/json'
            else:
                resp = make_response(json.dumps([msg.json() for msg in msgs]), 200)
                resp.mimetype = 'application/json'
        else:
            resp = make_response(json.dumps([]), 200)
            resp.mimetype = 'application/json'
        
        return resp
        
    def find_hub_msg(self, hub_id, session, request):
        hub_id = int(hub_id)
        count = False
        start = 0
        end = None
        
        if 'count' in request.args:
            count = True
        if 'start' in request.args:
            start = int(request.args['start'])
        if 'end' in request.args:
            end = int(request.args['end'])    
        
        msgs = self.db.get_by_hub(hub_id, count=count, start=start, end=end)
        if msgs != None:
            if count:
                resp = make_response(json.dumps([msgs]), 200)
                resp.mimetype = 'application/json'
            else:
                resp = make_response(json.dumps([msg.json() for msg in msgs]), 200)
                resp.mimetype = 'application/json'
        else:
            resp = make_response(json.dumps([]), 200)
            resp.mimetype = 'application/json'
        
        return resp
    
    @user_loggedin
    @post_data('text')
    def post_msg(self, hub_id, session, request):
        text = request.parsed_data['text']
        user_id = int(session.get_user_id())
        hub_id = int(hub_id)
        
        msg = self.db.post(user_id, hub_id, text)
        if msg:
            resp = make_response(json.dumps(msg.json()), 200)
            resp.mimetype = 'application/json'
            self.app.signals['hub-message'].send(self, user_id=user_id, hub_id=hub_id, msg_id=msg.msg_id)
        else:
            resp = make_response('NOK', 500)
        
        return resp
        
this_service = app.services['bbs'] = Bbs(app)
#===============================================================================
# client i/f
#===============================================================================
@app.route('/bbs/message/<msg_id>', methods=['GET', 'PUT', 'DELETE'])
@xsite_enabled
def msg_ops(msg_id):
    if request.method == "GET":
        return this_service.get_msg(msg_id)
    elif request.method == "PUT":
        return this_service.modify_msg(msg_id, session, request)
    elif request.method == "DELETE":
        return this_service.delete_msg(msg_id, session, request)

@app.route('/bbs/user_msgs', methods=['GET'])
@xsite_enabled
def msg_user_find():
    return this_service.find_user_msg(session, request)

@app.route('/bbs/hub/<hub_id>/messages', methods=['GET', 'POST'])
@xsite_enabled
def msg_hub_ops(hub_id):
    if request.method == "GET":
        return this_service.find_hub_msg(hub_id, session, request)
    elif request.method == "POST":
        return this_service.post_msg(hub_id, session, request)