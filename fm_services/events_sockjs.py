'''
Created on Sep 19, 2013

@author: gluedig
'''
from sockjs.tornado import SockJSRouter, SockJSConnection
from tornado import web
from tornado.log import app_log
from fm_services.signals import hub_signals, user_signals


class EventFwrdr():
    def __init__(self, signal, socket, params):
        self.signal = signal
        self.sockjs = socket
        self.params = params
        app_log.debug(str.format("New forwarder for signal: {0} args: {1}", signal.name, params))

    def forward(self, sender, **args):
        app_log.debug(str.format('Signal: {0} from: {1} args: {2}', self.signal.name, sender, args))
        send = True
        for (key, value) in self.params.iteritems():
            if key in args and args[key] == value:
                continue
            else:
                send = False
                #app_log.debug(str.format('key {0} not found or wrong value (expected: {1})', key, value))
                break
        if send:
            self._send(self.signal.name, **args)

    def _send(self, op, **kwargs):
        data = {'msgtype': op}
        data.update(**kwargs)
        self.sockjs.send(data)

class HubEvents(SockJSConnection):
    forwarders = {}
    def on_open(self, info):
        app_log.debug("HubEvents ticker open hub: "+self.hub)
        for signal in hub_signals:
            self.forwarders[signal.name] = EventFwrdr(signal, self, {'hub_id': int(self.hub)})
            signal.connect(self.forwarders[signal.name].forward)
        
    def on_close(self):
        app_log.debug("HubEvents ticker close hub: "+self.hub)
        self.stream.stop_on_recv()

class HubEventsGetHandler(web.RequestHandler):
    
    def __init__(self, app, req, **kwargs):
        super(HubEventsGetHandler, self).__init__(app, req, **kwargs)
        self.registered_tickers = {}
    
    def _make_ticker_class(self, **kwargs):
        class_name = str.format("HubEventsTicker_{0}", kwargs['hub'])
        app_log.debug("HubEvents ticker make hub: "+kwargs['hub'])
        return type(class_name, (HubEvents,), dict(**kwargs))
    
    def _make_or_get_ticker(self, hub):
        if hub not in self.registered_tickers:
            srv_url = str.format('/events/hub/{0}', hub)
            TickerRouter = SockJSRouter(self._make_ticker_class(hub=hub), srv_url)
            self.application.add_handlers(".*$", TickerRouter.urls)
            self.registered_tickers[hub] = (TickerRouter, srv_url)
            return srv_url
        else:
            return self.registered_tickers[hub][1]
    
    def get(self, params):
        parameters = params.split('/')
        hub = parameters[0]
        ticker_url = self._make_or_get_ticker(hub)
        red_url = str.format('{0}/{1}', ticker_url, '/'.join(parameters[1:]))
        self.redirect(red_url)

class UserEvents(SockJSConnection):
    forwarders = {}
    def on_open(self, info):
        app_log.debug("UserEvents ticker open uid: "+self.user_id)
        for signal in user_signals:
            self.forwarders[signal.name] = EventFwrdr(signal, self, {'user_id': int(self.user_id)})
            signal.connect(self.forwarders[signal.name].forward)

    def on_close(self):
        app_log.debug("UserEvents ticker close uid: "+self.user_id)
        self.stream.stop_on_recv()

class UserEventsGetHandler(web.RequestHandler):
    def __init__(self, app, req, **kwargs):
        super(UserEventsGetHandler, self).__init__(app, req, **kwargs)
        self.registered_tickers = {}

    def _make_ticker_class(self, **kwargs):
        user_id = kwargs['user_id']
        class_name = str.format("UserEventsTicker_{0}", user_id)
        app_log.debug("UserEvents ticker make uid: "+user_id)
        return type(class_name, (UserEvents,), dict(**kwargs))

    def _make_or_get_ticker(self, user_id):
        if user_id not in self.registered_tickers:
            srv_url = str.format('/events/user/{0}', user_id)
            TickerRouter = SockJSRouter(self._make_ticker_class(user_id=user_id), srv_url)
            self.application.add_handlers(".*$", TickerRouter.urls)
            self.registered_tickers[user_id] = (TickerRouter, srv_url)
            return srv_url
        else:
            return self.registered_tickers[user_id][1]

    def get(self, params):
        parameters = params.split('/')
        hub = parameters[0]
        ticker_url = self._make_or_get_ticker(hub)
        red_url = str.format('{0}/{1}', ticker_url, '/'.join(parameters[1:]))
        self.redirect(red_url)
