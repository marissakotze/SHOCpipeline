#! /usr/bin/env python

#####################################
# Data reduction Pipeline for SHOC  #
#####################################

import sys
import numpy
import pyfits
import os

#################################################
# Function: prompt user input of GPS start time #
#################################################

def changeSTARTtime(cubenumber):
   """ Promt the user for the start time of the cube if observations were externally triggered by GPS  """
   # Get the GPS trigger Start date
   GPSstartdate = raw_input("GPS (POP) start date [CCYY-MM-DD]:  ")
   checkflag = 0
   while checkflag == 0:
      if GPSstartdate.count('-')==2:
          splitGPSstartdate = GPSstartdate.split('-')
          if float(splitGPSstartdate[0])<=9999 and float(splitGPSstartdate[1])<=12 and float(splitGPSstartdate[2])<=31 and len(GPSstartdate)==10:
              checkflag = 1
      if checkflag == 0:
          GPSstartdate = raw_input("The format is:    CCYY-MM-DD   ")
   # Get the GPS trigger Start time
   GPSstarttime = raw_input("GPS (POP) start time in UT [HH:MM:SS.SSSSSSS]:  ")
   checkflag = 0
   while checkflag == 0:
      if GPSstarttime.count(':')==2:
          splitGPSstarttime = GPSstarttime.split(':')
          if float(splitGPSstarttime[0])<24 and float(splitGPSstarttime[1])<60 and float(splitGPSstarttime[2])<60:
               checkflag = 1
      if checkflag == 0:
          GPSstarttime = raw_input("The format is:    HH:MM:SS.SSSSSSS   ")
   GPSstart = GPSstartdate+'T'+GPSstarttime
   print "The 'FRAME' fits header will now be updated with the value:   "+GPSstart
   fits[0].header.update('FRAME',GPSstart,'GPS start time of the cube')   
   # return values to main program 
   return GPSstart

#################################################
# Function: Check validity of RA input format   #
#################################################

def checkRAinput(variable):
   """ Check validity of RA input format  """
   checkflag = 0
   while checkflag == 0:
      if variable.count(':')==2:
         splitvariable = variable.split(':')
         if float(splitvariable[0])<24 and float(splitvariable[1])<60 and float(splitvariable[2])<60:
             checkflag = 1
      if checkflag == 0:
         variable = raw_input("Try again. The correct format for RA is   hh:mm:ss   ")
   # return values to main program 
   return variable

#################################################
# Function: Check validity of DEC input format   #
#################################################

def checkDECinput(variable):
   """ Check validity of DEC input format  """
   checkflag = 0
   while checkflag == 0:
      if variable.count(':')==2:
         splitvariable = variable.split(':')
         if float(splitvariable[0])>=-90 and float(splitvariable[0])<=90 and float(splitvariable[1])<60 and float(splitvariable[2])<60:
             checkflag = 1
      if checkflag == 0:
         variable = raw_input("Try again. The correct format for DEC is   deg:arcmins:arcsecs   ")
   # return values to main program 
   return variable

#############################################
# Function: check user input for FILE names #
#############################################

def checkFILEname(file,FILEtype):
   checkfile = 0
   while checkfile == 0:
      try:
         inputfitslist = open(file,'r')
         checkfile = 1
      except IOError:
         file = raw_input("Invalid file name! Please supply a valid "+FILEtype+" file name in this directory:  ")
   return file

####################
##################
#  MAIN PROGRAM  #
##################
####################

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      TARGETSfile = raw_input("File containing the list of raw TARGET files (0 if none or the name of a single fits file):  ")
      if TARGETSfile != '0':
          TARGETSfile = checkFILEname(TARGETSfile,'TARGET')
      FLATSfile = raw_input("File containing the list of raw FLATS (0 if none or the name of a single fits file):  ")
      if FLATSfile != '0':
          FLATSfile = checkFILEname(FLATSfile, 'FLAT')
      BIASfile = raw_input("File containing the list of raw BIAS frames (0 if none or the name of a single fits file):  ")
      if BIASfile != '0':
          BIASfile = checkFILEname(BIASfile,'BIAS')
      targetname = raw_input("Provide Target Name (0 if n.a.): ")
      ra = raw_input("Provide Target RA [hh:mm:ss] (0 if n.a.): ")
      if ra != '0' and TARGETSfile != '0':
          ra = checkRAinput(ra)
      dec = raw_input("Provide Target DEC [deg:arcmin:arcsec] (0 if n.a.): ")
      if dec != '0' and TARGETSfile != '0':
          dec = checkDECinput(dec)
      epoch = raw_input("Provide Target EPOCH (0 if n.a): ")
      site = raw_input("Provide SITE info (e.g. SAAO): ")
      telescope = raw_input("Provide TELESCOPE info (e.g. 30in/40in/74in): ")
      instrument = raw_input("Provide INSTRUMENT info (e.g. shocnawe/shocndisbelief/shocnhorror): ")
      filters = raw_input("Provide FILTER info [<wheelA><wheelB>] (e.g. 38): ")
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
   
   if ra == '0' and dec == '0' and TARGETSfile != '0' and targetname != 'QuickLook':
      print '                                                                                                                    '
      print '####################################################################################################################'
      print ' WARNING: Since the RA and DEC of the target is not supplied, the HJD values in the lightcurves will not be correct'
      print ' However, the relative timing will be correct for those interested in variability'
      print '####################################################################################################################'

   if TARGETSfile != '0':
      TARGETSfile = checkFILEname(TARGETSfile,'TARGET')
   if FLATSfile != '0':
      FLATSfile = checkFILEname(FLATSfile, 'FLAT')
   if BIASfile != '0':
      BIASfile = checkFILEname(BIASfile,'BIAS')
   if ra != '0':
      ra = checkRAinput(ra)
   if dec != '0':
      dec = checkDECinput(dec)

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
       os.system('rm PHOTscript')
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
#   PLOTscript = open('PLOTscript','w')
#   print >> PLOTscript, "#! /bin/bash"

   # Open script file for COPYING raw data
   COPYscript = open('COPYscript','w')
   print >> COPYscript, "#! /bin/bash"

   # Compile all scripts to be executable from the commandline
   os.system('chmod a+x SHOCscript')
   os.system('chmod a+x PHOTscript')
#   os.system('chmod a+x PLOTscript')
   os.system('chmod a+x COPYscript')
 
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
      CUBEtooBIGflag = []
      tooBIGopened = 0
      tooBIGisolated = 0
      for i in range(len(TARGETSdatalist)): 
         cubenumber = TARGETSdatalist[i].split('.')[1]
         try:
            GPSstart, increment = numpy.loadtxt('GPSinfo'+cubenumber,dtype="str", unpack=True)
            GPSflag = 1
         except IOError, e: 
            GPSflag = 0
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
                 if GPSflag == 0:
                    print "############################################################################################################"
                    print "The timing was triggered via the GPS. The user must supply the appropriate information for the FITS headers:"
                    print "############################################################################################################"
                    GPSstart = changeSTARTtime(cubenumber)
                    exposure = raw_input("Supply the exposure time (POP repeat interval) in milliseconds [ms]:   ")
                    while exposure.isdigit() == False:
                       exposure = raw_input("Not a number. Supply the input in the correct format!:   ")
                    exposuresec = float(exposure)/1000
                    print "The 'EXPOSURE', 'ACT' and 'KCT' fits headers will now be updated with the value:   "+str(exposuresec)+ "   in seconds [s]"
                    GPSinfo = open('GPSinfo'+cubenumber,'w')
                    print >> GPSinfo, GPSstart, exposuresec
                 else:
                    exposuresec = increment
                    fits[0].header.update('FRAME',GPSstart,'GPS start time of the cube')
                 fits[0].header.update('EXPOSURE',exposuresec,'GPS repeat interval [s]')
                 fits[0].header.update('ACT',exposuresec,'GPS repeat interval [s]')
                 fits[0].header.update('KCT',exposuresec,'GPS repeat interval [s]')
                 fits[0].header.update('TRIGGER','GPS','Trigger mode (External)')                 
             else:
                 print "#####################################################################################################################"
                 print " The timing appears to have been triggered externally, but the timing mode that was used is not currently supported."
                 print "#####################################################################################################################"
                 os.system('rm SHOCscript PHOTscript')
                 sys.exit()
         elif fits[0].header['TRIGGER'] == 'Internal':
             fits[0].header.update('FRAME',fits[0].header['FRAME'],'End of 1st Exposure in Data Cube')
         elif fits[0].header['TRIGGER'] == 'External Start':
             if GPSflag == 0:
                print "######################################################################################################################"
                print "The timing was triggered externally. The user is required to supply the appropriate information for the FITS headers:"
                print "######################################################################################################################"
                GPSstart = changeSTARTtime(cubenumber)
                exposureseconds = float(fits[0].header['EXPOSURE']) + 0.00676
                GPSinfo = open('GPSinfo'+cubenumber,'w')
                print >> GPSinfo, GPSstart, exposureseconds
             else:
                exposureseconds = increment
                fits[0].header.update('FRAME',GPSstart,'GPS start time of the cube')
             fits[0].header.update('ACT',exposureseconds,'Integration cycle time [s]')
             fits[0].header.update('KCT',exposureseconds,'Kinetic cycle time [s]')

         elif fits[0].header['TRIGGER'] != 'GPS':
             print "##########################################################"
             print " The timing mode that was used is not currently supported."
             print "##########################################################"
             os.system('rm SHOCscript PHOTscript')
             sys.exit()
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

         # SAVE the updated FITS cube if it can, otherwise set up an alternate route (tooBIG)
         try:
             fits.flush()
             tooBIGflag = 0
             fits.close()
         except ValueError:
             tooBIGflag = 1
             if tooBIGopened == 0:
                 tooBIG =  open('tooBIG','w')
                 print >> tooBIG, "#! /bin/bash" 
                 print >> tooBIG, "rm tmp*"     
                 tooBIGopened = 1   
         CUBEtooBIGflag.append(tooBIGflag)     
    
         # SPLIT the data CUBES into separate FITS files
         if tooBIGflag == 0:
             print >> SHOCscript, "../slice.py "+ TARGETSdatalist[i]
             print >> SHOCscript, "cp sort"+cubenumber+' splittedtarget'+cubenumber
             print >> SHOCscript, 'rm sort*'
             print >> SHOCscript, 'rm rename*'
         if tooBIGflag == 1 and tooBIGisolated == 0:
             print >> tooBIG, "../slice.py "+TARGETSdatalist[i]
             print >> tooBIG, "../SHOCpipeline.py sort"+cubenumber+" "+FLATSfile+" "+BIASfile+" '"+targetname+"' "+ra+" "+dec+" "+epoch+" "+site+" "+telescope+" "+instrument+" "+filters
             print >> tooBIG, 'rm SHOCscript PHOTscript'      
             print >> tooBIG, "cp sort"+cubenumber+" splittedtarget"+cubenumber
             tooBIGisolated = 1

   #######################################
   # Create MASTER FLATS from RAW flats: #
   #######################################
   flatfielded = 'N'
   vbinflat = []
   hbinflat = []
   flatfiles = []

   if makemasterflats == 'Y':
      # Determine the binning of the FLATfiles and update their FITS HEADERS
      for i in range(len(FLATSdatalist)): 
         fits = pyfits.open(FLATSdatalist[i],mode='update')
         vbinflattemp = fits[0].header['VBIN']
         hbinflattemp = fits[0].header['HBIN']
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

         # Determine unique binnings among FLAT files
         flatfilename = str(vbinflattemp)+'x'+str(hbinflattemp)+"flats"+str(filters)        
         if flatfiles.count(flatfilename) < 1:
            flatfiles.append(flatfilename)
            vbinflat.append(vbinflattemp)
            hbinflat.append(hbinflattemp)
            print >> SHOCscript, "../MasterFlats.py "+ flatfilename+' ' +str(filters)

      # Make a list containing only the individual FLAT fits files:
      os.system('cat splittedflats* > sortedflats')
      os.system('rm splittedflats*')

      splittedFLATSlist = numpy.loadtxt('sortedflats',dtype="str")   
      # Write FLAT filenames into lists per binning
      for i in range(len(flatfiles)):
         flatfile = open(flatfiles[i],'w')
         for j in range(len(splittedFLATSlist)):
            fits = pyfits.open(splittedFLATSlist[j])
            vbin = fits[0].header['VBIN']
            hbin = fits[0].header['HBIN']
            if vbin == vbinflat[i] and hbin == hbinflat[i]:
               print >> flatfile, splittedFLATSlist[j]


   #######################################
   # Create MASTER BIAS from RAW bias: #
   #######################################
   #######################################
   # Create MASTER BIAS from RAW bias: #
   #######################################
   biased = 'N'
   vbinbias = []
   hbinbias = []
   biasfiles = []

   if makemasterbias == 'Y':
      # Determine the binning of the BIASfiles and update their FITS HEADERS
      for i in range(len(BIASdatalist)): 
         fits = pyfits.open(BIASdatalist[i],mode='update')
         vbinbiastemp = fits[0].header['VBIN']
         hbinbiastemp = fits[0].header['HBIN']
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

         # Determine unique binnings among BIAS files
         biasfilename = str(vbinbiastemp)+'x'+str(hbinbiastemp)+"bias"        
         if biasfiles.count(biasfilename) < 1:
            biasfiles.append(biasfilename)
            vbinbias.append(vbinbiastemp)
            hbinbias.append(hbinbiastemp)
            print >> SHOCscript, "../MasterBias.py "+ biasfilename

      # Make a list containing only the individual BIAS fits files:
      os.system('cat splittedbias* > sortedbias')
      os.system('rm splittedbias*')

      splittedBIASlist = numpy.loadtxt('sortedbias',dtype="str")   
      # Write BIAS filenames into lists per binning
      for i in range(len(biasfiles)):
         biasfile = open(biasfiles[i],'w')
         for j in range(len(splittedBIASlist)):
            fits = pyfits.open(splittedBIASlist[j])
            vbin = fits[0].header['VBIN']
            hbin = fits[0].header['HBIN']
            if vbin == vbinbias[i] and hbin == hbinbias[i]:
               print >> biasfile, splittedBIASlist[j]


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
         observationdate = TARGETSdatalist[i].split('.')[0]

         ######################################
         # Subtract Master Bias from umages:  #
         ######################################

         for i in range(len(biasfiles)):
            if vbincube[j] == vbinbias[i] and hbincube[j] == hbinbias[i]:
               biased = 'Y'
               print >> SHOCscript, "../BiasCorrection.py "+"splittedtarget"+cubenumber+" "+str(vbinbias[i])+'x'+str(hbinbias[i])+"Bias"+".fits"

         if masterbias == 'Y':
            biasstring = 'b'
            biased = 'Y'
            defaultBIAS = str(int(vbincube[j]))+'x'+str(int(hbincube[j]))+"Bias"+".fits"
            suppliedmasterbias = raw_input("Supply the name of the appropriate master BIAS file (default: "+defaultBIAS+"):  ")
            if suppliedmasterbias == '':
               suppliedmasterbias = defaultBIAS
            if CUBEtooBIGflag[j] == 0:               
               print >> SHOCscript, "../BiasCorrection.py "+"splittedtarget"+cubenumber+" "+suppliedmasterbias               
            else:
               print >> tooBIG, "../BiasCorrection.py splittedtarget"+cubenumber+" "+suppliedmasterbias
         else: biasstring = ''

         if biased == 'Y':
            if CUBEtooBIGflag[j] == 0:
               print >> SHOCscript, 'awk '+"'"+'{print "b'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "bs"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001"
            else:
               print >> tooBIG, "awk '{print "+'"b"'+"$0}' splittedtarget"+cubenumber+" > reduced"+cubenumber
               print >> tooBIG, "rm s"+TARGETSdatalist[j].replace('fits','')+"*"
         else:
               print >> SHOCscript, 'awk '+"'"+'{print "'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "s"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001"

         if biased == 'N' and targetname != 'QuickLook':
               print '                                                                                                       '
               print '#########################################################################################################'
               print ' WARNING: Since NO appropriate MASTER BIAS were found, '+TARGETSdatalist[j]+' will NOT be bias-corrected!'
               print '#########################################################################################################'

         ###################################
         # Divide images by Master Flats:  #
         ###################################
         for i in range(len(flatfiles)):
            if vbincube[j] == vbinflat[i] and hbincube[j] == hbinflat[i]:
               flatfielded = 'Y'
               print >> SHOCscript, "../FlatFielding.py "+"reduced"+cubenumber+ " c"+str(vbinflat[i])+'x'+str(hbinflat[i])+"Flat"+str(filters)+".fits"

         if masterflats == 'Y':
            flatstring = 'c'
            flatfielded = 'Y'
            defaultFLAT = 'c'+str(int(vbincube[j]))+'x'+str(int(hbincube[j]))+"Flat"+str(filters)+".fits"
            suppliedmasterflat = raw_input("Supply the name of the appropriate master FLAT file (default: "+defaultFLAT+"):  ")
            if suppliedmasterflat == '':
               suppliedmasterflat = defaultFLAT
            if CUBEtooBIGflag[j] == 0:
               print >> SHOCscript, "../FlatFielding.py "+"reduced"+cubenumber+ " "+suppliedmasterflat
            else:
               print >> tooBIG, "../FlatFielding.py reduced"+cubenumber+" "+suppliedmasterflat
               print >> tooBIG, "awk '{print "+'"cb"'+"$0}' splittedtarget"+cubenumber+" > reduced"+cubenumber
               print >> tooBIG, "rm bs"+TARGETSdatalist[j].replace('fits','')+"* s"+TARGETSdatalist[j].replace('fits','')+"*"               
         else: flatstring = ''

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
            if CUBEtooBIGflag[j] == 0:
               print >> SHOCscript, 'awk '+"'"+'{print "'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "s"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001"
            else:
               print >> tooBIG, "cp sort"+cubenumber+" reduced"+cubenumber
         elif flatfielded == 'Y' and biased == 'N':
               print >> SHOCscript, 'awk '+"'"+'{print "c'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "cs"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001"
               print >> SHOCscript, 'rm '+startFITSfile.replace('.0001','.*').replace('cs','s')

         startFITSfiles.append(startFITSfile)

         #######################################
         # Write timing information to HEADERS #
         #######################################
         if CUBEtooBIGflag[j] == 0:
            print >> SHOCscript, "../time.py "+"reduced"+cubenumber
         else:
            print >> tooBIG, "../time.py reduced"+cubenumber
         # Set JD, Airmass and HJD in HEADERS
         if targetname != 'QuickLook':
            if CUBEtooBIGflag[j] == 0:
               print >> SHOCscript, "../Set_Airmass_JD_HJD.py "+"reduced"+cubenumber
            else:
               print >> tooBIG, "../Set_Airmass_JD_HJD.py reduced"+cubenumber

         triggerstart = trigger[j]

         ###################################
         # Move reduced data to sub-folder #
         ###################################
         if CUBEtooBIGflag[j] == 0:
            print >> SHOCscript, "cp reduced"+cubenumber+" temp"
            print >> SHOCscript, 'awk '+"'"+'{print "ReducedData/'+'"$0}'+"'"+' temp > temptemp'
            print >> SHOCscript, 'mv temptemp reduced'+cubenumber
            print >> SHOCscript, 'rm temp'
            print >> SHOCscript, 'mv *s*.'+cubenumber+'.*.fits ReducedData'
            print >> SHOCscript, 'echo "########################################################################################"'
            print >> SHOCscript, 'echo "# Individual FITS files with corrected headers are saved in the ReducedData folder.    #"'
            if targetname != 'QuickLook':
               print >> SHOCscript, 'echo "# The raw fits cube will now be deleted, but may be retrieved by running: ./COPYscript #"'
            else:
               print >> SHOCscript, 'echo "# The raw fits cube will now be deleted                                                #"'
            print >> SHOCscript, 'echo "########################################################################################"'
            if targetname != 'QuickLook':
               print >> COPYscript, 'scp ccd'+telescope.rstrip('in')+'@ltsp.suth.saao.ac.za:/data/'+telescope+'/'+instrument+'/'+observationdate[0:4]+'/'+observationdate[4:8]+'/'+TARGETSdatalist[j]+' .'
            else:
               print >> COPYscript, 'scp ccdX@ltsp.suth.saao.ac.za:/data/Xin/shocnY/'+observationdate[0:4]+'/'+observationdate[4:8]+'/'+TARGETSdatalist[j]+' .'
               print >> COPYscript, '# where X = 30/40/74 for 0.75m/1.0m/1.9m and Y = awe/disbelief/horror'
            print >> SHOCscript, 'rm '+ TARGETSdatalist[j]
            print >> SHOCscript, "#----------------------------------------------------------------"
         else:
            print >> tooBIG, "cp reduced"+cubenumber+" temp"
            print >> tooBIG, 'awk '+"'"+'{print "ReducedData/'+'"$0}'+"'"+' temp > temptemp'
            print >> tooBIG, 'mv temptemp reduced'+cubenumber
            print >> tooBIG, 'rm temp'
            print >> tooBIG, 'mkdir ReducedData'
            print >> tooBIG, 'mv *s*.'+cubenumber+'.*.fits ReducedData'
            print >> tooBIG, 'echo "########################################################################################"'
            print >> tooBIG, 'echo "# Individual FITS files with corrected headers are saved in the ReducedData folder.    #"'
            if targetname != 'QuickLook':
               print >> tooBIG, 'echo "# The raw fits cube will now be deleted, but may be retrieved by running: ./COPYscript #"'
            else:
               print >> tooBIG, 'echo "# The raw fits cube will now be deleted                                                #"'
            print >> tooBIG, 'echo "########################################################################################"'
            if targetname != 'QuickLook':
               print >> COPYscript, 'scp ccd'+telescope.rstrip('in')+'@ltsp.suth.saao.ac.za:/data/'+telescope+'/'+instrument+'/'+observationdate[0:4]+'/'+observationdate[4:8]+'/'+TARGETSdatalist[j]+' .'
            else:
               print >> COPYscript, 'scp ccdX@ltsp.suth.saao.ac.za:/data/Xin/shocnY/'+observationdate[0:4]+'/'+observationdate[4:8]+'/'+TARGETSdatalist[j]+' .'
               print >> COPYscript, '# where X = 30/40/74 for 0.75m/1.0m/1.9m and Y = awe/disbelief/horror'
            print >> tooBIG, 'rm '+ TARGETSdatalist[j]
            print >> tooBIG, "#----------------------------------------------------------------"
            print >> tooBIG, "../Photometry.py reduced"+cubenumber+" N"
            print >> tooBIG, "#----------------------------------------------------------------"
#            if triggerstart == 'GPS' or triggerstart == 'External':
#               print >> tooBIG, "../extract_lcs.py apcor.out"+cubenumber+" "+flatstring+biasstring+"s"+TARGETSdatalist[j].replace('fits','')+"0003.fits"
#               print >> tooBIG, "../plot_lcs.py lightcurves_based_on_"+flatstring+biasstring+"s"+TARGETSdatalist[j].replace('fits','')+"0003"
#            else:
#               print >> tooBIG, "../extract_lcs.py apcor.out"+cubenumber+" "+flatstring+biasstring+"s"+TARGETSdatalist[j].replace('fits','')+"0001.fits"
#               print >> tooBIG, "../plot_lcs.py lightcurves_based_on_"+flatstring+biasstring+"s"+TARGETSdatalist[j].replace('fits','')+"0001"
#            print >> tooBIG, "#----------------------------------------------------------------"
            tooBIG.close()
            os.system('chmod a+x tooBIG')
            os.system('rm SHOCscript PHOTscript')
            os.system('cp tooBIG tooBIG'+cubenumber)
            print "######################################################################################################################"
            print "The FITS file "+TARGETSdatalist[j] +" is too large. It may be handled separately by running:           ./tooBIG"+cubenumber
            if j >0:
               print "Remove it from '"+TARGETSfile+"' and re-run the script for the rest of the files in the list. "
            print "######################################################################################################################"
            sys.exit()
         catlist = catlist+" reduced"+cubenumber

      reducedlist = catlist.split(' reduced')
      reducedcombined = 'reduced'+reducedlist[1]+'to'+reducedlist[-1]
      print >> SHOCscript, 'cat'+catlist+' > '+reducedcombined     

      #################
      # Do PHOTOMETRY #
      #################
      if CUBEtooBIGflag[j] == 0:
         print >> PHOTscript, "../Photometry.py "+reducedcombined+" N"
         print >> PHOTscript, "#----------------------------------------------------------------"

      #######################
      # Extract lightcurves #
      #######################

#         if triggerstart == 'GPS':
#            startingFITSfile = startFITSfiles[0].replace('.0001','.0003')
#         else:
#            startingFITSfile = startFITSfiles[0]
#         print >> PLOTscript, "../extract_lcs.py apcor.out"+(reducedcombined.lstrip('reduced')).split('to')[0]+" "+startingFITSfile+ ".fits"
#         print >> PLOTscript, "../plot_lcs.py lightcurves_based_on_"+startingFITSfile
#         print >> PLOTscript, "#----------------------------------------------------------------"

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
            print >> SHOCscript, 'rm PHOTscript'
