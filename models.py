'''
Created on Jan 20, 2013

@author: Erik Bjareholt
'''

from google.appengine.ext import db

class Asset(db.Model):
    market = db.StringProperty(required = True)
    amount = db.FloatProperty(required = True)
    currency = db.StringProperty(required = True)
    orders = db.ListProperty(db.Key, required = True)
    
    created = db.DateTimeProperty(auto_now_add = True)
    
class Order(db.Model):
    market = db.StringProperty(required = True)
    otype = db.StringProperty(required = True)
    amount = db.FloatProperty(required = True)
    price = db.FloatProperty(required = True)
    
class MyOrder(Order):
    status = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    
class Trade(db.Model):
    """
        Kapiton:
           { "date": <epoch-tid>,
             "price": <price>,
             "amount": <amount>,
             "tid": <trade-id> }
             
        MtGox:
            Look it up
    """
    # key_name = trade-id
    amount = db.FloatProperty(required = True)
    price = db.FloatProperty(required = True)
    executed = db.DateTimeProperty(required = True)
    

class User(db.Model):
    firstname = db.StringProperty()
    lastname = db.StringProperty()
    
    api_keys = db.StringListProperty()