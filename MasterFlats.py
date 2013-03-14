#! /usr/bin/env python
import sys
import os
import pyfits

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Name of the file that contains the the list of raw flat files:  ")
      filters = raw_input("Provide Filter info  (fitsheader: FILTER)")
   else:
      file = sys.argv[1]
      filters = sys.argv[2]

import pyraf
from pyraf import iraf
from pyraf.iraf import images
from pyraf.iraf import immatch
from pyraf.iraf import imutil

masterflat = str(file).split('flats')[0]+'tempFlat'+str(filters)+'.fits'
savedmasterflat = str(file).split('flats')[0]+'Flat'+str(filters)+'.fits'

immatch.imcombine.input = '@'+file
immatch.imcombine.output = masterflat                               
immatch.imcombine.combine = "average"
immatch.imcombine.reject = "none"
immatch.imcombine.mode = "h"
immatch.imcombine()

imutil.minmax.images = masterflat
imutil.minmax.update = "yes"
imutil.minmax.mode = "h" 
imutil.minmax()

fits = pyfits.open(masterflat)
datamin = float(fits[0].header['DATAMIN'])
datamax = float(fits[0].header['DATAMAX'])
dataaverage = (datamin+datamax)/2

imutil.imarith.operand1 = masterflat
imutil.imarith.op = "/"
imutil.imarith.operand2 = str(dataaverage)
imutil.imarith.result = "c"+masterflat
imutil.imarith.title = "Normalized " +str(file).replace('flats',' ')+ " MASTER FLAT"
imutil.imarith.mode = "h"
imutil.imarith()

imutil.minmax.images = "c"+masterflat
imutil.minmax.update = "yes"
imutil.minmax.mode = "h" 
imutil.minmax()

os.system('mv '+"c"+masterflat+' c'+savedmasterflat)
os.system('mv '+""+masterflat+' '+savedmasterflat)
