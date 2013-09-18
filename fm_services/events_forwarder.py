'''
Created on Jun 26, 2013

@author: developer
'''
from fm_services import app
import zmq
zmq_internal_endpoint = "inproc://#events"

class EventUpdates():
    class EventFwrdr():
        def __init__(self, signal, socket):
            self.signal = signal
            self.zmq_socket = socket
            self.n = 0

        def forward(self, sender, **args):
            app.logger.debug(str.format('Signal: {0} from: {1} args: {2}', self.signal.name, sender, args))
            self._send(self.signal.name, **args)

        def _send(self, op, **kwargs):
            data = {'msgtype': op, 'n': self.n}
            data.update(**kwargs)
            app.logger.debug(data)
            self.n += 1
            self.zmq_socket.send_json(data)

    def __init__(self, app):
        self.app = app
        self.zmq_ctx = zmq.Context.instance()
        self.zmq_socket = self.zmq_ctx.socket(zmq.PUB)
        self.zmq_socket.bind(zmq_internal_endpoint)
        self.app.logger.debug("Bound to zmq socket: "+zmq_internal_endpoint)
        self.forwarders = {}

        for signal in self.app.signals.values():
            self.forwarders[signal.name] = self.EventFwrdr(signal, self.zmq_socket)
            signal.connect(self.forwarders[signal.name].forward, self.app)


app.services['events_forwarder'] = EventUpdates(app)

pd = zmq.devices.ThreadProxy(zmq.SUB, zmq.PUB)
pd.connect_in(zmq_internal_endpoint)
pd.setsockopt_in(zmq.SUBSCRIBE, '')
pd.bind_out(app.config['EVENTS_ZMQ_ENDPOINT'])
pd.start()
app.logger.info("Event source bound to: "+app.config['EVENTS_ZMQ_ENDPOINT'])
