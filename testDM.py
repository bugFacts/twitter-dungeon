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
import math

				
PLAYERLIST = 'P:\python_twitter\scrips\yourdmLogs\PLAYERLIST.txt'				
			
class Player:

	def __init__(self, userID=None, userName=None, reTime=None, 
				pos_x=None, pos_y=None, pos_z=None,
				xp=None, 
				char_name=None, char_class=None, char_race=None, 
				char_Helm=None, char_Chest=None, char_Hand=None,
				char_Ring=None,
				char_inv1=None, char_inv2=None, char_inv3=None, 
				enemy=None):
		
		self.userID = userID
		self.userName = userName
		self.reTime = reTime
		#self.pos = (pos_x,pos_y,pos_z)
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.pos_z = pos_z
		self.xp = xp
		
		self.char_name=char_name
		self.char_class=char_class 
		self.char_race=char_race 
		
		self.char_Helm=char_Helm 
		self.char_Chest=char_Chest
		self.char_Hand=char_Hand
		self.char_Ring=char_Ring
		#self.char_inv = (char_inv1, char_inv2, char_inv3)
		self.char_inv1 = char_inv1
		self.char_inv2 = char_inv2
		self.char_inv3 = char_inv3
		
		self.enemy = enemy
	# def __getitem__(self, key): return self.data[key]
	
	# def __setitem__(self, key, item): self.data[key] = item
	
	def print_info(self):
		print "Twitter id:", self.userID
		print "Twitter username: ", self.userName
		print "Last time seen: ", self.reTime
		
		print "Pos x: ", self.pos_x
		print "Pos y: ",self.pos_y
		print "Pos z: ",self.pos_z
		
		print "XP: ", self.xp
		print "level: ", self.get_level()
		print "Character Name: ", self.char_name
		print "Character Class: ", self.char_class 
		print "Character Race: ", self.char_race
		
		print "Helm: ", self.char_Helm
		print "Armor: ", self.char_Chest
		print "Hand: ", self.char_Hand
		print "Ring: ", self.char_Ring
		
		print "Inventory Slot 1: ", self.char_inv1
		print "Inventory Slot 2: ", self.char_inv2
		print "Inventory Slot 3: ", self.char_inv3
		
		print "Current enemy: ", self.enemy
														
	def prompt_missing(self):
		if (
				not self.pos_x or not self.pos_y or not self.pos_z or
				#self.pos_x=None or self.pos_y=None or self.pos_z=None or
				self.pos_x=="None" or self.pos_y=="None" or self.pos_z=="None"
			):

			self.begin_dungeon()
		if not self.char_name or self.char_name==None or self.char_name=="None":
			self.prompt_name()
		if not self.char_class or self.char_class==None or self.char_class=="None":
			self.prompt_class()
					
	def get_level(self):
		if not self.xp or self.xp==0 or self.xp=="None":
			level = 0
			x = 0
		else:
			x = int(self.xp)
			level = 10 % (x + 1)
		self.level = level
		self.xp = x

	
	# def set_name(self,name):
		# self.char_name = name
		
	# def set_helm(self,helm_name):
		# self.char_Helm = helm_name
		
	# def set_chest(self,char_Chest):
		# self.char_Chest = char_Chest
	
	# def set_hand(self,char_Hand):
		# self.char_Hand = char_Hand
		
	# def set_ring(self,char_Ring):
		# self.char_Ring = char_Ring
		
	# def set_inv1(self,char_inv1):
		# self.char_inv1 = char_inv1
		
	# def set_inv2(self,char_inv2):
		# self.char_inv2 = char_inv2
		
	# def set_inv3(self,char_inv3):
		# self.char_inv3 = char_inv3
		
class Player_Dict:
	def __init__(self):
		self.members = []
		self.PlayerDict = defaultdict(list)
		self.PlayerDict = {}
	
	# def __getitem__(self, key): return self.data[key]
	
	# def __setitem__(self, key, item): self.data[key] = item
	
	def load_from_file(self):
		with open(PLAYERLIST, 'r') as fp:
			fPlayerlist = fp.readlines()

		for i in fPlayerlist:
			if i.strip() == "" or i.strip()=="None":	#skip empty lines
				continue
			
			userID = i.split('|')[0].rstrip()
			userName = i.split('|')[1].rstrip()
			reTime = 0 if i.split('|')[2].rstrip()=="None" else float( i.split('|')[2].rstrip() )
			
			pos_x = 0 if i.split('|')[3].rstrip()=="None" else int(float( i.split('|')[3].rstrip() ))
			pos_y = 0 if i.split('|')[4].rstrip()=="None" else int(float( i.split('|')[4].rstrip() ))
			pos_z = 0 if i.split('|')[5].rstrip()=="None" else int(float( i.split('|')[5].rstrip() ))
			
			xp = i.split('|')[6].rstrip()
			
			char_name = i.split('|')[7].rstrip()
			char_class = i.split('|')[8].rstrip() 
			char_race = i.split('|')[9].rstrip()
			
			char_Helm=i.split('|')[10].rstrip()
			char_Chest=i.split('|')[11].rstrip()
			char_Hand=i.split('|')[12].rstrip()
			char_Ring=i.split('|')[13].rstrip()
			
			char_inv1 = i.split('|')[14].rstrip()
			char_inv2 = i.split('|')[15].rstrip()
			char_inv3 = i.split('|')[16].rstrip()
			
			char_inv = (char_inv1, char_inv2, char_inv3)
			
			enemy = i.split('|')[17].rstrip()

			self.PlayerDict[userName] = Player(userID=userID, 
												userName=userName,
												reTime=reTime,
												pos_x=pos_x,
												pos_y=pos_y,
												pos_z=pos_z,
												xp=xp,
												char_name=char_name,
												char_class=char_class,
												char_race=char_race,
												char_Helm=char_Helm,
												char_Chest=char_Chest,
												char_Hand=char_Hand,
												char_Ring=char_Ring,
												char_inv1=char_inv1,
												char_inv2=char_inv2,
												char_inv3=char_inv3,
												enemy=enemy
												)
		
		return self.PlayerDict
						
	def save_to_file(self, changed_player_dict):
		#copy the updates to a new dict
		merged_player_dict = changed_player_dict.copy()
		
		#get the original dictionary from the text file
		old_player_dict = self.load_from_file()
		
		#replace the original values with modified ones
		changed_player_dict.update(merged_player_dict)
				
		#instantiate a blank updated dictionary
		updated_player_list = []
		
		for key, value in changed_player_dict.items():
			#tear each entry in the useful python dictionary into a dumb tuple
			selfs = \
					(
					value.userID,
					value.userName,
					value.reTime,
					value.pos_x,
					value.pos_y,
					value.pos_z,
					value.xp,												
					value.char_name,
					value.char_class, 
					value.char_race,												
					value.char_Helm, 
					value.char_Chest,
					value.char_Hand,
					value.char_Ring,
					value.char_inv1,
					value.char_inv2,
					value.char_inv3,
					value.enemy
					)

			a = ''
			
			#smash the dumb tuples into an ugly plain string
			for x in selfs:
				a = ''.join([a,str(x),'|'])
			
			#make a list of strings
			updated_player_list.append(a)
		
		#grab each string in the list and save them to the text file
		with open(PLAYERLIST, 'w') as fp:
			fp.write(''.join([ '%s\n' % (line) for line in updated_player_list]))

			
