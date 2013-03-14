#! /usr/bin/env python

###################################################################################################################
#  Update headers with UT time spaced at EXP time + the deadtime (FITS header ACT) from START (FITS header FRAME).#
###########################################################################################################################################################
# Note that the times in the header of the first image reflects the time AT THE END of the first exposure correct the times to the start of each exposure
#
# E.g.
# ecl> hsel c0001 $I,frame yes
# c0001   2011-10-05T18:31:42.000
#
# UT: 18:31:42.0  (t0) is the END of the first frame (the time stamp does not record fractional seconds, even though the exposure time was 0.5 seconds)
# We thus take 18:31:41.5 as the START time for this sequence and note that UT 18:31:41.5 = 66701.5 s   
###########################################################################################################################################################

import sys
import numpy
import pyfits
import os

#################
#  MAIN PROGRAM #
#################
if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Name of the file that contains the list of FITS filenames:  ")
   else:
      file = sys.argv[1]

   filenamelist = numpy.loadtxt(file,dtype="str")
   try:
      length = len(filenamelist)
   except TypeError, e:
      templist = str(filenamelist)
      filenamelist = []
      filenamelist.append(str(templist))

   # Determine the timing values at the start of the data cube
   fits = pyfits.open(filenamelist[0])
   t0 = fits[0].header['FRAME']
   exp = fits[0].header['ACT']
   trigger = fits[0].header['TRIGGER']
   date = t0.split('T')
   field0 = date[0].split('-')
   years = int(field0[0])
   months = int(field0[1])
   days = int(field0[2])
   field1 = date[1].split(':')
   hrs = int(field1[0])
   mins = int(field1[1])
   secs = float(field1[2])
   # express t0 in number of seconds since midnight (00:00) in UT
   t0sec = 3600*float(hrs) + 60*float(mins) + secs

   print "######################################################################"
   print "# PLEASE be PATIENT: all the timing FITS headers are being corrected #"
   print "######################################################################"
   for x in range(len(filenamelist)):

#   Correct the headers that were populated with FLAT's info during IRAF operation IMARITH (reinstate if this error occurs again for IMARITH)
#      fits = pyfits.open(filenamelist[x].replace('c','').replace('b',''))
      fixedfits = pyfits.open(filenamelist[x],mode='update')
#      fixedfits[0].header.update('OBJECT',fits[0].header['OBJECT'],'Target Name')
#      fixedfits[0].header.update('RA_PNT',fits[0].header['RA_PNT'],'RA of source for Nominal pointing')
#      fixedfits[0].header.update('DEC_PNT',fits[0].header['DEC_PNT'],'DEC of source for Nominal pointing')
#      fixedfits[0].header.update('RA',fits[0].header['RA_PNT'],'RA of source')
#      fixedfits[0].header.update('DEC',fits[0].header['DEC_PNT'],'DEC of source')
#      fixedfits[0].header.update('EPOCH',fits[0].header['EPOCH'],'EPOCH')
#      fixedfits[0].header.update('FRAME',fits[0].header['FRAME'],'End of 1st Exposure in Data Cube')
#      fixedfits[0].header.update('ACT',fits[0].header['ACT'],'Integration cycle time')
#      fixedfits[0].header.update('KCT',fits[0].header['KCT'],'Kinetic cycle time')
#      fixedfits[0].header.update('EXPOSURE',fits[0].header['EXPOSURE'],'Total Exposure Time')
#      fixedfits[0].header.update('RON',fits[0].header['RON'],'Read-out Noise')

      ##########################################
      #  Determine the correct TIMING headers: #
      ##########################################

      ########################################
      # INTERNALLY triggered (Computer time) #
      ########################################
      if trigger == 'Internal':
          # starts at x=0, so the first timing value is t0sec-(exposure+deadtime), which corrects for SHOC recording 'FRAME' at the end of the 1st exposure
          t = t0sec + float(exp)*(x-1)

      #################
      # GPS triggered #
      #################
      if trigger == 'GPS' and filenamelist[0].count('.0001.fits')==1:
      # The user needs to enter the start time of the cube (Ts) and GPS triggering time (dT). These have been stored as FRAME and EXPOSURE fits headers
      # In general the start time for frame number n  = CS + (n-2)dT
          t = t0sec + float(exp)*((x+1)-2)
      # The first file in the list is now already the 3rd frame, beacuse the first 2 would have been eliminated by a previous run of this code
      elif trigger == 'GPS':
          t = t0sec + float(exp)*((x+3)-2)

      # the time in UT [hrs] since midnight (00:00) of DATE-OBS
      th = t/3600.0

      # Write the correct date
      fixedfits[0].header.update('DATE-OBS',date[0],'Observation Date (CCYY:MM:DD)')
      # Write the correct time in hours since midnight of the DATE-OBS
      fixedfits[0].header.update('UTC-OBS',str(th),'Observation Time (UTC) [hrs] from DATE-OBS 0hrs')
      # update fits file
      fixedfits.flush()

   if trigger == 'GPS' and filenamelist[0].count('.0001.fits')==1:
   # Delete frames number 1 and 2 (don't show them, don't use them and specifically not to determine a standard deviation for the background from them).
      os.system('rm '+filenamelist[0]+' '+filenamelist[1])
      adjustedlist = open('adj'+file,'w')
      for i in range(2,len(filenamelist)):
          print >> adjustedlist, filenamelist[i]     
      adjustedlist.close()
      os.system('cp '+'adj'+str(file)+' '+str(file))
