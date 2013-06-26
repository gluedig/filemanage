'''
Created on Jun 26, 2013

@author: developer
'''
from fm_services import app
import zmq

zmq_endpoint = "tcp://lo:5556"

class EventUpdates():
    def __init__(self, app):
        self.app = app
        self.n = 0
        self.app.signals['group-member-add'].connect(self._grp_add_signal, self.app)
        self.app.signals['group-member-remove'].connect(self._grp_del_signal, self.app)
        self.app.signals['file-upload'].connect(self._file_add_signal, self.app)
        zmq_ctx = zmq.Context()
        self.zmq_socket = zmq_ctx.socket(zmq.PUB)
        self.zmq_socket.bind(zmq_endpoint)
        
    def _grp_add_signal(self, sender, group_id, mac, **args):
        self.app.logger.debug(str.format("Added client: {0} to group: {1}", mac, group_id))
        self._send('add-member', group_id=group_id, mac=mac)
    
    def _grp_del_signal(self, sender, group_id, mac, **args):
        self.app.logger.debug(str.format("Removed client: {0} from group: {1}", mac, group_id))
        self._send('remove-member', group_id=group_id, mac=mac)
        
    def _file_add_signal(self, sender, mac, group_id, filename, **args):
        self.app.logger.debug(str.format("File uploaded client: {0} for group: {1} filename {2}",
                                     mac, group_id, filename))
        self._send('file-upload', mac=mac, group_id=group_id, filename=filename)
    
    def _send(self, op, **kwargs):
        data = {'msgtype': op, 'n': self.n}
        data.update(**kwargs)
        self.app.logger.debug(data)
        self.n += 1
        self.zmq_socket.send_json(data)

app.services['events_forwarder'] =  EventUpdates(app)