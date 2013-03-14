#! /usr/bin/env python
import sys
import os
import pyfits

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Name of the file that contains the the list of raw bias files:  ")
#      filters = raw_input("Provide Filter info  (fitsheader: FILTER)")
   else:
      file = sys.argv[1]
#      filters = sys.argv[2]

import pyraf
from pyraf import iraf
from pyraf.iraf import images
from pyraf.iraf import immatch
from pyraf.iraf import imutil

masterbias = str(file).split('bias')[0]+'tempBias'+'.fits'
savedmasterbias = str(file).split('bias')[0]+'Bias'+'.fits'

immatch.imcombine.input = '@'+file
immatch.imcombine.output = masterbias                               
immatch.imcombine.combine = "average"
immatch.imcombine.reject = "none"
immatch.imcombine.mode = "h"
immatch.imcombine()

#imutil.minmax.images = masterbias
#imutil.minmax.update = "yes"
#imutil.minmax.mode = "h" 
#imutil.minmax()

fits = pyfits.open(masterbias,mode='update')
fits[0].header.update('OBJECT',str(file).replace('bias',' ')+"MASTER BIAS")
fits.flush()
#datamin = float(fits[0].header['DATAMIN'])
#datamax = float(fits[0].header['DATAMAX'])
#dataaverage = (datamin+datamax)/2

#imutil.imarith.operand1 = masterbias
#imutil.imarith.op = "/"
#imutil.imarith.operand2 = str(dataaverage)
#imutil.imarith.result = "c"+masterbias
#imutil.imarith.title = "Normalized " +str(file).replace('bias',' ')+ " Master Bias"
#imutil.imarith.mode = "h"
#imutil.imarith()

#imutil.minmax.images = "c"+masterbias
#imutil.minmax.update = "yes"
#imutil.minmax.mode = "h" 
#imutil.minmax()

os.system('mv '+masterbias+' '+savedmasterbias)
