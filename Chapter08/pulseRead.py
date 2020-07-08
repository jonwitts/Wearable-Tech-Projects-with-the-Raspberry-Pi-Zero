#!/usr/bin/python3 

# based on https://github.com/udayankumar/heart-rate-raspberry-pi/blob/master/heartBeats.py
# adapted for the Enviro pHAT 

import time
import scrollphathd as sph
from scrollphathd.fonts import font3x5
from envirophat import analog

# define our scroll phat functions
# a large and small heart to animate
# display a number or message
def largeHeart(b):
    sph.clear_rect(0, 0, 6, 7)
    sph.show()
    sph.set_pixel(0, 0, b/2)
    sph.set_pixel(1, 0, b)
    sph.set_pixel(3, 0, b)
    sph.set_pixel(4, 0, b/2)
    sph.set_pixel(0, 1, b)
    sph.set_pixel(1, 1, b)
    sph.set_pixel(2, 1, b)
    sph.set_pixel(3, 1, b)
    sph.set_pixel(4, 1, b)
    sph.set_pixel(0, 2, b)
    sph.set_pixel(1, 2, b)
    sph.set_pixel(2, 2, b)
    sph.set_pixel(3, 2, b)
    sph.set_pixel(4, 2, b)
    sph.set_pixel(0, 3, b/2)
    sph.set_pixel(1, 3, b)
    sph.set_pixel(2, 3, b)
    sph.set_pixel(3, 3, b)
    sph.set_pixel(4, 3, b/2)
    sph.set_pixel(1, 4, b)
    sph.set_pixel(2, 4, b)
    sph.set_pixel(3, 4, b)
    sph.set_pixel(1, 5, b/2)
    sph.set_pixel(2, 5, b)
    sph.set_pixel(3, 5, b/2)
    sph.set_pixel(2, 6, b)
    sph.show()

def smallHeart(b):
    sph.clear_rect(0, 0, 6, 7)
    sph.show()
    sph.set_pixel(1, 1, b)
    sph.set_pixel(2, 1, b)
    sph.set_pixel(1, 2, b)
    sph.set_pixel(2, 2, b)
    sph.set_pixel(3, 2, b)
    sph.set_pixel(1, 3, b/2)
    sph.set_pixel(2, 3, b)
    sph.set_pixel(3, 3, b/2)
    sph.set_pixel(2, 4, b)
    sph.show()

def printBPM(b, msg):
    sph.clear_rect(6, 0, 11, 8)
    sph.write_string(msg, x=6, y=1, font=font3x5, letter_spacing=1, brightness=b)
    sph.show()

# set up our pulse rate variables and constants
curState = 0
thresh = 1.65 #half of 3.3V
P = 1.0 
T = 1.0 
stateChanged = 0
sampleCounter = 0
lastBeatTime = 0
firstBeat = True
secondBeat = False
Pulse = False
IBI = 600
rate = [0]*10
amp = 100

lastTime = int(time.time()*1000)

while True:
    # read from the ADC
    Signal = analog.read(0)
    curTime = int(time.time()*1000)
    sampleCounter += curTime - lastTime
    lastTime = curTime
    N = sampleCounter - lastBeatTime # monitor the time since the last beat to avoid noise
    ##  find the peak and trough of the pulse wave
    if Signal < thresh and N > (IBI/5.0)*3.0 : # avoid dichrotic noise by waiting 3/5 of last IBI
        if Signal < T : # T is the trough
            T = Signal  # keep track of lowest point in pulse wave
            smallHeart(0.25) # measured a trough so show small heart

    if Signal > thresh and Signal > P: # thresh condition helps avoid noise
        P = Signal # P is the peak - keep track of highest point in pulse wave
        largeHeart(0.25) # measured a peak so show a large heart

    # signal surges up in value every time there is a pulse
    if N > 250 : # avoid high frequency noise
        if  (Signal > thresh) and  (Pulse == False) and  (N > (IBI/5.0)*3.0)  :       
            Pulse = True # set the Pulse flag when we think there is a pulse
            IBI = sampleCounter - lastBeatTime # measure time between beats
            lastBeatTime = sampleCounter # keep track of time for next pulse

            if secondBeat : # if secondBeat == TRUE
                secondBeat = False # clear secondBeat flag
                for i in range(0,10): # seed the running total to get a realisitic BPM at startup
                    rate[i] = IBI;                      

            if firstBeat : # if firstBeat == TRUE
                firstBeat = False # clear firstBeat flag
                secondBeat = True # set the second beat flag
                continue # IBI value is unreliable so discard it

            # keep a running total of the last 10 IBI values
            runningTotal = 0 # clear the runningTotal variable    

            for i in range(0,9): # shift data in the rate array
                rate[i] = rate[i+1] # and drop the oldest IBI value 
                runningTotal += rate[i] # add up the 9 oldest IBI values

            rate[9] = IBI # add the latest IBI to the rate array
            runningTotal += rate[9]  # add the latest IBI to runningTotal
            runningTotal /= 10       # average the last 10 IBI values 
            BPM = 60000/runningTotal # how many beats can fit into a minute? that's BPM!
            printBPM(0.25, str(int(BPM))) # we have a BPM lets display it

        if Signal < thresh and Pulse == True : # when the values are going down, the beat is over
            Pulse = False # reset the Pulse flag so we can do it again
            amp = P - T # get amplitude of the pulse wave
            thresh = amp/2 + T # set thresh at 50% of the amplitude
            P = thresh # reset these for next time
            T = thresh

        if N > 2500 : # if 2.5 seconds go by without a beat
            thresh = 1.65 # set thresh default
            P = 1.0 # set P default
            T = 1.0 # set T default
            lastBeatTime = sampleCounter # bring the lastBeatTime up to date        
            firstBeat = True # set these to avoid noise
            secondBeat = False # when we get the heartbeat back
            printBPM(0.25, "-^-")

        time.sleep(0.005)
