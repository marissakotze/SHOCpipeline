#! /usr/bin/env python
import sys
import os

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Name of the data cube that has to be split:  ")
   else:
      file = sys.argv[1]

cubenumber = file.split('.')[1]
date = file.split('.')[0]

import pyraf
from pyraf import iraf
from pyraf.iraf import images
from pyraf.iraf import imutil
imutil.imslice.input=file
imutil.imslice.output="0"
imutil.imslice.slice_dimens="3"
imutil.imslice.verbose="yes"
imutil.imslice.mode="h"
imutil.imslice()

os.system('ls 0*.fits > list')
os.system('sort -g list > sort')
os.system('awk '+"'"+'{print "s'+date+'.'+cubenumber+'."$0}'+"'"+' sort > sort'+cubenumber)
os.system('awk '+"'"+'{print "mv "$0" s'+date+'.'+cubenumber+'."$0}'+"'"+' sort > rename'+cubenumber)
os.system('chmod a+x ./rename'+cubenumber)
os.system("echo 'PLEASE WAIT'")
os.system('./rename'+cubenumber)
os.system('rm list sort')
