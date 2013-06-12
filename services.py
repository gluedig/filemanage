'''
Created on Jun 12, 2013

@author: developer
'''
from resolve import MacResolver
from monitor_manager import MonitorManager

from flask import Flask, request, redirect, session

app = Flask(__name__)
app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.mac_resolve = MacResolver()
app.mon_manager = MonitorManager()

#mac finder i/f
@app.route('/resolve')
def mac_route():
    ip = request.remote_addr
    mac =  app.mac_resolve.resolve(ip)
    
    if mac:
        return redirect('client/register/'+mac)
    else:
        return ('Not found', 404)

#client i/f
@app.route('/client/register/<mac>')
def client_register_route(mac):
    ip = request.remote_addr
    session['mac'] = mac
    return "Registered IP: "+ip+" MAC: "+mac

@app.route('/client/unregister')
def client_unregister_route():
    if 'mac' in session:
        mac = session.pop('mac', None)
        return "Unregistered MAC: "+mac
    else:
        return ('No MAC in session', 404)
    
    
#wifi monitor i/f
@app.route('/monitor/register/<mon_id>')
def mon_register_route(mon_id):
    ip = request.remote_addr
    return app.mon_manager.register(ip, mon_id)

@app.route('/monitor/unregister/<mon_id>')
def mon_unregister_route(mon_id):
    return app.mon_manager.unregister(mon_id)

@app.route('/monitor/event/<mon_id>/<event>/<mac>')
def mon_event_route(mon_id, event, mac):
    return app.mon_manager.client_event(mon_id, event, mac)

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
