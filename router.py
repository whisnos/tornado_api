from webhandler import basehandler
import tornado.web

class MainHandler(basehandler.BaseHandler):
    def get(self):
        # print(self.request.body, self.request.query)
        print(123)
        self.write("Hello, get!")

    def post(self):
        # print(self.request.body, self.request.query)
        self.write("Hello, post!")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        # (r"/user/login", LoginHandler),                          # 登录
        ],
        # cookie_secret = 'cb56YAgMjpevlWBNqgrv5g==',
        # login_url = '/',
        # xheader= True,
        # debug = True,
        # autoreload = True,
        # serve_traceback= True
    )