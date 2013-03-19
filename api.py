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
                        market = Market.gql("WHERE name = :1", order["market"]).get()
                        newOrder = MyOrder( market=market, 
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
                
                result = "success"
            else:
                result = "invalid_auth"
        except Exception as e:
            logging.error(e)
            result = "error"
            raise
        self.render(data={"result": result})


""" Perhaps not to be implemented, perhaps Google Charts API is to be preferred?

class Plots(HandlerJSON):
    def post(self):
        data = json.loads(self.request.body)
"""        

app = webapp2.WSGIApplication([('/api/assets', Assets)],
                               debug=True)