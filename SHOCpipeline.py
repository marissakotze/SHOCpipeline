#! /usr/bin/env python

#####################################
# Data reduction Pipeline for SHOC  #
#####################################

import sys
import numpy
import pyfits
import os

####################
##################
#  MAIN PROGRAM  #
##################
####################

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      TARGETSfile = raw_input("File containing the list of raw TARGET files (0 if none or the name of a single fits file):  ")
      FLATSfile = raw_input("File containing the list of raw FLATS (0 if none or the name of a single fits file):  ")
      BIASfile = raw_input("File containing the list of raw BIAS frames (0 if none or the name of a single fits file):  ")
      targetname = raw_input("Provide Target Name , 0 if n.a.    (fitsheader: OBJECT): ")
      ra = raw_input("Provide Target RA [hh:mm:ss] , 0 if n.a.   (fitsheader: RA): ")
      dec = raw_input("Provide Target DEC [deg:arcmin:arcsec] , 0 if n.a.    (fitsheader: DEC): ")
      epoch = raw_input("Provide Target EPOCH , 0 if n.a.    (fitsheader: EPOCH): ")
      site = raw_input("Provide Site info     (fitsheader: OBSERVAT): ")
      telescope = raw_input("Provide Telescope info     (fitsheader: TELESCOP): ")
      instrument = raw_input("Provide Instrument info     (fitsheader: INSTRUME): ")
      filters = raw_input("Provide Filter info [e.g. <wheelA><wheelB>]    (fitsheader: FILTER): ")
   else:
      TARGETSfile = sys.argv[1]
      FLATSfile = sys.argv[2]
      BIASfile = sys.argv[3]
      targetname = sys.argv[4]
      ra = sys.argv[5]
      dec = sys.argv[6]
      epoch = sys.argv[7]
      site = sys.argv[8]
      telescope = sys.argv[9]
      instrument = sys.argv[10]
      filters = sys.argv[11]

#   try:
#      f = open('login.cl','r')
#   except IOError, e:
   os.system('chmod 754 *fits')      
   os.system('ln -s ../iraf/login.cl login.cl')

   try:
      f = open('parameters','r')
   except IOError, e: 
      os.system('cp ../defaultparameters parameters')

   ####################
   # Load input files #
   ####################

   masterbias = 'N'
   masterflats = 'N'
   dophotometry = 'N'

   if targetname != 'QuickLook': 
       if FLATSfile == '0':
           makemasterflats = 'N'
           print 'There were no raw FLATS supplied.'
           masterflats = raw_input("Are the appropriate MASTER FLATS available? (Y/N):  ")
           while masterflats not in ('Y','y','N','n',''):
               masterflats = raw_input("Invalid input. Are the appropriate MASTER FLATS available? (Y/N):  ")
           if masterflats in ('Y','y'):
               masterflats = 'Y'
           else:
               masterflats = 'N'
       else:
           makemasterflats = 'Y'
           if FLATSfile.count('.fits') >= 1:
               FLATSdatalist = []
               FLATSdatalist.append(FLATSfile)
           else:
               FLATSdatalist = numpy.loadtxt(FLATSfile,dtype="str")
   else:
       makemasterflats = 'N'

   if TARGETSfile == '0':
       dophotometry = 'N'
       print '                                                                                                       '
       print '#######################################################################################################'
       print ' WARNING: There were no raw TARGET files supplied. Only master BIAS and/or FLAT files will be created.'
       print '#######################################################################################################'
       os.system('rm PHOTscript PLOTscript')
   else:
       dophotometry = 'Y'
       if TARGETSfile.count('.fits') >= 1:
           TARGETSdatalist = []
           TARGETSdatalist.append(TARGETSfile)
       else:
           TARGETSdatalist = numpy.loadtxt(TARGETSfile,dtype="str")
           try:
               test = len(TARGETSdatalist)
           except TypeError:
               singlefilename = str(TARGETSdatalist)
               TARGETSdatalist = []
               TARGETSdatalist.append(singlefilename)
   if targetname != 'QuickLook':
       if BIASfile == '0':
           makemasterbias = 'N'
           print 'There were no raw BIAS frames supplied.'
           masterbias = raw_input("Are the appropriate MASTER BIAS files available? (Y/N):  ")
           while masterbias not in ('Y','y','N','n',''):
               masterbias = raw_input("Invalid input. Are the appropriate MASTER BIAS files available? (Y/N):  ")
           if masterbias in ('Y','y'):
               masterbias = 'Y'
           else:
               masterbias = 'N'
       else:
           makemasterbias = 'Y'
           if BIASfile.count('.fits') >= 1:
               BIASdatalist = []
               BIASdatalist.append(BIASfile)
           else:
               BIASdatalist = numpy.loadtxt(BIASfile,dtype="str")
   else:
       makemasterbias = 'N'

   if ra == '0' and dec == '0' and TARGETSfile != '0' and targetname != 'QuickLook':
       print '                                                                                                                    '
       print '####################################################################################################################'
       print ' WARNING: Since the RA and DEC of the target is not supplied, the HJD values in the lightcurves will not be correct'
       print ' However, the relative timing will be correct for those interested in variability'
       print '####################################################################################################################'

   # Read the specification table for readnoise
   readoutnoise = numpy.loadtxt('../ReadoutNoiseTable',dtype="str",delimiter = '\t',unpack=True)
   serialnr = readoutnoise[0]
   mode = readoutnoise[3]
   preAmp = readoutnoise[4]
   sensitivity = readoutnoise[5]
   readnoise = readoutnoise[6]
   readtime = readoutnoise[7]

   tempreadnoise = 0

   # Open script file for PRE-REDUCTIONS
   SHOCscript = open('SHOCscript','w')
   print >> SHOCscript, "#! /bin/bash"

   # Open script file for PHOTOMETRY
   PHOTscript = open('PHOTscript','w')
   print >> PHOTscript, "#! /bin/bash"

   # Open script file for PLOTTING
   PLOTscript = open('PLOTscript','w')
   print >> PLOTscript, "#! /bin/bash"

   # Compile all scripts to be executable from the commandline
   os.system('chmod a+x SHOCscript')
   os.system('chmod a+x PHOTscript')
   os.system('chmod a+x PLOTscript')
 
   ##############################
   # Prepare RAW TARGET FILES:  # 
   ##############################

   startFITSfiles = []

   print "####################################################################"
   print "# Please be patient while crucial FITS headers are being corrected #"
   print "####################################################################"
   if dophotometry == 'Y':
      # Determine the binning of the TARGETfiles and update their FITS HEADERS
      vbincube = []
      hbincube = []
      EMmode = [] 
      trigger = []
      for i in range(len(TARGETSdatalist)): 
         fits = pyfits.open(TARGETSdatalist[i],mode='update')
         vbincube.append(float(fits[0].header['VBIN']))
         hbincube.append(float(fits[0].header['HBIN']))
         EMmode.append(fits[0].header['OUTPTAMP'])
         fits[0].header.update('OBJECT',targetname,'----Source information block------')
         fits[0].header.update('RA_PNT',ra,'RA of source for Nominal pointing in deg')
         fits[0].header.update('DEC_PNT',dec,'DEC of source for Nominal pointing in deg')
         fits[0].header.update('RA',ra,'RA of source')
         fits[0].header.update('DEC',dec,'DEC of source')
         fits[0].header.update('EPOCH',epoch,'EPOCH')
         fits[0].header.update('FILTER',filters,'WheelA WheelB')
         fits[0].header.update('OBSERVAT',site,'Observatory')
         fits[0].header.update('TELESCOP',telescope,'Telescope')
         fits[0].header.update('INSTRUME',instrument,'Instrument')
         if fits[0].header['TRIGGER'] == 'External':
             if float(fits[0].header['EXPOSURE']) == 0.00001: 
                 print "The timing was triggered externally via the GPS. The user is required to supply the appropriate information for the FITS headers:"
                 GPSstartdate = raw_input("GPS (POP) start date [CCYY-MM-DD]:  ")
                 while GPSstartdate.count('-')!=2 or float(GPSstartdate[5:7])>12 or len(GPSstartdate)<10:
                     GPSstartdate = raw_input("The format is:    CCYY-MM-DD   ")
                 GPSstarttime = raw_input("GPS (POP) start time in UT [HH:MM:SS.SSSSSSS]:  ")
                 while GPSstarttime.count(':')!=2 or float(GPSstarttime[0:2])>24 or float(GPSstarttime[3:5])>60 or float(GPSstarttime[6:8])>60:
                     GPSstarttime = raw_input("The format is:    HH:MM:SS.SSSSSSS   ")
                 GPSstart = GPSstartdate+'T'+GPSstarttime
                 print "The 'FRAME' fits header will now be updated with the value:   "+GPSstart
                 fits[0].header.update('FRAME',GPSstart,'GPS start time of the cube')
                 exposure = raw_input("Supply the exposure time (POP repeat interval) in milliseconds [ms]:   ")
                 exposuresec = float(exposure)/1000
                 print "The 'EXPOSURE', 'ACT' and 'KCT' fits headers will now be updated with the value:   "+str(exposuresec)+ "   in seconds [s]"
                 fits[0].header.update('EXPOSURE',exposuresec,'GPS repeat interval [s]')
                 fits[0].header.update('ACT',exposuresec,'GPS repeat interval [s]')
                 fits[0].header.update('KCT',exposuresec,'GPS repeat interval [s]')
                 fits[0].header.update('TRIGGER','GPS','Trigger mode (External)')
             else:
                 print "The timing appears to have been triggered externally, but the timing mode that was used is not currently supported."
         if fits[0].header['TRIGGER'] == 'Internal':
             fits[0].header.update('FRAME',fits[0].header['FRAME'],'End of 1st Exposure in Data Cube')
         trigger.append(str(fits[0].header['TRIGGER']))
         for j in range(len(serialnr)): 
             if float(fits[0].header['SENSITIVITY'])== float(sensitivity[j]) and float(fits[0].header['SERNO'])== float(serialnr[j]):
                 fits[0].header.update('RON',readnoise[j],'Read-out Noise')
                 tempreadnoise = readnoise[j]
#             elif float(fits[0].header['SENSITIVITY']) == float(0)  and str(fits[0].header['SERNO']) == serialnr[j] and str(fits[0].header['PREAMP'])== preAmp[j] and float(fits[0].header['READTIME']) == float(readtime[j]) and fits[0].header['OUTPTAMP'] == mode[j]:
             elif str(fits[0].header['SERNO']) == serialnr[j] and str(fits[0].header['PREAMP'])== preAmp[j] and float(fits[0].header['READTIME']) == float(readtime[j]) and fits[0].header['OUTPTAMP'] == mode[j]:
                 fits[0].header.update('RON',readnoise[j],'Read-out Noise') 
                 tempreadnoise = readnoise[j]
                 fits[0].header.update('HIERARCH SENSITIVITY',sensitivity[j],'Sensitivity of 0 replaced from RON Table')  

         if tempreadnoise == 0:
             print "WARNING: the Read-out noise value could not be determined for: "+ str(TARGETSdatalist[i])
         # for CONVENTIONAL mode the fits-header 'GAIN'=0 and the real value for GAIN is in fits-header 'SENSITIVITY' [e/ADU]
         if fits[0].header['OUTPTAMP'] == 'Conventional':
             fits[0].header.update('GAIN',fits[0].header['SENSITIVITY'], 'Replaced 0 with actual gain from SENSITIVITY')   
         # For EM mode the READNOISE and GAIN values equals the specification sheet values divided by the value given in the GAIN keyword. 
         # And if GAIN = 0 change it to GAIN = 1 and use the RON and GAIN from the specification sheet. Once changed to 1 it won't be changed again.
         if fits[0].header['OUTPTAMP'] == 'Electron Multiplying':
             if float(fits[0].header['GAIN']) == 0:
                 fits[0].header.update('GAIN','1', 'Replaced value of '+str(fits[0].header['GAIN']))
             elif float(fits[0].header['GAIN']) > 1:
                 fits[0].header.update('RON',float(tempreadnoise)/float(fits[0].header['GAIN']),'Read-out Noise')
                 fits[0].header.update('GAIN',float(fits[0].header['GAIN'])/float(fits[0].header['GAIN']), 'Replaced value of '+str(fits[0].header['GAIN']))
         # save updated fits file
         cubenumber = TARGETSdatalist[i].split('.')[1]
         bins = str(fits[0].header['VBIN'])
         try:
             fits.flush()
         except ValueError:
#         except MemoryError:
             tooBIG =  open('tooBIG','w')
             print >> tooBIG, "#! /bin/bash"
             print >> tooBIG, "../slice.py "+TARGETSdatalist[i]
             print >> tooBIG, "../SHOCpipeline.py sort"+cubenumber+" "+FLATSfile+" "+BIASfile+" '"+targetname+"' "+ra+" "+dec+" "+epoch+" "+site+" "+telescope+" "+instrument+" "+filters
             print >> tooBIG, 'rm SHOCscript PHOTscript PLOTscript'      
             print >> tooBIG, "cp sort"+cubenumber+" splittedtarget"+cubenumber
             if masterbias == 'Y':
                 print >> tooBIG, "../BiasCorrection.py splittedtarget"+cubenumber+" "+bins+"x"+bins+"Bias.fits"
                 print >> tooBIG, "awk '{print "+'"b"'+"$0}' splittedtarget"+cubenumber+" > reduced"+cubenumber
                 print >> tooBIG, "rm s"+TARGETSdatalist[i].replace('fits','')+"*"
                 biasstring = 'b'
             else: biasstring = ''
             if masterflats == 'Y':
                 print >> tooBIG, "../FlatFielding.py reduced"+cubenumber+" c"+bins+"x"+bins+"Flat"+filters+".fits"
                 print >> tooBIG, "awk '{print "+'"cb"'+"$0}' splittedtarget"+cubenumber+" > reduced"+cubenumber
                 print >> tooBIG, "rm bs"+TARGETSdatalist[i].replace('fits','')+"* s"+TARGETSdatalist[i].replace('fits','')+"*"
                 flatstring = 'c'
             else: flatstring = ''
             if  masterflats == 'N' and  masterbias == 'N':
                 print >> tooBIG, "cp sort"+cubenumber+" reduced"+cubenumber
             print >> tooBIG, "../time.py reduced"+cubenumber
             if targetname != 'QuickLook':
                 print >> tooBIG, "../Set_Airmass_JD_HJD.py reduced"+cubenumber
             print >> tooBIG, 'mkdir ReducedData'
             print >> tooBIG, "cp reduced"+cubenumber+" temp"
             print >> tooBIG, 'awk '+"'"+'{print "ReducedData/'+'"$0}'+"'"+' temp > temptemp'
             print >> tooBIG, 'mv temptemp reduced'+cubenumber
             print >> tooBIG, 'mkdir ReducedData'
             print >> tooBIG, 'mv *s*.fits ReducedData'
             print >> tooBIG, 'mv ReducedData/*Bias.fits .'
             print >> tooBIG, 'rm temp'
             print >> tooBIG, "../Photometry.py reduced"+cubenumber+" N"
             print >> tooBIG, "../extract_lcs.py apcor.out"+cubenumber+" "+flatstring+biasstring+"s"+TARGETSdatalist[i].replace('fits','')+"0001.fits"
             print >> tooBIG, "../plot_lcs.py lightcurves_based_on_"+flatstring+biasstring+"s"+TARGETSdatalist[i].replace('fits','')+"0001"
             tooBIG.close()
             os.system('chmod a+x tooBIG')
             if fits[0].header['TRIGGER'] == 'External' or fits[0].header['TRIGGER'] == 'GPS':
                 sys.exit("The FITS file "+TARGETSdatalist[i] +" is too large. Split it into smaller cubes and try again.")
             else:
                 os.system('rm SHOCscript PHOTscript PLOTscript')
                 os.system('cp tooBIG tooBIG'+cubenumber)
                 print "#############################################################################################################################################################"
                 print "The FITS file "+TARGETSdatalist[i] +" is too large. It may be handled separately by running:               ./tooBIG "
                 print "Remove it from '"+TARGETSfile+"' and re-run the script for the rest of the files in the list. "
                 print "#############################################################################################################################################################"
                 sys.exit()
         
         fits.close()

         # SPLIT the data CUBES into separate FITS files
         print >> SHOCscript, "../slice.py "+ TARGETSdatalist[i]
         print >> SHOCscript, "cp sort"+cubenumber+' splittedtarget'+cubenumber
         print >> SHOCscript, 'rm sort*'
         print >> SHOCscript, 'rm rename*'

   #######################################
   # Create MASTER FLATS from RAW flats: #
   #######################################
   masterflats1x1 = 'N'
   masterflats2x2 = 'N'
   masterflats4x4 = 'N'
   masterflats8x8 = 'N'
   masterflats16x16 = 'N'
   flatfielded = 'N'

   if makemasterflats == 'Y':
      # Determine the binning of the FLATfiles and update their FITS HEADERS
      for i in range(len(FLATSdatalist)): 
         fits = pyfits.open(FLATSdatalist[i],mode='update')
         fits[0].header.update('OBJECT','SKYFLAT','----Source information block------')
         fits[0].header.update('RA_PNT','00:00:00','RA of source for Nominal pointing in deg')
         fits[0].header.update('DEC_PNT','00:00:00','DEC of source for Nominal pointing in deg')
         fits[0].header.update('EPOCH','0','EPOCH')
         fits[0].header.update('FILTER',filters,'WheelA WheelB')
         fits[0].header.update('OBSERVAT',site,'Observatory')
         fits[0].header.update('TELESCOP',telescope,'Telescope')
         fits[0].header.update('INSTRUME',instrument,'Instrument')
         # update fits file
         fits.flush()
         fits.close()

         # SPLIT the data CUBES into separate FITS files
         cubenumber = FLATSdatalist[i].split('.')[1]
         os.system('../slice.py '+ FLATSdatalist[i])
         os.system('cp sort'+cubenumber+' splittedflats'+cubenumber)
         os.system('rm sort*')
         os.system('rm rename*')

      # Make a list containing only the individual FLAT fits files:
      os.system('cat splittedflats* > sortedflats')
      os.system('rm splittedflats*')

      # Open lists with FLAT files per binning
      binned1x1flats = open('1x1flats'+str(filters),'w')
      binned2x2flats = open('2x2flats'+str(filters),'w')
      binned4x4flats = open('4x4flats'+str(filters),'w')
      binned8x8flats = open('8x8flats'+str(filters),'w')
      binned16x16flats = open('16x16flats'+str(filters),'w')
      binned1x1flag = 0
      binned2x2flag = 0
      binned4x4flag = 0
      binned8x8flag = 0
      binned16x16flag = 0

      splittedFLATSlist = numpy.loadtxt('sortedflats',dtype="str")   
      # Write FLAT filenames into lists per binning
      for j in range(len(splittedFLATSlist)):
         fits = pyfits.open(splittedFLATSlist[j])
         vbin = float(fits[0].header['VBIN'])
         hbin = float(fits[0].header['HBIN'])
         if vbin == 1 and hbin == 1:
            print >> binned1x1flats, splittedFLATSlist[j]
            binned1x1flag = 1
         if vbin == 2 and hbin == 2:
            print >> binned2x2flats, splittedFLATSlist[j]
            binned2x2flag = 1
         if vbin == 4 and hbin == 4:
            print >> binned4x4flats, splittedFLATSlist[j]
            binned4x4flag = 1
         if vbin == 8 and hbin == 8:
            print >> binned8x8flats, splittedFLATSlist[j]
            binned8x8flag = 1
         if vbin == 16 and hbin == 16:
            print >> binned16x16flats, splittedFLATSlist[j]
            binned16x16flag = 1

      # Add tasks to script to make master flats
      if binned1x1flag == 1:
         print >> SHOCscript, "../MasterFlats.py "+ '1x1flats'+str(filters)+' ' +str(filters)
         masterflats1x1 = 'Y'
      if binned2x2flag == 1:
         print >> SHOCscript, "../MasterFlats.py "+ '2x2flats'+str(filters)+' ' +str(filters)
         masterflats2x2 = 'Y'
      if binned4x4flag == 1:
         print >> SHOCscript, "../MasterFlats.py "+ '4x4flats'+str(filters)+' ' +str(filters)
         masterflats4x4 = 'Y'
      if binned8x8flag == 1:
         print >> SHOCscript, "../MasterFlats.py "+ '8x8flats'+str(filters)+' ' +str(filters)
         masterflats8x8 = 'Y'
      if binned16x16flag == 1:
         print >> SHOCscript, "../MasterFlats.py "+ '16x16flats'+str(filters)+' ' +str(filters)
         masterflats16x16 = 'Y'

   #######################################
   # Create MASTER BIAS from RAW bias: #
   #######################################

   masterbias1x1 = 'N'
   masterbias2x2 = 'N'
   masterbias4x4 = 'N'
   masterbias8x8 = 'N'
   masterbias16x16 = 'N'
   biased = 'N'

   if makemasterbias == 'Y':
      # Determine the binning of the BIASfiles and update their FITS HEADERS
      for i in range(len(BIASdatalist)): 
         fits = pyfits.open(BIASdatalist[i],mode='update')
         fits[0].header.update('OBJECT','BIAS','----Source information block------')
         fits[0].header.update('RA_PNT','00:00:00','RA of source for Nominal pointing in deg')
         fits[0].header.update('DEC_PNT','00:00:00','DEC of source for Nominal pointing in deg')
         fits[0].header.update('EPOCH','0','EPOCH')
         fits[0].header.update('FILTER','N.A.','WheelA WheelB')
         fits[0].header.update('OBSERVAT',site,'Observatory')
         fits[0].header.update('TELESCOP',telescope,'Telescope')
         fits[0].header.update('INSTRUME',instrument,'Instrument')
         # update fits file
         fits.flush()
         fits.close()

         # SPLIT the data CUBES into separate FITS files
         cubenumber = BIASdatalist[i].split('.')[1]
         os.system('../slice.py '+ BIASdatalist[i])
         os.system('cp sort'+cubenumber+' splittedbias'+cubenumber)
         os.system('rm sort*')
         os.system('rm rename*')

      # Make a list containing only the individual BIAS fits files:
      os.system('cat splittedbias* > sortedbias')
      os.system('rm splittedbias*')

      # Open lists with FLAT files per binning
      binned1x1bias = open('1x1bias','w')
      binned2x2bias = open('2x2bias','w')
      binned4x4bias = open('4x4bias','w')
      binned8x8bias = open('8x8bias','w')
      binned16x16bias = open('16x16bias','w')
      binned1x1flag = 0
      binned2x2flag = 0
      binned4x4flag = 0
      binned8x8flag = 0
      binned16x16flag = 0

      splittedBIASlist = numpy.loadtxt('sortedbias',dtype="str")   
      # Write FLAT filenames into lists per binning
      for j in range(len(splittedBIASlist)):
         fits = pyfits.open(splittedBIASlist[j])
         vbin = float(fits[0].header['VBIN'])
         hbin = float(fits[0].header['HBIN'])
         if vbin == 1 and hbin == 1:
            print >> binned1x1bias, splittedBIASlist[j]
            binned1x1flag = 1
         if vbin == 2 and hbin == 2:
            print >> binned2x2bias, splittedBIASlist[j]
            binned2x2flag = 1
         if vbin == 4 and hbin == 4:
            print >> binned4x4bias, splittedBIASlist[j]
            binned4x4flag = 1
         if vbin == 8 and hbin == 8:
            print >> binned8x8bias, splittedBIASlist[j]
            binned8x8flag = 1
         if vbin == 16 and hbin == 16:
            print >> binned16x16bias, splittedBIASlist[j]
            binned16x16flag = 1

      # Add tasks to script to make master bias
      if binned1x1flag == 1:
         print >> SHOCscript, "../MasterBias.py "+ '1x1bias '
         masterbias1x1 = 'Y'
      if binned2x2flag == 1:
         print >> SHOCscript, "../MasterBias.py "+ '2x2bias '
         masterbias2x2 = 'Y'
      if binned4x4flag == 1:
         print >> SHOCscript, "../MasterBias.py "+ '4x4bias '
         masterbias4x4 = 'Y'
      if binned8x8flag == 1:
         print >> SHOCscript, "../MasterBias.py "+ '8x8bias '
         masterbias8x8 = 'Y'
      if binned16x16flag == 1:
         print >> SHOCscript, "../MasterBias.py "+ '16x16bias '
         masterbias16x16 = 'Y'

   # Make sub-folder
   print >> SHOCscript, 'mkdir ReducedData'


#################################################################################
   #############################################################################
   # Do flatfielding, update HEADERS with timing information and do PHOTOMETRY #
   #############################################################################
#################################################################################

   
   if dophotometry == 'Y':
      catlist = ''
      for j in range(len(TARGETSdatalist)):
         print >> SHOCscript, "#----------------------------------------------------------------"
         cubenumber = str(TARGETSdatalist[j]).split('.')[1]

         ######################################
         # Subtract Master Bias from umages:  #
         ######################################
         if (masterbias1x1 == 'Y' or masterbias == 'Y') and vbincube[j] == 1 and hbincube[j] == 1:
               print >> SHOCscript, "../BiasCorrection.py "+"splittedtarget"+cubenumber+ " 1x1Bias"+".fits"
               biased = 'Y'
         if (masterbias2x2 == 'Y' or masterbias == 'Y') and vbincube[j] == 2 and hbincube[j] == 2:
               print >> SHOCscript, "../BiasCorrection.py "+"splittedtarget"+cubenumber+ " 2x2Bias"+".fits"
               biased = 'Y'
         if (masterbias4x4 == 'Y' or masterbias == 'Y') and vbincube[j] == 4 and hbincube[j] == 4:
               print >> SHOCscript, "../BiasCorrection.py "+"splittedtarget"+cubenumber+ " 4x4Bias"+".fits"
               biased = 'Y'
         if (masterbias8x8 == 'Y' or masterbias == 'Y') and vbincube[j] == 8 and hbincube[j] == 8:
               print >> SHOCscript, "../BiasCorrection.py "+"splittedtarget"+cubenumber+ " 8x8Bias"+".fits"
               biased = 'Y'
         if (masterbias16x16 == 'Y' or masterbias == 'Y') and vbincube[j] == 16 and hbincube[j] == 16:
               print >> SHOCscript, "../BiasCorrection.py "+"splittedtarget"+cubenumber+ " 16x16Bias"+".fits"
               biased = 'Y'

         if biased == 'Y':
               print >> SHOCscript, 'awk '+"'"+'{print "b'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "bs"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001"
               
         else:
               print >> SHOCscript, 'awk '+"'"+'{print "'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "s"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001"

         startFITSfiles.append(startFITSfile)

         if biased == 'N' and targetname != 'QuickLook':
               print '                                                                                                       '
               print '#########################################################################################################'
               print ' WARNING: Since NO appropriate MASTER BIAS were found, '+TARGETSdatalist[j]+' will NOT be bias-corrected!'
               print '#########################################################################################################'

         ###################################
         # Divide images by Master Flats:  #
         ###################################
         if (masterflats1x1 == 'Y' or masterflats == 'Y') and vbincube[j] == 1 and hbincube[j] == 1:
               print >> SHOCscript, "../FlatFielding.py "+"reduced"+cubenumber+ " c1x1Flat"+filters+".fits"
               flatfielded = 'Y'
         if (masterflats2x2 == 'Y' or masterflats == 'Y') and vbincube[j] == 2 and hbincube[j] == 2:
               print >> SHOCscript, "../FlatFielding.py "+"reduced"+cubenumber+ " c2x2Flat"+filters+".fits"
               flatfielded = 'Y'
         if (masterflats4x4 == 'Y' or masterflats == 'Y') and vbincube[j] == 4 and hbincube[j] == 4:
               print >> SHOCscript, "../FlatFielding.py "+"reduced"+cubenumber+ " c4x4Flat"+filters+".fits"
               flatfielded = 'Y'
         if (masterflats8x8 == 'Y' or masterflats == 'Y') and vbincube[j] == 8 and hbincube[j] == 8:
               print >> SHOCscript, "../FlatFielding.py "+"reduced"+cubenumber+ " c8x8Flat"+filters+".fits"
               flatfielded = 'Y'
         if (masterflats16x16 == 'Y' or masterflats == 'Y') and vbincube[j] == 16 and hbincube[j] == 16:
               print >> SHOCscript, "../FlatFielding.py "+"reduced"+cubenumber+ " c16x16Flat"+filters+".fits"
               flatfielded = 'Y'

         if flatfielded == 'N' and targetname != 'QuickLook':
               print '                                                                                                       '
               print '#########################################################################################################'
               print ' WARNING: Since NO appropriate MASTER FLATS were found, '+TARGETSdatalist[j]+' will NOT be flat-fielded!'
               print '#########################################################################################################'

         ################################################
         # Determine the filenames of the reduced files #
         ################################################
         if flatfielded == 'Y' and biased == 'Y':
               print >> SHOCscript, 'awk '+"'"+'{print "cb'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "cbs"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001"
               print >> SHOCscript, 'rm '+startFITSfile.replace('.0001','.*').replace('cbs','bs')+' '+startFITSfile.replace('.0001','.*').replace('cbs','s')
         elif flatfielded == 'N' and biased == 'Y':
               print >> SHOCscript, 'awk '+"'"+'{print "b'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "bs"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001"
               print >> SHOCscript, 'rm '+startFITSfile.replace('.0001','.*').replace('bs','s')
         elif flatfielded == 'N' and biased == 'N':
               print >> SHOCscript, 'awk '+"'"+'{print "'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "s"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001"
         elif flatfielded == 'Y' and biased == 'N':
               print >> SHOCscript, 'awk '+"'"+'{print "c'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "cs"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001"
               print >> SHOCscript, 'rm '+startFITSfile.replace('.0001','.*').replace('cs','s')

         startFITSfiles.append(startFITSfile)

         #######################################
         # Write timing information to HEADERS #
         #######################################
         print >> SHOCscript, "../time.py "+"reduced"+cubenumber
         # Set JD, Airmass and HJD in HEADERS
         if targetname != 'QuickLook':
               print >> SHOCscript, "../Set_Airmass_JD_HJD.py "+"reduced"+cubenumber

         ###################################
         # Move reduced data to sub-folder #
         ###################################
         print >> SHOCscript, "cp reduced"+cubenumber+" temp"
         print >> SHOCscript, 'awk '+"'"+'{print "ReducedData/'+'"$0}'+"'"+' temp > temptemp'
         print >> SHOCscript, 'mv temptemp reduced'+cubenumber
         print >> SHOCscript, 'rm temp'

         print >> SHOCscript, "#----------------------------------------------------------------"
         print >> SHOCscript, 'mv *s*.'+cubenumber+'.*.fits ReducedData'

         catlist = catlist+" reduced"+cubenumber
         triggerstart = trigger[j]

      reducedlist = catlist.split(' reduced')
      reducedcombined = 'reduced'+reducedlist[1]+'to'+reducedlist[-1]
      print >> SHOCscript, 'cat'+catlist+' > '+reducedcombined      

      #################
      # Do PHOTOMETRY #
      #################

      print >> PHOTscript, "../Photometry.py "+reducedcombined+" N"
      print >> PHOTscript, "#----------------------------------------------------------------"

      #######################
      # Extract lightcurves #
      #######################

      if triggerstart == 'GPS':
         startingFITSfile = startFITSfiles[0].replace('.0001','.0003')
      else:
         startingFITSfile = startFITSfiles[0]
      print >> PLOTscript, "../extract_lcs.py apcor.out"+(reducedcombined.lstrip('reduced')).split('to')[0]+" "+startingFITSfile+ ".fits"
      print >> PLOTscript, "../plot_lcs.py lightcurves_based_on_"+startingFITSfile
      print >> PLOTscript, "#----------------------------------------------------------------"

      # Comments on screen to prompt the user on next steps
      if targetname != 'QuickLook':
         print '                                                                                                       '
         print "###########################################################################################"
         print "Run the LINUX script that does all PRE-REDUCTIONS and FITS header corrections by typing:"
         print "./SHOCscript"
         print "                    OR                 "
         print "The commands contained therein can be run partially and/or repeated in the commandline."
         print "###########################################################################################"
         print '                                                                                                      '
         if TARGETSfile != '0': 
            print "###########################################################################################"
            print "Thereafter, run the LINUX script that does the PHOTOMETRY by typing:"
            print "./PHOTscript"
            print "                    OR                 "
            print "The commands contained therein can be run partially and/or repeated in the commandline."
            print "###########################################################################################"
            print '                                                                                                       '
            print "###########################################################################################"
            print "Thereafter, run the LINUX script that PLOTS raw lightcurves by typing:"
            print "./PLOTscript"
            print "                    OR                 "
            print "The commands contained therein can be run partially and/or repeated in the commandline."
            print "###########################################################################################"
         else:
            print >> SHOCscript, 'mv s*.*.fits ReducedData'
            print >> SHOCscript, 'rm PHOTscript PLOTscript'
