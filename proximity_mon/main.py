'''
Created on Jun 12, 2013

@author: developer
'''
import zmq
import sys
import json
import urllib2
import atexit
from multiprocessing.pool import ThreadPool

service_url = "http://localhost:5000"
register_url_tmp = "{0}/monitor/register/{1}" 
unregister_url_tmp = "{0}/monitor/unregister/{1}"
event_url_tmp = "{0}/monitor/event/{1}"

monitor_id = 'test1'

def exit_func(zmq_ctx, pool):
    pool.close()
    pool.join()
    
    zmq_ctx.destroy()
    
    unregister_url = str.format(unregister_url_tmp, service_url, monitor_id)
    urllib2.urlopen(unregister_url)

def send_func(msg_json):
    url = str.format(event_url_tmp, service_url, monitor_id)
    try:
        urllib2.urlopen(url, msg_json)
    except:
        pass
    

if __name__ == '__main__':
    endpoint = sys.argv[1]
    if not endpoint:
        sys.exit()
    
    
    
    register_url = str.format(register_url_tmp, service_url, monitor_id)
    result = urllib2.urlopen(register_url)
    if result.getcode() != 200:
        sys.exit()
    
    pool = ThreadPool()
    zmq_ctx = zmq.Context()
    
    atexit.register(exit_func, zmq_ctx, pool)
    
    zmq_socket = zmq_ctx.socket(zmq.SUB)
    zmq_socket.setsockopt(zmq.SUBSCRIBE, '')
    zmq_socket.connect(endpoint)
    
    while True:
        msg = zmq_socket.recv_unicode()
        msg_json = json.loads(msg)[0]
        event = msg_json['event_type']
        mac = msg_json['mac']
        rssi = msg_json['rssi']
        if event == 2:
            prev_rssi = msg_json['prev_rssi']
            print str.format("Event: {0} MAC: {1} RSSI: {2} {3} SSIDs: {4}", event, mac, rssi, prev_rssi, len(msg_json['probed_ssids']))
        else:
            print str.format("Event: {0} MAC: {1} RSSI: {2}", event, mac, rssi)
        
        pool.apply_async(send_func, (msg,))
