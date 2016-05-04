import subprocess
import json
import requests
import operator
import time
import datetime
import sys

graph_json = {}
graph_json['nodes'] = []
graph_json['links'] = []
nodes_list = []
related_artists_and_input = []

node_size_dict = {}
link_scores_dict = {}
link_dict = {}
source_groups = {}
node_colors = {}

def formatInput(input, join_character):
	input_list = input.split()
	capitalized_input_list = []
	for word in input_list:
		capitalized_input_list.append(word.lower())
	return join_character.join(capitalized_input_list)

def formatDate(date):
	split_date = date.split('-')
	return split_date[1] + '/' + split_date[2] + '/' + split_date[0]

def formatArtist(artist):
	split_artist = artist.split(' ')
	return '-'.join(split_artist).upper()

def formatArtist2(artist, join_character):
	input_list = artist.split()
	capitalized_input_list = []
	for word in input_list:
		capitalized_input_list.append(word.capitalize())
	return join_character.join(capitalized_input_list)

def dateDifference(date):
	today = datetime.datetime.today()
	# today = datetime.datetime.strptime(today, '%y-%m-%d')
	date = datetime.datetime.strptime(date, '%Y-%m-%d')
	return abs((date-today).days)

def findNodeValueExtrema(number_related_artists, sorted_related_artists, user_input):
	max_node_value = 0
	min_node_value = node_size_dict[sorted_related_artists[0][0]]
	for i in range(0, number_related_artists):
		# print sorted_related_artists[i]
		if node_size_dict[sorted_related_artists[i][0]] > max_node_value:
			max_node_value = node_size_dict[sorted_related_artists[i][0]]
		elif node_size_dict[sorted_related_artists[i][0]] < min_node_value:
			min_node_value = node_size_dict[sorted_related_artists[i][0]]

	if node_size_dict[formatArtist2(user_input, ' ')] > max_node_value:
		max_node_value = node_size_dict[formatArtist2(user_input, ' ')]
	elif node_size_dict[formatArtist2(user_input, ' ')] < min_node_value:
		min_node_value = node_size_dict[formatArtist2(user_input, ' ')]

	return (max_node_value, min_node_value)


def assignGroup(artist):
	print "artist:", artist
	value = 0
	if artist in source_groups:
		value = source_groups[artist]
	else:
		print link_dict[artist]
		print "length:", len(link_dict[artist])
		for link in link_dict[artist]:
			print "adding:", source_groups[link]
			value += source_groups[link]
	if value == 10:
		return 1
	if value == 100:
		return 2
	if value == 1000:
		return 3
	if value == 1010:
		return 4
	if value == 1100:
		return 5
	if value == 1110:
		return 6


# d1 = datetime.date(2013,1,10)
# d1 = '2013-01-01'
# print dateDifference(d1)


def getSongkickEvents(query):
	r = requests.get('http://api.songkick.com/api/3.0/search/artists.json?query=' + query + '&apikey=f7IM56tGd91ix3Kq')
	songkick_search = r.json()
	artist_id = str(songkick_search['resultsPage']['results']['artist'][0]['id'])
	artist_name = songkick_search['resultsPage']['results']['artist'][0]['displayName'].encode('utf-8')
	print artist_name

	r = requests.get('http://api.songkick.com/api/3.0/artists/' + artist_id + '/gigography.json?apikey=f7IM56tGd91ix3Kq&per_page=all')
	songkick_data = r.json()
	return (songkick_data['resultsPage']['results']['event'], artist_name)

def findRelatedArtists(events, user_input):
	artist_dict = {}
	for event in events:
		# print event['start']['date']
		# print dateDifference(event['start']['date'].encode('utf-8'))
		event_type = event['type'].encode('utf-8')
		event_date = event['start']['date'].encode('utf-8')

		artists = event['performance']
		for artist in artists:
			artist_name = artist['artist']['displayName'].encode('utf-8')
			billing_index = artist['billingIndex']

			# print artist_name

			# found = False
			# if formatArtist2(artist_name, ' ') == 'Devildriver':
			# 	print "Found Devildriver", user_input
			# 	print artist_name
			# 	found = True
			# if formatArtist2(artist_name, ' ') == 'DevilDriver':
			# 	print "Found DevilDriver", user_input
			# 	found = True
			
			# if formatArtist2(artist_name, ' ') in node_size_dict:
			# 	node_size_dict[formatArtist2(artist_name, ' ')] += billing_index
			# else:
			# 	node_size_dict[formatArtist2(artist_name, ' ')] = billing_index
			
			# if formatInput(user_input, ' ') == artist_name.lower():
			# 	# print "HERE\n"
	 	# 		continue
	 		
			if artist_name in node_size_dict:
				node_size_dict[artist_name] = (node_size_dict[artist_name]+billing_index)/2
			else:
				node_size_dict[artist_name] = billing_index
			


			#################################################
			# if formatInput(user_input, ' ') == artist_name.lower():
			if user_input == artist_name:
				# print "HERE\n"
	 			continue



	 		tmp_artist = artist_name
	 		# score = dateDifference(event_date)/100.0 - 15
	 		# score = dateDifference(event_date)
	 		score = 30
	 		if event_type == 'Festival':
	 			score = 20

	 		max_date_difference = 365*10
	 		date_difference = dateDifference(event_date)
	 		if date_difference > max_date_difference:
	 			date_difference = max_date_difference

	 		# print event_date
	 		# print date_difference
	 		# print max_date_difference
	 		# print 10*(float(date_difference)/max_date_difference)
	 		# print

	 		# score += 10*(date_difference/max_date_difference)

	 		# print score



	 		####################################################
	 		# link_tuple1 = (formatArtist2(user_input, ' '), artist_name)
	 		# link_tuple2 = (artist_name, formatArtist2(user_input, ' '))
	 		
	 		link_tuple1 = (user_input, artist_name)
	 		link_tuple2 = (artist_name, user_input)



	 		# if found:
	 		# 	print "HERE"
	 		# 	print link_tuple1
	 		if link_tuple1 in link_scores_dict:
	 			link_scores_dict[link_tuple1] += score
	 			link_scores_dict[link_tuple2] += score
	 		else:
	 			link_scores_dict[link_tuple1] = score
	 			link_scores_dict[link_tuple2] = score

	 		# if artist_name in link_dict:
	 		# 	if formatArtist2(user_input, ' ') not in link_dict[artist_name]:
	 		# 		link_dict[artist_name].append(formatArtist2(user_input, ' '))
	 		# else:
	 		# 	link_dict[artist_name] = [formatArtist2(user_input, ' ')]	

	 		if tmp_artist in node_colors:
	 			current_group = node_colors[tmp_artist]


	 			##############################
	 			# source_group = source_groups[formatArtist2(user_input, ' ')]
	 			source_group = source_groups[user_input]
	 			



	 			thousand = False
	 			hundred = False
	 			ten = False
	 			if current_group / 1000 >= 1:
	 				thousand = True
	 				current_group -= 1000
	 			if current_group / 100 >= 1:
	 				hundred = True
	 				current_group -= 100
	 			if current_group / 10 >= 1:
	 				ten = True

	 			if source_group == 1000 and not thousand:
	 				node_colors[tmp_artist] += 1000
	 			if source_group == 100 and not hundred:
	 				node_colors[tmp_artist] += 100
	 			if source_group == 10 and not ten:
	 				node_colors[tmp_artist] += 10

	 		else:

	 			##############################
	 			# node_colors[tmp_artist] = source_groups[formatArtist2(user_input, ' ')]
	 			print tmp_artist
	 			node_colors[tmp_artist] = source_groups[user_input]


	 		# print "test:", link_scores_dict[link_tuple1] 			

	 		if tmp_artist in artist_dict:
	 			# print adding
	 			artist_dict[tmp_artist] += score
	 		else:
	 			artist_dict[tmp_artist] = score

	 	# break

	# print sorted(artist_dict.items(), key=operator.itemgetter(1), reverse=True)
	return sorted(artist_dict.items(), key=operator.itemgetter(1), reverse=True)

def addLinks(sorted_artist_dict, user_artist, number_related_artists, max_node_value, min_node_value):
	

	#################################
	# user_artist = formatArtist2(user_input, ' ')
	# user_artist = user_input



	if len(sorted_artist_dict) < number_related_artists:
		number_related_artists = len(sorted_artist_dict)
	for i in range(0, number_related_artists):
		# related_artist_names.append(sorted_artist_dict[i][0])
		tmp_artist_tuple = sorted_artist_dict[i]

		tmp_link_json = {}
		tmp_link_json['source'] = user_artist
		tmp_link_json['target'] = tmp_artist_tuple[0]
		link_tuple = (user_artist, tmp_artist_tuple[0])
		# if link_tuple not in link_scores_dict:
		# 	# print link_scores_dict
		# 	tmp_link_json['value'] = 10
			# print "link tuple =", link_tuple
		# else:
			# tmp_link_json['value'] = link_scores_dict[link_tuple]
		tmp_link_json['value'] = link_scores_dict[link_tuple]
		# tmp_link_json['value'] = 3
		graph_json['links'].append(tmp_link_json)

		if tmp_artist_tuple[0] in link_dict:
			link_dict[tmp_artist_tuple[0]].append(user_artist)
		else:
			link_dict[tmp_artist_tuple[0]] = [user_artist]

def addNodes(sorted_artist_dict, user_artist, number_related_artists, max_node_value, min_node_value):
	
	###########################
	# user_artist = formatArtist2(user_input, ' ')
	# user_artist = user_input



	if user_artist not in nodes_list:
		nodes_list.append(user_artist)
		tmp_node_json = {}
		tmp_node_json['id'] = user_artist
		tmp_node_json['value'] = node_size_dict[user_artist]
		# tmp_node_json['group'] = source_groups[user_artist]
		tmp_node_json['group'] = assignGroup(user_artist)
		# print (node_size_dict[user_input]-min_node_value)
		# print float((max_node_value-min_node_value))

		# tmp_value = (1-(node_size_dict[user_input]-min_node_value)/float((max_node_value-min_node_value)))*100+1
		# tmp_node_json['value'] = max_node_value - node_size_dict[user_artist] + 1
		# print tmp_value, "\n"
		# tmp_node_json['value'] = tmp_value
		graph_json['nodes'].append(tmp_node_json)

	if len(sorted_artist_dict) < number_related_artists:
		number_related_artists = len(sorted_artist_dict)
	for i in range(0, number_related_artists):
	# related_artist_names.append(sorted_artist_dict[i][0])
		tmp_artist_tuple = sorted_artist_dict[i]
		print tmp_artist_tuple[0]
		if tmp_artist_tuple[0] not in nodes_list:
			# print tmp_artist_tuple[0]
			# print user_input
			nodes_list.append(tmp_artist_tuple[0])
			tmp_node_json = {}
			tmp_node_json['id'] = tmp_artist_tuple[0]
			# tmp_node_json['value'] = tmp_artist_tuple[1]
			# tmp_value = (1-(node_size_dict[tmp_artist_tuple[0]]-min_node_value)/float((max_node_value-min_node_value)))*100+1
			# tmp_node_json['value'] = tmp_value
			# print tmp_value
			tmp_node_json['value'] = node_size_dict[tmp_artist_tuple[0]]
			# if tmp_artist_tuple[0] in source_groups:
			# 	tmp_node_json['group'] = source_groups[tmp_artist_tuple[0]]
			# else:
			# 	tmp_node_json['group'] = assignGroup(tmp_artist_tuple[0])
			tmp_node_json['group'] = assignGroup(tmp_artist_tuple[0])
				
			# tmp_node_json['value'] = max_node_value - node_size_dict[tmp_artist_tuple[0]] + 1
			graph_json['nodes'].append(tmp_node_json)

def createJSONDict(sorted_artist_dict, user_artist, number_related_artists, max_node_value, min_node_value):
	# graph_json = {}
	# graph_json['nodes'] = []
	# graph_json['links'] = []

	###########################
	# user_artist = formatArtist2(user_input, ' ')
	# user_artist = user_input
	


	# max_node_value = node_size_dict[max(node_size_dict, key=lambda i: node_size_dict[i])]
	# min_node_value = node_size_dict[min(node_size_dict, key=lambda i: node_size_dict[i])]
	
	# print "max_node_value =", max_node_value
	# print "min_node_value =", min_node_value
	# print user_artist
	if user_artist not in nodes_list:
		nodes_list.append(user_artist)
		tmp_node_json = {}
		tmp_node_json['id'] = user_artist
		tmp_node_json['value'] = node_size_dict[user_artist]
		# tmp_node_json['group'] = source_groups[user_artist]
		tmp_node_json['group'] = assignGroup(user_artist)
		# print (node_size_dict[user_input]-min_node_value)
		# print float((max_node_value-min_node_value))

		# tmp_value = (1-(node_size_dict[user_input]-min_node_value)/float((max_node_value-min_node_value)))*100+1
		# tmp_node_json['value'] = max_node_value - node_size_dict[user_artist] + 1
		# print tmp_value, "\n"
		# tmp_node_json['value'] = tmp_value
		graph_json['nodes'].append(tmp_node_json)

	# Get the top related artists
	# number_related_artists = 10
	# related_artist_names = []
	if len(sorted_artist_dict) < number_related_artists:
		number_related_artists = len(sorted_artist_dict)
	for i in range(0, number_related_artists):
		# related_artist_names.append(sorted_artist_dict[i][0])
		tmp_artist_tuple = sorted_artist_dict[i]

		print tmp_artist_tuple[0]

		tmp_link_json = {}
		tmp_link_json['source'] = user_artist
		tmp_link_json['target'] = tmp_artist_tuple[0]
		link_tuple = (user_artist, tmp_artist_tuple[0])
		# if link_tuple not in link_scores_dict:
		# 	# print link_scores_dict
		# 	tmp_link_json['value'] = 10
			# print "link tuple =", link_tuple
		# else:
			# tmp_link_json['value'] = link_scores_dict[link_tuple]
		tmp_link_json['value'] = link_scores_dict[link_tuple]
		# tmp_link_json['value'] = 3
		graph_json['links'].append(tmp_link_json)

		if tmp_artist_tuple[0] not in nodes_list:
			# print tmp_artist_tuple[0]
			# print user_input
			nodes_list.append(tmp_artist_tuple[0])
			tmp_node_json = {}
			tmp_node_json['id'] = tmp_artist_tuple[0]
			# tmp_node_json['value'] = tmp_artist_tuple[1]
			# tmp_value = (1-(node_size_dict[tmp_artist_tuple[0]]-min_node_value)/float((max_node_value-min_node_value)))*100+1
			# tmp_node_json['value'] = tmp_value
			# print tmp_value
			tmp_node_json['value'] = node_size_dict[tmp_artist_tuple[0]]
			# if tmp_artist_tuple[0] in source_groups:
			# 	tmp_node_json['group'] = source_groups[tmp_artist_tuple[0]]
			# else:
			# 	tmp_node_json['group'] = assignGroup(tmp_artist_tuple[0])
			tmp_node_json['group'] = assignGroup(tmp_artist_tuple[0])
				
			# tmp_node_json['value'] = max_node_value - node_size_dict[tmp_artist_tuple[0]] + 1
			graph_json['nodes'].append(tmp_node_json)


	# return graph_json


def driver(user_input):

	



	query = formatInput(user_input, '-')
	api_tuple = getSongkickEvents(query)
	events = api_tuple[0]
	artist_name = api_tuple[1]
	# sorted_related_artists = findRelatedArtists(events, user_input)
	sorted_related_artists = findRelatedArtists(events, artist_name)
	number_related_artists = 5
	# extrema = findNodeValueExtrema(number_related_artists, sorted_related_artists, user_input)
	# extrema = findNodeValueExtrema(number_related_artists, sorted_related_artists, artist_name)
	# max_node_value = extrema[0]
	# min_node_value = extrema[1]
	# print "max_node_value", max_node_value
	# print "min_node_value", min_node_value
	# related_artists_and_input.append((sorted_related_artists, user_input))
	related_artists_and_input.append((sorted_related_artists, artist_name))

	# createJSONDict(sorted_related_artists, user_input, number_related_artists, max_node_value, min_node_value)
	


# user_input = 'In This Moment'
# user_input = 'Muse'
# query = formatInput(user_input, '-')

# events = getSongkickEvents(query)
# sorted_related_artists = findRelatedArtists(events)


# driver('Starset')
# print nodes_list
# driver('In This Moment')
# print nodes_list
# driver('Papa Roach')
# print nodes_list



arguments = sys.argv
number_arguments = int(sys.argv[1])
if 3 <= len(sys.argv) <= 6:
	if 1 <= number_arguments <= 3:

		for i in range(2, number_arguments+2):
			user_input = sys.argv[i]
			user_artist = formatArtist2(user_input, ' ')
			source_groups[user_artist] = pow(10, i-1)

		for i in range(2, number_arguments+2):
			user_input = sys.argv[i]
			user_artist = formatArtist2(user_input, ' ')
			print user_artist
			driver(user_artist)

		# driver('In This Moment')
		# driver('Papa Roach')
		# driver('Five Finger Death Punch')

		# print node_size_dict

		# for i in range(0, len(related_artists_and_input)):
		# 	related_artists = related_artists_and_input[i][0]
		# 	for j in range(0, len(related_artists_and_input)):
		# 		if i == j:
		# 			continue



		number_related_artists = 5
		for i in range(0, len(related_artists_and_input)):
			addLinks(related_artists_and_input[i][0], related_artists_and_input[i][1], number_related_artists, 1, 1)
		for i in range(0, len(related_artists_and_input)):
			addNodes(related_artists_and_input[i][0], related_artists_and_input[i][1], number_related_artists, 1, 1)
			# createJSONDict(related_artists_and_input[i][0], related_artists_and_input[i][1], number_related_artists, 1, 1)

		# print graph_json

		# print link_scores_dict

		# print source_groups
		# print node_colors
		print link_dict


		with open('small_sample.json', 'w') as fp:
			json.dump(graph_json, fp)







	else:
		print "Invalid arguments"
else:
	print "Invalid arguments"