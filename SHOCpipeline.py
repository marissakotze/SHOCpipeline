#! /usr/bin/env python

#####################################
#####################################
# Data reduction Pipeline for SHOC  #
#####################################
#####################################

# IMPORT Python plug-ins
import sys
import numpy
import pyfits
import os


#################
################
#  FUNCTIONS  #
################
#################

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

#################################################
# Function: check user input for Y/N questions  #
#################################################

def checkYNinput(variable):
   """ Prompt the user again if invalid input was supplied  """
   while variable not in ('Y','y','N','n',''):
      variable = raw_input("Invalid input. The format is Y or N? ")   
   # return values to main program 
   return variable

#################################################
# Function: check validity of master FLAT/BIAS  #
#################################################

def checkBINNING(suppliedfile,FILEtype,hbin,vbin,subframe):
   """ Binning for target files and supplied master BIAS/FLAT must be the same. Allow the user to choose to continue regardless  """
   suppliedfile = checkFILEname(suppliedfile,FILEtype)
   fits = pyfits.open(suppliedfile)
   hbinsupplied = str(fits[0].header['HBIN'])
   vbinsupplied = str(fits[0].header['VBIN'])
   dimsupplied = str(fits[0].header['SUBRECT'])
   hbin = str(int(hbin))
   vbin = str(int(vbin))
   if hbinsupplied != hbin or vbinsupplied != vbin or dimsupplied != subframe:
      print '                                                                                                       '
      print '#########################################################################################################'
      print ' WARNING: Target files are binned at '+hbin+'x'+vbin+' but '+FILEtype+' at '+hbinsupplied+'x'+vbinsupplied
      print '          and Target files are subframed at '+subframe+' but '+FILEtype+' at '+dimsupplied
      print '          Subsequently '+TARGETSdatalist[j]+' will NOT be '+FILEtype.strip('master ')+' corrected!'
      print '#########################################################################################################'
      userprompt = raw_input("Do you wish to continue regardless? (Y/N):  ")
      userprompt = checkYNinput(userprompt)
      if userprompt not in ('Y','y'):
         sys.exit()
      suppliedfile = 'dud'
   # return values to main program 
   return suppliedfile


####################
##################
#  MAIN PROGRAM  #
##################
####################


if __name__=='__main__':
   _nargs = len(sys.argv)
   ################
   #  User inputs #
   ################
   # Prompt user for inputs
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
   # Inputs from arguments in command line
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

   # Open file for saving inputs given to SHOCpipeline.py
   SHOCpipelineINPUTS = open('SHOCpipelineINPUTS','w')
   print >> SHOCpipelineINPUTS, "../SHOCpipeline.py "+TARGETSfile+" "+FLATSfile+" "+BIASfile+" "+targetname+" "+ra+" "+dec+" "+epoch+" "+site+" "+telescope+" "+instrument+" "+filters
   SHOCpipelineINPUTS.close()
   os.system('chmod a+x SHOCpipelineINPUTS')

   # Determine if the main control script executing is the tooBIG scenario (alternate route for cubes > 2GB)
   if TARGETSfile.count('sort')>0 and FLATSfile=='0' and BIASfile=='0':
      tooBIGexecuting = 1
   else:
      tooBIGexecuting = 0

   # Warn the user if the RA and DEC is 0s. For quicklook the user should know this anyway!
   if ra == '0' and dec == '0' and TARGETSfile != '0' and targetname != 'QuickLook':
      print '                                                                                                                    '
      print '####################################################################################################################'
      print ' WARNING: Since the RA and DEC of the target is not supplied, the HJD values in the lightcurves will not be correct'
      print ' However, the relative timing will be correct for those interested in variability'
      print '####################################################################################################################'

   # Check the validity of filenames supplied
   if TARGETSfile != '0':
      TARGETSfile = checkFILEname(TARGETSfile,'TARGET')
   if FLATSfile != '0':
      FLATSfile = checkFILEname(FLATSfile, 'FLAT')
   if BIASfile != '0':
      BIASfile = checkFILEname(BIASfile,'BIAS')
   # Check the validity of RA and DEC values supplied
   if ra != '0':
      ra = checkRAinput(ra)
   if dec != '0':
      dec = checkDECinput(dec)

   # Correct the permissions of the fits cubes to avoid access issues
   os.system('chmod 754 *fits')      
   # Create symbolic link to user's login.cl in their IRAF directory
   os.system('ln -s ../iraf/login.cl login.cl')

   # Copy the 'defaultparameters' to 'parameters' (which the user may edit) if the latter is not already present
   try:
      f = open('parameters','r')
   except IOError, e: 
      os.system('cp ../defaultparameters parameters')

   ####################
   # Determine tasks  #
   ####################

   masterbias = 'N'
   masterflats = 'N'
   dophotometry = 'N'

   # Determine if masterflats need to be made and the list of FLATS cubes to use
   if targetname != 'QuickLook' and tooBIGexecuting == 0: 
       if FLATSfile == '0':
           makemasterflats = 'N'
           print 'There were no raw FLATS supplied.'
           masterflats = raw_input("Are the appropriate MASTER FLATS available? (Y/N):  ")
           masterflats = checkYNinput(masterflats)
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

   # Determine if only masterflats and masterbias need to be made, or photometry on TARGET cubes also
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

   # Determine if masterbias need to be made and the list of BIAS cubes to use
   if targetname != 'QuickLook' and tooBIGexecuting == 0:
       if BIASfile == '0':
           makemasterbias = 'N'
           print 'There were no raw BIAS frames supplied.'
           masterbias = raw_input("Are the appropriate MASTER BIAS files available? (Y/N):  ")
           masterbias = checkYNinput(masterbias)
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
   tooBIGflag = 0

   # Open script file for PRE-REDUCTIONS
   SHOCscript = open('SHOCscript','w')
   print >> SHOCscript, "#! /bin/bash"

   # Open script file for PHOTOMETRY
   PHOTscript = open('PHOTscript','w')
   print >> PHOTscript, "#! /bin/bash"

   # Open script file for COPYING raw data
   COPYscript = open('COPYscript','w')
   print >> COPYscript, "#! /bin/bash"

   # Compile all scripts to be executable from the commandline
   os.system('chmod a+x SHOCscript')
   os.system('chmod a+x PHOTscript')
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
      dimcube = []
      EMmode = [] 
      trigger = []
      CUBEtooBIGflag = []
      tooBIGopened = 0
      tooBIGisolated = 0
      for i in range(len(TARGETSdatalist)): 
         cubenumberlist = TARGETSdatalist[i].split('.')
         # Distinguish the cubenumber for the Spooling scenario
         if TARGETSdatalist[i].count('_')==0:
            cubenumber = cubenumberlist[1]
         else:
            cubenumber = cubenumberlist[1]+cubenumberlist[2]
         # Check if the GPSinfo has already been supplied for a cube (or the parent cube in the case of Spooling scenario)
         try:
            if cubenumber.count('_') > 0:
               GPSstart, increment = numpy.loadtxt('GPSinfo'+cubenumber.split('_')[0],dtype="str", unpack=True)
            else:
               GPSstart, increment = numpy.loadtxt('GPSinfo'+cubenumber,dtype="str", unpack=True)
            GPSflag = 1
         except IOError, e: 
            GPSflag = 0
         # Open the fits cube and attempt to correct its primary header (there is only one header per cube)
         fits = pyfits.open(TARGETSdatalist[i],mode='update')
         vbincube.append(float(fits[0].header['VBIN']))
         hbincube.append(float(fits[0].header['HBIN']))
         dimcube.append(fits[0].header['SUBRECT'])
         EMmode.append(fits[0].header['OUTPTAMP'])
         # Populate the missing FITS headers
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
         # Correct TIMING headers for GPS triggered frames
         if fits[0].header['TRIGGER'] == 'External':
             if float(fits[0].header['EXPOSURE']) == 0.00001: 
                 if GPSflag == 0:
                    print "######################################################################################################################################"
                    print "The timing for "+TARGETSdatalist[i]+" was triggered via the GPS. The user must supply the appropriate information for the FITS headers :"
                    print "######################################################################################################################################"
                    GPSstart = changeSTARTtime(cubenumber)
                    exposure = raw_input("Supply the exposure time (POP repeat interval) in milliseconds [ms]:   ")
                    while exposure.isdigit() == False:
                       exposure = raw_input("Not a number. Supply the input in the correct format!:   ")
                    exposuresec = float(exposure)/1000
                    print "The 'EXPOSURE', 'ACT' and 'KCT' fits headers will now be updated with the value:   "+str(exposuresec)+ "   in seconds [s]"
                    GPSinfo = open('GPSinfo'+cubenumber,'w')
                    print >> GPSinfo, GPSstart, exposuresec
                    GPSinfo.close()
                 else:
                    exposuresec = increment
                    fits[0].header.update('FRAME',GPSstart,'GPS start time of the cube')
                 fits[0].header.update('EXPOSURE',exposuresec,'GPS repeat interval [s]')
                 fits[0].header.update('ACT',exposuresec,'GPS repeat interval [s]')
                 fits[0].header.update('KCT',exposuresec,'GPS repeat interval [s]')
                 fits[0].header.update('TRIGGER','GPS','Trigger mode (External)')                 
             else:
                 print "###############################################################################################################################################"
                 print " The timing for "+TARGETSdatalist[i]+" appears to have been triggered externally, but the timing mode that was used is not currently supported."
                 print "###############################################################################################################################################"
                 os.system('rm SHOCscript PHOTscript')
                 sys.exit()
         # Correct TIMING headers for Internally triggered frames
         elif fits[0].header['TRIGGER'] == 'Internal':
             fits[0].header.update('FRAME',fits[0].header['FRAME'],'End of 1st Exposure in Data Cube')
         # Correct TIMING headers for GPS triggered start with subsequent Internal triggering of frames
         elif fits[0].header['TRIGGER'] == 'External Start':
             if GPSflag == 0:
                print "############################################################################################################################################"
                print "The timing "+TARGETSdatalist[i]+" was triggered externally. The user is required to supply the appropriate information for the FITS headers:"
                print "############################################################################################################################################"
                GPSstart = changeSTARTtime(cubenumber)
                exposureseconds = float(fits[0].header['EXPOSURE']) + 0.00676
                GPSinfo = open('GPSinfo'+cubenumber,'w')
                print >> GPSinfo, GPSstart, exposureseconds
                GPSinfo.close()
             else:
                exposureseconds = increment
                fits[0].header.update('FRAME',GPSstart,'GPS start time of the cube')
             fits[0].header.update('ACT',exposureseconds,'Integration cycle time [s]')
             fits[0].header.update('KCT',exposureseconds,'Kinetic cycle time [s]')
         # Warn user if unsupported triggering mode was used and exit
         elif fits[0].header['TRIGGER'] != 'GPS':
             print "######################################################################################"
             print " The timing mode that was used for "+TARGETSdatalist[i]+" is not currently supported."
             print "######################################################################################"
             os.system('rm SHOCscript PHOTscript')
             sys.exit()
         trigger.append(str(fits[0].header['TRIGGER']))

         # Determine theoreticel Read-out noise and populate the 'RON' header (and 'SENSITIVIY' if it is absent)
         for j in range(len(serialnr)): 
             if float(fits[0].header['HIERARCH SENSITIVITY'])== float(sensitivity[j]) and float(fits[0].header['SERNO'])== float(serialnr[j]):
                 fits[0].header.update('RON',readnoise[j],'Read-out Noise')
                 tempreadnoise = readnoise[j]
             elif str(fits[0].header['SERNO']) == serialnr[j] and str(fits[0].header['PREAMP'])== preAmp[j] and float(fits[0].header['READTIME']) == float(readtime[j]) and fits[0].header['OUTPTAMP'] == mode[j]:
                 fits[0].header.update('RON',readnoise[j],'Read-out Noise') 
                 tempreadnoise = readnoise[j]
                 fits[0].header.update('SENSITIV',sensitivity[j],'Sensitivity of 0 replaced from RON Table')  

         if tempreadnoise == 0:
             print "WARNING: the Read-out noise value could not be determined for: "+ str(TARGETSdatalist[i])
         # for CONVENTIONAL mode the fits-header 'GAIN'=0 and the real value for GAIN is in fits-header 'SENSITIVITY' [e/ADU]
         if fits[0].header['OUTPTAMP'] == 'Conventional':
             fits[0].header.update('GAIN',fits[0].header['HIERARCH SENSITIVITY'], 'Replaced 0 with actual gain from SENSITIVITY')   
         # For EM mode the READNOISE and GAIN values equals the specification sheet values divided by the value given in the GAIN keyword. 
         # And if GAIN = 0 change it to GAIN = 1 and use the RON and GAIN from the specification sheet. Once changed to 1 it won't be changed again.
         if fits[0].header['OUTPTAMP'] == 'Electron Multiplying':
             if float(fits[0].header['GAIN']) == 0:
                 fits[0].header.update('GAIN','1', 'Replaced value of '+str(fits[0].header['GAIN']))
             elif float(fits[0].header['GAIN']) > 1:
                 fits[0].header.update('RON',float(tempreadnoise)/float(fits[0].header['GAIN']),'Read-out Noise')
                 fits[0].header.update('GAIN',float(fits[0].header['GAIN'])/float(fits[0].header['GAIN']), 'Replaced value of '+str(fits[0].header['GAIN']))

         # SAVE the updated FITS cube if it can, otherwise set up an alternate SHOCscript route (tooBIG)
         try:
             fits.flush()
             tooBIGflag = 0
             fits.close()
         except (ValueError,MemoryError):
             tooBIGflag = 1
             if tooBIGopened == 0:
                 tooBIG =  open('tooBIG','w')
                 print >> tooBIG, "#! /bin/bash" 
                 print >> tooBIG, "rm tmp*"     
                 tooBIGopened = 1   
                 # Note that closing a fits file that could not be flushed, causes the file to be corrupted
         CUBEtooBIGflag.append(tooBIGflag)     
    
         # SPLIT the data CUBES into separate FITS image files (one frame each)
         if tooBIGflag == 0:
             print >> SHOCscript, "../slice.py "+ TARGETSdatalist[i]
             print >> SHOCscript, "cp sort"+cubenumber+' splittedtarget'+cubenumber
             print >> SHOCscript, 'rm sort*'
             print >> SHOCscript, 'rm rename*'
         if tooBIGflag == 1 and tooBIGisolated == 0:
             print >> tooBIG, "../slice.py "+TARGETSdatalist[i]
             FLATSfile = '0'
             BIASfile = '0'
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
   dimflat = []
   flatfiles = []

   if makemasterflats == 'Y':
      # Determine the binning of the FLATfiles and update their FITS HEADERS
      for i in range(len(FLATSdatalist)): 
         fits = pyfits.open(FLATSdatalist[i],mode='update')
         vbinflattemp = fits[0].header['VBIN']
         hbinflattemp = fits[0].header['HBIN']
         dimflat.append(fits[0].header['SUBRECT'])
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
         flatfile.close()
         if tooBIGflag == 0:
            print >> SHOCscript, "../MasterFlats.py "+ flatfiles[i]+' ' +str(filters)
         else:
            os.system("../MasterFlats.py "+ flatfiles[i]+' ' +str(filters))
         masterflats = 'Y'


   #######################################
   # Create MASTER BIAS from RAW bias: #
   #######################################

   biased = 'N'
   vbinbias = []
   hbinbias = []
   dimbias = []
   biasfiles = []
   EMmodebias = []

   if makemasterbias == 'Y':
      # Determine the binning of the BIASfiles and update their FITS HEADERS
      for i in range(len(BIASdatalist)): 
         fits = pyfits.open(BIASdatalist[i],mode='update')
         vbinbiastemp = fits[0].header['VBIN']
         hbinbiastemp = fits[0].header['HBIN']
         dimbias.append(fits[0].header['SUBRECT'])
         EMmodebias.append(fits[0].header['OUTPTAMP'])
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

      # Make a list containing only the individual BIAS fits files:
      os.system('cat splittedbias* > sortedbias')
      os.system('rm splittedbias*')

      # Write BIAS filenames into lists per binning
      splittedBIASlist = numpy.loadtxt('sortedbias',dtype="str")   
      for i in range(len(biasfiles)):
         biasfile = open(biasfiles[i],'w')
         for j in range(len(splittedBIASlist)):
            fits = pyfits.open(splittedBIASlist[j])
            vbin = fits[0].header['VBIN']
            hbin = fits[0].header['HBIN']
            if vbin == vbinbias[i] and hbin == hbinbias[i]:
               print >> biasfile, splittedBIASlist[j]
         biasfile.close()
         if tooBIGflag == 0:
            print >> SHOCscript, "../MasterBias.py "+ biasfiles[i]
         else:
            os.system("../MasterBias.py "+ biasfiles[i])
         masterbias = 'Y'

   #############################################################################
   # Do flatfielding, update HEADERS with timing information and do PHOTOMETRY #
   #############################################################################

   biasflag = 0
   flatflag = 0
   if dophotometry == 'Y':
      catlist = ''
      for j in range(len(TARGETSdatalist)):
         print >> SHOCscript, "#----------------------------------------------------------------"
         # Distinguish the cubenumber for the Spooling scenario
         cubenumberlist = TARGETSdatalist[j].split('.')
         if TARGETSdatalist[j].count('_')==0:
            cubenumber = cubenumberlist[1]
         else:
            cubenumber = cubenumberlist[1]+cubenumberlist[2]
         # Extract Observation date (night where observing started) from the filenames [ONLY used in COPYscript]
         observationdate = str(TARGETSdatalist[j]).split('.')[0]

         ######################################
         # Subtract Master Bias from images:  #
         ######################################

         defaultBIAS = str(int(vbincube[j]))+'x'+str(int(hbincube[j]))+"Bias"+".fits"

         # Do Bias subtraction if appropriate raw bias frames we included
         for i in range(len(biasfiles)):
            if vbincube[j] == vbinbias[i] and hbincube[j] == hbinbias[i] and dimcube[j] == dimbias[i]:
               biased = 'Y'
               biasstring = 'b'
               if CUBEtooBIGflag[j] == 0:
                  print >> SHOCscript, "../BiasCorrection.py "+"splittedtarget"+cubenumber+" "+defaultBIAS
               else:
                  print >> tooBIG, "../BiasCorrection.py splittedtarget"+cubenumber+" "+defaultBIAS

         # Do Bias-subtraction if appropriate master bias is already available
         if masterbias == 'Y' and makemasterbias == 'N':
            biasstring = 'b'
            biased = 'Y'
            if CUBEtooBIGflag[j] == 0 and tooBIGexecuting == 0 and makemasterbias == 'N' and biasflag == 0:
               suppliedmasterbias = raw_input("Supply the name of the appropriate master BIAS file (default: "+defaultBIAS+"):  ")
               biasflag = 1
            else:
               suppliedmasterbias = ''
            if suppliedmasterbias == '':
               suppliedmasterbias = defaultBIAS
            if CUBEtooBIGflag[j] == 0:
               suppliedmasterbias = checkFILEname(suppliedmasterbias,'master BIAS')
               suppliedmasterbias = checkBINNING(suppliedmasterbias,'master BIAS',hbincube[j],vbincube[j],dimcube[j])
            if suppliedmasterbias != 'dud':
               if CUBEtooBIGflag[j] == 0:               
                  print >> SHOCscript, "../BiasCorrection.py "+"splittedtarget"+cubenumber+" "+suppliedmasterbias               
               else:
                  print >> tooBIG, "../BiasCorrection.py splittedtarget"+cubenumber+" "+suppliedmasterbias
            else:
               biased = 'N'
               biasstring = ''
         elif biased == 'Y': biasstring = 'b'
         else: biasstring = ''

         # Adjust lists of fits filenames to include 'b' for Bias-correction
         if CUBEtooBIGflag[j] == 0:
            print >> SHOCscript, 'awk '+"'"+'{print "'+biasstring+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
            startFITSfile = biasstring+"s"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001.fits"
         else:
            print >> tooBIG, "awk '{print "+'"'+biasstring+'"'+"$0}' splittedtarget"+cubenumber+" > reduced"+cubenumber

         # Warn the user if BIAS-subtraction is not done
         if biased == 'N' and targetname != 'QuickLook' and tooBIGexecuting == 0:
               print '                                                                                                       '
               print '#########################################################################################################'
               print ' WARNING: Since NO appropriate BIAS files were found, '+TARGETSdatalist[j]+' will NOT be bias-corrected!'
               print '#########################################################################################################'
               if BIASfile != '0':
                  userprompt = raw_input("Do you wish to continue regardless? (Y/N):  ")
                  userprompt = checkYNinput(userprompt)
                  if userprompt not in ('Y','y'):
                     sys.exit()               

         ###################################
         # Divide images by Master Flats:  #
         ###################################

         defaultFLAT = 'c'+str(int(vbincube[j]))+'x'+str(int(hbincube[j]))+"Flat"+str(filters)+".fits"

         # Do Flat-fielding if appropriate raw flat frames were included
         for i in range(len(flatfiles)):
            if vbincube[j] == vbinflat[i] and hbincube[j] == hbinflat[i] and dimcube[j] == dimflat[i]:
               flatfielded = 'Y'
               flatstring = 'c'
               if CUBEtooBIGflag[j] == 0:
                  print >> SHOCscript, "../FlatFielding.py "+"reduced"+cubenumber+" "+defaultFLAT
               else:
                  print >> tooBIG, "../FlatFielding.py reduced"+cubenumber+" "+defaultFLAT

         # Do Flat-fielding if appropriate master flat is already available
         if masterflats == 'Y' and makemasterflats == 'N':
            flatstring = 'c'
            flatfielded = 'Y'
            if CUBEtooBIGflag[j] == 0 and tooBIGexecuting == 0 and makemasterflats == 'N' and flatflag == 0:
               suppliedmasterflat = raw_input("Supply the name of the appropriate master FLAT file (default: "+defaultFLAT+"):  ")
               flatflag = 1
            else:
               suppliedmasterflat = ''
            if suppliedmasterflat == '':
               suppliedmasterflat = defaultFLAT
            if CUBEtooBIGflag[j] == 0:
               suppliedmasterflat = checkFILEname(suppliedmasterflat,'master FLAT')
               suppliedmasterflat = checkBINNING(suppliedmasterflat,'master FLAT',hbincube[j],vbincube[j],dimcube[j])   
            if suppliedmasterflat != 'dud':         
               if CUBEtooBIGflag[j] == 0:
                  print >> SHOCscript, "../FlatFielding.py "+"reduced"+cubenumber+ " "+suppliedmasterflat
               else:
                  print >> tooBIG, "../FlatFielding.py reduced"+cubenumber+" "+suppliedmasterflat 
            else:
               flatfielded = 'N'    
               flatstring = ''
         elif flatfielded == 'Y': flatstring = 'c'       
         else: flatstring = ''

         # Warn the user if FLAT-fielding is not done
         if flatfielded == 'N' and targetname != 'QuickLook' and tooBIGexecuting == 0:
               print '                                                                                                       '
               print '#########################################################################################################'
               print ' WARNING: Since NO appropriate FLAT files were found, '+TARGETSdatalist[j]+' will NOT be flat-fielded!'
               print '#########################################################################################################'
               if FLATSfile != '0':
                  userprompt = raw_input("Do you wish to continue regardless? (Y/N):  ")
                  userprompt = checkYNinput(userprompt)
                  if userprompt not in ('Y','y'):
                     sys.exit()

         ################################################
         # Determine the filenames of the reduced files #
         ################################################

         # Adjust lists of fits filenames to include 'b' for Bias-correction and 'c' for Flat-fielding
         if flatfielded == 'Y' and biased == 'Y':
            if CUBEtooBIGflag[j] == 0:
               print >> SHOCscript, 'awk '+"'"+'{print "cb'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "cbs"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001.fits"
               print >> SHOCscript, 'rm '+startFITSfile.replace('.0001.fits','.*').replace('cbs','bs')+' '+startFITSfile.replace('.0001.fits','.*').replace('cbs','s')
            else:
               print >> tooBIG, "awk '{print "+'"cb"'+"$0}' splittedtarget"+cubenumber+" > reduced"+cubenumber  
         elif flatfielded == 'N' and biased == 'Y':
            if CUBEtooBIGflag[j] == 0:
               print >> SHOCscript, 'awk '+"'"+'{print "b'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "bs"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001.fits"
               print >> SHOCscript, 'rm '+startFITSfile.replace('.0001.fits','.*').replace('bs','s')
            else:
               print >> tooBIG, "awk '{print "+'"b"'+"$0}' splittedtarget"+cubenumber+" > reduced"+cubenumber
         elif flatfielded == 'N' and biased == 'N':
            if CUBEtooBIGflag[j] == 0:
               print >> SHOCscript, 'awk '+"'"+'{print "'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "s"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001.fits"
            else:
               print >> tooBIG, "cp sort"+cubenumber+" reduced"+cubenumber
         elif flatfielded == 'Y' and biased == 'N':
            if CUBEtooBIGflag[j] == 0:
               print >> SHOCscript, 'awk '+"'"+'{print "c'+'"$0}'+"'"+' splittedtarget'+cubenumber+" > reduced"+cubenumber
               startFITSfile = "cs"+str(TARGETSdatalist[j]).split('.')[0]+'.'+cubenumber+ ".0001.fits"
               print >> SHOCscript, 'rm '+startFITSfile.replace('.0001.fits','.*').replace('cs','s')
            else:
               print >> tooBIG, "awk '{print "+'"c"'+"$0}' splittedtarget"+cubenumber+" > reduced"+cubenumber
         
         if CUBEtooBIGflag[j] == 0:
            startFITSfiles.append(startFITSfile)

         #######################################
         # Write timing information to HEADERS #
         #######################################

         # Set UTC header in hrs from 00:00 of date contained in FRAME header
         if CUBEtooBIGflag[j] == 0:
            print >> SHOCscript, "../frametime.py "+"reduced"+cubenumber
         else:
            print >> tooBIG, "../frametime.py reduced"+cubenumber
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

         # If the cube is < 2GB it is handled via the optimized route (SHOCscript)
         if CUBEtooBIGflag[j] == 0:
            print >> SHOCscript, "cp reduced"+cubenumber+" temp"
            print >> SHOCscript, 'awk '+"'"+'{print "ReducedData/'+'"$0}'+"'"+' temp > temptemp'
            print >> SHOCscript, 'mv temptemp reduced'+cubenumber
            print >> SHOCscript, 'rm temp'
            # Make sub-folder for the Reduced fits images
            print >> SHOCscript, 'mkdir ReducedData'
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
         # If the cube is > 2GB it is handled via an alternative route (tooBIG script)
         else:
            print >> tooBIG, "cp reduced"+cubenumber+" temp"
            print >> tooBIG, 'awk '+"'"+'{print "ReducedData/'+'"$0}'+"'"+' temp > temptemp'
            print >> tooBIG, 'mv temptemp reduced'+cubenumber
            print >> tooBIG, 'rm temp'
            # Make sub-folder for the Reduced fits images
            print >> tooBIG, 'mkdir ReducedData'
            print >> tooBIG, 'mv '+flatstring+biasstring+'s*.'+cubenumber+'.0[0-1]*.fits ReducedData'
            print >> tooBIG, 'mv '+flatstring+biasstring+'s*.'+cubenumber+'.0[2-3]*.fits ReducedData'
            print >> tooBIG, 'mv '+flatstring+biasstring+'s*.'+cubenumber+'.0[4-5]*.fits ReducedData'
            print >> tooBIG, 'mv '+flatstring+biasstring+'s*.'+cubenumber+'.0[6-7]*.fits ReducedData'
            print >> tooBIG, 'mv '+flatstring+biasstring+'s*.'+cubenumber+'.0[8-9]*.fits ReducedData'
            print >> tooBIG, 'mv '+flatstring+biasstring+'s*.'+cubenumber+'.*.fits ReducedData'
            print >> tooBIG, 'rm *s*.'+cubenumber+'.0[0-1]*.fits'
            print >> tooBIG, 'rm *s*.'+cubenumber+'.0[2-3]*.fits'
            print >> tooBIG, 'rm *s*.'+cubenumber+'.0[4-5]*.fits'
            print >> tooBIG, 'rm *s*.'+cubenumber+'.0[6-7]*.fits'
            print >> tooBIG, 'rm *s*.'+cubenumber+'.0[8-9]*.fits'
            print >> tooBIG, 'rm *s*.'+cubenumber+'.*.fits'
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
            print >> tooBIG, "./PLOTscript"
            tooBIG.close()
            os.system('chmod a+x tooBIG')
            os.system('rm SHOCscript PHOTscript')
            os.system('mv tooBIG tooBIG'+cubenumber)
            print "######################################################################################################################"
            print "The FITS file "+TARGETSdatalist[j] +" is too large. It may be handled separately by running:           ./tooBIG"+cubenumber
            if len(TARGETSdatalist) > 1:
               print "Then remove it from '"+TARGETSfile+"' and re-run the SHOCpipeline.py script for the rest of the files in the list, "
               print "by running:       ./SHOCpipelineINPUTS"
            print "######################################################################################################################"
            sys.exit()
         catlist = catlist+" reduced"+cubenumber

      # Create combined list of all frames for multiple cubes
      reducedlist = catlist.split(' reduced')
      reducedcombined = 'reduced'+reducedlist[1]+'to'+reducedlist[-1]
      print >> SHOCscript, 'cat'+catlist+' > '+reducedcombined     

      #################
      # Do PHOTOMETRY #  (PHOTscript which will generate PLOTscript if successful)
      #################

      if CUBEtooBIGflag[j] == 0:
         print >> PHOTscript, "../Photometry.py "+reducedcombined+" N"
         print >> PHOTscript, "#----------------------------------------------------------------"

      #######################################################
      # Comments on screen to prompt the user on next steps #
      #######################################################

      if targetname != 'QuickLook' and tooBIGexecuting == 0:
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
