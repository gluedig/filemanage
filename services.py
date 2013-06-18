'''
Created on Jun 12, 2013

@author: developer
'''
from resolve import MacResolver
from monitor_manager import MonitorManager
from client_manager import ClientManager
from group_manager import GroupManager

from flask import Flask, request, redirect, session

app = Flask(__name__)
app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.mac_resolve = MacResolver()
app.mon_manager = MonitorManager()
app.clt_manager = ClientManager()
app.grp_manager = GroupManager(app.clt_manager, app.mon_manager)

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
    return app.clt_manager.register(mac, session)

@app.route('/client/unregister')
def client_unregister_route():
    return app.clt_manager.unregister(session)

@app.route('/client/dump')
def client_dump_route():
    return app.clt_manager.dump()

#group i/f
@app.route('/group/join')
def group_join_route():
    ip = request.remote_addr
    return app.grp_manager.join(ip, session)

@app.route('/group/leave')
def group_leave_route():
    return app.grp_manager.leave(session)

@app.route('/group/members')
def group_members_route():
    return app.grp_manager.members(session)

@app.route('/group/dump')
def group_dump_route():
    return app.grp_manager.dump()

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

@app.route('/monitor/find/<mac>')
def mon_find_route(mac):
    ip = request.remote_addr
    monitor = app.mon_manager.find_client(ip, mac)
    if monitor:
        return monitor
    else:
        return ("Not found", 404)

@app.route('/monitor/dump')
def mon_dump_route():
    return app.mon_manager.dump()

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
