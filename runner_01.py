import twitter, os
import time
import sys
import Interactor
from collections import deque
from testDM import *

api=twitter.Api(consumer_key='qRIvRBrUGfjd4EmERiMlg',
				consumer_secret='892XliWFk9NqqoBDQ2FzhSdMIKcTPzBiL4hbNr02I',
				access_token_key='1584713700-q3SvdgoLh2DJWyvf6eWJ0tPP5y6fihzWJ0yZBTH',
				access_token_secret='KHXNr38qWTkBgVKEqqTg5Tupk1rDb4uOgkIdtXC8') 
				
QFILE = r'P:\python_twitter\scrips\yourdmLogs\testQ.txt'
DFILE = r'P:\python_twitter\scrips\yourdmLogs\testQdone.txt'

#load action Q
def rebuild(TEXTFILE):
	textFileList = deque()
	try:
		with open(TEXTFILE, 'r') as fp:
			fload = fp.readlines()
		
		for item in fload:
			if item.strip() == '':
				continue
			textFileList.append(long(item))
	except Exception:
		print "nothing read from file!!"
	return textFileList
	
def initRoster():
	roster = Player_Dict().load_from_file()
	return roster
	
def saveRoster(roster):
	Player_Dict().save_to_file(roster)
	
def amendQfromTwitter(actionQ,debug=False):
	KnownCommands = [
					'?start',
					'?name',
					'?xp',
					'?gear',
					]
					
	mentionList = deque()
	if not debug:
		mentionList = api.GetMentions()
	else:
		print "debug mode preventing mention grab from twitter"
		
	if mentionList:
		for tweet in mentionList:
			if (
				any(word in KnownCommands for word in tweet.text.split(' ') ) and
				tweet.id not in actionQ
				):
				
				print "action present!", tweet.text
				actionQ.append(tweet.id)
				
	return actionQ

def saveList(slist, TEXTFILE):
	with open(TEXTFILE, 'w') as fp:
		fp.write('\n'.join(['%s' % (str(i)) for i in slist]))

		
#########################################################
# 				 LET'S ROLL MOTHERFUCKER				#
#########################################################

debug = False
############ load everything ################
actionQ = rebuild(QFILE)					#
actionQ = amendQfromTwitter(actionQ,debug)	#
resolvedList = rebuild(DFILE)				#
playerRoster = initRoster()					#
############ load everything ################

KnownCommands = [
				'?start',
				'?name',
				'?xp',
				'?gear',
				]
					
# print "Q: ", actionQ
# print "R: ", resolvedList
# print "O: ", playerRoster

impetusID = actionQ.popleft()		#grab first item from Q
try:
	#heres where we try to interact
	
	#DISCARD IF:
	if impetusID in resolvedList:
		
		pass 	#pass cuz we popped it outta the Q
				#so when Q gets resaved this will be gone
	
	responseTweet = ''
	
	if not debug:
		print "tweet passed checks! sending to Interactor!"
		impetusTweet = api.GetStatus(id = impetusID)
		responseTweet = Interactor.parseTweet(impetusTweet)
	else:
		print "debug mode is preventing Interactor from being called\n"
		print "putting impetusID back at top of deck"
		actionQ.appendleft(impetusID)
		
	
	if impetusID not in resolvedList:
		resolvedList.append(impetusID)	#tell prog we resolved it

except Exception:
	#put back in Q if we fuck up
	#for example, exceeding rate limits t(-_-t) 
	print "error. putting tweet at back of Q"
	actionQ.append(impetusID)

if responseTweet:
	twit_name = impetusTweet.user.screen_name	 #we need to fiddle with the roster here
	if not debug:
		api.PostUpdate('@%s %s' % (twit_name, responseTweet), in_reply_to_status_id=impetusID)
	
# print "impetusID: ", impetusID
# print "Q: ", actionQ
# print "R: ", resolvedList
# print "O: ", playerRoster

############ save everything ################
saveList(actionQ,QFILE)						#
saveList(resolvedList,DFILE)				#
saveRoster(playerRoster)					#
############ save everything ################



		
#do action
#clean up action Q