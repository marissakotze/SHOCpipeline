#! /usr/bin/env python
import sys
import os
import numpy
import pyfits

import pyraf
from pyraf import iraf
from pyraf.iraf import images
from pyraf.iraf import imutil

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Name of the file that contains the list of FITS filenames:  ")  
      ext = raw_input("Which amplifier's extentions should be extracted (0 if all):  ")  
   else:
      file = sys.argv[1]
      ext = sys.argv[2]

pulsetiming = open('pulsetiming','w')

cube = file.split('reduced')[1]

means = []
exposures = []
fitslist = numpy.loadtxt(file,dtype="str")
for i in range(len(fitslist)):
   fits = pyfits.open(fitslist[i])
   instrument = fits[0].header['INSTRUME']
   if instrument.count('RSS') > 0:
      amplifiers = 6
      exposure = fits[0].header['EXPTIME']
   elif instrument.count('SALTICAM') > 0:
      amplifiers = 4
      exposure = fits[0].header['EXPTIME']
   else:
      amplifiers = 1
      exposure = fits[0].header['KCT']
      instrument = 'SHOC'
   if i == 0:
      start = (fits[0].header['FRAME']).split('T')[1]
   if i == len(fitslist)-1:
      frames = (fits[0].header['NUMKIN'])
   if ext in ('0',''):
      extensions = 1
      imagestatistics = imutil.imstat(images = fitslist[i]+'[0]'+'[]', mode = "h", fields = 'image,mean',Stdout=1)
      image = imagestatistics[1].split()[0]
      mean = imagestatistics[1].split()[-1]
      print 'Image:', image, 'Mean: ', mean
      means.append(float(mean))
      exposures.append(float(exposure))
      utc = imutil.hselect(images = fitslist[i]+'[0]', fields = '$I,UTC-OBS', expr = 'yes',Stdout=1)[0]
      print >> pulsetiming, image, mean
      print >> pulsetiming, utc
   else:
      ext = int(ext)
      extensions = int(fits[0].header['NEXTEND'])
      print >> pulsetiming, '#  Extentions per cube: ', extensions
      for j in range(extensions/amplifiers):
         imagestatistics = imutil.imstat(images = fitslist[i]+'['+str(j*amplifiers+ext)+']'+'[]', mode = "h", fields = 'image,mean',Stdout=1)
         image = imagestatistics[1].split()[0]
         mean = imagestatistics[1].split()[-1]
         print 'Image:', image, 'Mean: ', mean
         means.append(float(mean))
         exposures.append(float(exposure))
         utc = imutil.hselect(images = fitslist[i]+'['+str(j*amplifiers+ext)+']', fields = '$I,UTC-OBS', expr = 'yes',Stdout=1)[0]
         print >> pulsetiming, image, mean
         print >> pulsetiming, utc
pulsetiming.close()

if instrument == 'SHOC':
   os.system('../readPULSEtiming_shoc.py pulsetiming')
   os.system('mv pulsetimingresults pulsetimingresults'+cube)
   os.system('mv pulsetiming pulsetiming'+cube)
   duration = float(frames)*float(exposure)
   os.system('../predictedPULSEtiming.py '+start[:8]+' 1 '+str(duration))
else:
   os.system('../readPULSEtiming.py pulsetiming')


pulsetimingSCRIPT = open('pulsetimingSCRIPT'+cube,'w')
os.system('chmod a+x pulsetimingSCRIPT'+cube)
meanperexposure = []
exposureperexposure = []
sumperexp = 0
count = 0
listperexposure = []
maxperexposure = []
minperexposure = []
for j in range(1,len(exposures)):
   if exposures[j] != exposures[j-1]:      
      meanperexposure.append(sumperexp/count)
      exposureperexposure.append(exposures[j-1])
      maxperexposure.append(max(listperexposure))
      minperexposure.append(min(listperexposure))
      sumperexp = 0
      count = 0
      listperexposure = []
   else:
      sumperexp = sumperexp + means[j]
      count = count + 1
      listperexposure.append(means[j])
meanperexposure.append(sumperexp/count)
exposureperexposure.append(exposures[j])
maxperexposure.append(max(listperexposure))
minperexposure.append(min(listperexposure))



for k in range(len(exposureperexposure)):
   factors = int(0.250/exposureperexposure[k])+1
   #print >> pulsetimingSCRIPT, '../detectedPULSEtiming.py pulsetimingresults pulsetimingpredictions '+str(exposureperexposure[k])+' 0.001 '+str(1.1*minperexposure[k])+' 1'
   print >> pulsetimingSCRIPT, '../detectedPULSEtiming_pulsewidths.py pulsetimingresults'+cube+' pulsetimingpredictions_UTCstart_'+start.replace(':','_')[:8]+' '+str(exposureperexposure[k])+' 0.001 '+str(1.2*minperexposure[k])+' '+str(factors)+' 0.1'
   print >> pulsetimingSCRIPT, 'mv pulsetimingaccuracy pulsetimingaccuracy'+cube
   print >> pulsetimingSCRIPT, 'mv pulsetiminganalysis pulsetiminganalysis'+cube
   print 'Maximum: ', maxperexposure[k], 'for Exposure:', exposureperexposure[k], 'with Mean:', meanperexposure[k]
