'''
Created on Jan 20, 2013

@author: Erik Bjareholt
'''

import logging

import webapp2
from google.appengine.api import users
from google.appengine.api import memcache

from handlers import HandlerHTML
from models import *

"""
                                    THIS!!!
http://blog.initlabs.com/post/16359268329/how-i-reduced-google-app-engine-costs-by-75

"""

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
            chartData = self.getChartData()
            myOrders = self.getMyOrders()
            assets = self.getAssets()
            self.render("dashboard.html", 
                        chartData=chartData, 
                        myOrders=myOrders, 
                        assets=assets)
        else:
            self.redirect("/login")
            
    def getChartData(self):
        chartData = memcache.get("chartData")
        if chartData is not None:
            logging.debug("chartData found in memcache")
            return chartData
        else:
            orderbookQuery = Orderbook.all()
            orderbook = orderbookQuery.order("-created").get()
            if orderbook:
                entries = {"asks":[], "bids":[]}
                for entryType in ["asks", "bids"]:
                    keys = getattr(orderbook, entryType)
                    entries[entryType] = Order.get(keys)
                    accumvolume = 0
                    for idx, entry in enumerate(entries[entryType]):
                        accumvolume += entry.amount
                        setattr(entries[entryType][idx], "accumvolume", accumvolume)
            else:
                logging.error("Couldn't get orderbook from DB")
            
            tradeQuery = Trade.all()
            trades = []
            for trade in tradeQuery.order("-executed").run(limit=100):
                trades.append(trade)
            if trades:
                accumvolume = 0
                for idx, trade in enumerate(trades):
                    accumvolume += trade.amount
                    setattr(trades[idx], "accumvolume", accumvolume)
            else:
                logging.error("Couldn't get trades from DB")
            
            chartData = { "orderbook":entries, "trades":trades }
            memcache.add("chartData", chartData, 300)
            logging.debug("chartData added to memcache")
            return chartData
            
    def getMyOrders(self):
        myOrders = memcache.get("myOrders")
        if myOrders is not None:
            logging.debug("myOrders found in memcache")
            return myOrders
        else:
            myOrderQuery = MyOrder.all()
            myOrdersBatch = myOrderQuery.order("-created").filter('status =', "OPEN").run(limit=10)
            myOrders = []
            for myOrder in myOrdersBatch:
                myOrders.append(myOrder)
            memcache.add("myOrders", myOrders, 60)
            logging.debug("myOrders added to memcache")
            return myOrders
    
    def getAssets(self):
        assets = memcache.get("assets")
        if assets is not None:
            logging.debug("assets found in memcache")
            return assets
        else:
            assetQuery = Asset.all()
            assetsBatch = assetQuery.order("-created").run(limit=10)
            assets = []
            for asset in assetsBatch:
                assets.append(asset)
            memcache.add("assets", assets, 60)
            logging.debug("assets added to memcache")
            return assets
            
class Login(HandlerHTML):
    def get(self):
        self.login()
        
        self.render("login.html", loginURL = users.create_login_url('/dashboard'))
        
class Account(HandlerHTML):
    def get(self):
        self.login()
        
        if self.user:
            api_keys = [db.get(key) for key in self.userData["user"].api_keys]
            logging.info(api_keys)
            api_keys2 = []
            for api_key in api_keys:
                api_key.keyid = api_key.key().id()
                api_keys2.append(api_key)
            self.render("account.html", api_keys=api_keys2)
        else:
            self.redirect("/login")
            
class NewAPIKey(HandlerHTML):
    def post(self):
        self.login()
        
        if self.user:
            host = self.request.get("host")
            level = self.request.get("level")
            key = self.request.get("key")
            apikey = API_Key(host=host, level=level, apikey=key).put()
            self.userData["user"].api_keys.append(apikey)
            self.userData["user"].put()
            self.redirect("/account")
        else:
            self.redirect("/login")
            
class DelAPIKey(HandlerHTML):
    def get(self):
        self.login()
        
        # ToDo: Should check if user owns API-key before deleting
        
        if self.user:
            keyid = self.request.get("keyid")
            apikey = API_Key.get_by_id(int(keyid))
            self.userData["user"].api_keys.remove(apikey.key())
            self.userData["user"].put()
            apikey.delete()
            self.redirect("/account")
        else:
            self.redirect("/login")

app = webapp2.WSGIApplication([('/', Root),
                               ('/dashboard', Dashboard), 
                               ('/login', Login),
                               ('/account', Account),
                               ('/account/newkey', NewAPIKey),
                               ('/account/delkey', DelAPIKey)],
                               debug=True)