#!/usr/bin/python

import gps 
import simplekml 
from gpiozero import Button, LED 
from os import system 
from time import sleep

# first create our gpsd socket
system("sudo killall gpsd") 
system("sudo gpsd /dev/ttyS0 -F /var/run/gpsd.sock")

# now we create our connection to gpsd
session = gps.gps("localhost", "2947") 
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

# create our SimpleKML object
kml = simplekml.Kml()

# create our stop button and LED
stop_btn = Button(21, hold_time=3) 
stop_led = LED(16)

# Define a function to stop the logger
def stopTracker():
    # flash our LED for half a second
    stop_led.on()
    sleep(0.5)
    stop_led.off()
    # create our filename stripping colon characters
    lineName = "gpsKML-{0}-{1}".format(firstTime, gpsTime).replace(":", "-")
    # create our kml line object
    linestring = kml.newlinestring(name=lineName)
    # pass our compiled lineCoords to the new line object
    linestring.coords = lineCoords
    # set the altitude mode to clampedToGround
    linestring.altitudemode = simplekml.AltitudeMode.clamptoground
    # save our file
    kml.save("/home/pi/WearableTech/Chapter9/" + lineName + ".kml")
    # signal the loop to stop
    global stopLoop
    stopLoop = True
    # shutdown the pi
    system("sudo shutdown now -hP")

# do this if we hold the button for 3 sec
stop_btn.when_held = stopTracker

# wait for this to change to True 
# i.e. when button pressed for 3 sec
stopLoop = False
# create an empty list for our coordinates
lineCoords = []
# set firstTime to empty string
firstTime = "" 

while stopLoop != True:
    report = session.next()
    if report['class'] == 'TPV':
        if hasattr(report, 'time'):
            gpsTime = report.time
            if firstTime == "":
                # This is the first time reading update the variable
                firstTime = gpsTime
            if hasattr(report, 'lon'):
                gpsLon = report.lon
                if hasattr(report, 'lat'):
                    gpsLat = report.lat
                    if hasattr(report, 'alt'):
                        gpsAlt = report.alt
                        # add our 3 variables into the coordinates tuple
                        coordsTup = (gpsLon, gpsLat, gpsAlt)
                        # append our current tuple to our list
                        lineCoords.append(coordsTup)
