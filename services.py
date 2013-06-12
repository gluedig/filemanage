'''
Created on Jun 12, 2013

@author: developer
'''
from mac_resolver import resolve


from flask import Flask, request, redirect, session

app = Flask(__name__)
app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.mac_resolve = resolve.MacResolver()

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
def register_route(mac):
    ip = request.remote_addr
    session['mac'] = mac
    return "Registered IP: "+ip+" MAC: "+mac

@app.route('/client/unregister')
def unregister_route():
    if 'mac' in session:
        mac = session.pop('mac', None)
        return "Unregistered MAC: "+mac
    else:
        return ('No MAC in session', 404)
    
    
#wifi monitor i/f
@app.route('/monitor/register/<mon_id>')
def mon_register_route(mon_id):
    return "OK"

@app.route('/monitor/unregister/<mon_id>')
def mon_unregister_route(mon_id):
    return "OK"

@app.route('/monitor/event/<mon_id>/<op>/<mac>')
def event_route(mon_id, op, mac):
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
