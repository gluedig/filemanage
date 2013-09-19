'''
Created on Jun 19, 2013

@author: developer
'''
from fm_services import app
from fm_services.events_sockjs import HubEventsGetHandler
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, Application
from tornado.options import parse_command_line
from tornado.log import app_log
import sys

tr = WSGIContainer(app)

handlers = [
            (r"/events/hub/(.+)", HubEventsGetHandler),
            (r".*", FallbackHandler, dict(fallback=tr)),
        ]
application = Application(handlers)

if __name__ == "__main__":
    parse_command_line(sys.argv)
    app_log.info("Running on port %i"%app.config['LISTEN_PORT'])
    application.listen(app.config['LISTEN_PORT'])
    IOLoop.instance().start()
