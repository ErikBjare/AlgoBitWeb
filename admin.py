#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

'''
Created on Feb 04, 2013

@author: Erik Bjareholt
'''

import webapp2

import handlers
from models import Currency, Market

class DBinit(handlers.Handler):
    def get(self):
        self.dbinit()
        self.write("Initialized DB!")
    
    def dbinit(self):
        # Currencies
        currencies = {}
        currencies["BTC"] = Currency(key_name="BTC", 
                                     name="Bitcoin",
                                     symbol="BTC")
        currencies["USD"] = Currency(key_name="USD", 
                                     name="US Dollar",
                                     symbol=u"$")
        currencies["EUR"] = Currency(key_name="EUR", 
                                     name="Euro",
                                     symbol=u"€")
        currencies["SEK"] = Currency(key_name="SEK", 
                                     name="Swedish Kronor",
                                     symbol="kr")
        for currency in currencies:
            currencies[currency].put()
            
        # Markets
        markets = {}
        markets["KapitonSEK"] = Market(key_name="KapitonSEK", 
                                       name="Kapiton",
                                       url="http://kapiton.se/", 
                                       currency=currencies["SEK"],
                                       fee=0.0135)
        markets["MtGoxEUR"] = Market(key_name="MtGoxEUR", 
                                     name="MtGox",
                                     url="http://mtgox.com/", 
                                     currency=currencies["EUR"],
                                     fee=0.006)
        markets["MtGoxUSD"] = Market(key_name="MtGoxUSD", 
                                     name="MtGox",
                                     url="http://mtgox.com/", 
                                     currency=currencies["USD"],
                                     fee=0.006)
        for market in markets:
            markets[market].put()

app = webapp2.WSGIApplication([('/admin/dbinit', DBinit)],
                               debug=True)