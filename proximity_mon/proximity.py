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
import argparse
import logging

service_url = "http://gluedig.dnsd.info:443"
register_url_tmp = "{0}/monitor/register/{1}" 
unregister_url_tmp = "{0}/monitor/unregister/{1}"
event_url_tmp = "{0}/monitor/event/{1}"
monitor_id = None

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
    parser = argparse.ArgumentParser()
    parser.add_argument('id', help='monitor id')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--url', help='service url: %(default)s', default=service_url)
    parser.add_argument('--endpoint', help='ZMQ event source endpoint default: %(default)s', default="tcp://localhost:49152")

    args = parser.parse_args()
    endpoint = args.endpoint
    service_url = args.url
    monitor_id = args.id
    
    logging.getLogger().setLevel(logging.DEBUG if args.debug else logging.INFO)
    
    register_url = str.format(register_url_tmp, service_url, monitor_id)
    logging.info(str.format("Registering at: {0}", register_url))
    result = urllib2.urlopen(register_url)
    if result.getcode() != 200:
        sys.exit()
    
    pool = ThreadPool()
    zmq_ctx = zmq.Context()
    
    atexit.register(exit_func, zmq_ctx, pool)
    
    zmq_socket = zmq_ctx.socket(zmq.SUB)
    zmq_socket.setsockopt(zmq.SUBSCRIBE, '')
    logging.info(str.format("Connecting to eventsource: {0}", endpoint))
    zmq_socket.connect(endpoint)
    
    while True:
        msg = zmq_socket.recv_unicode()
        msg_json = json.loads(msg)[0]
        event = msg_json['event_type']
        mac = msg_json['mac']
        rssi = msg_json['rssi']
        if event == 2:
            prev_rssi = msg_json['prev_rssi']
            logging.debug(str.format("Event: {0} MAC: {1} RSSI: {2} {3} SSIDs: {4}", event, mac, rssi, prev_rssi, len(msg_json['probed_ssids'])))
        else:
            logging.debug(str.format("Event: {0} MAC: {1} RSSI: {2}", event, mac, rssi))
        
        pool.apply_async(send_func, (msg,))
