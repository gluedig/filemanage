'''
Created on Jul 31, 2013

@author: developer
'''
from fm_services import app
from fm_services.decorators import xsite_enabled, user_loggedin, post_data
from flask import session, request, make_response, render_template
import hashlib
import json
import datetime

class UserManager:
    def __init__(self, app):
        self.app = app
        self.db = app.db['users']
    
    def _login(self, session, user):
        session.login(user.user_id)
        self.db.login(user.user_id)
        self._maybe_associate_device(session)
        resp = make_response(json.dumps(user.json()), 200)
        resp.mimetype = 'application/json'
        self.app.signals['user-login'].send(self, id=user.user_id)
        return resp
    
    def check_login(self, session):
        if session.is_logged_in() and self.db.find_by_id(session.get_user_id()):
            self._maybe_associate_device(session)
            resp = make_response(json.dumps([session.get_user_id()], 200))
            resp.mimetype = 'application/json'
            return resp
        else:
            session.logout()
            resp = make_response(json.dumps([], 200))
            resp.mimetype = 'application/json'
            return resp
    
    def _maybe_associate_device(self, session):
        if session.has_device() and session.is_logged_in():
            self.db.associate_device(session.get_user_id(), session.get_device())
            self.app.signals['user-device-associate'].send(self, id=session.get_user_id(), mac=session.get_device())

    @post_data('email', 'password')
    def login_password(self, session, request):
        email = request.parsed_data['email']
        password = request.parsed_data['password']
        if email == '':
            return make_response('Wrong email data', 400)
        user = self.db.find_by_name(email)
        if user:
            if user.check_password(password):
                return self._login(session, user)
            else:
                return make_response("Wrong username/password", 401)
        else:
            return make_response("User not found", 404)
    
    def logout(self, session):
        if session.is_logged_in():
            user_id = session.get_user_id()
            session.logout()
            self.db.logout(user_id)
            self.app.signals['user-logout'].send(self, id=user_id)
        return make_response('OK', 200)

    def create_user_random(self, session):
        user = self.db.add("", "", "")
        if user:
            user.email = str.format("User_{0}@sens.us", user.user_id)
            return self._login(session, user)
        else:
            return make_response("User creation failed", 400)

    @post_data('email', 'password')
    def create_user(self, session, request):
        email = request.parsed_data['email']
        password = request.parsed_data['password']
        email_hash = hashlib.md5(email.strip().lower()).hexdigest()

        if email == '':
            return make_response('Wrong email data', 400)

        img_url = str.format("http://www.gravatar.com/avatar/{0}?d=mm", email_hash)
        user = self.db.add(email, password, img_url)

        if user:
            return self._login(session, user)
        else:
            return make_response("User creation failed", 400)

    def get_user(self, user_id):
        user = self.db.find_by_id(user_id)
        if user:
            resp = make_response(json.dumps(user.json()), 200)
            resp.mimetype = 'application/json'
            return resp
        else:
            return make_response("User not found", 404)

    @user_loggedin
    def modify_user(self, user_id, session, request):
        if not int(user_id) == int(session.get_user_id()):
            return make_response('Cannot modify other user', 403)

        user = self.db.find_by_id(user_id)
        if not user:
            return make_response('user not found', 404)

        new_data = request.get_json(silent=True)
        if not new_data:
            return make_response('Cannot parse user data JSON', 400)

        modified = False
        for key, value in new_data[0].iteritems():
            if hasattr(user, key):
                setattr(user, key, value)
                modified = True

        if modified:
            user.modified = datetime.datetime.now()
        return make_response('OK', 200)

    @user_loggedin
    def get_contacts(self, session):
        user_id = int(session.get_user_id())
        contacts = self.db.get_contacts(user_id)
        resp = make_response(json.dumps([contact.json() for contact in contacts]), 200)
        resp.mimetype = 'application/json'
        return resp 

    @user_loggedin
    def add_contact(self, session, request):
        if 'id' not in request.args:
                    return ("Not enough form params", 400)
                
        user_id = int(session.get_user_id())
        contact_id = int(request.args['id'])
        if self.db.add_contact(user_id, contact_id):
            resp = make_response('OK', 200)
        else:
            resp = make_response('NOK', 500)
        return resp

    @user_loggedin
    def delete_contact(self, session, request):
        if 'id' not in request.args:
                    return ("Not enough form params", 400)
                
        user_id = int(session.get_user_id())
        contact_id = int(request.args['id'])
        if self.db.remove_contact(user_id, contact_id):
            resp = make_response('OK', 200)
        else:
            resp = make_response('NOK', 500)
        return resp

    def users_search(self, session, request):
        if 'query' not in request.args:
                    return ("Not enough form params", 400)
        search_term = request.args['query']
        cont = []
        for contact in self.db.find(search_term):
            cont.append(contact.json())

        resp = make_response(json.dumps(cont), 200)
        resp.mimetype = 'application/json'
        return resp

    def users_list(self):
        cont = []
        for contact in self.db.find(''):
            cont.append(contact.json())

        resp = make_response(json.dumps(cont), 200)
        resp.mimetype = 'application/json'
        return resp


app.services['user_manager'] = UserManager(app)
this_service = app.services['user_manager']

#===============================================================================
# client i/f
#===============================================================================
@app.route('/user/<user_id>', methods=["PUT","GET"])
@xsite_enabled
def user_get(user_id):
    if request.method == "GET":
        return this_service.get_user(user_id)
    elif request.method == "PUT":
        return this_service.modify_user(user_id, session, request)

@app.route('/user/login', methods=["POST", "GET"])
@xsite_enabled
def user_login():
    if request.method == 'POST':
        return this_service.login_password(session, request)
    elif request.method == 'GET':
        return this_service.check_login(session)

@app.route('/user/logout', methods=["GET"])
@xsite_enabled
def user_logout():
    return this_service.logout(session)

@app.route('/user/create', methods=["POST","GET"])
@xsite_enabled
def user_create():
    if request.method == "GET":
        return this_service.create_user_random(session)
    elif request.method == "POST":
        return this_service.create_user(session, request)

@app.route('/user/contacts', methods=["POST", "GET", "DELETE"])
@xsite_enabled
def user_contacts():
    if request.method == 'POST':
        return this_service.add_contact(session, request)
    elif request.method == 'DELETE':
        return this_service.delete_contact(session, request)
    elif request.method == 'GET':
        return this_service.get_contacts(session)

@app.route('/users', methods=["GET"])
@xsite_enabled
def users_search():
    return this_service.users_search(session, request)

@app.route('/users/list', methods=["GET"])
@xsite_enabled
def users_list():
    return this_service.users_list()

@app.route('/user/create_form', methods=["GET"])
def user_create_form():
    mac = None
    if 'mac' in session:
        mac = session['mac']
    if not mac and request.args and 'mac' in request.args:
        mac = request.args['mac']
    if not mac:
        mac = 'unknown'
    return render_template('create_user.html', client_mac=mac)

@app.route('/user/login_form', methods=["GET"])
def user_login_form():
    mac = None
    if 'mac' in session:
        mac = session['mac']
    if not mac and request.args and 'mac' in request.args:
        mac = request.args['mac']
    if not mac:
        mac = 'unknown'
        
    hub = None
    if request.args and 'hub' in request.args:
        hub = request.args['hub']
    if not hub:
        hub = 'unknown'
    return render_template('login_user.html', client_mac=mac, hub=hub)
