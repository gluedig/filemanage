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
event_url_tmp = "{0}/monitor/event/{1}/{2}/{3}"

monitor_id = 'dupa'

def exit_func(zmq_ctx, pool):
    pool.close()
    pool.join()
    
    zmq_ctx.destroy()
    
    unregister_url = str.format(unregister_url_tmp, service_url, monitor_id)
    urllib2.urlopen(unregister_url)

def send_func(event, mac):
    url = str.format(event_url_tmp, service_url, monitor_id, event, mac)
    print url
    try:
        urllib2.urlopen(url)
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
        string = zmq_socket.recv_unicode()
        msg_json = json.loads(string)[0]
        event = msg_json['event_type']
        mac = msg_json['mac']
        #print str.format("Event: {0} MAC: {1}", event, mac)
        
        if event == 0 or event == 1:
            pool.apply_async(send_func, (event, mac))
            