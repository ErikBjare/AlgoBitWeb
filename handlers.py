'''
Created on Jan 20, 2013

@author: Erik Bjareholt
'''


import os
import logging
import json
import urllib

import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import db

from models import User



"""
    ToDo:
         PRI    WHAT
        (HIGH)  Receive Assets and insert into database
"""

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
        
class HandlerHTML(Handler):
    def render(self, template, **params):
        self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        t = jinja_env.get_template(template)
        self.write(t.render(params, 
                            userData=self.userData))
            
    def login(self):
        self.user = users.get_current_user()
        if self.user:
            self.checkUser()
            self.userData = {"user":User.get_by_key_name(self.user.nickname()),
                             "logoutURL":users.create_logout_url('/'),
                             "admin":users.is_current_user_admin(), 
                             "nick":self.user.nickname() }
        else:
            self.userData = None
            
    def checkUser(self):
        user = User.get_by_key_name(self.user.nickname())
        if not user:
            logging.info("Creating user with key_name: {}".format(self.user.nickname()))
            newUser = User(key_name=self.user.nickname())
            newUser.put()
        else:
            logging.info("User \"{}\" logged in".format(user.key().name()))
            return True
        
class HandlerJSON(Handler):
    def render(self, data):
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json.dumps(data))
        
    def authenticate(self, identity, key):
        user = User.get_by_key_name(identity)
        # Implement: Check that API-key is correct!
        logging.info("Identity: {0}, key: {1}. Found matching user {2} in datastore".format(identity, key, user))
        if user:
            api_keys = [db.get(key) for key in user.api_keys]
            for api_key in api_keys:
                if api_key.host == "AlgoBitWeb":
                    if api_key.apikey == key:
                        logging.info("Identity: {0}, key: {1}. Found matching user {2} in datastore".format(identity, key, user))
                        return True
            return True
        return False
        
class HandlerPNG(Handler):
    def render(self, image):
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(image)