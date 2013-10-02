'''
Created on Jun 12, 2013

@author: developer
'''
from flask import Flask, render_template, request, session, make_response, redirect, url_for

app = Flask(__name__, static_url_path='')
app.config.from_object('fm_services.default_settings')


from session_interface import SensusSessionInterface
app.session_interface = SensusSessionInterface()

app.signals = {}
app.services = {}
app.db = {}

import signals

from decorators import xsite_enabled
@xsite_enabled
def options_response():
    return Flask.make_default_options_response(app)
app.make_default_options_response = options_response

import db.sql.sqllite
import db.sql.user
import db.sql.hub
import db.sql.message

from db.sql import Base
#Base.metadata.tables['devices'].drop()
Base.metadata.create_all()

import monitor_manager
import user_manager
import hub_manager
import bbs
#import events_forwarder

@app.route('/')
def index():
    return redirect('/index.html')

@app.route('/index')
@xsite_enabled
def root():
    mac = None
    if request.args and 'mac' in request.args:
        mac = request.args['mac']
        session.set_device(mac)
    if not mac and session.has_device():
        mac = session.get_device()
    if not mac:
        mac = 'unknown'

    hub = None
    if request.args and 'hub' in request.args:
        hub = request.args['hub']
    if not hub:
        hub = 'unknown'
    return render_template('index.html', client_mac=mac, hub=hub)

@app.route('/splash')
@xsite_enabled
def splash():
    if request.args and 'mac' in request.args:
        mac = request.args['mac']
        session.set_device(mac)

    if request.args and\
     'authaction' in request.args and\
     'tok' in request.args and\
     'redir' in request.args:
        authtarget = request.args['authaction']
        tok = request.args['tok']
        redir = request.args['redir']
        app.logger.debug(authtarget)
        app.logger.debug(redir)
        if authtarget.startswith(redir):
            redir='http://www.sens.us'

        from urllib import quote
        newtarget = str.format("{0}?redir={1}&tok={2}", authtarget, quote(redir,""), quote(tok, ""))
        dumptarget =  str.format("{0}?redir={1}&tok={2}", authtarget, quote(request.url_root,""), quote(tok, ""))
        return render_template('splash.html', authtarget=newtarget, dumptarget=dumptarget)
    return make_response('NOK', 500)
