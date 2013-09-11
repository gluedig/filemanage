'''
Created on Jun 12, 2013

@author: developer
'''
from flask import Flask, render_template, request, session

app = Flask(__name__, static_url_path='')
app.config.from_object('fm_services.default_settings')

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
import db.memory.client

from db.sql import Base
Base.metadata.create_all()

import monitor_manager
import client_manager
#import event_manager
#import filebox
#import events_forwarder
import user_manager
import hub_manager
import bbs

@app.route('/')
def root():
    mac = None
    if request.args and 'mac' in request.args:
        mac = request.args['mac']
    if not mac and 'mac' in session:
        mac = session['mac']
    if not mac:
        mac = 'unknown'
    
    hub = None
    if request.args and 'hub' in request.args:
        hub = request.args['hub']
    if not hub:
        hub = 'unknown'
    return render_template('index.html', client_mac=mac, hub=hub, sockjs_url = app.config['SOCKJS_URL'])
