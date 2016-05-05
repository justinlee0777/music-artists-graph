import subprocess
import json
import requests
import operator
import time
import datetime
import sys
import uuid

# Data structures to store final JSON information
graph_json = {}
graph_json['nodes'] = []
graph_json['links'] = []

# Data structures to store intermediate information as 
nodes_list = []
related_artists_and_input = []
node_size_dict = {}
link_scores_dict = {}
link_dict = {}
source_groups = {}
node_colors = {}

# Format the user input for the Songkick API query
def formatInput(input, join_character):
	input_list = input.split()
	capitalized_input_list = []
	for word in input_list:
		capitalized_input_list.append(word.lower())
	return join_character.join(capitalized_input_list)

# Format the user artist to the official display name of the artist
def formatArtist(artist, join_character):
	input_list = artist.split()
	capitalized_input_list = []
	for word in input_list:
		capitalized_input_list.append(word.capitalize())
	return join_character.join(capitalized_input_list)


# def dateDifference(date):
# 	today = datetime.datetime.today()
# 	date = datetime.datetime.strptime(date, '%Y-%m-%d')
# 	return abs((date-today).days)

# Assign the group based on the nodes value
def assignGroup(artist):
	value = 0
	if artist in source_groups:
		value = source_groups[artist]
	else:
		for link in link_dict[artist]:
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


def getSongkickEvents(query):
	# Search for the artist and get the Songkick Artist ID
	r = requests.get('http://api.songkick.com/api/3.0/search/artists.json?query=' + query + '&apikey=f7IM56tGd91ix3Kq')
	songkick_search = r.json()
	artist_id = str(songkick_search['resultsPage']['results']['artist'][0]['id'])
	artist_name = songkick_search['resultsPage']['results']['artist'][0]['displayName'].encode('utf-8')

	# Get the artist's gigography
	r = requests.get('http://api.songkick.com/api/3.0/artists/' + artist_id + '/gigography.json?apikey=f7IM56tGd91ix3Kq&per_page=all')
	songkick_data = r.json()
	return (songkick_data['resultsPage']['results']['event'], artist_name)


def findRelatedArtists(events, user_input):
	artist_dict = {}

	# Loop through every event the artist has performed in
	for event in events:
		event_type = event['type'].encode('utf-8')
		event_date = event['start']['date'].encode('utf-8')

		# Get the artists that performed in the event
		artists = event['performance']
		for artist in artists:
			artist_name = artist['artist']['displayName'].encode('utf-8')
			billing_index = artist['billingIndex']

			# Average the billing indices to store the value to calculate node size later
			if artist_name in node_size_dict:
				node_size_dict[artist_name] = (node_size_dict[artist_name]+billing_index)/2
			else:
				node_size_dict[artist_name] = billing_index
			
			if user_input == artist_name:
	 			continue

	 		# Weight the scores differently if the event was a concert or a festival
	 		tmp_artist = artist_name
	 		score = 30
	 		if event_type == 'Festival':
	 			score = 20

	 		# max_date_difference = 365*10
	 		# date_difference = dateDifference(event_date)
	 		# if date_difference > max_date_difference:
	 		# 	date_difference = max_date_difference

	 		# Create the links and store them with their scores
	 		link_tuple1 = (user_input, artist_name)
	 		link_tuple2 = (artist_name, user_input)
	 		if link_tuple1 in link_scores_dict:
	 			link_scores_dict[link_tuple1] += score
	 			link_scores_dict[link_tuple2] += score
	 		else:
	 			link_scores_dict[link_tuple1] = score
	 			link_scores_dict[link_tuple2] = score	

	 		# Calculate the score to determine group number later
	 		if tmp_artist in node_colors:
	 			current_group = node_colors[tmp_artist]
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
	 			node_colors[tmp_artist] = source_groups[user_input]

	 		# Store the score for every artist
	 		if tmp_artist in artist_dict:
	 			artist_dict[tmp_artist] += score
	 		else:
	 			artist_dict[tmp_artist] = score

	# Return the sorted dictionary of artists based on their score, starting with the highest score
	return sorted(artist_dict.items(), key=operator.itemgetter(1), reverse=True)


def addLinks(sorted_artist_dict, user_artist, number_related_artists, max_node_value, min_node_value):
	
	# Loop through the top related artists
	if len(sorted_artist_dict) < number_related_artists:
		number_related_artists = len(sorted_artist_dict)
	for i in range(0, number_related_artists):
		tmp_artist_tuple = sorted_artist_dict[i]

		# Create the JSON object for the link
		tmp_link_json = {}
		tmp_link_json['source'] = user_artist
		tmp_link_json['target'] = tmp_artist_tuple[0]
		link_tuple = (user_artist, tmp_artist_tuple[0])
		tmp_link_json['value'] = link_scores_dict[link_tuple]
                tmp_link_json['id'] = str( uuid.uuid4() )
		graph_json['links'].append(tmp_link_json)

		# Keep track of all of the links that each node has
		if tmp_artist_tuple[0] in link_dict:
			link_dict[tmp_artist_tuple[0]].append(user_artist)
		else:
			link_dict[tmp_artist_tuple[0]] = [user_artist]


def addNodes(sorted_artist_dict, user_artist, number_related_artists, max_node_value, min_node_value):
	
	# Create a node for the user artist if it hasn't been created yet
	if user_artist not in nodes_list:
		nodes_list.append(user_artist)
		tmp_node_json = {}
		tmp_node_json['id'] = user_artist
		tmp_node_json['value'] = node_size_dict[user_artist]
		tmp_node_json['group'] = assignGroup(user_artist)
		tmp_node_json['source'] = 'true'
		graph_json['nodes'].append(tmp_node_json)

	# Loop through the related artists
	if len(sorted_artist_dict) < number_related_artists:
		number_related_artists = len(sorted_artist_dict)
	for i in range(0, number_related_artists):
		tmp_artist_tuple = sorted_artist_dict[i]

		# Create the node if it hasn't been created yet
		if tmp_artist_tuple[0] not in nodes_list:
			nodes_list.append(tmp_artist_tuple[0])
			tmp_node_json = {}
			tmp_node_json['id'] = tmp_artist_tuple[0]
			tmp_node_json['value'] = node_size_dict[tmp_artist_tuple[0]]
			tmp_node_json['group'] = assignGroup(tmp_artist_tuple[0])
			
			# Record if it is a source or not
			if tmp_artist_tuple[0] in source_groups:
				tmp_node_json['source'] = 'true'
			else:
				tmp_node_json['source'] = 'false'
				
			graph_json['nodes'].append(tmp_node_json)


def driver(user_input):

	# Get the Songkick data
	query = formatInput(user_input, '-')
	api_tuple = getSongkickEvents(query)
	events = api_tuple[0]
	artist_name = api_tuple[1]

	# Create all of the temporary dictionaries and lists
	sorted_related_artists = findRelatedArtists(events, artist_name)
	related_artists_and_input.append((sorted_related_artists, artist_name))




# Command line inputs
arguments = sys.argv
number_arguments = int(sys.argv[1])
if 3 <= len(sys.argv) <= 6:
	if 1 <= number_arguments <= 3:

		# Assign the original values to source nodes
		for i in range(2, number_arguments+2):
			user_input = sys.argv[i]
			user_artist = formatArtist(user_input, ' ')
			source_groups[user_artist] = pow(10, i-1)

		# Create and populate all of the temporary data structures
		for i in range(2, number_arguments+2):
			user_input = sys.argv[i]
			user_artist = formatArtist(user_input, ' ')
			driver(user_artist)

		# Number of top related artists to display
		number_related_artists = int(sys.argv[len(sys.argv)-1])
		
		# Create the links and nodes and append them to the final JSON object
		for i in range(0, len(related_artists_and_input)):
			addLinks(related_artists_and_input[i][0], related_artists_and_input[i][1], number_related_artists, 1, 1)
		for i in range(0, len(related_artists_and_input)):
			addNodes(related_artists_and_input[i][0], related_artists_and_input[i][1], number_related_artists, 1, 1)

		# Create and write to the JSON file
		with open('graph_data.json', 'w') as fp:
			json.dump(graph_json, fp)

	# Primitive error handling
	else:
		print "Invalid arguments"
else:
	print "Invalid arguments"
