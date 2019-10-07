import requests
import json
from json import JSONEncoder
import pdb


class SportsAPI_():

    def __init__(self, payload, ssoid, headers):
        self.payload = payload
        headers.update({'X-Authentication': ssoid, 'Content-Type': 'application/json'}) 
        self.headers = headers
        self.url = 'https://api.betfair.com/exchange/betting/json-rpc/v1'
        self.path_cert = '/home/gary/Desktop/Development/Betfair/Python/betfair/login/'

    def send_sports_req(self, my_json):
        # INSERT YOUR OWN CERT HERE
        req = requests.post(self.url, data=json.dumps(my_json), cert=(self.path_cert+'client-2048.crt', self.path_cert+'client-2048.key'), headers=self.headers) 
        print("send_sports_req:", req.status_code)
        return req.json()


# Classes and function for MarketCatalogue request
class MarketCatalogueRequest():

    def __init__(self):
        self.jsonrpc  = "2.0"
        self.method = "SportsAPING/v1.0/listMarketCatalogue"
        self.params = Params()   
        self.id = 1
    
    def __dir__(self): 
        return[self.jsonrpc, self.method, 'df', self.id] 

class Params():

    def __init__(self):    
        self.filter = Filter()
        self.sort = "FIRST_TO_START"
        self.maxResults = "200"
        self.marketProjection = []

    def __dir__(self): 
        return[dir(self.filter), self.sort, self.maxResults, self.marketProjection] 

class Filter():

    def __init__(self):    
        self.eventTypeIds = []
        self.marketCountries = []
        self.marketTypeCodes = []
        self.marketStartTime = StartTime()
    
    def __dir__(self): 
        return[self.eventTypeIds, self.marketCountries, self.marketTypeCodes, dir(self.marketStartTime)] 

class StartTime():

    def __init__(self):    
        self._from = ''
        self._to = ''

    def __dir__(self): 
        return[self._from, self._to] 

def SerializeMarketCatalogueRequest(requestList, tree_level):
    
    possible_classes = [Params, Filter, StartTime]
    encodings = {} 
    for attr, value in tree_level.__dict__.items(): # Loop through MCR

        if type(value) in possible_classes:
            encodings.update({attr: SerializeMarketCatalogueRequest(requestList, tree_level=value)})
        else:
            encodings.update({attr: value})
    
    return encodings



# A specialised JSONEncoder that encodes MobilePhone
#                 objects as JSON
#
class custom_encoder(JSONEncoder):

    def default(self, object):

        if isinstance(object, MarketCatalogueRequest) or isinstance(object, Params) or isinstance(object, Filter) or isinstance(object, StartTime):

            return object.__dict__


        else:
            # call base class implementation which takes care of
            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object)

class Payload(object):

    def __init__(self, j): 
        a = j.replace("True", "'TRUE'").replace("False", "'FALSE'").replace('"', "'").replace("'", '"').replace('""TRUE"', '"True').replace('""FALSE"', '"False') # Bug Fixed: Runners sometimes contain the name 'True ..' or 'False ..'
        self.__dict__ = json.loads(a)
    
   
# Classes and function for listMarketCatalogue response
class MarketCatalogueResponse():
    def __init__(self, jsonrpc, result, _id):
        self.jsonrpc = jsonrpc
        self.result = self.populate_list_catalogue(result) # List of market catalogues
        self.id = _id

    def populate_list_catalogue(self, result):
        list_catalogue = []
        for market_catalogue in result:
            list_catalogue.append(MarketCatalogue(market_catalogue))
        return list_catalogue

class MarketCatalogue:
    def __init__(self, market_catalogue):
        self.marketId = market_catalogue['marketId']
        self.marketName = market_catalogue['marketName']
        self.marketStartTime = market_catalogue['marketStartTime']
        self.totalMatched = market_catalogue['totalMatched']
        self.runners = self.populate_runners(market_catalogue['runners'])
        self.event = Event(market_catalogue['event'])
    
    def populate_runners(self, runners):
        runner_list = []
        for runner in runners:
            runner_list.append(Runner(runner))
        return runner_list

class Runner:
    def __init__(self, runner):
        self.selectionId = runner['selectionId']
        self.runnerName = runner['runnerName']
        self.handicap = runner['handicap']
        self.sortPriority = runner['sortPriority']

class Event: # Strange case [Event]
    def __init__(self, event):
        self.id = event['id']
        self.name = event['name']
        self.countryCode = event['countryCode']
        self.timezone = event['timezone']
        self.venue = event['venue']
        self.openDate = event['openDate']

def DeserializeMarketCatalogueResponse(jsonResponse):
    dsjson = Payload(str(jsonResponse))
    market_catalogue_response = MarketCatalogueResponse(dsjson.jsonrpc, dsjson.result, dsjson.id)
    return market_catalogue_response


# --------------------------------------


# Classes and function for listMarketBook request
class MarketBookRequest:
    def __init__(self):
        self.jsonrpc = "2.0"
        self.method = "SportsAPING/v1.0/listMarketBook"
        self.params = MarketBookParams()
        self.id = 1

    def __dir__(self): 
        return[self.jsonrpc, self.method, 'df', self.id] 


class MarketBookParams:
    def __init__(self):
        self.marketIds = []
        self.priceProjection = PriceProjection()
        self.orderProjection = ""

    def __dir__(self): 
        return[self.marketIds, dir(self.priceProjection), self.orderProjection] 

class PriceProjection:
    def __init__(self):
        self.priceData = []

    def __dir__(self): 
        return[self.priceData] 

def SerializeMarketBookRequest(requestList, tree_level):
    possible_classes = [MarketBookParams, PriceProjection]
    encodings = {} 
    for attr, value in tree_level.__dict__.items(): # Loop through MCR
        if type(value) in possible_classes:
            encodings.update({attr: SerializeMarketBookRequest(requestList, tree_level=value)})
        else:
            encodings.update({attr: value})
    return encodings

#'classes and functions for listMarketBook response 
class MarketBookResponse:
    def __init__(self, jsonrpc, result, _id):
        self.jsonrpc = jsonrpc
        self.result = self.populate_list_book(result) # List of market catalogues
        self.id = _id

    def populate_list_book(self, result):
        list_book = []
        for market_book in result:
            list_book.append(MarketBook(market_book))
        return list_book

class MarketBook:
    def __init__(self, market_book):
        self.marketId = market_book['marketId']
        self.isMarketDataDelayed = market_book['isMarketDataDelayed']
        self.status = market_book['status']
        self.betDelay = market_book['betDelay']
        self.bspReconciled = market_book['bspReconciled']
        self.complete = market_book['complete']
        self.inplay = market_book['inplay']
        self.numberOfWinners = market_book['numberOfWinners']
        self.numberOfRunners = market_book['numberOfRunners']
        self.numberOfActiveRunners = market_book['numberOfActiveRunners']
        self.lastMatchTime = market_book['lastMatchTime'] if 'lastMatchTime' in market_book else None
        self.totalMatched = market_book['totalMatched']
        self.totalAvailable = market_book['totalAvailable']
        self.crossMatching = market_book['crossMatching']
        self.runnersVoidable = market_book['runnersVoidable']
        self.version = market_book['version']
        self.runners = self.populate_runner_class(market_book['runners'])

    def populate_runner_class(self, runners):
        runner_list = []
        for runner in runners:
            runner_list.append(MarketBookRunnerclass(runner))
        return runner_list

class MarketBookRunnerclass:
    def __init__(self, runner):
        self.selectionId = runner['selectionId']    # 'Wrong type was assigned to this variable previously causing error in json repsonse
        self.handicap = runner['handicap']
        self.status = runner['status']
        self.adjustmentFactor = runner['adjustmentFactor']
        self.lastPriceTraded = runner['lastPriceTraded'] if 'lastPriceTraded' in runner else None
        self.totalMatched = runner['totalMatched'] if 'lastPriceTraded' in runner else None
        # self.removalDate = runner['removalDate']  # 'Wrong type was assigned to this variable previously causing error in json repsonse
        self.ex = ex(runner['ex'])
        # self.orders = self.populate_order_class(runner['orders'])

    def populate_order_class(self, orders):
        orders_list = []
        for order in orders:
            orders.append(Order(order))
        return orders

class Order:
    def __init__(self, order):
        self.betId = order['betId']
        self.orderType = order['orderType']
        self.status = order['status']
        self.persistenceType = order['persistenceType']
        self.side = order['side']
        self.price = order['price']
        self.size = order['size']
        self.bspLiability = order['bspLiability']
        self.placedDate = order['placedDate']
        self.avgPriceMatched = order['avgPriceMatched']
        self.sizeMatched = order['sizeMatched']
        self.sizeRemaining = order['sizeRemaining']
        self.sizeLapsed = order['sizeLapsed']
        self.sizeCancelled = order['sizeCancelled']
        self.sizeVoided = order['sizeVoided']


class ex:
    def __init__(self, ex):
        self.availableToBack = self.populate_atb(ex['availableToBack'])
        self.availableToLay = self.populate_atl(ex['availableToLay'])
        self.tradedVolume = self.populate_tv(ex['tradedVolume'])

    def populate_atb(self, atb):
        atb_list = []
        for a in atb:
            atb_list.append(AvailableToBack(a))
        return atb_list

    def populate_atl(self, atl):
        atl_list = []
        for a in atl:
            atl_list.append(AvailableToLay(a))
        return atl_list

    def populate_tv(self, tv):
        tv_list = []
        for t in tv:
            tv_list.append(TradedVolume(t))
        return tv_list

class AvailableToBack:
    def __init__(self, a):
        self.price = a['price']
        self.size = a['size']

class AvailableToLay:
    def __init__(self, a):
        self.price = a['price']
        self.size = a['size']

class TradedVolume:
    def __init__(self, t):
        self.price = t['price']
        self.size = t['size']


def DeserializeMarketBookResponse(jsonRequest):
    jsonResponse = sports_api.send_sports_req(jsonRequest)
    dsjson = Payload(str(jsonResponse))
    market_book_response = MarketBookResponse(dsjson.jsonrpc, dsjson.result, dsjson.id)
    return market_book_response

# Gives option for saving for offline analysis
def GetRawBook(jsonRequest, sports_api):
    return sports_api.send_sports_req(jsonRequest)

def DeserializeRawBook(jsonResponse):
    dsjson = Payload(str(jsonResponse))
    market_book_response = MarketBookResponse(dsjson.jsonrpc, dsjson.result, dsjson.id)
    return market_book_response

