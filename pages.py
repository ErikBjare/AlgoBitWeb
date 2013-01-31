'''
Created on Jan 20, 2013

@author: Erik Bjareholt
'''

import webapp2
from google.appengine.api import users

from handlers import HandlerHTML
from models import *

class Root(HandlerHTML):
    def get(self):
        self.login()
        
        if self.user:
            self.redirect("/dashboard")
        else:
            self.redirect("/login")

class Dashboard(HandlerHTML):
    def get(self):
        self.login()
        
        if self.user:
            myOrderQuery = MyOrder.all()
            myOrders = myOrderQuery.order("-created").run(limit=10)
            
            assetQuery = Asset.all()
            assets = assetQuery.order("-created").run(limit=10)
            
            self.render("dashboard.html", myorders=myOrders, assets=assets, userData=self.userData, logoutURL = users.create_logout_url('/'))
        else:
            self.redirect("/login")
            
class Login(HandlerHTML):
    def get(self):
        self.login()
        
        self.render("login.html", loginURL = users.create_login_url('/dashboard'))
        
class Account(HandlerHTML):
    def get(self):
        self.login()
        
        if self.user:
            self.render("account.html")
        else:
            self.redirect("/login")

app = webapp2.WSGIApplication([('/', Root),
                               ('/dashboard', Dashboard), 
                               ('/login', Login),
                               ('/account', Account)],
                               debug=True)