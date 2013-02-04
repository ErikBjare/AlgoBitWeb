'''
Created on Jan 20, 2013

@author: Erik Bjareholt
'''

import webapp2
from google.appengine.api import users

from handlers import HandlerHTML
from models import *

class Dashboard(HandlerHTML):
    def get(self):
        user = users.get_current_user()
        if not user:
            return self.redirect('/')
        myOrderQuery = MyOrder.all()
        myOrders = myOrderQuery.order("-created").run(limit=10)
        
        assetQuery = Asset.all()
        assets = assetQuery.order("-created").run(limit=10)
        
        self.render("dashboard.html", myorders=myOrders, assets=assets, username=user.nickname(), logout_url = users.create_logout_url('/'))
        
class Login(HandlerHTML):
    def get(self):
        self.login()
        
    def login(self):
        user = users.get_current_user()
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." %
                        users.create_login_url("/dashboard"))

        self.response.out.write("<html><body>%s</body></html>" % greeting)
        
app = webapp2.WSGIApplication([('/dashboard', Dashboard), ('/', Login)],
                               debug=True)