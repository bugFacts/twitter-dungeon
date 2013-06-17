from __future__ import unicode_literals
import twitter, os
import random
import linecache
import xlrd
import sys
import time
from string import maketrans  
import re

import unicodedata
#loadup dictionary 
wb = xlrd.open_workbook('mob2.xls')

shMobs = wb.sheet_by_name(u'mob list')
shAdjs = wb.sheet_by_name(u'adjective')
shAtak = wb.sheet_by_name(u'attacks')
shOoze = wb.sheet_by_name(u'OozeColors')
shDung = wb.sheet_by_name(u'dungeons')
shShop = wb.sheet_by_name(u'shops')
shKing = wb.sheet_by_name(u'kings')
shFREQ = wb.sheet_by_name(u'letFreq')
shCOMP = wb.sheet_by_name(u'testComp')
shBITS = wb.sheet_by_name(u'bits')
shBOOK = wb.sheet_by_name(u'booky')
shLOST = wb.sheet_by_name(u'lostEmpire')

def pick_random(prob_list):
	#takes a list of tuples, index followed by probability (out of one)
	#and returns the index or something
	r, s = random.random(), 0
	for num in prob_list:
		s += num[1]
		if s >= r:
			return num[0]
	print >> sys.stderr, "Error: what"
	
def PickAdjPhrase(numCol):
	strOut = ""
	if numCol == 0:	#if no adjectives needed break out
		#print "woah 0"
		pass
	else:			#pick columns randomly!#
		listColn = range(1, shAdjs.ncols+1)
		listAdjCol = random.sample(listColn,numCol)#dont pick same column twice
		#pick one adj from each selected column
		for k in sorted(listAdjCol):
			adj_list = filter(None, shAdjs.col_values(k-1,1))
			iAdj = random.randint(0,len(adj_list)-1)
			strAdj = adj_list[iAdj]
	#slam them into one adjective string
			strOut = strOut + " " + strAdj
	return strOut

def SimplePicker(sheet, column):
	#Pick a random element from the specified sheet and coloumn
	col_list = filter(None, sheet.col_values(column,1))
	strOut = col_list[random.randint(0,len(col_list)-1)]
	return strOut

def PickRandomMob():
	### MONSTER PICKER ###
	#pick monster category#
	iMobType = random.randint(0,shMobs.ncols-1)
	#pick monster#
	mob_list = filter(None, shMobs.col_values(iMobType,1))
	iMob = random.randint(0,len(mob_list)-1)
	strOut = mob_list[iMob]
	return strOut

def PickAnimalMob():
	strOut = SimplePicker(shMobs,0)
	return strOut
	
def PickSuperMob():
	strOut = SimplePicker(shMobs,1)
	return strOut
	
def PickHumanoidMob():
	strOut = SimplePicker(shMobs,2)
	return strOut
	
def VowConMatch(letterList,matchstr):
	#takes a composition template and returns a random string
	#matching that composition
	strVowels = "aeiouy"
	strConsos = "bcdfghjklmnpqrstvwxz"
	strLetterToMatch = str(pick_random(letterList)).lower()
	k = 1
	while k <= 1:
		if matchstr != 'v' and matchstr != 'c':
			strLetter = matchstr
			return strLetter
			k = 6
		elif strLetterToMatch in strVowels and matchstr == 'v':
			strLetter = strLetterToMatch
			return strLetter
			k = 6
		elif strLetterToMatch in strConsos and matchstr == 'c':
			strLetter = strLetterToMatch
			return strLetter
			k = 6
		else:
			strLetterToMatch = str(pick_random(letterList)).lower()
				
def buildRule( (pattern, search, replace) ): 
	#enables Pluralizer() and similar to apply a list of regular expressions
	#to a string via map()
    return lambda word: re.search(pattern, word, flags=re.I) and re.sub(search, replace, word, flags=re.I)
	
def Pluralizer(strIn):
	#pluralizes input string
	if strIn.lower() == 'brain in a jar':
		return 'brains in jars'
	
	strTail = ''.join([x for x in re.split(r'( of +)',strIn)[1:]])	#cut off tail of strings when they are like <thing> of <thing>
	strIn  = re.split(r'( of +)',strIn)[0]							#the first word <thing> of <thing> strings
	patterns = \
	(
	('folk$', '',''),					#folk	
	('(?<!h)ouse$','ouse$','ice'),		#mice and houses
	('(?<!hu)man(?!\w)',r'an\b','en'),	#men,women,mantises,humans
	('[\w\D]us$','us$','i'),			#octopi,cacti
	('[sxz]$', '$', 'es'),				#horcruxes, mantises
	('[^aeioudgkprt]h$', '$', 'es'),	#attaches
	('(qu|[^aeiou])y$', 'y$', 'ies'),	#harpies
	('[(?<=oo)(?<=f)]f$', '$','s'),		#roofs,hoofs
	('[\w\D]f$','f$', 'ves'),			#elves, dwarves
	('$', '$', 's'),					#everything else??
	)
	ruleList = map(buildRule, patterns)
	for rule in ruleList:
		strOut = rule(strIn)
		if strOut: return strOut + strTail
	
def Verber(strIn):
	#turns a verb into a verber
	#for use in flavor names
	#like walrusstabber or orclicker
	
	strTail = ''.join([x for x in re.split(r'( +)',strIn)[1:]])	#cut off tail of strings when they are like <verb> at
	strIn = re.split(r'( +)',strIn)[0]						#the first word <verb> at strings
	
	patterns = \
	(
	(r'[ie]t$','$','ter'),
	(r'[ie]p$','$','per'),
	(r'[s|p]t$|[p|s]p$', '$','er'),	
	(r't$|p$|b$', '$', 'er'),
	(r'e$', '$', 'r'),
	(r'h$','$','er'),
	('$', '$', 'er'),					#everything else??
	)
	ruleList = map(buildRule, patterns)
	for rule in ruleList:
		strOut = rule(strIn)
		if strOut: return strOut + strTail

#################################################
# adds a random diacritical mark to each letter #
# depending on probability						#
# WILL RETURN ERRORS IF YOU TRY TO PRINT THIS 	#
# STRING TO SCREEN TERMINAL. FUCK				#
#################################################
def FlavorLetter(oNam, prob=0.1):
		#print oNam
		flavNam = ""
		possComb = [u'\u0300',u'\u0301',u'\u0302',u'\u0303',u'\u0308',u'\u0311',u'\u0327']
		for l in oNam:
			newLet = l
			if not re.search("[_\d\W]",l) and random.random() < prob:
				#fuck with letter
				try:
					conMark = l+random.choice(possComb)
					newLet = unicodedata.normalize("NFKC",unicode(conMark))
					#print newLet, ",len= ",len(newLet)
					
					#windows console cant print this shit 
					# but if above line uncommented it can
					#for some fucking reason ????
					unicodedata.normalize("NFKC",unicode(conMark))
					
				except Exception:
					newLet = l
					#pass

			flavNam=''.join([flavNam,unicode(newLet)])

		return flavNam
		
def RandomProperNoun():
	#Creates a random name
	shFREQ = wb.sheet_by_name(u'letFreq')
	shCOMP = wb.sheet_by_name(u'testComp')

	list1 = []
	alfa = filter(None, shFREQ.col_values(0,1))
	for i in range(1,shFREQ.ncols):
		col_list = filter(None, shFREQ.col_values(i,1))

		for j in range(1,len(col_list)+1):
			#print shFREQ.cell_value(j,i)
			list1.append((alfa[j-1],shFREQ.cell_value(j,i)))

	######GET GENDER TAG#####
	iType = random.randint(0,2)	

	######GENERATE DISTRIBUTION LISTS#####
	distFirs = []
	for i in range(26*(iType+4),26*(iType+5)):
		#print list1[0+i]
		distFirs.append((list1[0+i]))
		
	distLets = []
	for i in range((26*iType),26*(iType+1)):
		#print list1[0+i]
		distLets.append((list1[0+i]))

	######GET FIRST LETTER#####
	comp_list = filter(None, shCOMP.col_values(iType,1))
	iComp = random.randint(0,len(comp_list)-1)
	strForm = comp_list[iComp].lower()

	strVowels = "aeiouy"
	strConsos = "bcdfghjklmnpqrstvwxz"

	strFirstLetter = VowConMatch(distLets,strForm[0])

	strOut = ''
	for let in range(1, len(strForm)):
		strNewLet = VowConMatch(distLets,strForm[let])
		strOut = strOut+strNewLet

	strOut = strFirstLetter + strOut	

	#print strForm.upper()

	return strOut.title()
	
def FlavorfulProperNoun():
	strVerb = SimplePicker(shAtak,0)[:-1].lower()
	
	strVerber = Verber(strVerb)
	
	iMobType = random.randint(0,1)
	strRanMob = SimplePicker(shMobs, iMobType)
	k = 1
	while k==1:
		if ' ' in strRanMob.strip():
			strRanMob = SimplePicker(shMobs, iMobType)
		else:
			k = 2
	#strFullName = strHroNam.title() + ' ' + strRanMob.title() +'-' + strAttack.lower()
	strOut = strRanMob.title() +'-' + strVerber.lower()
	return strOut
	
def ExitString():
	#random string of exit letters
	exit_tuples = [(1,'N'),(2,'E'),(3,'S'),(4,'W')]
	exit_list = random.sample(exit_tuples,random.randint(0,4))
	strOut = ','.join([item[1] for item in sorted(exit_list)])
	return strOut
	
def DoWeAddPhrase(strIn, strAdd, prob):
	#can we add the two given strings
	#also maybe we dont even if we can
	if (random.random() < prob) and (len(strIn) + len(strAdd)) < 140:
		strOut = strIn + strAdd
		return strOut
	else:
		return strIn
		
def AnAFixer(strIn):
	strVowel = 'aeiouAEIOU'
	
	k = 1
	while k == 1:
		if strIn.strip() != "":
			if strIn.lower().strip() == 'belly of the beast' or 'yggdrasil' in strIn.lower():
				strOut = 'The %s' % (strIn.strip())
				k = 2
			if strIn[0].strip() in strVowel:
				strOut = 'An %s' % (strIn.strip())
				k =2 
			else:
				strOut = 'A %s' % (strIn.strip())
				k =2
		else:
			#print 'errpr'
			strOut = 'A %s' % (strIn.strip())
			k = 2
		
	return strOut.title()
	
def RollDice(numDice,sizeDice):
	diceTotal = 0
	k = 0
	while k < numDice:
		diceroll = random.randint(1,sizeDice)
		diceTotal = diceTotal + diceroll
		k = k + 1
	return diceTotal

############################################################
############################################################
##														  ##
##														  ##
##					STATUS GENERATORS					  ##
##														  ##
##														  ##
############################################################
############################################################	

def Status01(debug=0):	### Attacks
	#2 
	#A [mob_desc] [mob] arrives! 
	#{1} It [attack verbs] you for [# 3d12] damage! 
	#{2} It hasn't noticed you. 
	#{3} It [attack verbs] your [body_part] for [# 3d12] damage! 
	#{4} [nothing]
	sRanMob = PickRandomMob()
	
	sAttacks = SimplePicker(shAtak,0).strip()
	sStatus = SimplePicker(shAtak,1).strip()
	sClass = SimplePicker(shAtak,2).strip()
	sBodyPt = SimplePicker(shAtak,3).strip()
	sDefeat = SimplePicker(shAtak,4).strip()
	sDefeating = SimplePicker(shAtak,5).strip()
	sDefeated = SimplePicker(shAtak,6).strip()
	sAbilty = SimplePicker(shAtak,7).strip()
	
	sUArriveAt = SimplePicker(shDung,0).strip()
	sDungeon = SimplePicker(shDung,1).strip()
	sItIs = SimplePicker(shDung,2).strip()
	sHeroItem = SimplePicker(shDung,3).strip()
	sItArrivesAt = SimplePicker(shDung,4).strip()
	sItAppears = SimplePicker(shDung,5).strip()
	
	arrNumOfAdjProb = [[0,.12],[1,.8],[2,.08]]#decide on number of adjectives 1 most common, 0 , 2 , 3
	sMobAdj = PickAdjPhrase(pick_random(arrNumOfAdjProb))
	
	if random.randint(0,1) == 1:
		strLfOrRt = 'right'
	else:
		strLfOrRt = 'left'
	
	strAdjAndMob = sMobAdj + ' ' + sRanMob
	
	strStart = '%s %s.' % (AnAFixer(strAdjAndMob[1:]).title().strip(), sItAppears)
		
	strOpt1 = ' It %s you for %i damage!' % (sAttacks,RollDice(2,12))
	strOpt2 = ' It hasn\'t noticed you.'
	strOpt3 = ' It %s your %s %s for %i damage!' % (sAttacks, strLfOrRt, sBodyPt, RollDice(2,12))
	strOpt4 = ''

	optID = [[0,.5],[1,.08],[2,.3],[3,.12]]
	iChoice = pick_random(optID)

	if iChoice == 0:
		strStart = DoWeAddPhrase(strStart, strOpt1, 1)
	elif iChoice == 1:
		strStart = DoWeAddPhrase(strStart, strOpt2, 1)
	elif iChoice == 2:
		strStart = DoWeAddPhrase(strStart, strOpt3, 1)
	elif iChoice == 3:
		strStart = DoWeAddPhrase(strStart, strOpt4, 1)
	else:
		strStart = 'thers been an error'

	return strStart
	
def Status02(debug=0):	#### AREA DESC LONG 
	sRanMob = PickRandomMob().strip()
	sAniMob = PickAnimalMob().strip()
	sSupMob = PickSuperMob().strip()
	sHumMob = PickHumanoidMob().strip()
	
	sUArriveAt = SimplePicker(shDung,0).strip()
	sDungeon = SimplePicker(shDung,1).strip()
	sItIs = SimplePicker(shDung,2).strip()
	sHeroItem = SimplePicker(shDung,3).strip()
	sItArrivesAt = SimplePicker(shDung,4).strip()
	sItAppears = SimplePicker(shDung,5).strip()
	
	sExits = ExitString()
	
	sPropNoun1 = RandomProperNoun()
	if debug == 0:
		sPropNoun1 = FlavorLetter(sPropNoun1)

	strOut1 = 'You %s %s' % (sUArriveAt,AnAFixer(sDungeon))
	iChoice = random.randint(0,13)
	if iChoice <= 10:	#regular dungeon descrip
		sApp = '. It is %s.' % (sItIs)
	elif iChoice == 11:	#old year
		sApp = ' in the year %i BC.' % (random.randint(0,3000)) 
	elif iChoice == 12:	#new year
		sApp = ' in the year %i.' % (random.randint(0,3000))	
	elif iChoice == 13:	#day and month
		sApp = ' on day %i in the month of %s.' % (random.randint(1,31),sPropNoun1)

	strOut = strOut1 + sApp
	strOpt2 = ' You have %s.' % (sHeroItem)
	strOpt3 = ' There are %s here!' % (Pluralizer(sRanMob))
	
	if len(sExits) >= 2:
		strOpt4 = ' There are exits to the %s and %s.' % (sExits[:len(sExits)-1],sExits[len(sExits)-1:])
	elif len(sExits) != 0:
		strOpt4 = ' There are exits to the %s.' % (sExits)
	else:
		strOpt4 = ""

	strOut = DoWeAddPhrase(strOut, strOpt2, .8)
	strOut = DoWeAddPhrase(strOut, strOpt3, .6)
	strOut = DoWeAddPhrase(strOut, strOpt4, .4)
	
	return strOut
	
def Status03(debug=0):	#AREA DESC SHORT
	sUArriveAt = SimplePicker(shDung,0).strip()
	sDungeon = SimplePicker(shDung,1).strip()
	sItIs = SimplePicker(shDung,2).strip()
	sHeroItem = SimplePicker(shDung,3).strip()
	sShopItem = SimplePicker(shShop,1).strip()
	
	sRanMob = PickRandomMob()
	
	sThereAR = SimplePicker(shDung,6).strip()
	
	k = random.randint(0,3)
	if k <= 2:
		sThereIS = SimplePicker(shDung,7).strip()
	else:
		sThereIS = AnAFixer(sRanMob)
	
	iChoice = random.randint(0,5)
	if iChoice == 0:
		strOut = 'You %s %s.' % (sUArriveAt,AnAFixer(sDungeon))
	elif iChoice == 1:
		strOut = 'You are in %s.' % (AnAFixer(sDungeon))
	elif iChoice == 2:
		strOut = 'It is %s.' % (sItIs)
	elif iChoice == 3:
		strOut = 'You have %s.' % (sHeroItem)
	elif iChoice == 4:
		strOut = 'It is the year %i BC.' % (random.randint(0,3000))
	elif iChoice == 5:
		strOut = 'It is the year %i.' % (random.randint(0,3000))
	#elif iChoice == 4:
	#	strOut = 'There is %s here.' % (sHeroItem)	
	#elif iChoice == 7:
	#	strOut = 'There are %s here.' % (sShopItem)
	
	strOpt1 = ' There are %s here.' % (sThereAR)
	strOpt2 = ' There is %s here.' % (sThereIS)
	
	iChoice2 = random.randint(0,1)
	if iChoice2 == 0:
		strOut = DoWeAddPhrase(strOut, strOpt1, .7)
	else:
		strOut = DoWeAddPhrase(strOut, strOpt2, .7)
	
	return strOut

def TavernMaker():
	sObject1 = SimplePicker(shShop,6).strip().title()	#cup
	sObject2 = SimplePicker(shShop,6).strip().title()	#sword
	sSaloon = SimplePicker(shShop,7).strip().title()
	
	sTitles = SimplePicker(shKing,0).title()			#king's
	sHumDesc1 = SimplePicker(shKing,3).title()			#anxious
	
	iMobType = random.randint(0,1)
	mob_list = filter(None, shMobs.col_values(iMobType,1))
	allit_list = []
	for i in mob_list:
		if i[0] == sHumDesc1[0]:
			allit_list.append(i)	#gets list of all alliterive mobs
	if len(allit_list) == 1:
		strRanMob = allit_list[0]
	elif len(allit_list) == 0:
		strRanMob = 'len(alliterive_list) = 0'
	else:
		strRanMob = allit_list[random.randint(0,len(allit_list)-1)].title()
		
	optTavern = []
	
	optTavern.append(DoWeAddPhrase('The %s and %s ' % (sObject1, sObject2), sSaloon, .5))
	optTavern.append(DoWeAddPhrase('The %s %s ' % (sHumDesc1, sObject1), sSaloon, .8))
	optTavern.append(DoWeAddPhrase('The %s %s ' % (sHumDesc1, strRanMob), sSaloon, .3))
	optTavern.append("The %s %s's %s" % (sHumDesc1, sTitles, sSaloon))
	optTavern.append("The %s of %ss"  % (sSaloon, sObject1))
	optTavern.append("The %s of the %s" % (sSaloon, sObject1))
	optTavern.append("The %s of the %s %s" % (sSaloon, sHumDesc1, sObject1))
	
	return random.choice(optTavern)
	
def Status04(debug=0):	### SHOP ADS
	#2 
	#The [color].title() [mob_animal].title() is selling 
		#{1}[adj]
		#{2}[color]
		#{3}[material]
		#[item]s for [# 1-5000] gold pieces!.
		
	sMaterial = SimplePicker(shShop,0).strip()#
	sShopItem = SimplePicker(shShop,1).strip()#
	sColors = SimplePicker(shShop,2).strip()#
	
	
	arrNumOfAdjProb = [[0,.12],[1,.8],[2,.08]]#decide on number of adjectives 1 most common, 0 , 2 , 3
	sMobAdj = PickAdjPhrase(pick_random(arrNumOfAdjProb))#
	
	
	x = random.randint(0,2)
	if x == 0:
		strStart = '%s is having a sale on' % (TavernMaker().strip())
	elif x == 1:
		strStart = 'Well *I* heard that %s is the best place to get' % (TavernMaker().strip())
	elif x == 2:
		strStart = "If I were you, I'd avoid %s altogether. I mean, they were selling" % (TavernMaker().strip())
	
	strOpt1 = ' ' + sMobAdj.lower().strip()
	strOpt2 = ' ' + sColors.lower().strip()
	strOpt3 = ' ' + sMaterial.lower().strip()
	
	strEnd = ' %s for %i gold pieces! Each!' % (sShopItem.lower(), random.randint(1,5000))

	optID = [[1,.18],[2,.22],[3,.6]]
	
	iChoice = pick_random(optID)
	
	if iChoice == 1:
		strStart = DoWeAddPhrase(strStart, strOpt1, 1)
	elif iChoice == 2:
		strStart = DoWeAddPhrase(strStart, strOpt2, 1)
	elif iChoice == 3:
		strStart = DoWeAddPhrase(strStart, strOpt3, 1)
		
	strUpdate = strStart + strEnd
	
	return strUpdate
	
def Status05(debug=0): ### DOUBTFUL SHOP
	#2 
	#The [color].title() [mob_animal].title() is selling 
		#{1}[adj]
		#{2}[color]
		#{3}[material]
		#[item]s for [# 1-5000] gold pieces!.
		
	sMaterial = SimplePicker(shShop,0).encode('utf8',errors='replace').strip()
	sShopItem = SimplePicker(shShop,1).encode('utf8',errors='replace').strip()
	sColors = SimplePicker(shShop,2).encode('utf8',errors='replace').strip()
	sEffect = SimplePicker(shShop,3).encode('utf8',errors='replace').strip()
	sDoubts = SimplePicker(shShop,4).encode('utf8',errors='ignore').strip()
	sButs = SimplePicker(shShop,5).encode('utf8',errors='replace').strip()
	
	sHumDesc1 = SimplePicker(shKing,3)
	
	m = 1
	while m == 1:
		if 'water' in sDoubts or 'risly' in sDoubts:
			sDoubts = SimplePicker(shShop,4).encode('utf8',errors='ignore').strip()
		elif 'are' in sDoubts:
			sDoubts = sDoubts.replace('are','is')
		elif "don't" in sDoubts:
			sDoubts = sDoubts.replace("don't","doesn't")
		elif 'do not' in sDoubts:
			sDoubts = sDoubts.replace('do not','does not')
		elif 'have' in sDoubts and 'to have' not in sDoubts:
			sDoubts = sDoubts.replace('have', 'has')
		elif 'to has' in sDoubts:
			sDoubts = sDoubts.replace('to has','to have')
		else:
			m = 2			
	
	arrNumOfAdjProb = [[0,.12],[1,.8],[2,.08]]#decide on number of adjectives 1 most common, 0 , 2 , 3
	sMobAdj = PickAdjPhrase(pick_random(arrNumOfAdjProb))
	#pick monster#
	iMobType = random.randint(0,1)
	mob_list = filter(None, shMobs.col_values(iMobType,1))
	allit_list = []
	
	for i in mob_list:
		if i[0] == sHumDesc1[0] and ' ' not in i:
			allit_list.append(i)	
	if len(allit_list) == 1:
		strRanMob = allit_list[0]
	elif len(allit_list) == 0:
		strRanMob = 'len(alliterive_list) = 0'
	else:
		strRanMob = allit_list[random.randint(0,len(allit_list)-1)]
		
		
	#print sHumDesc1
	#print strRanMob
	#print sDoubts
	#print sShopItem
	#k = random.randint(0,1)
	#if k == 0:
		#strOut = "The %s %s %s have %s in stock." % (sHumDesc1.title(), strRanMob.title(), sDoubts, sShopItem.lower())
	#elif k == 1:
		#strOut = "The %s %s %s have %s in stock, but %s." % (sHumDesc1.title(), strRanMob.title(), sDoubts, sShopItem.lower(),sButs)
		
	#elif k == 2:
	#	strOut = "The %s %s %s has been the best place to get %s, but %s." % (sHumDesc1.title(), strRanMob.title(), sDoubts, sShopItem.lower(), sButs)
	
	strOut = DoWeAddPhrase("%s %s have %s in stock" % (TavernMaker().strip(), sDoubts, sShopItem.lower()), ", but " + sButs, 0.5) + "."
	
	return strOut
	
def Status06(debug=0): ### POTIONS
#depe
	pass
	
def Status07(debug=0):### YOU POTIONS
	
	sAdj1 = random.choice([SimplePicker(shShop,2).strip(),SimplePicker(shShop,8).strip()])
	sAdj2 = random.choice([SimplePicker(shShop,2).strip(),SimplePicker(shShop,8).strip()])
	if sAdj2 == sAdj1:
		sAdj2 = random.choice([SimplePicker(shShop,2).strip(),SimplePicker(shShop,8).strip()])
	else:
		k = 2
			
	sAdj3 = random.choice([SimplePicker(shShop,2).strip(),SimplePicker(shShop,8).strip()])
	k = 1
	while k == 1:
		if sAdj3 == sAdj1 or sAdj3 == sAdj2:
			sAdj3 = random.choice([SimplePicker(shShop,2).strip(),SimplePicker(shShop,8).strip()])
		else:
			k = 2
			
	sAdj4 = random.choice([SimplePicker(shShop,2).strip(),SimplePicker(shShop,8).strip()])
	k = 1
	while k == 1:
		if sAdj4 == sAdj1 or sAdj4 == sAdj2 or sAdj4 == sAdj3:
			sAdj4 = random.choice([SimplePicker(shShop,2).strip(),SimplePicker(shShop,8).strip()])
		else:
			k = 2
			
	sLiquid1 = SimplePicker(shShop,9).strip()
	sLiquid2 = SimplePicker(shShop,9).strip()
	
	sTaste1 = SimplePicker(shShop,10).strip()
	sTaste2 = SimplePicker(shShop,10).strip()
	k = 1
	while k == 1:
		if sTaste2 == sTaste1:
			sTaste2 = SimplePicker(shShop,8).strip()
		else:
			k = 2
	sTaste3 = SimplePicker(shShop,10).strip()
	k = 1
	while k == 1:
		if sTaste3 == sTaste1 or sTaste3 == sTaste2:
			sTaste3 = SimplePicker(shShop,8).strip()
		else:
			k = 2
	sTaste4 = SimplePicker(shShop,10).strip()
	k = 1
	while k == 1:
		if sTaste4 == sTaste1 or sTaste4 == sTaste2 or sTaste4 == sTaste3:
			sTaste4 = SimplePicker(shShop,8).strip()
		else:
			k = 2
	
	sPie = SimplePicker(shShop,11).strip()
	
	sColors = SimplePicker(shShop,2).strip()
	
	sEffect1 = SimplePicker(shShop,3).strip()
	sEffect2 = SimplePicker(shShop,3).strip()
	sDoubts = SimplePicker(shShop,4).encode('utf8',errors='replace')

	sButs = SimplePicker(shShop,5).strip().encode('utf8',errors='replace')
	
	#####################################################
	sAdjOpt = [	sAdj1,
				sAdj1 + " and " + sAdj2,
				sAdj1 + ", " + sAdj2 + " and " + sAdj3]
	sPotion1 = (random.choice(sAdjOpt) + " " + sLiquid1).strip()
	sPotion2 = (random.choice(sAdjOpt) + " " + sLiquid2).strip()
	#####################################################			
	sPieces = "with %s %s" % (sAdj4, sPie)
	#####################################################
	sCanCause = "%s %s %s" % (sDoubts, random.choice(["grant","cause"]), sEffect1)
	#####################################################
	sFlav1 = DoWeAddPhrase(sTaste1, " and " + sTaste2, .4)
	sFlav2 = DoWeAddPhrase(sTaste3, " and " + sTaste4, .4)
	sSmellTaste = random.choice(["smells like %s." % (sFlav1),
									"smells and tastes like %s." % (sFlav1),
									"smells like %s but tastes like %s." % (sFlav1, sFlav2)])
	#####################################################
	
	sPotionPhrase1 = DoWeAddPhrase("This %s" % sPotion, " (" + sPieces + ")",.3) + " " + sSmellTaste
	sPotionPhrase2 = DoWeAddPhrase("%ss" % sPotion.title(), " (" + sPieces + ")",.3) + " " + sCanCause + "."
	
	sPotionA = "Be sure to avoid %ss%s, though!" % (sPotion.strip(), DoWeAddPhrase("", " (" + sPieces + ")", .2))
	sPotionB = "Those %s %s!" % (sCanCause, sEffect2)
	
	sPotion3 = "If you need to cure %s, quaff a %s%s." % (sEffect1,sPotion,DoWeAddPhrase(""," (" + sPieces + ")",.3)) + DoWeAddPhrase(" ", DoWeAddPhrase(sPotionA, sPotionB, .2),.2)
	
	sPotion4 = "If you want to gain %s, quaff a %s%s." % (sEffect1,sPotion,DoWeAddPhrase(""," (" + sPieces + ")",.3)) + DoWeAddPhrase(" ", DoWeAddPhrase(sPotionA, sPotionB, .2),.2)
	
	sPotion5 = "Afflicted by %s? Quaff a %s%s." % (sEffect1,sPotion,DoWeAddPhrase(""," (" + sPieces + ")",.3)) + DoWeAddPhrase(" ", sPotionA, .2)
	sPotion6 = "Wishing you had %s? Try a %s%s." % (sEffect1,sPotion,DoWeAddPhrase(""," (" + sPieces + ")",.3)) + DoWeAddPhrase(" ", sPotionA, .2)
	return random.choice([sPotionPhrase1,sPotionPhrase1,sPotionPhrase1,
							sPotionPhrase2,sPotionPhrase2,sPotionPhrase2,
							sPotion3,
							sPotion4,
							sPotion5,
							sPotion6])
	
	
def Status08(debug=0): ##### KING REPORT
		#6 
	#[hero name], the [adj][title] of [place name] has [king_action]
	sDefeated = SimplePicker(shAtak,6).strip()
	
	sRanMob = PickRandomMob()
	
	sTitle = SimplePicker(shKing,0)
	#gender tuple stuffs
	sKingDoes = SimplePicker(shKing,2)
	sHumDesc1 = SimplePicker(shKing,3)
	sHumDesc2 = SimplePicker(shKing,3)
	sHumDesc3 = SimplePicker(shKing,3)
	
	sPropNoun1 = RandomProperNoun()
	sPropNoun2 = RandomProperNoun()
	sPropNoun3 = RandomProperNoun()
	
	if debug == 0:
		sPropNoun1 = FlavorLetter(sPropNoun1)
		sPropNoun2 = FlavorLetter(sPropNoun2)
		sPropNoun3 = FlavorLetter(sPropNoun3)
		
	sFlavNoun = FlavorfulProperNoun()

	strFullName = sPropNoun1.title() + ' ' + sFlavNoun.title()
	
	k = random.randint(0,1)
	if k == 0:
		strStart = '%s, the %s and %s %s of %s, has %s!' % (strFullName.title(), sHumDesc1.lower(), sHumDesc2.lower(), sTitle.title(), sPropNoun2.title(), sKingDoes)
	elif k == 1:
		strStart = 'Poor %s, %s by a %s %s!' % (sPropNoun1.title(), sDefeated.lower(), sHumDesc1.lower(), sRanMob.title())
		
	return strStart
	
def Status09(debug=0):##### YOU KING
			#6 
	#[hero name], the [adj][title] of [place name] has [king_action]
	sTitle = SimplePicker(shKing,0)
	#gender tuple stuffs
	sKingDoes = SimplePicker(shKing,2)
	sHumDesc1 = SimplePicker(shKing,3)
	sHumDesc2 = SimplePicker(shKing,3)
	sHumDesc3 = SimplePicker(shKing,3)
	
	sRelation = SimplePicker(shKing,4)
		
	sPropNoun1 = RandomProperNoun()
	sPropNoun2 = RandomProperNoun()
	sPropNoun3 = RandomProperNoun()
	
	if debug == 0:
		sPropNoun1 = FlavorLetter(sPropNoun1)
		sPropNoun2 = FlavorLetter(sPropNoun2)
		sPropNoun3 = FlavorLetter(sPropNoun3)
		
	sFlavNoun = FlavorfulProperNoun()
	
	sHumMob1 = PickHumanoidMob()
	sHumMob2 = PickHumanoidMob()

	strFullName = sPropNoun1.title() + ' ' + sFlavNoun.title()
	
	sHeroItem = SimplePicker(shDung,3).strip()
	
	sDefeater = Verber(SimplePicker(shAtak,4).strip())
	
	sDungeon = SimplePicker(shDung,1).strip()
	
	x = random.randint(0,10)
	if x <= 7:
		strStart = 'You are reborn as %s, the %s and %s %s of the land of %s!' % (strFullName.title(), sHumDesc1.lower(), sHumDesc2.lower(), sTitle.title(), sPropNoun2.title())
	elif x == 8:
		strStart = 'You are %s %s, the %s %s of %s %s and %s %s.' % (sTitle.title(), sPropNoun1.title(), sHumDesc1.lower(), sRelation, AnAFixer(sHumDesc2).lower(), sHumMob1.title(), AnAFixer(sHumDesc3).lower(), sHumMob2.title())
	elif x == 9:
		strStart = 'You are %s, %s of %s! You have %s!' % (sPropNoun1.title(), sRelation, sPropNoun2.title(), sHeroItem)
	elif x == 10:
		strStart = "Oh my God! Tell me you're not %s, %s of the %s %s!" % (strFullName, sDefeater.lower(), sHumDesc1.title(), sDungeon.title())
	return strStart
	
def Status10(debug=0): ##### STATUSED BY A WIZARD
	#3 
	#You have been [statused] by [name], a level [# 1-99] [mob_humanoid] [spell caster]!

	sPropNoun1 = RandomProperNoun()
	sHumMob = PickHumanoidMob()
	
	sStatus = SimplePicker(shAtak,1).strip()
	sClass = SimplePicker(shAtak,2).strip()
	sBodyPt = SimplePicker(shAtak,3).strip()
	
	sColors = SimplePicker(shShop,2).strip()

	
	if random.randint(0,1) == 1:
		strLfOrRt = 'right'
	else:
		strLfOrRt = 'left'
		
	optID = [[0,.22],[1,.21],[2,.18],[3,.14],[4,.13],[5,.12]]
	iChoice = pick_random(optID)
	
	if iChoice == 0:
		strOut = 'You have been %s by %s, a level %i %s %s!' % (sStatus,sPropNoun1,random.randint(1,99),sHumMob,sClass)
	elif iChoice == 1:
		strOut = 'Your %s %s has been %s by %s, a level %i %s %s!' % (strLfOrRt,sBodyPt,sStatus,sPropNoun1,random.randint(1,99),sHumMob,sClass)
	elif iChoice == 2:
		strOut = 'You have been %s by a level %i %s %s!' % (sStatus,random.randint(1,99),sHumMob,sClass)
	elif iChoice == 3:
		strOut = 'You have been %s by %s. Is this awesome? y/n' % (sStatus, AnAFixer(sClass))
	elif iChoice == 4:
		strOut = 'You have been %s by %s potion.' % (sStatus, AnAFixer(sColors))
	elif iChoice == 5:
		strOut = 'Your %s %s has been %s by %s potion.' % (strLfOrRt,sBodyPt,sStatus,AnAFixer(sColors))
	return strOut
	
def Status11(debug=0): ##### Your race

	sAttacks = SimplePicker(shAtak,0).strip()
	
	k = 0
	while k == 0:
		if ' at' in sAttacks:
			sAttacks = SimplePicker(shAtak,0).strip()
		else:
			k = 1
			
	sAttacks = sAttacks[:-1].lower()
	if sAttacks[-2:] == 'he':
		sAttacks = sAttacks[:-1]
	
	strOut = "Your race/class combination does not have access to %s attacks without the aid of potions." % (sAttacks.title())
	
	return strOut
	
def Status12(debug=0): #### Bits and Pieces
	
	sBits = SimplePicker(shBITS,0).strip()
	
	strOut = sBits
	
	return strOut
	
def Status13(debug=0): #### Goofy Book Review shit
	strOut = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	while len(strOut) >= 140:
		sNoun1 = SimplePicker(shBOOK,0).strip().encode('utf8',errors='replace') #idea of
		sNoun2 = SimplePicker(shBOOK,0).strip().encode('utf8',errors='replace') #reading of
			
		sMody1 = SimplePicker(shBOOK,1).strip().encode('utf8',errors='replace') #civil society
		sMody2 = SimplePicker(shBOOK,1).strip().encode('utf8',errors='replace') #the image
		
		sVerb = SimplePicker(shBOOK,2).strip().encode('utf8',errors='replace') 	#highlights
		sBook = SimplePicker(shBOOK,3).strip().encode('utf8',errors='replace') 	#informal sketch of
		sRevw = SimplePicker(shBOOK,4).strip().encode('utf8',errors='replace') 	#is important
		
		sPropNoun1 = RandomProperNoun()
		
		x = random.randint(0,10)
		if x == 0:
			#strOut = "The " + sNoun1 + " " + sMody1 + " " + sVerb + " " + "the " + sNoun2 + " " + sMody2 + "."
			strOut = "The %s %s %s the %s %s." % (sNoun1,sMody1,sVerb,sNoun2,sMody2)
		elif x == 1:
			#strOut = "Your " + sBook + " the relationship between the " + sNoun1 + " " + sMody1 + " and the " + sNoun2 + " " + sMody2 + " " + sRevw + "."
			strOut = "Your %s the interplay between the %s %s and the %s %s %s." % (sBook,sNoun1,sMody1, sNoun2,sMody2, sRevw)
		elif x == 2:
			strOut = "%s\'s %s the %s %s and the %s %s %s." % (sPropNoun1,sBook,sNoun1,sMody1, sNoun2,sMody2, sRevw)
		elif x >= 3:
			strOut = "Your %s the %s %s and the %s %s %s." % (sBook,sNoun1,sMody1, sNoun2,sMody2, sRevw)
		
	return strOut
	
def Status14(debug=0):		### GIBBERISH
	numWords = random.randint(3,14)
	strStart = ""
	for i in range(numWords):
		each = RandomProperNoun()
		if debug == 0:
			each = FlavorLetter(each)
		strStart = DoWeAddPhrase(strStart, each, 1)
		strStart += " "
	
	if random.random() <= 0.001:
		strStart = ""
		for i in range(numWords):
			each = random.choice(['yolo','swag','lol'])
			if debug == 0:
				each = FlavorLetter(each,prob=.8)
			strStart = DoWeAddPhrase(strStart, each, 1)
			strStart += " "
			
	strOut = ''
	optID = [[0,.400],[1,.150],[2,.140],[3,.130],[4,.100],[5,.050],[6,.020],[7,.010]]
	punctOpt = [' ',
				', ',
				'. ',
				'? ',
				'! ',
				'?! ',
				'!! ',
				': ']

	for word in strStart.lower().split():
		iChoice = pick_random(optID)
		if strOut != '':
			if any(x in ['.','?','!'] for x in punctOpt[iChoice]):				#if puct is a sentence ender
				strOut = punctOpt[iChoice].join([strOut, word.capitalize()])	#combine and cpitalize the new word
			else:
				strOut = punctOpt[iChoice].join([strOut, word])
		else:
			strOut = word.capitalize()
	
	
	punc = punctOpt[pick_random(optID)] #pick ending punctuation
	k = 0
	while k < 1:
		if any(x in ['.','?','!'] for x in punc):
			k = 2
		else:
			punc = punctOpt[pick_random(optID)]
			
	#print len(strOut + punc)
	return strOut + punc
	
def Status15(debug=0):		### GIBBERISH
	sPlace = RandomProperNoun()
	
	sTrait = SimplePicker(shLOST,0).strip()
	sBiome = SimplePicker(shLOST,1).strip()
	sGovrn = SimplePicker(shLOST,2).strip()
	
	sKnown = SimplePicker(shLOST,3).strip()
	sAchev = SimplePicker(shLOST,4).strip()
	sTechs = SimplePicker(shLOST,5).strip()
	sDisas = SimplePicker(shLOST,6).strip()
	
	sBadT1 = SimplePicker(shLOST,7).strip()
	sBadT2 = SimplePicker(shLOST,7).strip()
	
	sFlaws = SimplePicker(shLOST,8).strip()
	
	sRuin1 = SimplePicker(shLOST,9).strip()
	sRuin2 = SimplePicker(shLOST,9).strip()
	k = 1
	while k == 1:
		if sRuin1 == sRuin2:
			sRuin2 = SimplePicker(shLOST,9).strip()
		else:
			k = 2
	
	sDesc = random.choice([sTrait,sBadT1])
	
	if debug == 0:
		sPlace = FlavorLetter(sPlace)
	

	sAdjPhrase = ""
	sAdjPhrase = DoWeAddPhrase(sAdjPhrase, " " + sDesc, 0.5)
	sAdjPhrase = DoWeAddPhrase(sAdjPhrase, " " + sBiome, 0.5)
	

	if random.choice([0,1]) == 0:
		sCivilization = AnAFixer((sAdjPhrase + " " + sGovrn).strip())
	else:
		sCivilization = "The " + (sAdjPhrase + " " + sGovrn).strip().title()
	
	
	sOnceKnown = "once %s for its %s %s" % (sKnown, sAchev, sTechs)
	sWasDestroyed = "was destroyed by %s" % (sDisas.title())
	sCaused = "caused by its peoples' %s %s" % (sBadT2,sFlaws.title())
	sRemains = " Now only %s remain." % (DoWeAddPhrase(sRuin1, " and "+sRuin2,0.5))
		
	sCivKnownDestroyed = DoWeAddPhrase(DoWeAddPhrase(sPlace, ", " + sCivilization, 0.5),", " + sOnceKnown +",", .7) + " " + sWasDestroyed
	
	sCivCaused = DoWeAddPhrase(sCivKnownDestroyed, "; " + sCaused, .2) + "."
	
	sOut = DoWeAddPhrase(sCivCaused, sRemains, .9)
	
	return sOut
	
# def Status16(debug=0):		### GIBBERISH

def StatusMaker(debug=0,force=None):

	optID = [[1,.105],[2,.120],[3,.095],[4,.035],[5,.010],[6,.045],[7,.050],[8,.100],[9,.090],[10,.070],[11,.005],[12,.075],[13,.060],[14,.055],[15,.085]]
	
	iChoice = pick_random(optID)
	
	if force is not None:
		iChoice = force
		
	if iChoice == 1:
		strUpdate = Status01(debug) #### Attacks
	elif iChoice == 2:
		strUpdate = Status02(debug) #### AREA DESC LONG 
	elif iChoice == 3:
		strUpdate = Status03(debug) #### AREA DESC SHORT
	elif iChoice == 4:
		strUpdate = Status04(debug) #### SHOP ADS
	elif iChoice == 5:
		strUpdate = Status05(debug) #### DOUBTFUL SHOP ADS
	elif iChoice == 6:
		strUpdate = Status07(debug) #### deprecated deprecated deprecated
	elif iChoice == 7:
		strUpdate = Status07(debug) #### POTIONS
	elif iChoice == 8:
		strUpdate = Status08(debug) #### KING REPORT
	elif iChoice == 9:
		strUpdate = Status09(debug) #### YOU KING
	elif iChoice == 10:
		strUpdate = Status10(debug) #### STATUSED BY A WIZARD
	elif iChoice == 11:
		strUpdate = Status11(debug) #### Your race cant do that
	elif iChoice == 12:
		strUpdate = Status12(debug) #### Bits and Pieces
	elif iChoice == 13:
		strUpdate = Status13(debug) #### Goofy Book Review shit
	elif iChoice == 14:
		strUpdate = Status14(debug)	#### GIBBERISH
	elif iChoice == 15:
		strUpdate = Status15(debug)	#### Lost Civilization
	else:
		strUpdate = 'Error(0): Status Missing'	
	
	return strUpdate
	
