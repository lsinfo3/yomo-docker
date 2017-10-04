#!/usr/bin/env python

import time
import shutil
import os
import csv
import time
import datetime
import sys
import random
import psutil
import numpy as np

import monroe_exporter
import json

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from subprocess import call

CONFIGFILE = '/monroe/config'
EXPCONFIG = {
"ytId":"pJ8HFgPKiZE",
"duration":20,
"bitrates":"144p:110.139,240p:246.425,360p:262.750,480p:529.500,720p:1036.744,1080p:2793.167"
}


def runVideo():

	# start display	
	display = Display(visible=0, size=(1920, 1080)) #display size has to be cutomized 1920, 1080
	print time.time(), ' start display'
	display.start()
	time.sleep(10)

	# get url
	url = 'https://www.youtube.com/watch?v=' + EXPCONFIG['ytId']

	# set file prefix
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
	prefix = "YT_" + EXPCONFIG['ytId'] + '_' + st

	# define firefox settings
	caps = DesiredCapabilities().FIREFOX
	#caps["pageLoadStrategy"] = "normal"  #  complete
	caps["pageLoadStrategy"] = "none"


	try:

		# start firefox
		print time.time(), ' start firefox'
		browser = webdriver.Firefox(capabilities=caps)
		time.sleep(10)

		# read in js
		jsFile = open('/opt/monroe/pluginAsJS.js', 'r')
		js = jsFile.read()
		jsFile.close

		# open webpage
		print time.time(), ' start video ', EXPCONFIG['ytId']
		browser.get(url)
		browser.get_screenshot_as_file('/monroe/results/screenshot0.png')

		# inject js
		browser.execute_script(js)
		duration = EXPCONFIG['duration']
		time.sleep(duration)
		
		# get infos from js and write to file
		print "video playback ended"
		out = browser.execute_script('return document.getElementById("outC").innerHTML;')
		outE = browser.execute_script('return document.getElementById("outE").innerHTML;')
		with open('/monroe/results/' + prefix + '_buffer.txt', 'w') as f:
			f.write(out)
		with open('/monroe/results/' + prefix + '_events.txt', 'w') as f:
			f.write(outE.encode("UTF-8"))
			
		# close browser
		browser.close()
		print time.time(), ' finished firefox'

		
	except Exception as e:
		print time.time(), ' exception thrown'
		print e
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
		print st
	
	# stop display
	display.stop()
	print time.time(), 'display stopped'
	
	# calculate some infos
	bitrates = EXPCONFIG['bitrates'].split(",")
	with open('/monroe/results/' + prefix + '_outStream.txt', 'w') as f:
			f.write(getOutput(prefix, bitrates).encode("UTF-8"))

	return;



# Calculate average, max, min, 25-50-75-90 quantiles of the following: bitrate [KB], buffer [s], number of stalls, duration of stalls
def getOutput(prefix, bitrates):
	out = calculateBitrate(prefix, bitrates)+ "," + calculateBuffer(prefix)+ "," + calculateStallings(prefix)
	return out

def getEvents(prefix):
	timestamps = []
	qualities = []
	with open('/monroe/results/' + prefix + "_events.txt", "r") as filestream:
		for line in filestream:
			currentline = line.split("#")
			if ("quality" in currentline[1]): 
				timestamps.append(float(currentline[0]))
				quality = str(currentline[1])
				quality = quality.split(":")[1]
				quality = quality.split(" ")[0]
				qualities.append(quality)
			if ("ended" in currentline[1]):
				endtime = float(currentline[0])
	if 'endtime' not in locals():
		[times, playtime, buffertime, avPlaytime] = getBuffer(prefix)
		endtime = times[-1]
	return [timestamps, qualities, endtime]

def getBuffer(prefix):
	timestamps = []
	playtime = []
	buffertime = []
	avPlaytime = []
	isFirstLine = True
	with open('/monroe/results/' + prefix + "_buffer.txt", "r") as filestream:
		for line in filestream:
			currentline = line.split("#")
			# end of video
			if (isFirstLine is False and float(currentline[1]) == playtime[-1]): #TODO 
				break;
			timestamps.append(float(currentline[0]))
			playtime.append(float(currentline[1]))
			buffertime.append(float(currentline[2]))
			avPlaytime.append(float(currentline[3][:-1]))
			isFirstLine = False
	return [timestamps , playtime, buffertime, avPlaytime]

	
def calculateBitrate(prefix, bitrates):
	[timestamps, qualities, endtime] = getEvents(prefix)
	timestamps.append(endtime)
	periods = [x / 1000 for x in timestamps]
	periods = np.diff(periods)
	periods = np.round(periods)
	periods = [int(i) for i in periods]
		
	usedBitrates = []	
	
	for x in range(0,len(qualities)):
		index = [i for i, j in enumerate(bitrates) if qualities[x] in j]
		currRate = float(bitrates[index[0]].split(":")[1])
		usedBitrates.extend([currRate] * periods[x])
		
	avgBitrate = sum(usedBitrates)/len(usedBitrates)
	maxBitrate = max(usedBitrates)
	minBitrate = min(usedBitrates)
	q25 = np.percentile(usedBitrates, 25)
	q50 = np.percentile(usedBitrates, 50)
	q75 = np.percentile(usedBitrates, 75)
	q90 = np.percentile(usedBitrates, 90)
	return str(avgBitrate) + "," + str(maxBitrate) + "," + str(minBitrate) + "," + str(q25) + "," + str(q50) + "," + str(q75) + "," + str(q90)

def calculateBuffer(prefix):
	[timestamps , playtime, buffertime, avPlaytime] = getBuffer(prefix)	
	avgBuffer = sum(buffertime)/len(buffertime)
	maxBuffer = max(buffertime)
	minBuffer = min(buffertime)
	q25 = np.percentile(buffertime, 25)
	q50 = np.percentile(buffertime, 50)
	q75 = np.percentile(buffertime, 75)
	q90 = np.percentile(buffertime, 90)
	return str(avgBuffer) + "," + str(maxBuffer) + "," + str(minBuffer) + "," + str(q25) + "," + str(q50) + "," + str(q75) + "," + str(q90) 

def calculateStallings(prefix):
	[timestamps , playtime, buffertime, avPlaytime] = getBuffer(prefix)
	diffTimestamps = np.diff(timestamps)/1000
	diffPlaytime = np.diff(playtime)

	diffTimePlaytime = diffTimestamps - diffPlaytime
	stallings = [0]
	for i in diffTimePlaytime:
		if (i > 0.5):
			stallings.append(i)
		
	numOfStallings = len(stallings)
	avgStalling = sum(stallings)/len(stallings)
	maxStalling = max(stallings)
	minStalling = min(stallings)
	q25 = np.percentile(stallings, 25)
	q50 = np.percentile(stallings, 50)
	q75 = np.percentile(stallings, 75)
	q90 = np.percentile(stallings, 90)
	return str(numOfStallings) + "," + str(avgStalling) + "," + str(maxStalling) + "," + str(minStalling) + "," + str(q25) + "," + str(q50) + "," + str(q75) + "," + str(q90)



# ----- MAIN

# Write output without buffering
sys.stdout.flush()
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)


# Try to get the experiment config as provided by the scheduler
try:
    with open(CONFIGFILE) as configfd:
        EXPCONFIG.update(json.load(configfd))
except Exception as e:
    print "Cannot retrive expconfig {}".format(e), "-- use defaulte settings"



# Start Measurements
runVideo()

