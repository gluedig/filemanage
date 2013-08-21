'''
Created on Aug 21, 2013

@author: gluedig
'''
from functools import wraps
from flask import Response
from flask.sessions import SecureCookieSession
from fm_services import app
from werkzeug.local import LocalProxy

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

def user_loggedin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logged_in = False

        for arg in args:
            if isinstance(arg, LocalProxy):
                arg = arg._get_current_object()

            if isinstance(arg, SecureCookieSession):
                if 'user_id' in arg:
                    logged_in = True

        if logged_in:        
            resp = f(*args, **kwargs)
            return resp
        else:
            return ('No user_id in session', 400)

    return decorated_function