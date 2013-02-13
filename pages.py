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
                        userData=self.userData, 
                        myOrders=myOrders, 
                        assets=assets, 
                        logoutURL=users.create_logout_url('/'))
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
            myOrdersBatch = myOrderQuery.order("-created").run(limit=10)
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
            self.render("account.html")
        else:
            self.redirect("/login")

app = webapp2.WSGIApplication([('/', Root),
                               ('/dashboard', Dashboard), 
                               ('/login', Login),
                               ('/account', Account)],
                               debug=True)