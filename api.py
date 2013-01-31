'''
Created on Jan 20, 2013

@author: Erik Bjareholt
'''

import json
import logging
import webapp2

from handlers import HandlerJSON
from models import *


class Assets(HandlerJSON):
    def post(self):
        try:
            data = json.loads(self.request.body)
            identity = data["auth"]["identity"]
            key = data["auth"]["key"]
            
            logging.debug(data)
            
            if self.authenticate(identity, key):
                keyDict = {}
                
                for order in data["orders"]:
                    existing = MyOrder.get_by_key_name(str(order["orderID"]))
                    logging.info("Existing ?= {0}".format(existing))
                    if existing:
                        logging.info("Order with ID {0} existed, updating.".format(order["orderID"]))
                        existing.status = order["status"]
                        newOrder = existing
                    else:
                        logging.info("Order with ID {0} didn't exists, creating.".format(order["orderID"]))
                        newOrder = MyOrder( market=order["market"], 
                                            key_name=str(order["orderID"]), 
                                            otype=order["orderType"], 
                                            amount=order["amount"],
                                            price=order["price"],
                                            status=order["status"] )
                    if existing != newOrder:
                        newOrder.put()
                    keyDict[order["orderID"]] = newOrder.key()
                
                for asset in data["assets"]:
                    orderKeys = []
                    for orderID in asset["orders"]:
                        orderKeys.append(keyDict[orderID])
                    newAsset = Asset( market=asset["market"], 
                                      amount=asset["amount"],
                                      currency=asset["currency"],
                                      orders=orderKeys )
                    newAsset.put()   
                
                self.render(data={"result": "success"})
            else:
                self.render(data={"result": "invalid_auth"})
        except Exception as e:
            logging.error(e)
            self.render(data={"result": "error"})


class Trades(HandlerJSON):
    def post(self):
        try:
            data = json.loads(self.request.body)
            logging.info(data)
        
            
        
            trades = data["trades"]
        
            for trade in trades:
                dbTrade = Trade( market=trade["market"], 
                                 key_name=str(trade["orderID"]), 
                                 otype=trade["orderType"], 
                                 amount=trade["amount"],
                                 price=trade["price"],
                                 status=trade["status"] )
            self.render(data={"result": "incomplete_api"})
        except Exception as e:
            logging.error(e)
            self.render(data={"result": "error"})


""" Perhaps not to be implemented, perhaps Google Charts API is to be preferred?

class Plots(HandlerJSON):
    def post(self):
        data = json.loads(self.request.body)
"""        

app = webapp2.WSGIApplication([('/api/assets', Assets),
                               ('/api/trades', Trades)],
                               debug=True)