#! /usr/bin/env python
import sys
import os

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      targetfile = raw_input("Name of the datacube containing TARGET data:  ")
      masterflat = raw_input("Name of master FLATfile: ")
   else:
      targetfile = sys.argv[1]
      masterflat = sys.argv[2]

print "##################################################################################################################################"
print "# PLEASE be PATIENT: The IRAF task 'imarith' (from images immatch imutil) is dividing the target files by the master flat-fields #"
print "##################################################################################################################################"

import pyraf
from pyraf import iraf
from pyraf.iraf import images
from pyraf.iraf import immatch
from pyraf.iraf import imutil

imutil.imarith.operand1 = "@"+targetfile
imutil.imarith.op = "/"
imutil.imarith.operand2 = masterflat
imutil.imarith.result = "c//@"+targetfile
imutil.imarith.mode = "h"
imutil.imarith()
