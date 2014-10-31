import os
import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.web

root = os.path.dirname(__file__)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('base.html')

def main():
    application = tornado.web.Application(
        [(r"/", MainHandler),],
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
