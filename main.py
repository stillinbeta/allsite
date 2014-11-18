import os
import os.path
import logging

import tornado.httpserver
import tornado.ioloop
import tornado.log
import tornado.web

from allsite.search import SearchHandler

logger = tornado.log.gen_log
logger.setLevel(logging.DEBUG)

root = os.path.dirname(__file__)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('base.html')

def main():
    application = tornado.web.Application(
        [(r"/", MainHandler),
         (r"/search", SearchHandler)],
        template_path=os.path.join(root, 'templates'),
        static_path=os.path.join(root, 'static'),
        debug=True,
    )
    http_server = tornado.httpserver.HTTPServer(application)
    port = int(os.environ.get("PORT", 5000))
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
