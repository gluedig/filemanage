'''
Created on Jul 31, 2013

@author: developer
'''
from fm_services import app
from flask import session, request
import random
import json
import md5

class UserDb:
    class User:
        def __init__(self):
            self.user_id = None
            self.email = None
            self.image = None
            self.device = None
        def json(self):
            return json.dumps([{'id':self.user_id,
                                'email':self.email,
                                'image':self.image
                                }])
        def __str__(self):
            return self.json()
    
    def __init__(self):
        self.users = {}
        self.by_device = {}
    
    def find_by_device(self, device):
        if device in self.by_device:
            return self.by_device[device]
        else:
            return None
        
    def find_by_id(self, user_id):
        user_id = int(user_id)
        if user_id in self.users:
            return self.users[user_id]
        else:
            return None

    def add(self, email, image, device):
        if self.find_by_device(device):
            return None
        
        new_id = random.randint(0, 1000000)
        while self.find_by_id(new_id):
            new_id = random.randint(0, 1000000)
        
        new_user = UserDb.User()
        new_user.user_id = new_id
        new_user.email = email
        new_user.image = image
        new_user.device = device
        
        self.users[new_id] = new_user
        self.by_device[device] = new_user
        app.logger.debug(str.format("{0}", self.users))
        
        return new_user

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
                return (True, user.json())
            else:
                return (False, "Associated user not found")
    
    def create_user_random(self, session, mac):
        if self.db.find_by_device(mac):
            return (False, "Device already associated")
        
        new_user = self.db.add("", "", mac)
        if new_user:
            new_user.email = str.format("User_{0}@sens.us", new_user.user_id)
            return (True, new_user.json())
        else:
            return (False, "User creation failed")
        
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
            return (True, new_user.json())
        else:
            return (False, "User creation failed")

    def get_user(self, user_id):
        user = self.db.find_by_id(user_id)
        if user:
            return (True, user.json())
        else:
            return (False, str.format("{0}", self.db.users.values()))
            

app.db['users'] = UserDb()
app.services['user_manager'] = UserManager(app)
this_service = app.services['user_manager']

#===============================================================================
# client i/f
#===============================================================================
@app.route('/user/<user_id>', methods=["PUT","GET"])
def user_get(user_id):
    if request.method == "GET":
        (resp, data) = this_service.get_user(user_id)
        if resp:
            return (data, 200)
        else:
            return (data, 404)
    
    
    return ('Not yet', 501)
        

@app.route('/user/login', methods=["POST","GET"])
def user_login():
    if request.method == "GET":
        if 'id' in request.args:
            mac = request.args['id']
            (resp, data) = this_service.login_device(session, mac)
            if resp:
                return (data, 200)
            else:
                return (data, 400)
        else:
            return ('id missing', 400)
        
    return ('Not yet', 501)

@app.route('/user', methods=["POST","GET"])
def user_create():
    if request.method == "GET":
        if 'id' in request.args:
            mac = request.args['id']
            (resp, data) =  this_service.create_user_random(session, mac)
            if resp:
                return (data, 200)
            else:
                return (data, 400)
        else:
            return ('id missing', 400)
        
    elif request.method == "POST":
        (resp, data) =  this_service.create_user(session, request)
        if resp:
            return (data, 200)
        else:
            return (data, 400)
    
