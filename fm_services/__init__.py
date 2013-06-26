'''
Created on Jun 12, 2013

@author: developer
'''
from flask import Flask, render_template, request, session
from blinker import Namespace

app = Flask(__name__, static_url_path='')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['UPLOAD_FOLDER'] = '/var/tmp/uploads'

app.signals_namespace = Namespace()
app.signals = {}
app.signals['client-register'] = app.signals_namespace.signal('client-register')
app.signals['client-unregister'] = app.signals_namespace.signal('client-unregister')
app.signals['group-member-add'] = app.signals_namespace.signal('group-member-add')
app.signals['group-member-remove'] = app.signals_namespace.signal('group-member-remove')
app.signals['file-upload'] = app.signals_namespace.signal('file-upload')
app.signals['proximity-entered'] = app.signals_namespace.signal('proximity-entered')
app.signals['proximity-left'] = app.signals_namespace.signal('proximity-left')

app.services = {}

import monitor_manager
import client_manager
import group_manager
import filebox
#import update
import events_forwarder

@app.route('/')
def root():
    mac = None
    if request.args and 'mac' in request.args:
        mac = request.args['mac']

    if not mac and 'mac' in session:
        mac = session['mac']

    if not mac:
        return ('Client MAC address not known', 404)
    return render_template('index.html', client_mac=mac)

@app.route('/test/update')
def test_update_route():
    return render_template('update_test.html')
