'''
Created on Feb 04, 2013

@author: Erik Bjareholt
'''

import json
import logging
import urllib
from datetime import datetime

import webapp2
from google.appengine.api.urlfetch import fetch

from handlers import HandlerJSON
from models import *

class Fetcher(HandlerJSON):
    def get(self):
        m = self.request.get("m")
        self.market = Market.get_by_key_name(m)
        if self.market:
            data = self.fetchData()
            if data:
                self.saveData(data)
            self.render(data={"result":"success"})
        else:
            self.render(data={"result":"invalid market"})
            
class OrderbookFetcher(Fetcher):
    def fetchData(self):
        if self.market.name == "Kapiton":
            url = "https://kapiton.se/api/0/orderbook"
        else:
            logging.error("Unknown market {}, can not fetch orderbook".format(self.market.name))
            return None
        response = fetch(url)
        if response.status_code != 200:
            logging.error("Could not get orderbook from: {}".format(url))
            return None
        else:
            return json.loads(response.content)
    
    def saveData(self, data):
        if self.market.name == "Kapiton":
            # Here begins the Order-saving part
            orderKeys = {"asks":[], "bids":[]}
            for lookUpType in ["asks", "bids"]:
                for entry in data[lookUpType][:15]:
                    orderStruct = {"market":self.market,
                                   "otype":lookUpType[:-1],
                                   "price":entry[0],
                                   "amount":entry[1],
                                   "currency":Currency.get_by_key_name("SEK") }
                    orderKey = Order(**orderStruct).put()
                    orderKeys[lookUpType].append(orderKey)
            # Here begins the Orderbook-saving part
            orderbookStruct = {"market":self.market,
                               "bids":orderKeys["bids"], 
                               "asks":orderKeys["asks"] }
            Orderbook(**orderbookStruct).put()
            
class TradeFetcher(Fetcher):
    def fetchData(self):
        if self.market.name == "Kapiton":
            lastTradeKey = Trade.all().order("-executed").get(keys_only=True)
            if lastTradeKey:
                logging.info("Fetching trades since trade-ID: {}".format(lastTradeKey.name()))
                url = "https://kapiton.se/api/0/trades/?since={}".format(lastTradeKey.name())
            else:
                sinceTID = self.request.get("tid")
                logging.info("Fetching trades since trade-ID: {}".format(sinceTID))
                #logging.warning("Fetching ALL trades from {}".format(self.market.name))
                url = "https://kapiton.se/api/0/trades/?since={}".format(sinceTID)
        else:
            logging.error("Unknown market {}, can not fetch trades".format(self.market.name))
            return None
        response = fetch(url)
        if response.status_code != 200:
            logging.error("Could not fetch trades from {}".format(self.market.name))
            return None
        else:
            if not response.content:
                logging.info("Looks like the latest trades have already been fetched")
                return None
            return json.loads(response.content)

    def saveData(self, data):
        if self.market.name == "Kapiton":
            # Here begins the Trade-saving part
            for trade in data:
                tradeStruct = {"market":self.market,
                               "price":trade["price"],
                               "amount":trade["amount"],
                               "executed":datetime.fromtimestamp(trade["date"])}  # TODO Fix timezone!
                Trade(key_name=str(trade["tid"]), **tradeStruct).put()
                
class OrderStatusChecker(Fetcher):
    """
        ToDo:
         - Update fetcher so that it uses apikey specified in the orders user.apikeys
         - Make sure that it only queries trades from the current market.
    """
    apikey = "c8357855580484d035980d7effbddd6898c7804cb2e78932c155638f"
    
    def fetchData(self):
        if self.market.name == "Kapiton":
            activeOrders = MyOrder.gql("WHERE status IN ('OPEN', 'PRTF')").fetch(20)
            if len(activeOrders): 
                logging.info("Checking {0} active orders".format(len(activeOrders)))
                url = "http://kapiton.se/api/0/auth/getorder"
            else:
                return None
        else:
            logging.error("Unknown market {}, can not check orders".format(self.market.name))
            return None
        updated = []
        for order in activeOrders:
            payload = {"api_key":self.apikey, "id":int(order.key().name())}
            payloadEncoded = urllib.urlencode(payload).encode("ASCII")
            logging.info("Looking up order {}".format(payload["id"]))
            response = fetch(url, 
                             payloadEncoded, 
                             method="POST")
            if response.status_code != 200:            
                logging.error("Not OK statuscode while trying to look up order {}".format(payload["id"]))
                logging.info(response.content)
            else:
                if response.content:
                    responseData = json.loads(response.content)
                    if responseData["status"] != order.status:
                        order.status = responseData["status"]
                        updated.append(order)
                else:
                    logging.error("Something went wrong while trying to fetch orderstatus, error: {}".format(response["error"]))
        return updated

    def saveData(self, data):
        if self.market.name == "Kapiton":
            # Here begins the Trade-saving part
            for trade in data:
                trade.put()

app = webapp2.WSGIApplication([('/fetch/orderbook', OrderbookFetcher),
                               ('/fetch/trades', TradeFetcher),
                               ('/fetch/checkorders', OrderStatusChecker)],
                               debug=True)