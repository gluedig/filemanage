'''
Created on Jun 12, 2013

@author: developer
'''
from flask import Flask
from blinker import Namespace

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['UPLOAD_FOLDER'] = '/var/tmp/uploads'

app.signals_namespace = Namespace()
app.signals = {}
app.signals['client-register'] = app.signals_namespace.signal('client-register')
app.signals['client-unregister'] = app.signals_namespace.signal('client-unregister')

app.services = {}

import monitor_manager
import client_manager
import group_manager
import filebox
