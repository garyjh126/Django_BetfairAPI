from . import * 
import time
import pdb
from .SportsAPI import * 
from login.models import Market, Runner

marketDictionary = {}
bookRequestList = []

class MarketDetail: 
    def __init__(self):
        self.marketId = ""
        self.status = ""
        self.inPlay = "" 
        self.removed = "" 

runnerDictionary = {}
class RunnerDetail: 
    def __init__(self):
        self.marketId = ""
        self.status = ""
        self.backPrice = "" 
        self.layPrice = "" 


class Form():

    def __init__(self, mcr, params, start_time):
        self.request = mcr
        self.params = params
        self.start_time = start_time

    def ListMarketCatalogue(self, sports_api): #'Gets list of today's races

        requestList = [] # list of MarketCatalogueRequest

        eventTypeIds = []
        eventTypeIds.append("7")
        self.params.filter.eventTypeIds = eventTypeIds

        marketCountries = []
        marketCountries.append("GB")
        self.params.filter.marketCountries = marketCountries

        marketProjection = []
        marketProjection.append("MARKET_START_TIME")
        marketProjection.append("RUNNER_DESCRIPTION")
        marketProjection.append("EVENT")
        self.params.marketProjection = marketProjection

        marketTypeCodes = []
        marketTypeCodes.append("WIN")
        self.params.filter.marketTypeCodes = marketTypeCodes

        marketStartTime = self.start_time

        # Possible correction to be made here
        if time.localtime() == 0:
            marketStartTime._from = self.get_dateTime(dlst = True)

        else:
            marketStartTime._from = self.get_dateTime()

        temp_time = marketStartTime._from
        marketStartTime._to = temp_time.replace(temp_time[11:19], "00:00:00").replace("00:00", "23:00")
        self.params.filter.marketStartTime = marketStartTime

        self.request.params = self.params
        requestList.append(self.request)

        serialization = SerializeMarketCatalogueRequest(requestList[0], requestList[0]) # Remember to deal with entire list, not just first element
        req = sports_api.send_sports_req(serialization)
        allMarkets = DeserializeMarketCatalogueResponse(req) # Magic line

        my_data_dict = []
        market_list = []
        
        Runner.objects.all().delete()
        Market.objects.all().delete()
        runner_di = {}
        for n in range(len(allMarkets.result)): # Loops through each market in the reuslt
            detail = MarketDetail()
            detail.marketId = allMarkets.result[n].marketId
            detail.removed = False
            marketDictionary.update({allMarkets.result[n].marketId: detail})
            course = allMarkets.result[n].event.name.split()
            market = Market(marketStartTime=allMarkets.result[n].marketStartTime, marketId = allMarkets.result[n].marketId, marketStatus='', inPlay='', course=course[0]+ " " + allMarkets.result[n].marketName, back=0.0, lay = 0.0)
            market_list.append( {'marketStartTime':allMarkets.result[n].marketStartTime, 'marketId' : allMarkets.result[n].marketId, 'marketStatus':'', 'inPlay':'', 'course':course[0]+ " " + allMarkets.result[n].marketName, 'back':0.0, 'lay' : 0.0 })
            runner_di[market.marketId] = []
            # runners = Runner.objects.all()
            for m in range(len(allMarkets.result[n].runners)): # Loops through each runner in market
                data = allMarkets.result[n].marketStartTime[11:16] + " " + course[0] + " " + allMarkets.result[n].marketName + " " + allMarkets.result[n].runners[m].runnerName 
                my_data_dict.append(str(data))
                runner_di[market.marketId].append( {'market' : market, 'selectionId' : allMarkets.result[n].runners[m].selectionId, 'runnerName' : allMarkets.result[n].runners[m].runnerName, 'runnerStatus':''} )

                if not (allMarkets.result[n].runners[m].selectionId in runnerDictionary):
                    data = RunnerDetail()
                    data.marketId = allMarkets.result[n].marketId
                    runnerDictionary.update( { allMarkets.result[n].runners[m].selectionId: data } )
           

        # Markets must be commited before runners in the database as the 
        # runners rely on them for foreign key

        bulk_create_marketandrunner(allMarkets, market_list, runner_di)


    def get_dateTime(self, dlst = False):
        tf = []
        current_dtime = time.localtime()
        for i in range(6):
            if i != 0:
                x =  str(current_dtime[i]) if len(str(current_dtime[i])) == 2 else '0'+ str(current_dtime[i])
            else: 
                x = str(current_dtime[i])
            tf.append(x)
        if dlst: 
            tf[3] -= 1

        return tf[0]+'-'+tf[1]+'-'+tf[2]+'T'+tf[3]+':'+tf[4]+':'+tf[5]+'Z'


def bulk_create_marketandrunner(allMarkets, market_list, runner_di):
    market_l = [Market(**market_list[i]) for i in range(len(allMarkets.result))]
    Market.objects.bulk_create(market_l)
    runner_l = [Runner(**runner_di[market.marketId][runner_no]) for market in market_l for runner_no in range(len(runner_di[market.marketId]))]
    Runner.objects.bulk_create(runner_l)

def BuildListMarketBookRequests():

    count = 0
    marketIdList = []
    del bookRequestList[:]

    for key, value in marketDictionary.items():
        if not value.removed:
            marketIdList.append(value.marketId)

    for n in range(len(marketIdList) // 9):
        requestList = []
        request = MarketBookRequest()
        params = MarketBookParams()

        if n == (len(marketIdList) // 9):
            for m in range(1, len(marketIdList) % 9):
                params.marketIds.append(marketIdList[count])
                count += 1
        else:
            for m in range(1, 9):
                params.marketIds.append(marketIdList[count])
                count += 1

        params.priceProjection.priceData.append("EX_BEST_OFFERS")
        params.priceProjection.priceData.append("EX_TRADED")
        params.orderProjection = "ALL"

        request.params = params

        requestList.append(request)

        jsonRequest = SerializeMarketBookRequest(requestList[0], requestList[0]) # Remember to deal with entire list, not just first element

        bookRequestList.append(jsonRequest)


def ListMarketBook(sports_api):


    for n in range(len(bookRequestList) - 1 ): # Loop through each json request waiting to be sent to server

        # jsonResponse = GetRawBook(bookRequestList[n])

        jsonResponse = ""

        while True:
            jsonResponse = GetRawBook(bookRequestList[n], sports_api) # Send the json request (from backed-up list) to server
            if jsonResponse == "":
                print("jsonResponse empty - retrying")
            else:
                break

        book = DeserializeRawBook(jsonResponse)

        for bookCount in range(len(book.result) - 1): # Loop through each market from the recent response from the server

            for runnerCount in range(len(book.result[bookCount].runners) - 1): # Loop through each runner from each market
                my_with = book.result[bookCount].runners[runnerCount]
                
                runner = Runner.objects.filter(selectionId=my_with.selectionId)
                associatedMarket = None
                if len(runner) == 1: 
                    associatedMarket = runner[0].market
                
                # runner = Runner.objects.filter(selectionId=str(my_with.selectionId)).get(market_id=str(book.result[bookCount].marketId))
                Market.objects.filter(marketId=book.result[bookCount].marketId).update(marketStatus=book.result[bookCount].status) 
                marketDictionary[book.result[bookCount].marketId].status = book.result[bookCount].status
                marketDictionary[book.result[bookCount].marketId].inPlay = book.result[bookCount].inplay

                if book.result[bookCount].inplay == True:
                    Market.objects.filter(marketId=associatedMarket.marketId).update(inPlay = "inPlay")
                else:
                    Market.objects.filter(marketId=associatedMarket.marketId).update(inPlay = "")


                runner.update(runnerStatus = my_with.status)
                runnerDictionary[my_with.selectionId].status = my_with.status

                if my_with.status == "ACTIVE":
                    runner.update(runnerStatus = "ACTIVE")
                    if len(my_with.ex.availableToBack) > 0:
                        runnerDictionary[my_with.selectionId].backPrice = my_with.ex.availableToBack[0].price
                        Market.objects.filter(marketId=associatedMarket.marketId).update(back=my_with.ex.availableToBack[0].price)
                    if len(my_with.ex.availableToLay) > 0:
                        runnerDictionary[my_with.selectionId].layPrice = my_with.ex.availableToLay[0].price
                        Market.objects.filter(marketId=associatedMarket.marketId).update(lay=my_with.ex.availableToLay[0].price)


def CheckMarkets():
    racesRemoved = False
    
    for key, value in marketDictionary.items():
        if value.status == "CLOSED" and value.removed == False:
            value.removed = True
            racesRemoved = True
        
        if racesRemoved:
            BuildListMarketBookRequests()