from __future__ import unicode_literals
import twitter, os
import random
import linecache
import xlrd
import sys
import time
from string import maketrans  
import re
from map_generator import *

def parseTweet(impetusTweet):
	twitName = impetusTweet.user.screen_name
	
	word_list = impetusTweet.text.split(' ')
	if '?start' in word_list:
	if '?name' in word_list:
	if '?xp' in word_list:
	if '?hp' in word_list:
	if ('?kill' in word_list or
		'?stab' in word_list or
		'?kick' in word_list or
		'?fight' in word_list):
	if '?gear' in word_list:
	if '?loc' in word_list or '?pos' in word_list:
	if '?who' in word_list:
	
	
	return "tweet returned from interactor!"