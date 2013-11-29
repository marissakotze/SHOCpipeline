#! /usr/bin/env python

#############################################################################################
#  Extract all lightcurves for targets on which aperture corrected photometry as been done. #
#############################################################################################

import sys
import numpy
import pyfits
import os
import datetime

#################
#  MAIN PROGRAM #
#################
if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Name of the file that contains the aperture corrected photometry:  ")
      startFITS = raw_input("Name of FITS file to base positions of sources on:  ").replace('.fits','')

   else:
      file = sys.argv[1]
      startFITS = sys.argv[2].replace('.fits','')

   cube = startFITS.split('_')[-1].split('.')[0]
   cubename = str(startFITS.split('.')[0]).replace('c','').replace('b','').replace('s','')
   cubenumber = str(startFITS.split('.')[1])

   flag = -1
   targets = 0

   # Extract parameter values from the 'parameters' file (which the user may edit)
   parameters = numpy.loadtxt('parameters',dtype="str")
   ApertureList = parameters[0]
   InnerBackgroundAnnulus = float(parameters[1])
   OuterBackgroundAnnulus = float(parameters[2])
   CentroidBoxSize = float(parameters[3])
   MaximumShift = float(parameters[4])
   edgemargin = float(parameters[5])
   crowdmargin = float(parameters[6])
   maxMAGerr = float(parameters[7])
   margin = float(parameters[8])

   # Determine if there is a 'windows' file
   try:
       coordinates = numpy.loadtxt('windows',dtype="float",unpack=True)
       Xcoord = coordinates[0]
       Ycoord = coordinates[1] 
       try:
          targets = len(Xcoord)
       except TypeError:
          targets = 1
       print "###############################################################################"
       print "Coordinates are based on the following positions supplied in the 'windows' file "
       print "###############################################################################"
       print "X        Y"
       os.system('cat windows')
       print "###############################################################################"
       usewindow = raw_input("Is this correct? (Y/N) :   ")
       if usewindow in ('Y','y'):
          fromwindows = 1
       else:
          fromwindows = 0
          targets = 0  
   except IOError, e:
       fromwindows = 0

   # Get the list of data entries in the IRAF output file that contain aperture-corrected photometry (apcor.out*)
   badflag = 0
   try:
      datalist = numpy.loadtxt(file,dtype="str",unpack=True) 
      if len(datalist) < 10:
         badflag = 1  
   except IOError, e:
      badflag = 1
   if badflag ==1:
      print "##########################################################################################"
      print "# The aperture-corrected photometry FAILED because the Curve of Growth did not converge. #"
      print "##########################################################################################"
      print "Suggestions: "
      print "- Adjust parameters in the 'parameters' file in this directory (particularly the list of apertures)."
      print "AND/OR"
      print "- Automatically remove sources close to edges and in close proximity to eachother:   "
      print "../construct_windows.py allcoo"+cubenumber+" "+startFITS+".fits"
      print "- Then copy its output-file to a 'windows' file (only useful for GUIDED observations):"
      print "cp windows"+cubenumber+" windows"
      print "AND/OR"
      print "- Re-run the photmetry with a data dump of the aperture photometry for the entire list:"
      print "../Photometry.py reduced"+cubenumber+" Y"
      print "Those outputs will help you determine which sources and apertures are to be eliminated (ones with 'INDEF' magnitude values)."
      sys.exit("")
   else:
      if file.count('apcor.out') > 0:
          print "#####################################################"
          print "# The aperture-corrected photometry was SUCCESSFUL. #"
          print "#####################################################"
      else:
          print "##################################"
          print "# The photometry was SUCCESSFUL. #"
          print "##################################"
      if fromwindows == 0:
          print "X        Y"
          os.system('cat allcoo'+cubenumber)
          print "##############################################################################################"
          print "# PLEASE WAIT while the lightcurves are extracted for all the potential sources listed above #"
          print "##############################################################################################"
      elif fromwindows == 1:
          print "X        Y"
          os.system('cat windows')
          print "###########################################################################################################################"
          print "# PLEASE WAIT while the lightcurves are extracted from "+str(file)+" for only the selected sources listed above #"
          print "###########################################################################################################################"

   # Split the data into the columns that are represented to create a PHOTOMETRY matrix that contain the following columns
   Fitsfiles = datalist[0]
   Filter = datalist[1]
   Exposure = datalist[2]
   Airmass = datalist[3]
   Obstime = datalist[4]
   X = datalist[5]
   Y = datalist[6]
   Mag = datalist[7]
   MagErr = datalist[8]
   Radius = datalist[9] 

   # Open OUTPUT files
   lightcurves = open('lightcurves_based_on_'+startFITS.replace('.fits',''),'w')

   # Determine the number of targets identified from the start FITS file (if not supplied in a 'windows' file)
   for i in range(len(Fitsfiles)):
       Fitsfiles[i] = Fitsfiles[i].replace('.fits','').replace('.fit','').replace('.fi','').replace('.f','').rstrip('.')
       if fromwindows == 0:
          if Fitsfiles[i] == startFITS and flag == 0:
             targets = targets + 1
          if Fitsfiles[i] == startFITS and flag == -1:
             flag = 0
             startLOOP = i+1-1
             targets = targets + 1         
   if targets == 0  and fromwindows == 0:
       print 'No data was extracted for the FITS file that was supplied to base source posistions on.'
       print 'Edit PHOTscript and change the FITS file specified there to an appropriate file, for which there are data in '+str(file)
       sys.exit()

   # Extract the HJD for each FITS file and save it, so the matrix now also contain HJD
   # Determine the UTC values
   hjd = []
   obstimeinseconds = []
   utc = []
   for i in range(len(Fitsfiles)):
       lc = pyfits.open('ReducedData/'+Fitsfiles[i]+'.fits')
       dateobstemp = (lc[0].header['DATE-OBS']).split('-')
       dateobs = datetime.datetime(int(dateobstemp[0]),int(dateobstemp[1]),int(dateobstemp[2]),0,0,0)  
       try:
          utctemp = float(lc[0].header['UTC-OBS'])
          utchrs = int(utctemp)
          utcmins = int((utctemp-utchrs)*60)
          utcsecs = round(((utctemp-utchrs)*60-utcmins)*60,6)
          utcinhrs = 1
       except ValueError:
          utctemp = lc[0].header['UTC-OBS'].split(':')
          utchrs = int(utctemp[0])
          utcmins = int(utctemp[1])
          utcsecs = round(float(utctemp[2]),6)
          utcinhrs = 0
       if lc[0].header['OBJECT'] != 'QuickLook' and utcinhrs == 1:
          hjdtemp = lc[0].header['HJD']  
          hjdvalue = str(int(hjdtemp))+'.'+str(round((hjdtemp-int(hjdtemp)),9)).lstrip('0.')
          if i==0:
             startHJD = hjdvalue
          hjd.append(hjdvalue)
          #timeunit = 'HJD'
       else:
          hjd.append('')
       inseconds = float(utchrs)*60*60 + float(utcmins)*60 + float(utcsecs)
       if inseconds < 12*60*60:
          inseconds = inseconds+24*60*60
       timeunit = 'Seconds since 00:00'
       obstimeinseconds.append(inseconds)
       if utcsecs >= 60:
          utcsecs = utcsecs - 60
          utcmins = utcmins + 1
       if utcmins >= 60:
          utcmins = utcmins - 60
          utchrs = utchrs + 1          
       if utchrs >= 24:
          utchrs = utchrs - 24 
          dateobs = dateobs + datetime.timedelta(days=1) 
       if len(str(dateobs.month)) < 2:
          dateobsmonth = '0'+str(dateobs.month)
       else:
          dateobsmonth = str(dateobs.month)
       if len(str(dateobs.day)) < 2:
          dateobsday = '0'+str(dateobs.day)
       else:
          dateobsday = str(dateobs.day)
       if len(str(utchrs)) < 2:
          utchrs = '0'+str(utchrs)
       if len(str(utcmins)) < 2:
          utcmins = '0'+str(utcmins)
       if len(str(int(utcsecs))) < 2:
          utcsecs = '0'+str(utcsecs)
       utcvalue = str(utchrs)+':'+str(utcmins)+':'+str(utcsecs)
       utcvalue = str(dateobs.year)+'-'+dateobsmonth+'-'+dateobsday+'T'+str(utchrs)+':'+str(utcmins)+':'+str(utcsecs)
       utc.append(utcvalue)

       if not str(Fitsfiles[i]) == str(Fitsfiles[i-1]):          
          if flag == 0:
             flag = 1
   # Separate the photometry data per target using X and Y centroid positions. Write the data blocks to a file from which it can be plotted.
   # If no 'windows' file is present to indicate the sources of interest, the sources from the first image forms the source list.
   if fromwindows == 0:
       for k in range(startLOOP,startLOOP+targets):
           previousX = float(X[k])
           previousY = float(Y[k])
           print >> lightcurves, '# Source:', k-startLOOP+1, 'at X=', X[k], 'and Y=', Y[k]
           print >> lightcurves, '# Source Nr  ', 'X  ','Y  ',timeunit+'  ','MAG   ','MAGerr   ','Optimal Aperture   ', 'File name   ', 'Start of exposure (UTC)', 'HJD'
           for j in range(startLOOP,len(Fitsfiles)):
               if float(X[j]) >= previousX-margin and float(X[j]) <= previousX+margin and float(Y[j]) >= previousY-margin and float(Y[j]) <= previousY+margin and Mag[j] not in ('INDEF') and MagErr[j] not in ('INDEF'):
                   print >> lightcurves, k-startLOOP+1, X[j], Y[j], obstimeinseconds[j], Mag[j], MagErr[j], Radius[j], Fitsfiles[j]+'.fits', utc[j], hjd[j] #Obstime[j]
                   previousX = float(X[j])
                   previousY = float(Y[j])
   # If a 'windows' file is present, it indicates the list of sources
   elif fromwindows == 1:
       for k in range(targets):
           if targets > 1:
               previousX = float(Xcoord[k])
               previousY = float(Ycoord[k])
               print >> lightcurves, '# Source:', k+1, 'at X=', Xcoord[k], 'and Y=', Ycoord[k]
           else:
               previousX = float(Xcoord)
               previousY = float(Ycoord)       
               print >> lightcurves, '# Source:', k+1, 'at X=', Xcoord, 'and Y=', Ycoord
           print >> lightcurves, '# Source Nr  ', 'X  ','Y  ',timeunit+'  ','MAG   ','MAGerr   ','Optimal Aperture   ', 'File name   ', 'Start of exposure (UTC)', 'HJD'
           for j in range(len(Fitsfiles)):
               if float(X[j]) >= previousX-margin and float(X[j]) <= previousX+margin and float(Y[j]) >= previousY-margin and float(Y[j]) <= previousY+margin and Mag[j] not in ('INDEF') and MagErr[j] not in ('INDEF'):
                   print >> lightcurves, k+1, X[j], Y[j], obstimeinseconds[j], Mag[j], MagErr[j], Radius[j], Fitsfiles[j]+'.fits', utc[j], hjd[j]  #Obstime[j]
                   previousX = float(X[j])
                   previousY = float(Y[j])
                   
