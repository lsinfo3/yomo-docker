#!/usr/bin/env python

import time
import shutil
import os
import csv
import time
import datetime
import sys
import random

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def runBaselineVideo():

	#start display	
	display = Display(visible=0, size=(1920, 1080)) #display size has to be cutomized 1920, 1080
	print time.time(), ' start display'
	display.start()
	time.sleep(10)

	bufferFactor = 2
	source = '/tmp'
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
	url = 'https://www.youtube.com/watch?v=QS7lN7giXXc'
	#url = 'https://www.youtube.com/watch?v=JOe7Pt4TZPk'

	#start video
	try:

		print time.time(), ' start firefox'
		browser = webdriver.Firefox()
		time.sleep(10)

		print time.time(), ' start video'
		browser.get(url)
		duration = browser.execute_script('return document.getElementsByTagName("video")[0].duration;')
		## document.getElementsByTagName("video")[0].buffered.end(document.getElementsByTagName("video")[0].buffered.length - 1)
		time.sleep(duration*bufferFactor)

		#time.sleep(200)


		browser.close()
		print time.time(), ' finished firefox'

		#move yomo output
		destination = '/monroe/results/' + 'base'
		if not os.path.exists(destination):
			os.makedirs(destination)
			print 'created dir' + destination
		print 'set destination of output to ' + destination

		files = os.listdir(source)
		for f in files:
			if (f.startswith("yomo_output_")):
				shutil.move(source + '/' + f, destination)
		print 'moved plugin output to ' + destination 
	except Exception as e:
		print time.time(), ' exception thrown'
		print e
		st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		print st
		
		#move yomo output
		destination = '/monroe/results/' + 'base'
		if not os.path.exists(destination):
			os.makedirs(destination)
			print 'created dir' + destination
		print 'set destination of output to ' + destination

		files = os.listdir(source)
		for f in files:
			if (f.startswith("yomo_output_")):
				shutil.move(source + '/' + f, destination)
		print 'moved plugin output to ' + destination 

	display.stop()
	print time.time(), 'display stopped'
	return;


def runRandomVideo():

	#start display	
	display = Display(visible=0, size=(1920, 1080)) #display size has to be cutomized
	display.start()
	print'started display'

	bufferFactor = 2
	source = '/tmp'
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')


	#get ytid
	r = random.randint(0,100)
	lines = []
	if (r > 60):
		#random video (40%)
		print 'random int', r ,' --> select video from random list'
		with open('/opt/monroe/randYTIDs.txt','r') as f:
		  for line in f:
		      lines.append(line.rstrip('\n'))
	else:
		#video from core set (60%)
		print 'random int', r ,' --> select video from core set'
		with open('/opt/monroe/coreSet.txt','r') as f:
		  for line in f:
		      lines.append(line.rstrip('\n'))
	#get random id from list
	randInt = random.randint(0,len(lines)-1)
	print 'select video number ', randInt
	randVideoId = lines[randInt]
	url = 'https://www.youtube.com/watch?v=' + randVideoId
	print 'selected VideoId: ', randVideoId
	

	#start video
	try:
		browser = webdriver.Firefox()
		browser.get(url)
		duration = browser.execute_script('return document.getElementsByTagName("video")[0].duration;')
		print 'started video ', randVideoId, ' with duration ', duration
		time.sleep(duration*bufferFactor)
		#time.sleep(20)
		browser.close()
		print 'finished video ', randVideoId, ' with duration ', duration

		#move yomo output
		destination = '/monroe/results/' + 'random'
		if not os.path.exists(destination):
			os.makedirs(destination)
			print 'created dir' + destination
		print 'set destination of output to ' + destination

		files = os.listdir(source)
		for f in files:
			if (f.startswith("yomo_output_")):
				shutil.move(source + '/' + f, destination)
		print 'moved plugin output to ' + destination 
	except Exception as e:
		print e
		st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		print st

	display.stop()
	print 'display stopped'
	return;


# ----- MAIN

#write output without buffering
sys.stdout.flush()
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

#runTest()
runBaselineVideo()
#runRandomVideo()
