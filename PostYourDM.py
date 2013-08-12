from __future__ import division
import RoomGenerator
import twitter, os
import random
import linecache
import xlrd
import sys
import time
from string import maketrans  
import re
import tweepy
from collections import defaultdict

ACCEPTLIST2 = 'P:\python_twitter\scrips\yourdmLogs\AcceptableToPost2.txt'
TWEETSRESPONDEDTO = 'P:\python_twitter\scrips\yourdmLogs\AlreadyReplied.txt'
BANLIST = 'P:\python_twitter\scrips\yourdmLogs\ANeverTalkTo.txt'
BADWORDS = r'P:\python_twitter\scrips\yourdmLogs\badwords.txt'

api=twitter.Api(consumer_key='',
				consumer_secret='',
				access_token_key='',
				access_token_secret='') 

######## READ FORMER RESPODERS INTO DICTIONARY ####
def DictUserRelat():
	with open(ACCEPTLIST2, 'r') as fp:
		fBugTime = fp.readlines()
	
	BugRelate = defaultdict(list)
	BugRelate = {}

	for i in fBugTime:
		if i.rstrip() == '':	#skip empty limes
			continue
			
		try:
			x = i.split('|')[0].rstrip();#screen name
		except IndexError:
			x = 0;
			
		try:
			y = i.split('|')[1].rstrip();#time stamp
		except IndexError:
			y = 0;
			
		try:
			z = i.split('|')[2].rstrip();#relationship
		except IndexError:
			z = 0;
			
		#print 'x= ' + str(x);
		#print 'y= ' + str(y);
		#print 'z= ' + str(z);
		
		if BugRelate.has_key(x):
			BugRelate[x]=y,z

		else:	
			BugRelate[x] = y, z
		#except Exception:
		#	sys.exc_clear()
	
	#print BugRelate.items()
	return BugRelate
	
######## READ LIST OF TWEET IDS RESPONDED TO ####
def CheckRepliedList():
	if os.path.exists(TWEETSRESPONDEDTO):
		with open(TWEETSRESPONDEDTO, 'r') as fp:
			rawReplied = fp.readlines()
		
		alreadyReplied = []
		for i in rawReplied:
			if i.strip() == '':
				continue
			try:
				alreadyReplied.append(i.strip())
			except Exception:
				sys.exc_clear()
	return alreadyReplied
	
def CheckBlackList():
	with open(BANLIST, 'r') as f:
		rawbanList = f.readlines()
		
	banList = []
	for i in rawbanList:
		if i.strip() == '':
			continue
		try:
			banList.append(i.strip())
		except Exception:
			sys.exc_clear()
				
	return banList
			
def CleanRelatDict(userName,reTime=None,reScore=None):
	BugRelate = DictUserRelat()
	
	if reTime is None:		#if no new values given use old ones
		reTime = BugRelate[userName][0]
	if reScore is None:	#if no new values given use old ones
		reScore = BugRelate[userName][1]
	
	BugRelate[userName] = reTime,reScore
	
	with open(ACCEPTLIST2, 'w') as fp:
		fp.write(''.join(['%s|%s|%s\n' % (key, value[0],value[1]) for key, value in BugRelate.iteritems()]))
		
def CleanUpReplied(tweetid):
	alreadyReplied = CheckRepliedList()
	alreadyReplied.append(tweetid)
	with open(TWEETSRESPONDEDTO, 'w') as fp:
		fp.write('\n'.join(['%s' % (i) for i in alreadyReplied]))
					
def DiceCode(numOfDice):

	syb_list = [u'\u2680',u'\u2681',u'\u2682',u'\u2683',u'\u2684',u'\u2685']
	strOut= ''
	for each in range(numOfDice):
		strOut = ''.join([strOut,random.choice(syb_list)])
	
	return strOut
	
def ReplyRoll(debug = 0):
	x = random.randint(1,6)
	#y = random.randint(1,20)
	y = random.choice([4,6,8,10,12,20,100])

	numname = ['zero','one','two','three','four','five','six']
	
	if y == 6 and debug == 0:
		r = DiceCode(x)
	else:
		r = random.randint(x,x*y)
	strUpdate = 'You roll %s %i-sided dice: %s. It will be weeks before we know what this means.' % (numname[x],y,r)
	return strUpdate
	
def ReplyAttack(debug = 0):
	x = random.randint(1,6)
	#y = random.randint(1,20)
	y = random.choice([4,6,8,10,12,20,100])
	z = random.randint(2,6)
	
	numname = ['zero','one','two','three','four','five','six']
	
	if y == 6 and debug == 0:
		r = DiceCode(x)
	else:
		r = random.randint(x,x*y)
		
	strPart = 'You roll %s %i-sided dice: %s.' % (numname[x],y,r)
	if r <= (x*y) / 3:
		strOpt1 = 'You drop your weapon, if you had one!'
	elif r >= (x*y) * 5/6:
		strOpt1 = 'You have soundly defeated your enemy!'
	else:
		strOpt1 = 'You have dealt %i damage to your enemy!' % (z)

	strUpdate = ' '.join([strPart,strOpt1])
	return strUpdate
	
def TryInteract(sTweet,debug=0):
	if 'roll ' in sTweet:
		strStatus = ReplyRoll(debug)
	elif 'attack' in sTweet or 'kill' in sTweet:
		strStatus = ReplyAttack(debug)
	elif 'quaff' in sTweet:
		strStatus = 'Successful Quaff!'
	elif 'where' in sTweet:
		strStatus = RoomGenerator.StatusMaker(debug=debug,force=19)
	elif 'what' in sTweet or 'who' in sTweet or "I " in sTweet:
		strStatus = RoomGenerator.StatusMaker(debug=debug,force=20,strIn=sTweet)
	else:
		strStatus = RoomGenerator.StatusMaker(debug=debug)
		
	return strStatus
				
def GetScore(statusObj, threshold=1000):
	banList = CheckBlackList()

	with open(BADWORDS, 'r') as fp:
		fbadWords = fp.readlines()
	
	badWords = []
	for i in fbadWords:
		badWords.append(i.strip())
		
	BugRelate = DictUserRelat()
	
	usrName = statusObj.user.screen_name
	tweet = statusObj.text.encode('utf8', errors='replace').lower()
	
	if BugRelate.has_key(usrName):
		lastTime = BugRelate[usrName][0]
		iFriendly = BugRelate[usrName][1]
	else:
		lastTime = 1
		iFriendly = 1
		
	currTime = time.time()
	
	if statusObj.user.description is not None:
		usrDesc = statusObj.user.description.encode('utf8',errors='replace')
	else:
		usrDesc = ""

	score = 0
	#dont play with assholes
	if any(x in tweet for x in badWords): score -= 100000; KillRelation(usrName)
	
	# very bad
	if " rape" in tweet: score -= 10000
	if "passed away" in tweet: score -= 1000
	if "died" in tweet: score -= 1000
	if "donate" in tweet: score -= 1000
	if "fuck you" in tweet: score -= 1000
	if "grumpy cat" in tweet: score -= 1000
	# bad
	if "gay" in tweet: score -= 500
	if "follow" in tweet: score -= 500
	if "piss" in tweet: score -= 500
	if "http:" in tweet: score -= 500
	if "illhueminati" in tweet: score -= 500
	# meh
	if "homework" in tweet: score -= 100
	if "teacher" in tweet: score -= 100
	if "twitter" in tweet: score -= 100
	if "instagram" in tweet: score -= 100
	if "sex" in tweet: score -= 100
	if currTime - float(lastTime) < (24*60*60): score -= int(((24*60*60)-(currTime - float(lastTime)))/100)
	# ok
	if "cloud" in tweet: score += 100
	if "sleep" in tweet: score += 100
	if "creep" in tweet: score += 100
	if "food" in tweet: score += 100
	if "potion" in tweet: score += 100
	if statusObj.favorited: score += 250
	if len(tweet) <= 4: score += 100
	if statusObj.user.followers_count < 200: score += 250
	# good
	if "vampire" in tweet: score += 500
	if "wizard" in tweet: score += 500
	if "favstar" in usrDesc: score += 500#; print usrName,"FAVSTAR"
	if statusObj.user.followers_count > 500: score += 500
	# very good
	if "dungeon" in tweet: score += 1000
	if "blood" in tweet: score += 1000
	if "piss wizard" in tweet: score += 1000
	if "neil patrick harris" in tweet or 'nph' in tweet: score += 1000
	if palindrome(tweet): score += 1000
	if statusObj.user.followers_count > 2000: score += 1000
	
	
	score += int(float(iFriendly))*10
	#return '%s | %i' % (tweet, score)
	return score

def palindrome(stringer):
	strLetters = [c for c in stringer.lower() if c.isalpha()]
	#print strLetters
	return (strLetters == strLetters[::-1])
	
def KillRelation(user):
	banList = CheckBlackList()
	
	if user not in banList:
		banList.append(user)
	
	with open(BANLIST, 'w') as fp:
		fp.write('\n'.join(['%s' % (i) for i in banList]))
	

def PostUpdateToTwitter(numOfTimes,sleepMin=0,sleepMax=10,debug=0):
	for count in range(numOfTimes):
		strStatus = RoomGenerator.StatusMaker(debug=debug)
		
		if debug == 1:
			print count, ": ", strStatus
			
		else:
			api.PostUpdate(strStatus)
			time.sleep(60*random.randint(sleepMin,sleepMax))
		
def PesterPost(numOfTimes,results=None,sleepMin=0,sleepMax=10,debug=0):
	k = 1												#counter - keep less than numOfTimes
	
	if len(results) == 0:
		sys.exit()
		
	statusDict = {}										#init dictionary of tweets
	
	for i in results:									#get score for each tweet
		statusDict[i] = GetScore(i)						#and add to dictionary of tweets

	#convert tweet dictionary to list sorted by score
	scoredStats = sorted(statusDict.iteritems(), key=lambda x:x[1], reverse=True)
	
	currTime = time.time()								#current time
	
	for each in scoredStats:
		BugRelate = DictUserRelat()							#get relations
		banList = CheckBlackList()							#get ban list
		alreadyReplied = CheckRepliedList()					#get list of tweet objects already replied to
		listReplied = ([long(i) for i in alreadyReplied])	#fix list of tweet objects already replied to (ids get read as strings but need to be numbers)
		
		statusObj = each[0]
		usrName = statusObj.user.screen_name
		sTweet = statusObj.text.encode('utf8', errors='ignore').lower()
		postTime = statusObj.created_at_in_seconds
		

		
		score = each[1]

		###NEW RELATIONSHIP CODE###
		if usrName in BugRelate:
			lastTime = BugRelate[usrName][0]
			RelationScore = int(BugRelate[usrName][1])
		else:
			BugRelate[usrName] = 5,5					#add them to the dictionary
			lastTime = BugRelate[usrName][0]			# get the last time i talked to them from dict (5)
			RelationScore = int(BugRelate[usrName][1])	# get their friendliness score (5)
			with open(ACCEPTLIST2, 'a') as fp:			#add them to text file of approved users
				fp.write(''.join(['%s|%s|%s\n' % (key, value[0],value[1]) for key, value in BugRelate.iteritems()]))
				
		if 'rt @_yourdm' in sTweet:
			RelationScore += 2												#reward retweeters
				
		CleanRelatDict(usrName,reTime=lastTime,reScore=RelationScore)		#update txt file with dictionary
		
		if (currTime - postTime < (24*60*60)								#dont reply to day old tweets
			and k <= numOfTimes												#control how many tweets to do per call
			and statusObj.id not in listReplied								#dont respond to same tweet over and over
			and (currTime - float(lastTime)) > (12*60*60)					#dont bug the same person every fucking second
			and usrName not in banList										#skip angry people
			and 'rt @_yourdm' not in sTweet									#skip RTs			
			and score >= 0):												#pick good tweets
						
			strStatus = TryInteract(sTweet,debug=debug)
			if usrName == 'DigimonOtis':
				strStatus = RoomGenerator.StatusMaker(debug=debug,force=13)	#Otis only gets pedantic tweets
			try:
				if debug == 1:
					#print '@%s %s' % (statusObj.user.screen_name, statusObj.text.encode('utf8', errors='ignore').lower())
					print strStatus
				else:
					lenCheck = 1
					while lenCheck == 1:
						if len('@%s %s') + len(strStatus) >= 141:
							strStatus = TryInteract(sTweet,debug=debug)
						else:
							lenCheck = 2
							
						api.PostUpdate('@%s %s' % (usrName, strStatus), in_reply_to_status_id=statusObj.id)
				
				k += 1
			except Exception:
				print "Unexpected error in PesterPost:", sys.exc_info()[0:2]
				
			if debug == 1:
				pass
			else:
				CleanRelatDict(usrName,reTime=currTime,reScore=RelationScore)
				CleanUpReplied(statusObj.id)
				time.sleep(60*random.randint(sleepMin,sleepMax))
		else:
			CleanRelatDict(usrName)
	#for each in scoredStats:
	#	if '_yourDM' not in each[0].user.screen_name:
	#		print each[0].text.encode('utf8', errors='replace'), 'score: ',each[1]


#################################################
# TWITTER TIMING SEARCH AND POST SHIT			#
#################################################
#debug mode, use 1
#should turn off waiting, twitter posting
#and text file updates
debug = 0

TweetAtFriendMinWait = 10
TweetAtFriendMaxWait = 20

TweetAtMentionMinWait = 2
TweetAtMentionMaxWait = 10

TweetPlainMinWait = 10
TweetPlainMaxWait = 20

try:	
	RepliesToMe = api.GetMentions()
	PesterPost(3,results=RepliesToMe,sleepMin=TweetAtMentionMinWait,sleepMax=TweetAtMentionMaxWait,debug = debug)
except Exception:
	pass
	
try:	
	MyTimeline = api.GetHomeTimeline(count=90)
	PesterPost(1,results=MyTimeline,sleepMin=TweetAtFriendMinWait,sleepMax=TweetAtFriendMaxWait,debug = debug)
except Exception:
	pass
	
try:
	PostUpdateToTwitter(1,sleepMin=TweetPlainMinWait,sleepMax=TweetPlainMaxWait,debug = debug)
except Exception:
	pass

try:
	PostUpdateToTwitter(1,sleepMin=TweetPlainMinWait,sleepMax=TweetPlainMaxWait,debug = debug)
except Exception:
	pass

