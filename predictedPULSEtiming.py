#! /usr/bin/env python
import sys
import os
import numpy

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      start = raw_input("Start time of GPS-triggered PULSEs (UT) [hh:mm:ss]:  ")  
      interval = raw_input("Interval between PULSEs [sec]:  ")
      duration = raw_input("The duration of triggered pulses [sec]:  ") 
   else:
      start = sys.argv[1]
      interval = sys.argv[2]
      duration = sys.argv[3]

interval =float(interval)/3600
duration = float(duration)/3600

pulsetimingpredictions = open('pulsetimingpredictions_UTCstart_'+str(start).replace(':','_'),'w')

temp = start.split(':')
UTCstart = float(temp[0]) + float(temp[1])/60 + float(temp[2])/(60*60)
UTCend = UTCstart + duration

for i in range(int((UTCend-UTCstart)/interval)+1+1):
   if float(UTCstart + i*interval)*3600 <= float(UTCend)*3600:
      print >> pulsetimingpredictions, float(UTCstart + i*interval)*3600, 1
      print float(UTCstart + i*interval)*3600, float(UTCend)*3600, (UTCend-UTCstart)/interval
