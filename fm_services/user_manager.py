'''
Created on Jul 31, 2013

@author: developer
'''
from fm_services import app
from flask import session, request, make_response, render_template, Response
import hashlib
from functools import wraps
import json
import datetime

class UserManager:
    def __init__(self, app):
        self.app = app
        self.db = app.db['users']
    
    def _login(self, session, user):
        session['user_id'] = user.user_id
        self.db.login(user.user_id)
        resp = make_response(json.dumps([user.json()]), 200)
        resp.mimetype = 'application/json'
        return resp
    
    def check_login(self, session):
        if 'user_id' in session and self.db.find_by_id(session['user_id']):
            resp = make_response(json.dumps([session['user_id']], 200))
            resp.mimetype = 'application/json'
            return resp
        else:
            if 'user_id' in session:
                session.pop('user_id')
            resp = make_response(json.dumps([], 200))
            resp.mimetype = 'application/json'
            return resp
    
    def login_password(self, session, request):
        if 'email' not in request.form \
        or 'password' not in request.form:
            return ("Not enough form params", 400)
        
        email = request.form['email']
        password = request.form['password']
        if email == '':
            return ('Wrong form data', 400)
        user = self.db.find_by_name(email)
        if user:
            if user.check_password(password):
                return self._login(session, user)
            else:
                return ("Wrong username/password", 401)
        else:
            return ("User not found", 404)
    
    def logout(self, session):
        if 'user_id' in session:
            session.pop('user_id')
        return ('OK', 200)

    def create_user_random(self, session):
        user = self.db.add("", "", "")
        if user:
            user.email = str.format("User_{0}@sens.us", user.user_id)
            return self._login(session, user)
        else:
            return ("User creation failed", 400)
        
    def create_user(self, session, request):
        if 'email' not in request.form \
        or 'password' not in request.form:
                    return ("Not enough form params", 400)
        
        email = request.form['email']
        password = request.form['password']
        email_hash = hashlib.md5(email.strip().lower()).hexdigest()

        if email == '':
            return ('Wrong form data', 400)

        img_url = str.format("http://www.gravatar.com/avatar/{0}?d=mm", email_hash)
        user = self.db.add(email, password, img_url)

        if user:
            return self._login(session, user)
        else:
            return ("User creation failed", 400)

    def get_user(self, user_id):
        user = self.db.find_by_id(user_id)
        if user:
            resp = make_response(json.dumps([user.json()]), 200)
            resp.mimetype = 'application/json'
            return resp
        else:
            return ("User not found", 404)
    
    def modify_user(self, user_id, session, request):
        if 'user_id' not in session:
            return ('No user_id in session', 400)
        if not int(user_id) == int(session['user_id']):
            return ('Cannot modify other user', 403)

        user = self.db.find_by_id(user_id)
        if not user:
            return ('user not found', 404)

        new_data = request.get_json(silent=True)
        if not new_data:
            return ('Cannot parse user data JSON', 400)

        modified = False
        for key, value in new_data[0].iteritems():
            if hasattr(user, key):
                setattr(user, key, value)
                modified = True

        if modified:
            user.modified = datetime.datetime.now()
        return 'OK'

    def get_contacts(self, session):
        if 'user_id' not in session:
            return ('No user_id in session', 400)
        user_id = int(session['user_id'])
        contacts = self.db.get_contacts(user_id)
        
        cont = []
        for contact in contacts:
            cont.append(contact.json())
            
        resp = make_response(json.dumps(cont), 200)
        resp.mimetype = 'application/json'
        return resp 
    
    def add_contact(self, session, request):
        if 'user_id' not in session:
            return ('No user_id in session', 400)
        
        if 'id' not in request.args:
                    return ("Not enough form params", 400)
                
        user_id = int(session['user_id'])
        contact_id = int(request.args['id'])
        if self.db.add_contact(user_id, contact_id):
            return ('OK', 200)
        else:
            return ('NOK', 500)
    
    def delete_contact(self, session, request):
        if 'user_id' not in session:
            return ('No user_id in session', 400)
        
        if 'id' not in request.args:
                    return ("Not enough form params", 400)
                
        user_id = int(session['user_id'])
        contact_id = int(request.args['id'])
        if self.db.remove_contact(user_id, contact_id):
            return ('OK', 200)
        else:
            return ('NOK', 500)
    
app.services['user_manager'] = UserManager(app)
this_service = app.services['user_manager']

#===============================================================================
# client i/f
#===============================================================================
def xsite_enabled(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = f(*args, **kwargs)
        if isinstance(resp, Response):
            resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT'
            resp.headers['Access-Control-Allow-Origin'] = '*'
            #resp.headers['Access-Control-Allow-Headers'] = 'X-Requested-With'
        return resp
    return decorated_function


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
    

@app.route('/user/create_form', methods=["GET"])
@xsite_enabled
def user_create_form():
    mac = None
    if 'mac' in session:
        mac = session['mac']
    if not mac and request.args and 'mac' in request.args:
        mac = request.args['mac']
    if not mac:
        mac = 'unknown'
    return render_template('create_user.html', client_mac=mac)


