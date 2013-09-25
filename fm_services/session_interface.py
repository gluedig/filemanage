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

class SensusSessionInterface(SecureCookieSessionInterface):
    session_class = SensusSecureCookieSession
    