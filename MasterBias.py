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

if len(str(file).split('bias'))<=1:
   masterbias = str(file).split('bias')[0]+'tempBias'+'.fits'
   savedmasterbias = str(file).split('bias')[0]+'Bias'+'.fits'
else:
   masterbias = str(file).split('bias')[0]+'tempBias'+str(file).split('bias')[1]+'.fits'
   savedmasterbias = str(file).split('bias')[0]+'Bias'+str(file).split('bias')[1]+'.fits'

immatch.imcombine.input = '@'+file
immatch.imcombine.output = masterbias                               
immatch.imcombine.combine = "median"
immatch.imcombine.reject = "none"
immatch.imcombine.mode = "h"
immatch.imcombine()

fits = pyfits.open(masterbias,mode='update')
fits[0].header.update('OBJECT',str(file).replace('bias',' ')+"MASTER BIAS")
fits.flush()

os.system('mv '+masterbias+' '+savedmasterbias)
