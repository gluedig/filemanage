'''
Created on Aug 21, 2013

@author: gluedig
'''
from functools import wraps
from flask import Response, make_response, Request
#from flask.sessions import SecureCookieSession
from werkzeug.local import LocalProxy
from fm_services.session_interface import SensusSecureCookieSession

def xsite_enabled(f):
    '''
    enable cross site requests
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = f(*args, **kwargs)
        if isinstance(resp, Response):
            resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type'
        return resp
    return decorated_function

#def insession(variable):
#    '''
#    check if variable is present in session data
#    '''
#    def real_decorator(function):
#        def wrapper(*args, **kwargs):
#            found = False
#            for arg in args:
#                if isinstance(arg, LocalProxy):
#                    arg = arg._get_current_object()
#
#                if isinstance(arg, SecureCookieSession):
#                    if variable in arg:
#                        found = True
#
#            if found:
#                resp = function(*args, **kwargs)
#                return resp
#            else:
#                return make_response(str.format('No {0} in session', variable), 400)
#        return wrapper
#    return real_decorator

def user_loggedin(f):
    '''
    check if user is logged in by looking at session data
    '''
    @wraps(f)
    def wrapper(*args, **kwargs):
        logged_in = False
        for arg in args:
            if isinstance(arg, LocalProxy):
                arg = arg._get_current_object()
            if isinstance(arg, SensusSecureCookieSession):
                logged_in = arg.is_logged_in()

        if logged_in:
            resp = f(*args, **kwargs)
            return resp
        else:
            return make_response('User not logged in', 400)
    return wrapper

def post_data(*data):
    '''
    handle posted data either from HTML form or JSON object
    '''
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, LocalProxy):
                    arg = arg._get_current_object()

                if isinstance(arg, Request):
                    request = arg
                    break

            if request:
                parsed_data = {}
                if 'Content-Type' in request.headers:
                    if request.headers['Content-Type'].startswith('application/json'):
                        json_data = request.get_json(silent=True)
                        if not json_data:
                            return make_response('Cannot parse data JSON', 400)

                        for field in data:
                            if field not in json_data:
                                return make_response("Not enough json params", 400)
                            parsed_data[field] = json_data[field]
                    else:
                        for field in data:
                            if field not in request.form:
                                return make_response("Not enough form params", 400)
                            parsed_data[field] = request.form[field]
                else:
                    return make_response("Content-Type not specified", 400)

                request.parsed_data = parsed_data

            resp = function(*args, **kwargs)
            return resp

        return wrapper
    return real_decorator