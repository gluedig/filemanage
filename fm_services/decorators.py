'''
Created on Aug 21, 2013

@author: gluedig
'''
from functools import wraps
from flask import Response, make_response
from flask.sessions import SecureCookieSession
from fm_services import app
from werkzeug.local import LocalProxy

def xsite_enabled(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = f(*args, **kwargs)
        if isinstance(resp, Response):
            resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type'
        return resp
    return decorated_function

def insession(variable):
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            found = False
            for arg in args:
                if isinstance(arg, LocalProxy):
                    arg = arg._get_current_object()

                if isinstance(arg, SecureCookieSession):
                    if variable in arg:
                        found = True

            if found:
                resp = function(*args, **kwargs)
                return resp
            else:
                return make_response(str.format('No {0} in session', variable), 400)
        return wrapper
    return real_decorator

def user_loggedin(f):
    return insession('user_id')(f)
