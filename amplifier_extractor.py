#! /usr/bin/env python
import sys
import os
import numpy

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("File containing the list of SLOTMODE fits files:  ")
      amplifier = raw_input("Which amplifier is the target on?:  ")
   else:
      file = sys.argv[1]
      amplifier = sys.argv[2]

datalist = numpy.loadtxt(file,dtype="str")
reduced = open('reduced','w')
os.system('mkdir ReducedData')

import pyraf
from pyraf import iraf
from pyraf.iraf import images
from pyraf.iraf import imutil

amplifier = float(amplifier)/4

for i in range(len(datalist)):
   extensions = imutil.hselect(images = datalist[0]+'[0]', mode = "h", expr = "yes", fields = "$I,NSCIEXT",Stdout=1)
   extensions = int(extensions[0].split()[-1])
   for j in range(25,extensions+1):
      ext = float(j)/4
      if round(ext-int(ext),2) == round(amplifier - int(amplifier),2):
         imutil.imcopy(input = datalist[i]+'['+str(j)+']', output = datalist[i].replace('.fits','')+'.00'+str(j)+'.fits', verbose = "y", mode = "h")
         print >> reduced, 'ReducedData/'+datalist[i].replace('.fits','')+'.00'+str(j)+'.fits'

os.system('mv *.*.fits ReducedData')
