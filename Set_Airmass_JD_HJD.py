#! /usr/bin/env python
import sys

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Name of the file that contains the list of FITS filenames:  ")
   else:
      file = sys.argv[1]

import pyraf
from pyraf import iraf
from pyraf.iraf import astutil

print "######################################################################################################################"
print "# PLEASE be PATIENT: The IRAF tasks 'asthedit' and 'setjd' (from astutil) are determining Airmass, JD and HJD values #"
print "######################################################################################################################"

astutil.asthedit.images = '@'+file

astutil.asthedit.commands = "../saao.dat"
astutil.asthedit.prompt = "asthedit> "
astutil.asthedit.update = "yes"
astutil.asthedit.mode = "h"
astutil.asthedit()

astutil.setjd.images = '@'+file
astutil.setjd.observatory = "saao"
astutil.setjd.date = "date-obs"
astutil.setjd.time = "utc-obs"
astutil.setjd.exposure = "exposure"
astutil.setjd.ra = "ra"
astutil.setjd.dec = "dec"
astutil.setjd.epoch = "epoch"
astutil.setjd.jd = "jd"
astutil.setjd.hjd = "hjd"
astutil.setjd.ljd = "ljd"
astutil.setjd.utdate = "yes"
astutil.setjd.uttime = "yes"
astutil.setjd.listonly = "no"
astutil.setjd.mode = "h"
astutil.setjd()
