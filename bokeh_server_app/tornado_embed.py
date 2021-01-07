from jinja2 import Environment, FileSystemLoader
from tornado.web import RequestHandler
import os

from bokeh.embed import server_document
from bokeh.server.server import Server
from bokeh.command.util import build_single_handler_application

env = Environment(loader=FileSystemLoader('templates'))

class IndexHandler(RequestHandler):
    def get(self):
        # template = env.get_template('embed.html')
        # script = server_document('http://localhost:5006/stocks')
        # self.write(template.render(script=script, template="Tornado"))
        self.write("")


# Setting num_procs here means we can't touch the IOLoop before now, we must
# let Server handle that. If you need to explicitly handle IOLoops then you
# will need to use the lower level BaseServer class.
# The `static/` end point is reserved for Bokeh resources, as specified in
# bokeh.server.urls. In order to make your own end point for static resources,
# add the following to the `extra_patterns` argument, replacing `DIR` with the desired directory.
# (r'/DIR/(.*)', StaticFileHandler, {'path': os.path.normpath(os.path.dirname(__file__) + '/DIR')})
myapp = build_single_handler_application(os.path.join(os.path.dirname(__file__), "myapp"))
stocks = build_single_handler_application(os.path.join(os.path.dirname(__file__), "stocks"))
server = Server({'/myapp': myapp, '/stocks': stocks}, num_procs=1, extra_patterns=[('/', IndexHandler)])
server.start()

if __name__ == '__main__':
    from bokeh.util.browser import view

    print('Opening Tornado app with embedded Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(view, "http://localhost:5006/")
    server.io_loop.start()
