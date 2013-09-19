'''
Created on Jun 19, 2013

@author: developer
'''
from fm_services import app
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, RequestHandler, Application

class MainHandler(RequestHandler):
    def get(self):
        self.write("This message comes from Tornado ^_^")

tr = WSGIContainer(app)

application = Application([
(r"/tornado/.*", MainHandler),
(r".*", FallbackHandler, dict(fallback=tr)),
])

if __name__ == "__main__":
    print("Running on port %i"%app.config['LISTEN_PORT'])
    application.listen(app.config['LISTEN_PORT'])
    IOLoop.instance().start()
