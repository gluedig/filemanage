'''
Created on Sep 25, 2013

@author: gluedig
'''
from flask.sessions import SecureCookieSessionInterface, SecureCookieSession

class SensusSecureCookieSession(SecureCookieSession):
    def is_logged_in(self):
        return 'user_id' in self
    
    def get_user_id(self):
        return self['user_id']
    
    def login(self, user_id):
        self['user_id'] = user_id
        
    def logout(self):
        if self.is_logged_in():
            self.pop('user_id')

    def has_device(self):
        return 'mac' in self

    def get_device(self):
        return self['mac']

    def set_device(self, mac):
        self['mac'] = mac

    def uset_device(self):
        if self.has_device():
            self.pop('mac')

class SensusSessionInterface(SecureCookieSessionInterface):
    session_class = SensusSecureCookieSession
    