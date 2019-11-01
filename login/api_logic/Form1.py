from . import * 
import time
import pdb
from .SportsAPI import * 
from login.models import Market, Runner, Form, MarketDictionaryM, RunnerDictionaryM


class MarketDetail: 
	def __init__(self, marketId="", status="", inPlay="", removed=""):
		self.marketId = marketId
		self.status = status
		self.inPlay = inPlay
		self.removed = removed


class RunnerDetail: 
	def __init__(self, marketId="", status="", inPlay="", removed=""):
		self.marketId = marketId
		self.status = status
		self.backPrice = inPlay
		self.layPrice = removed


class Form_:

	bookRequestList = []
	marketDictionary = {}
	runnerDictionary = {}
	
	def __init__(self, mcr, params, start_time):
		self.request = mcr
		self.params = params
		self.start_time = start_time
		
		self.model_instance, created = Form.objects.get_or_create(request = str(1), params = str(2), start_time = str(3))

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
		res = sports_api.send_sports_req(serialization)
		allMarkets = DeserializeMarketCatalogueResponse(res) # Magic line

		my_data_dict = []
		market_list = []
		
		Runner.objects.all().delete()
		Market.objects.all().delete()
		MarketDictionaryM.objects.all().delete()
		RunnerDictionaryM.objects.all().delete()

		runner_di = {}
		for n in range(len(allMarkets.result)): # Loops through each market in the reuslt
			detail = MarketDetail()
			detail.marketId = allMarkets.result[n].marketId
			detail.removed = False
			Form_.marketDictionary.update({allMarkets.result[n].marketId: detail})

			course = allMarkets.result[n].event.name.split()
			market = Market(marketStartTime=allMarkets.result[n].marketStartTime, marketId = allMarkets.result[n].marketId, marketStatus='', inPlay='', course=course[0]+ " " + allMarkets.result[n].marketName, back=0.0, lay = 0.0)
			market_list.append( {'marketStartTime':allMarkets.result[n].marketStartTime, 'marketId' : allMarkets.result[n].marketId, 'marketStatus':'', 'inPlay':'', 'course':course[0]+ " " + allMarkets.result[n].marketName, 'back':0.0, 'lay' : 0.0 })
			runner_di[market.marketId] = []
			# runners = Runner.objects.all()
			for m in range(len(allMarkets.result[n].runners)): # Loops through each runner in market
				data = allMarkets.result[n].marketStartTime[11:16] + " " + course[0] + " " + allMarkets.result[n].marketName + " " + allMarkets.result[n].runners[m].runnerName 
				my_data_dict.append(str(data))
				runner_di[market.marketId].append( {'market' : market, 'selectionId' : allMarkets.result[n].runners[m].selectionId, 'runnerName' : allMarkets.result[n].runners[m].runnerName, 'runnerStatus':''} )

				if not (allMarkets.result[n].runners[m].selectionId in Form_.runnerDictionary):
					data = RunnerDetail()
					data.marketId = allMarkets.result[n].marketId
					Form_.runnerDictionary.update( { allMarkets.result[n].runners[m].selectionId: data } )
			
		# Markets must be commited before runners in the database as the 
		# runners rely on them for foreign key
		self.bulk_create_marketandrunner(allMarkets, market_list, runner_di, Form_.marketDictionary, Form_.runnerDictionary)


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

	@classmethod
	def ListMarketBook(cls, sports_api, bookRequestList):
		print("url", sports_api.url)
		for n in range(len(bookRequestList) - 1 ): # Loop through each json request waiting to be sent to server

			jsonResponse = ""
			print(bookRequestList[n], sports_api)
			while True:
				jsonResponse = GetRawBook(bookRequestList[n], sports_api) # Send the json request (from backed-up list) to server
				if jsonResponse == "":
					print("jsonResponse empty - retrying")
				else:
					break


			marketList = []
			runner_di = {}
			book = DeserializeRawBook(jsonResponse)

			local_md, local_rd = Form_.getDictionaries()

			for bookCount in range(len(book.result) - 1): # Loop through each market from the recent response from the server
				# course = book.result[n].event.name.split()
				course = allMarkets.result[n].event.name.split()

				for runnerCount in range(len(book.result[bookCount].runners) - 1): # Loop through each runner from each market
					my_with = book.result[bookCount].runners[runnerCount]
					
					r_obj = Runner.objects.get(selectionId=my_with.selectionId)
					# associatedMarket = None
					# if len(runner) == 1: 
					#     associatedMarket = runner[0].market
					
					## runner = Runner.objects.filter(selectionId=str(my_with.selectionId)).get(market_id=str(book.result[bookCount].marketId))
					# Market.objects.filter(marketId=book.result[bookCount].marketId).update(marketStatus=book.result[bookCount].status) 

					
					# TASK: REWRITE ABOVE LINE TO USE .save() instead of update. Thus triggering signal. 
					m_obj = Market.objects.get(marketId=book.result[bookCount].marketId)
					m_obj.marketStatus = book.result[bookCount].status 

					local_md[book.result[bookCount].marketId].status = book.result[bookCount].status
					local_md[book.result[bookCount].marketId].inPlay = book.result[bookCount].inplay


					# TODO: Makes little sense to not keep market_dictionary and market model consistent with each other, 
					# so make attempt to tie together. 


					if book.result[bookCount].inplay == True:
						# Market.objects.filter(marketId=associatedMarket.marketId).update(inPlay = "inPlay")
						m_obj.inPlay = "inPlay"
					else:
						# Market.objects.filter(marketId=associatedMarket.marketId).update(inPlay = "")
						m_obj.inPlay = ""


					# runner.update(runnerStatus = my_with.status)
					r_obj.runnerStatus = my_with.status
					local_rd[str(my_with.selectionId)].status = my_with.status

					if my_with.status == "ACTIVE":
						# runner.update(runnerStatus = "ACTIVE")
						r_obj.runnerStatus = "ACTIVE"
						if len(my_with.ex.availableToBack) > 0:
							local_rd[str(my_with.selectionId)].backPrice = my_with.ex.availableToBack[0].price
							# Market.objects.filter(marketId=associatedMarket.marketId).update(back=my_with.ex.availableToBack[0].price)
							m_obj.back = my_with.ex.availableToBack[0].price
						if len(my_with.ex.availableToLay) > 0:
							local_rd[str(my_with.selectionId)].layPrice = my_with.ex.availableToLay[0].price
							# Market.objects.filter(marketId=associatedMarket.marketId).update(lay=my_with.ex.availableToLay[0].price)
							m_obj.lay = my_with.ex.availableToLay[0].price
			# 	market_list.append( {'marketStartTime':book.result[n].marketStartTime, 'marketId' : book.result[n].marketId, 'marketStatus': m_obj.marketStatus, 'inPlay': m_obj.inPlay, 'course': course[0]+ " " + book.result[n].marketName, 'back': m_obj.back, 'lay' :  m_obj.lay })
			# 	runner_di[market.marketId].append( {'market' : m_obj, 'selectionId' : book.result[n].runners[m].selectionId, 'runnerName' : book.result[n].runners[m].runnerName, 'runnerStatus':r_obj.runnerStatus} )

			
			# cls.bulk_create_marketandrunner(book.result, market_list, runner_di, local_md, local_rd)

	@classmethod
	def getDictionaries(cls):
		local_md = {}
		for m in MarketDictionaryM.objects.all():
			local_md.update({m.market_id: MarketDetail(m.market_id, m.market_status, m.market_inPlay, m.market_removed)})

		local_rd = {}
		for r in RunnerDictionaryM.objects.all():
			local_rd.update({r.runner_id: RunnerDetail(r.runner_id, r.runner_status, r.runner_backPrice, r.runner_layPrice)})

		return local_md, local_rd

	def bulk_create_marketandrunner(self, allMarkets, market_list, runner_di, marketDictionary, runnerDictionary):
		MarketDictionaryM.objects.all().delete()
		RunnerDictionaryM.objects.all().delete()

		market_l = [Market(**market_list[i]) for i in range(len(allMarkets.result))]
		Market.objects.bulk_create(market_l)
		market_dict = [MarketDictionaryM(market_id = key, market_status = value.status, market_inPlay = value.inPlay, market_removed = value.removed ) for key, value in marketDictionary.items()]
		MarketDictionaryM.objects.bulk_create(market_dict)

		runner_l = [Runner(**runner_di[market.marketId][runner_no]) for market in market_l for runner_no in range(len(runner_di[market.marketId]))]
		Runner.objects.bulk_create(runner_l)
		runner_dict = [RunnerDictionaryM(runner_id = key, runner_status = value.status, runner_backPrice = value.backPrice, runner_layPrice = value.layPrice ) for key, value in runnerDictionary.items()]
		RunnerDictionaryM.objects.bulk_create(runner_dict)

		# Problems may occur with duplicate runners. A runner may compete in one race today and 
		# another tomorrow. 
	
	@classmethod
	def BuildListMarketBookRequests(cls):
		count = 0
		marketIdList = []
		del cls.bookRequestList[:]


		local_md, _ = cls.getDictionaries()


		for key, value in local_md.items():
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

			cls.bookRequestList.append(jsonRequest)
		


	@classmethod
	def CheckMarkets(cls):
		racesRemoved = False

		_, local_rd = getDictionaries()
		
		for key, value in local_rd.items():
			if value.status == "CLOSED" and value.removed == False:
				value.removed = True
				racesRemoved = True
			
			if racesRemoved:
				BuildListMarketBookRequests()