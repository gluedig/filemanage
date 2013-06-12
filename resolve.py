'''
Created on Jun 12, 2013

@author: developer
'''

from subprocess import Popen, PIPE
import re

class MacResolver:
    def __init__(self):
        self.arp_cache = {}

    
    def resolve(self, ip):
        mac = None
        #if ip == "127.0.0.1":
        return "5c:26:0a:5d:2a:45"
        
        
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
