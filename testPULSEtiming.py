#! /usr/bin/env python
import sys
import os
import numpy

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Name of the file that contains the list of FITS filenames:  ")   
   else:
      file = sys.argv[1]

if file.count('.fits') >= 1:
   fitslist = []
   fitslist.append(file)
else:
   fitslist = numpy.loadtxt(file,dtype="str")
   try:
      test = len(fitslist)
   except TypeError:
      singlefilename = str(fitslist)
      fitslist = []
      fitslist.append(singlefilename)

HISTORY = open('pulsetimingHISTORY','w')
#fitslist = numpy.loadtxt(file,dtype="str")
for i in range(len(fitslist)):
   cube = fitslist[i].split('.')[1]
   print >> HISTORY, '../SHOCpipeline.py '+fitslist[i]+' 0 0 QuickLook 0 0 2000 0 0 0 0'
#   os.system('../SHOCpipeline.py '+fitslist[i]+' 0 0 QuickLook 0 0 2000 0 0 0 0')
   print >> HISTORY, './SHOCscript'
#   os.system('./SHOCscript')
   print >> HISTORY, '../PULSEtiming.py reduced'+cube+' 0'
#   os.system('../PULSEtiming.py reduced'+cube+' 0')
   print >> HISTORY, './pulsetimingSCRIPT'+cube
#   os.system('./pulsetimingSCRIPT'+cube)

HISTORY.close()

os.system('chmod a+x pulsetimingHISTORY')
os.system('./pulsetimingHISTORY')

print "#####################################################################"
print "Summary of the analysis is available in 'pulsetiminganalysis*' files"
print "#####################################################################"

