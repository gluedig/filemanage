'''
Created on Jun 12, 2013

@author: developer
'''
import argparse
from flask import Flask, request, redirect
app = Flask(__name__)

from subprocess import Popen, PIPE
import re

service_url="http://gluedig.dnsd.info:443/?mac="

class MacResolver:
    def __init__(self):
        self.arp_cache = {}
    
    def resolve(self, ip):
        mac = None
        
        if ip in self.arp_cache:
            mac =  self.arp_cache[ip]
        else:
            #ping it
            pid = Popen(["ping", "-c 1", ip], stdout=PIPE)
            s = pid.communicate()[0]
        
            #get arp entry
            pid = Popen(["arp", "-n", ip], stdout=PIPE)
            s = pid.communicate()[0]
        
            mac_re = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", s)
            if mac_re and mac_re.groups():
                mac = mac_re.groups()[0]
                self.arp_cache[ip] = mac
        
        return mac

app.mac_resolve = MacResolver()

#mac finder i/f
@app.route('/')
def mac_route():
    ip = request.remote_addr
    mac =  app.mac_resolve.resolve(ip)
    
    if mac:
        return redirect(service_url+mac)
    else:
        return redirect(service_url+'unknown')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--url', help='service url: %(default)s', default=service_url)
    parser.add_argument('--port', help='port to run on: %(default)s', default=5002)
    args = parser.parse_args()

    app.run(host='0.0.0.0', debug=args.debug, port=args.port)