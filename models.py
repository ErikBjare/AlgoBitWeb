'''
Created on Jan 20, 2013

@author: Erik Bjareholt
'''

from google.appengine.ext import db

class Currency(db.Model):
    # key_name = db.StringProperty(required = True)
    name = db.StringProperty(required = True)
    symbol = db.StringProperty(required = True)

class Market(db.Model):
    # key_name = name+currency, for example: MtGoxUSD
    
    # Name used to identify which API to use.
    name = db.StringProperty(required = True)
    
    # Address of market
    url = db.LinkProperty(required = True)
    
    # Currency of market
    currency = db.ReferenceProperty(Currency, required = True)
    
    # The fee of the market in per cent, example: 1% would be 0.01
    fee = db.FloatProperty()
    
class User(db.Model):
    firstname = db.StringProperty()
    lastname = db.StringProperty()
    
    api_keys = db.StringListProperty()
    
class Asset(db.Model):
    market = db.StringProperty(required = True)
    amount = db.FloatProperty(required = True)
    currency = db.StringProperty(required = True)
    orders = db.ListProperty(db.Key, required = True)
    
    created = db.DateTimeProperty(auto_now_add = True)
    updated = db.DateTimeProperty(auto_now = True)
    
class Order(db.Model):
    """
        Kapiton:
            {"asks": [<pris>, <antal>], 
             "bids": [<pris>, <antal>]}
    
    """
    market = db.ReferenceProperty(Market, required=True)
    otype = db.StringProperty(required=True) # ASK or BID
    amount = db.FloatProperty(required=True)
    price = db.FloatProperty(required=True)
    currency = db.ReferenceProperty(Currency, required=True)
    
    created = db.DateTimeProperty(auto_now_add = True)
    
class MyOrder(Order):
    status = db.StringProperty(required = True)
    
    updated = db.DateTimeProperty(auto_now = True)
    
class Orderbook(db.Model):
    market = db.ReferenceProperty(Market, required = True)
    bids = db.ListProperty(db.Key, required = True)
    asks = db.ListProperty(db.Key, required = True)
    
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
    market = db.ReferenceProperty(Market, required = True)
    amount = db.FloatProperty(required = True)
    price = db.FloatProperty(required = True)
    executed = db.DateTimeProperty(required = True)
    
    owner = db.ReferenceProperty(User)