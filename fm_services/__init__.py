'''
Created on Jun 12, 2013

@author: developer
'''
from flask import Flask, render_template, request, session
from blinker import Namespace

app = Flask(__name__, static_url_path='')
app.config.from_object('fm_services.default_settings')

app.signals_namespace = Namespace()
app.signals = {}
app.signals['client-register'] = app.signals_namespace.signal('client-register')
app.signals['client-unregister'] = app.signals_namespace.signal('client-unregister')
app.signals['group-member-add'] = app.signals_namespace.signal('group-member-add')
app.signals['group-member-remove'] = app.signals_namespace.signal('group-member-remove')
app.signals['file-upload'] = app.signals_namespace.signal('file-upload')
app.signals['proximity-entered'] = app.signals_namespace.signal('proximity-entered')
app.signals['proximity-left'] = app.signals_namespace.signal('proximity-left')
app.signals['proximity-change'] = app.signals_namespace.signal('proximity-change')

app.services = {}
app.db = {}

import db.memory.client
import db.memory.user

import monitor_manager
import client_manager
import group_manager
import filebox
import events_forwarder
import user_manager

@app.route('/')
def root():
    mac = None
    if request.args and 'mac' in request.args:
        mac = request.args['mac']

    if not mac and 'mac' in session:
        mac = session['mac']

    if not mac:
        return ('Client MAC address not known', 404)
    return render_template('index.html', client_mac=mac, sockjs_url = app.config['SOCKJS_URL'])
