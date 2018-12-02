#!/usr/bin/env python
import os
import time
import datetime
import glob
import sys
import RPi.GPIO as GPIO
from time import strftime
from time import sleep
from datetime import datetime
from datetime import timedelta

# GPIO 17 living_left	// Floor heating relay
# GPIO 22 kitchen	// Floor heating relay
# GPIO 23 living_right	// Floor heating relay
# GPIO 24 holway	// Floor heating relay
# GPIO 27 boiler	// Boiler heating relay

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

def heatingON(relay_port):
	#GPIO.setup(relay_port, GPIO.OUT, initial=GPIO.HIGH)
	GPIO.output(relay_port, GPIO.LOW)
	
def heatingOFF(relay_port):
	#GPIO.setup(relay_port, GPIO.OUT, initial=GPIO.LOW)
	GPIO.output(relay_port, GPIO.HIGH)

def inTime(startTime, endTime, nowTime):
    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else: #Over midnight
        return nowTime >= startTime or nowTime <= endTime

def Temp(sensor):
    part1 = "/sys/bus/w1/devices/"
    part2 = "/w1_slave"
    File_location = "%s%s%s" % (part1,sensor,part2)
    #print (File_location)
    try :
        t = open(File_location, 'r')
        lines = t.readlines()
        t.close()    
        temp_output = lines[1].find('t=')
        if temp_output != -1:
            temp_string = lines[1].strip()[temp_output+2:]
            temp_c = float(temp_string)/1000.0
        #print (round(temp_c,2))        
        return round(temp_c,2)      
    except KeyboardInterrupt:
        print ("KeyboardInterrupt from Temp_sensor")
        sys.exit()
        # Missing sensor value        
    else:
        print ("No Value!")                
        return 99.9

def HeatingStatus(place):
     living_left = GPIO.input(17)
     living_right = GPIO.input(23)
     kitchen = GPIO.input(22)
     holway = GPIO.input(24)
     boiler = GPIO.input(27)
     if place == "living_left" : return living_left
     if place == "living_right": return living_right
     if place == "kitchen"     : return kitchen
     if place == "holway"      : return holway
     if place == "boiler"      : return boiler

def AverageTemp(templist):
    return sum(templist)/len(templist)

def TempAverage(sensorname):
    list=[]
    while len(list) < 10:
        try:        
            list.append(Temp(sensorname))                    
        except KeyboardInterrupt:
            print ("KeyboardInterrupt from Temp_average")            
            break
    #print (list)

    return AverageTemp(list)           


while True:
  try :
    timeNow = strftime("%H:%M:%S")
    timeNow = datetime.strptime(timeNow, "%H:%M:%S")
    timeStart = str("17:00:00")
    timeStart = datetime.strptime(timeStart, "%H:%M:%S")
    timeEnd = ("05:30:00")
    timeEnd = datetime.strptime(timeEnd, "%H:%M:%S")
    #print(inTime(timeStart,timeEnd,timeEnd))
    desiredTemp = 19.5
    minTemp = desiredTemp - 0.5
    maxTemp = desiredTemp + 0.5
    #sensorName = "28-000008bb064b" # Livingroom
    #sensorName = "28-000008bceb86" # Master bedroom
    sensorName = "28-000008bcf918" # Double Room
    #TempAverage(sensorName)
    actualTemp = round(TempAverage(sensorName),2)
    #actualTemp = Temp(sensorName)
    print ("")
    print (actualTemp, " C")
    print ("Desired temp: ",desiredTemp)
    print ("Start and finish time: ",timeStart," ",timeEnd)
    print (inTime(timeStart, timeEnd, timeNow))
    if HeatingStatus("boiler") == 0 : print (timeNow, " Heating is on ..")
    if HeatingStatus("boiler") == 1 : print (timeNow, " Heating is off ..")
    if actualTemp < minTemp and HeatingStatus("boiler") == 1 and inTime(timeStart,timeEnd,timeNow) : 
        heatingON(27)
        print ("Heating on")
    #if actualTemp < maxTemp and HeatingStatus("boiler") == 0 and inTime(timeStart,timeEnd,timeEnd) : print ("Heating on")
    if actualTemp >= maxTemp and HeatingStatus("boiler") == 0 and inTime(timeStart,timeEnd,timeNow) : 
        heatingOFF(27)
        print ("Heating OFF")
    if HeatingStatus("boiler") == 0 and not inTime(timeStart,timeEnd,timeNow) : 
        heatingOFF(27)
        print ("Heating OFF")
    sleep (0)
  except KeyboardInterrupt:
    print ("KeyboardInterrupt")
    break
