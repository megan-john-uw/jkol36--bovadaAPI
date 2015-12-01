from search_dictionary_for_certain_keys import search_dictionary_for_certain_keys
import json
from error import BovadaException


class BovadaMatch(object):
	def __init__(self, *args, **kwargs):
		self.sport = kwargs.pop("sport")
		self.description = kwargs.pop("description")
		self.startTime = kwargs.pop("startTime")
		self.home_team_short_name = kwargs.pop("home_team_short_name")
		self.home_team_full_name = kwargs.pop("home_team_full_name")
		self.home_team_abbreviation = kwargs.pop("home_team_abbreviation")
		self.away_team_short_name = kwargs.pop("away_team_shortname")
		self.away_team_full_name = kwargs.pop("away_team_full_name")
		self.away_team_abbreviation= kwargs.pop("away_team_abbreviation")
		self.game_link = kwargs.pop("game_link")
		self.type = kwargs.pop("type")
		self.game_id = kwargs.pop("game_id")
		self.outcomes = kwargs.pop("outcomes")
		return super(BovadaMatch, self).__init__()

	@property
	def match_details(self):
		return "%s, %s, %s, %s, %s, %s, %s, %s" %(self.sport, self.game_link, 
			self.description, self.startTime, self.home_team_full_name,
			self.game_link, self.type, self.game_id)

	@classmethod
	def create_from_center_content(cls, content_center):
		match = search_dictionary_for_certain_keys("items", content_center)[0]
		outcome_objects_for_match = []
		game_sport = match['sport']
		game_id = int(match['id'])
		description = match['description']
		startTime = match['startTime']
		competitors = match['competitors']
		home_team_abbreviation = search_dictionary_for_certain_keys("abbreviation", competitors[0])
		home_team_short_name = search_dictionary_for_certain_keys("shortName", competitors[0])
		home_team_full_name = search_dictionary_for_certain_keys("description", competitors[0])
		away_team_short_name = search_dictionary_for_certain_keys("shortName", competitors[1])
		away_team_abbreviation=  search_dictionary_for_certain_keys("abbreviation", competitors[1])
		away_team_full_name = search_dictionary_for_certain_keys("description", competitors[1])
		game_link = "https://sports.bovada.lv{}".format(match['link'])
		type_ = match['type']
		displayGroups= match['displayGroups']
		for group in displayGroups:
			#if the group is not a gameline we'll skip over it.
			if group['description'] != "Game Lines":
				pass
			else:
				betting_lines = [x for x in group["itemList"]]
				for line in betting_lines:
					outcomes = OutCome.create_from_betting_line(line)
					for outcome in outcomes:
						outcome_objects_for_match.append(outcome)


					

		bmatch = BovadaMatch(
				sport=game_sport,
				description=description,
				startTime=startTime,
				home_team_short_name=home_team_short_name,
				home_team_full_name = home_team_full_name,
				home_team_abbreviation = home_team_abbreviation,
				away_team_shortname = away_team_short_name,
				away_team_abbreviation = away_team_abbreviation,
				away_team_full_name = away_team_full_name,
				game_link=game_link,
				type=type_,
				game_id=game_id, 
				outcomes=outcome_objects_for_match)
		return bmatch
	@classmethod
	def bulk_create_from_center_content(cls, center_content):
		bmatches = []
		try:
			gamelines = search_dictionary_for_certain_keys("items", center_content)[0] #index 0 is gamelines index 1 is futures
		except (IndexError, TypeError):
			return []
		for match in gamelines['itemList']['items']:
			outcome_objects_for_match = []
			game_sport = match['sport']
			game_id = int(match['id'])
			description = match['description']
			startTime = match['startTime']
			competitors = match['competitors']
			home_team_abbreviation = search_dictionary_for_certain_keys("abbreviation", competitors[0])
			home_team_short_name = search_dictionary_for_certain_keys("shortName", competitors[0])
			home_team_full_name = search_dictionary_for_certain_keys("description", competitors[0])
			away_team_short_name = search_dictionary_for_certain_keys("shortName", competitors[1])
			away_team_abbreviation=  search_dictionary_for_certain_keys("abbreviation", competitors[1])
			away_team_full_name = search_dictionary_for_certain_keys("description", competitors[1])
			game_link = "https://sports.bovada.lv{}".format(match['link'])
			type_ = match['type']
			displayGroups= match['displayGroups']
			for group in displayGroups:
				if group['description'] != "Game Lines":
					pass
				else:
					betting_lines = [x for x in group["itemList"]]
					for line in betting_lines:
						outcomes = OutCome.create_from_betting_line(line)
						for outcome in outcomes:
							outcome_objects_for_match.append(outcome)


						

			bmatch = BovadaMatch(
					sport=game_sport,
					description=description,
					startTime=startTime,
					home_team_short_name=home_team_short_name,
					home_team_full_name = home_team_full_name,
					home_team_abbreviation = home_team_abbreviation,
					away_team_shortname = away_team_short_name,
					away_team_abbreviation = away_team_abbreviation,
					away_team_full_name = away_team_full_name,
					game_link=game_link,
					type=type_,
					game_id=game_id, 
					outcomes=outcome_objects_for_match)
			
			bmatches.append(bmatch)
			
		return bmatches


class OutCome(object):
	def __init__(self, *args, **kwargs):
		self.odds_type = kwargs.pop("odds_type")
		self.total_line = kwargs.pop("total_line")
		self.spread_line = kwargs.pop("spread_line")
		self.name = kwargs.pop("name")
		self.price_decimal = kwargs.pop("price_decimal")
		self.spread_amount = kwargs.pop("spread_amount")
		self.total_amount = kwargs.pop("total_amount")
		self.price_id = kwargs.pop("price_id")
		self.outcome_id = kwargs.pop("outcome_id")
		return super(OutCome, self).__init__()

	@classmethod
	def create_from_betting_line(cls, betting_line, *args, **kwargs):
		outcome_objs = []
		odds_type = betting_line["description"]
		outcomes = betting_line["outcomes"]
		for outcome in outcomes:
			spread_amount = None
			total_amount = None
			spread_line = None
			total_line = None
			if odds_type == "Total":
				try:
					total_amount = float(outcome["price"]["handicap"])
				except Exception, e:
					total_amount = None

				total_line = outcome["type"]

			if odds_type == "Point Spread" or odds_type=="Goal Spread" or odds_type == "Point Spread --sets":
				try:
					spread_amount = float(outcome["price"]["handicap"])
				except Exception, e: 
					spread_amount = None

				spread_line = outcome["type"]


			try:
				name = outcome["description"]
			except KeyError, e:
				name = None
			try:
				price_decimal = float(outcome["price"]['decimal'])
			except KeyError, e:
				price_decimal = None

			try:
				status = outcome['status']
			except KeyError, e:
				status = None
			try:
				price_id = int(outcome['price']['id'])
			except KeyError, e:
				price_id = None
			try:
				outcome_id = int(outcome['price']['outcomeId'])
			except KeyError, e:
				outcome_id = None

			if status == "OPEN":
				outcome_objs.append(
					cls(
						odds_type=odds_type,
						total_line=total_line,
						spread_line=spread_line,
						name=name,
						price_decimal=price_decimal,
						spread_amount = spread_amount,
						total_amount = total_amount,
						price_id=price_id,
						outcome_id=outcome_id,

					)
				)
		for outcome_obj in outcome_objs:
			if outcome_obj.price_decimal == None:
				outcome_objs.remove(outcome_obj)
			elif odds_type == "Total" and not outcome_obj.total_amount:
				outcome_objs.remove(outcome_obj)

			elif odds_type.__contains__("Spread") and not outcome_obj.spread_amount:
				outcome_objs.remove(outcome_obj)
		return outcome_objs




def parse_special_response(response, action):
	if action == "balance":
		return int(search_dictionary_for_certain_keys("availableBalance", response.json())["amount"])
	elif action == "summary":
		return response.json()

	elif action == "wallets":
		return response.json()

	elif action == "open_bets":
		outstanding_bet_amount = 0
		try:
			items = response.json()["items"]
		except KeyError, e:
			items = None

		if items:
			for item in items:
				try:
					riskAmount = item["riskAmount"]
				except KeyError, e:
					riskAmount = None
				if riskAmount:
					try:
						riskAmount = float(riskAmount)
					except Exception, e:
						print e
						riskAmount = riskAmount

					outstanding_bet_amount += riskAmount
		return "number of outstanding bets: {} outstanding_bet_amount: {}".format(len(items), outstanding_bet_amount)

	elif action == "bet_history":
		total_profit = 0
		number_of_bets_won = 0
		number_of_bets_lost = 0
		try:
			items = response.json()["items"]
		except KeyError, e:
			items = None

		if items:
			for item in items:
				try:
					outcomeCode = item["outcomeCode"]
				except KeyError, e:
					outcomeCode = None

				if (outcomeCode and 
					outcomeCode == "W"
					):
					number_of_bets_won += 1
					total_profit += float(item["toWinAmount"]) + float(item["riskAmount"]) - float(item["riskAmount"])


				elif (outcomeCode and 
					outcomeCode == "L"
					):
					number_of_bets_lost +=1
					total_profit -= float(item["riskAmount"])
			return "total_profit: ${}, num_bets_won: {}:), number_of_bets_lost: {}:(".format(total_profit, number_of_bets_won, number_of_bets_lost)




	return response

def parse_response(response):
	center_content = response['data']['regions']['content_center'] #useful
	bmatches = BovadaMatch.bulk_create_from_center_content(center_content)
	return bmatches

	
			
