#! /usr/bin/env python
import sys
import os
import numpy

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Name of the file that contains PULSE timing PYRAF info:  ")  
   else:
      file = sys.argv[1]

outputs = numpy.loadtxt(file,dtype="str")

pulsetimingresults = open('pulsetimingresults','w')

for i in range(len(outputs)):
   if outputs[i-1][0].count(outputs[i][0]) > 0:
      temp = outputs[i][1]
      utc = float(temp)
      if float(outputs[i-1][1]) != 0:
          print >> pulsetimingresults, utc*3600, outputs[i-1][1], '#', outputs[i][1], outputs[i][0]
