from testDM import *
from map_generator import *
from RoomGenerator import buildRule
import twitter, os
import time
import sys

# api=twitter.Api(consumer_key='',
				# consumer_secret='',
				# access_token_key='',
				# access_token_secret='') 
				
api=twitter.Api(consumer_key='',
				consumer_secret='',
				access_token_key='',
				access_token_secret='') 
				
TWEETQ = r'P:\python_twitter\scrips\yourdmLogs\tweetQ.txt'
RESOLQ = r'P:\python_twitter\scrips\yourdmLogs\resolvedQ.txt'

#########################################################
# 					MISC UTILITIES						#
#########################################################
def AnAFixer(strIn):
	strVowel = 'aeiouAEIOU'
	
	k = 1
	while k == 1:
		if strIn.strip() != "":
			if strIn.lower().strip() == 'belly of the beast':
				#strOut = 'The %s' % (strIn.strip())
				strOut = ' '.join(['The', strIn.strip()])
				k = 2
			elif 'yggdrasil' in strIn.lower():
				strOut = strIn.strip()
			elif strIn[0].strip() in strVowel:
				strOut = ' '.join(['An', strIn.strip()])
				#strOut = 'An %s' % (strIn.strip())
				k =2 
			else:
				strOut = ' '.join(['A', strIn.strip()])
				#strOut = 'A %s' % (strIn.strip())
				k =2
		else:
			#print 'errpr'
			strOut = 'A %s' % (strIn.strip())
			k = 2
		
	return strOut.title()
	
def DoWeAddPhrase(strIn, strAdd, prob=1, max_let=140):
	#can we add the two given strings
	#also maybe we dont even if we can
	if (random.random() < prob) and (len(strIn) + len(strAdd)) < max_let:
		strOut = strIn + strAdd
		return strOut
	else:
		return strIn
	
def tweetQ_load():
	actionQueue = []
	### READ EXISTING ACTION QUEUE ###
	with open(TWEETQ, 'r') as fp:
		ftweetQ = fp.readlines()
	
	for i in ftweetQ:
		if i.strip() == '': #no empty lines
			continue
		i = long(i)
		actionQueue.append( i )
	return actionQueue
	
def doneList_load():
	doneList = []
	### READ EXISTING DONE LIST ###
	with open(RESOLQ, 'r') as fp:
		fdoneList = fp.readlines()
	
	for i in fdoneList:
		if i.strip() == '': #no empty lines
			continue	
		i = long(i)
		doneList.append( i )
	return doneList
	
def tweetQ_write(actionQueue):
	### UPDATE EXISTING ACTION QUEUE ###
	actionQueue = list(set( actionQueue ))
	with open(TWEETQ, 'w') as fp:
		fp.write('\n'.join(['%s' % (str(i)) for i in actionQueue]))
		
def doneList_write(doneList):
	### UPDATE EXISTING DONE QUEUE ###
	doneList = list(set( doneList ))
	with open(RESOLQ, 'w') as fp:
		fp.write('\n'.join(['%s' % (str(i)) for i in doneList]))
		
def CleanUp_TwitID(twitID):
	#eh is too much work cuz we gotta reload the new lists in the calling method anyway
	pass
#########################################################
# 					KNOWN COMMANDS						#
#########################################################

def updatePlayerDict(playerdict):
	master_player_dict.save_to_file(playerdict)
	
def ComStart(playerdict,usrName, usrID):
	playerdict[usrName] = Player(userName=usrName, userID=usrID, reTime=time.time())
	
	strRespond = "Welcome to your Adventure, Pupil! Select your Name by typing '?name' followed by what you wish your Adventurer to be known as!"
	
	playerdict[usrName].char_Chest = 'ripped leather tunic'
	playerdict[usrName].char_Hand = 'wooden sword'
	playerdict[usrName].char_inv1 = 'few gold coins'
	updatePlayerDict(playerdict)
	return strRespond


#########################################################
# 				LOAD PLAYER ROSTER						#
#########################################################
#define an object as a player dictionary
master_player_dict = Player_Dict()
#instantiate a new player dictionary and load saved info
playerdict = master_player_dict.load_from_file()

#########################################################
# CHECK TO SEE IF WE HAVE UNRESOLVED MENTIONS IN THE Q	#
#########################################################
actionQueue = []	
doneList = []
# actionQueue = tweetQ_load()
# doneList = doneList_load()

KnownCom = [ 
			'?start',
			'?name',
			'?xp',
			'?gear',
			]
			
#########################################################
# 		GRAB NEW ACTIONABLE MENTIONS FROM TWITTER		#
#########################################################
	####### check for newest mentions
mentions = api.GetMentions()


for tweet in mentions:
	#print tweet.user.screen_name, tweet.text.encode('utf-8', errors='replace')
	wordlist = tweet.text.split(' ')
	#print wordlist
	if any(word in KnownCom for word in wordlist):
		#print "actionable"
		
	### ACTIONABLE COMMAND PRESENT, ADD TO Q ###
		actionQueue = tweetQ_load()
		actionQueue.append(long(tweet.id))
		tweetQ_write(actionQueue)
	else:
		#print "non-action"
	## NOTHING ACTIONABLE, DISCARD ###
		doneList = doneList_load()
		doneList.append(tweet.id)
		doneList_write(doneList)

#########################################################
# 	DEAL WITH UNRESOLVED MENTIONS FROM LAST TIME		#
#########################################################

actionQueue = tweetQ_load()
for each in actionQueue:
	print each
	try:
		print api.GetStatus(id=each).text
	except Exception:
		print "possible deleted tweet"

if actionQueue:
	for each in actionQueue:
		#doID = int(float( each ))
		doID = each
		print doID
		if doID not in doneList:
			print "not in donelist"
			try:
				acton_UserID = api.GetStatus(id=doID).user.id
				acton_UserName = api.GetStatus(id=doID).user.screen_name
				acton_TweetText = api.GetStatus(id=doID).text
			except Exception:
				print "user deleted tweet?"
				actionQueue = tweetQ_load()
				if doID in actionQueue:
					actionQueue.remove( long(doID) )
					tweetQ_write(actionQueue)
				actionQueue = tweetQ_load()
				### add responded tweet id to responded file
				doneList = doneList_load()
				doneList.append( long(doID) )
				doneList_write(doneList)
				continue
			
			strRespond = ""
			if acton_UserName not in playerdict:
				continue
				##this is weird
			
			print acton_TweetText
			### search acton_TweetText for known command
			if '?start' in acton_TweetText.split(' '):
				print "start present"
				if acton_UserName in playerdict.keys() and playerdict[acton_UserName].char_name is not None and playerdict[acton_UserName].char_name != "None":
					strRespond = "You are already known as %s!" % (playerdict[acton_UserName].char_name)
				else:
					strRespond = ComStart(playerdict, acton_UserName, acton_UserID)

			elif '?name' in acton_TweetText.split(' '):
				print "name present"
				if playerdict[acton_UserName].char_name is not None and playerdict[acton_UserName].char_name != "None":
					strRespond = "You are already known as %s" % (playerdict[acton_UserName].char_name)
				else:
					#print acton_TweetText.split('?name')[1].strip()
					playerdict[acton_UserName].char_name=(acton_TweetText.split('?name')[1].strip())
					strRespond = "Greetings, %s. You are now a simple peasant but soon you will know your true calling!" % (playerdict[acton_UserName].char_name)

			elif '?xp' in acton_TweetText.split(' '):
				print "xp present"
				playerdict[acton_UserName].get_level()

				strRespond = '%s, you are now level %i, with %i actual experience points!.' % (playerdict[acton_UserName].char_name, int(playerdict[acton_UserName].level), int(playerdict[acton_UserName].xp) )
				
			elif '?gear' in acton_TweetText.split(' '):
				print "gear present"
				str1=""
				str2=""
				str3=""
				str4=""
				str5=""
				str6=""
				str7=""
				
				if playerdict[acton_UserName].char_Helm != "None": str1 = "donning %s" % (AnAFixer(playerdict[acton_UserName].char_Helm))
				if playerdict[acton_UserName].char_Chest != "None":str2 = "wearing %s" % (AnAFixer(playerdict[acton_UserName].char_Chest))
				if playerdict[acton_UserName].char_Hand != "None": str3 = "wielding %s" % (AnAFixer(playerdict[acton_UserName].char_Hand))
				if playerdict[acton_UserName].char_Ring != "None": str4 = "wearing %s" % (AnAFixer(playerdict[acton_UserName].char_Ring))
				if playerdict[acton_UserName].char_inv1 != "None": str5 = "%s" % (AnAFixer(playerdict[acton_UserName].char_inv1))
				if playerdict[acton_UserName].char_inv2 != "None": str6 = "%s" % (AnAFixer(playerdict[acton_UserName].char_inv2))
				if playerdict[acton_UserName].char_inv3 != "None": str7 = "%s" % (AnAFixer(playerdict[acton_UserName].char_inv3))
								
				strList = []
				strInv = []
				if str1:
					strList.append(str1)
				if str2:
					strList.append(str2)
				if str3:
					strList.append(str3)
				if str4:
					strList.append(str4)
				if str5:
					strInv.append(str5)
				if str6:
					strInv.append(str6)
				if str7:
					strInv.append(str7)
				
				strWorn = ""
				strHave = ""
				
				if strList:
					if len(strList) >= 2:
						strWorn = ', '.join(strList[:-1])
						strWorn = ' and '.join( strList[-1] )
					else:
						strWorn = ''.join(strList)
				if strInv:
					if len(strInv) >= 2:
						strHave = ', '.join(strInv[:-1])
						strHave = ' and '.join( strList[-1] )
					else:
						strHave = ''.join(strInv)
								
				if strWorn:
					if strHave:
						strRespond = "You are currently %s. You also have %s!" % (strWorn, strHave)
					else:
						strRespond = "You are currently %s." % (strWorn)
				else:
					if strHave:
						strRespond = "You own %s." % (strHave)
					else:
						strRespond = "You have no earthly possessions, including clothing."
						
			# print actonLevel
			# print acton_UserName
			# print acton_TweetText
			# print strRespond

			
			print acton_TweetText, strRespond
			### tweet response
			if strRespond is not None or not "":
				try:
					api.PostUpdate('@%s %s' % (acton_UserName, strRespond), in_reply_to_status_id=doID)
					time.sleep(120)
					continue
				except Exception:
					continue
			master_player_dict.save_to_file(playerdict)
		### rewrite queue to file without responded tweet id
		actionQueue = tweetQ_load()
		if doID in actionQueue:
			actionQueue.remove( long(doID) )
			tweetQ_write(actionQueue)
		actionQueue = tweetQ_load()
		### add responded tweet id to responded file
		doneList = doneList_load()
		doneList.append( long(doID) )
		doneList_write(doneList)



# for keys in new_player_dict:
	# new_player_dict[keys].print_info()
	

# for key in new_player_dict.keys():
	# print new_player_dict[key].reTime





