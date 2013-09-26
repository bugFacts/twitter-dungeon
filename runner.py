from testDM import *
from map_generator import *
from RoomGenerator import buildRule
import twitter, os
import time

api=twitter.Api(consumer_key='',
				consumer_secret='',
				access_token_key='-',
				access_token_secret='') 

#define an object as a player dictionary
master_player_dict = Player_Dict()
#instantiate a new player dictionary and load saved info
new_player_dict = master_player_dict.load_from_file()

#working_player_dict = new_player_dict.copy()


#check mentions
#mentions = api.GetMentions()




#for each in mentions:
	#print each.id
	
testUsername = 'another player'
testUserID = 5	


if testUsername in new_player_dict.keys():
	#print "already playing"
	pass
#if a twitter user shows up in a mention that isnt in the dictionary,	
else:
	#decide if we should add them
	#print len(new_player_dict.keys())
	#print "lets add the new player!"
	#add them
	new_player_dict[testUsername] = Player(userName=testUsername, userID=testUserID, reTime=time.time())

#dont add them
	#code

#run the game
# for keys in new_player_dict:
	# new_player_dict[keys].print_info()
	
	#if we messed with a player, update their reTime
new_player_dict[testUsername].char_Helm = "poophat lol"
#print new_player_dict[testUsername].char_Helm
#new_player_dict[testUsername].print_info()


# for key in new_player_dict.keys():
	# print new_player_dict[key].reTime

#save changes to the save file
master_player_dict.save_to_file(new_player_dict)


