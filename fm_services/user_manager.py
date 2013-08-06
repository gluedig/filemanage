'''
Created on Jul 31, 2013

@author: developer
'''
from fm_services import app
from flask import session, request, make_response, render_template, Response
import md5
from functools import wraps

class UserManager:
    def __init__(self, app):
        self.app = app
        self.db = app.db['users']
            
    def login_device(self, session, mac):
        if not app.services['client_manager'].register(mac, session):
            return (False, "Client registration failed")
        else:
            user = self.db.find_by_device(mac)
            if user:
                session['user_id'] = user.user_id
                self.db.login(user.user_id)
                resp = make_response(user.json(), 200)
                resp.mimetype = 'application/json'
                return resp
            else:
                return ("Associated user not found", 404)
    
    def create_user_random(self, session, mac):
        if self.db.find_by_device(mac):
            return (False, "Device already associated")
        
        new_user = self.db.add("", "", mac)
        if new_user:
            new_user.email = str.format("User_{0}@sens.us", new_user.user_id)
            resp = make_response(new_user.json(), 200)
            resp.mimetype = 'application/json'
            return resp
        else:
            return ("User creation failed", 400)
        
    def create_user(self, session, request):
        if 'email' not in request.form or 'mac' not in request.form:
            return (False, "Not enough form params")
        
        email = request.form['email']
        mac = request.form['mac']
        email_hash = md5.md5(email.strip().lower()).hexdigest()
        
        if email == '' or mac == '':
            return (False, 'Wrong form data')
        
        if self.db.find_by_device(mac):
            return (False, "Device already associated")
        
        img_url = str.format("http://www.gravatar.com/avatar/{0}?d=mm", email_hash)
        new_user = self.db.add(email, img_url, mac)
        if new_user:
            resp = make_response(new_user.json(), 200)
            resp.mimetype = 'application/json'
            return resp
        else:
            return ("User creation failed", 400)

    def get_user(self, user_id):
        user = self.db.find_by_id(user_id)
        if user:
            resp = make_response(user.json(), 200)
            resp.mimetype = 'application/json'
            return resp
        else:
            return ("User not found", 404)
    
    def find_by_device(self, mac):
        user = self.db.find_by_device(mac)
        if user:
            resp = make_response(user.json(), 200)
            resp.mimetype = 'application/json'
            return resp
        else:
            return ("User not found", 404)
            

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
        return resp
    return decorated_function


@app.route('/user/<user_id>', methods=["PUT","GET"])
@xsite_enabled
def user_get(user_id):
    if request.method == "GET":
        return this_service.get_user(user_id)

    return ('Not yet', 501)

@app.route('/user/login', methods=["POST","GET"])
@xsite_enabled
def user_login():
    if request.method == "GET":
        if 'id' in request.args:
            mac = request.args['id']
            return this_service.login_device(session, mac)
        else:
            return ('id missing', 400)
        
    return ('Not yet', 501)

@app.route('/user', methods=["POST","GET"])
@xsite_enabled
def user_create():
    if request.method == "GET":
        if 'id' in request.args:
            mac = request.args['id']
            return this_service.create_user_random(session, mac)
        else:
            return ('id missing', 400)
        
    elif request.method == "POST":
        return this_service.create_user(session, request)

@app.route('/user/find', methods=["GET"])
@xsite_enabled
def user_find():
    if 'id' in request.args:
        mac = request.args['id']
        return this_service.find_by_device(mac)
    else:
        return ('id missing', 400)

@app.route('/user/create', methods=["GET"])
@xsite_enabled
def user_create_form():
    mac = None
    if 'mac' in session:
        mac = session['mac']

    if not mac and request.args and 'mac' in request.args:
        mac = request.args['mac']

    if not mac:
        return ('Client MAC address not known', 404)
    
    return render_template('create_user.html', client_mac=mac)
