'''
Created on Aug 6, 2013

@author: gluedig
'''
from fm_services import app
import fm_services.db.user
from fm_services.db.user import userDb
import random
import datetime

class userDb(fm_services.db.user.userDb):
    
    class User(fm_services.db.user.userDb.User):
        def __init__(self):
            self.user_id = None
            self.firstname = "None"
            self.lastname = "None"
            self.email = None
            self.password = None
            self.image = None

            now = datetime.datetime.now()
            self.created = now
            self.modified = now
            self.seen = now

            self.device = []
    
    def __init__(self):
        self.users = {}
        self.by_device = {}
        
    def find_by_id(self, user_id):
        user_id = int(user_id)
        if user_id in self.users:
            return self.users[user_id]
        else:
            return None
        
    def find_by_name(self, user_name):
        for user in self.users.values():
            if user.email == user_name:
                return user
        return None

    def add(self, email, passwd, image):
        new_id = random.randint(0, 1000000)
        while self.find_by_id(new_id):
            new_id = random.randint(0, 1000000)
        
        new_user = userDb.User()
        new_user.user_id = new_id
        new_user.email = email
        new_user.set_password(passwd)
        new_user.image = image

        self.users[new_id] = new_user

        return new_user
    
    def login(self, user_id):
        user_id = int(user_id)
        if user_id in self.users:
            self.users[user_id].seen = datetime.datetime.now()

app.db['users'] = userDb()