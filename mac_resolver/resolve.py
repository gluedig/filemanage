'''
Created on Jun 12, 2013

@author: developer
'''
from flask import Flask, request, redirect
app = Flask(__name__)

from subprocess import Popen, PIPE
import re

SERVICES_URL="http://gluedig.dnsd.info:443/?mac="

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
@app.route('/resolve')
def mac_route():
    ip = request.remote_addr
    mac =  app.mac_resolve.resolve(ip)
    
    if mac:
        return redirect(SERVICES_URL+mac)
    else:
        return ('Not found', 404)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', threaded=True, port=5002)