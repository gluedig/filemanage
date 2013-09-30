'''
Created on Sep 11, 2013

@author: gluedig
'''
from blinker import Namespace
from fm_services import app

signals_namespace = Namespace()
app.signals['client-register'] = signals_namespace.signal('client-register')
app.signals['client-unregister'] = signals_namespace.signal('client-unregister')
app.signals['proximity-entered'] = signals_namespace.signal('proximity-entered')
app.signals['proximity-left'] = signals_namespace.signal('proximity-left')
app.signals['proximity-change'] = signals_namespace.signal('proximity-change')

app.signals['user-login'] = signals_namespace.signal('user-login')
app.signals['user-device-associate'] = signals_namespace.signal('user-device-associate')
app.signals['user-logout'] = signals_namespace.signal('user-logout')

app.signals['hub-associate'] = signals_namespace.signal('hub-associate')
app.signals['hub-unassociate'] = signals_namespace.signal('hub-unassociate')
app.signals['hub-message'] = signals_namespace.signal('hub-message')

#signals related to hub
hub_signals = [app.signals['hub-associate'],
               app.signals['hub-unassociate'],
               app.signals['hub-message']]

proximity_signals = [app.signals['proximity-entered'],
                     app.signals['proximity-left'],
                     app.signals['proximity-change']]