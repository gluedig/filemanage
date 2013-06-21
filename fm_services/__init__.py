'''
Created on Jun 12, 2013

@author: developer
'''
from flask import Flask, render_template
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


app.services = {}

import monitor_manager
import client_manager
import group_manager
import filebox
import update


@app.route('/')
def root():
    return render_template('index.html', client_mac='0000')

@app.route('/test/update')
def test_update_route():
    return render_template('update_test.html')
