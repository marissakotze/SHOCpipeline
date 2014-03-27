#! /usr/bin/env python
import sys
import os
import numpy

import pyraf
from pyraf import iraf
from pyraf.iraf import images
from pyraf.iraf import imutil

#################################################
# Function: check user input for Y/N questions  #
#################################################

def checkYNinput(variable):
   """ Prompt the user again if invalid input was supplied  """
   while variable not in ('Y','y','N','n',''):
      variable = raw_input("Invalid input. The format is Y or N? ")   
   # return values to main program 
   return variable

###################################################
# Function: check user input for value questions  #
###################################################

def checkNUMBERinput(variable):
   """ Prompt the user again if invalid input was supplied  """
   while variable.isdigit() == False:
       variable = raw_input("Not a number. Supply the input in the correct format!:   ")   
   # return values to main program 
   return variable

####################
##################
#  MAIN PROGRAM  #
##################
####################

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Name of the file that contains the list of FITS filenames:  ")  
      dumpdata =  raw_input("Do you want to dump the entire dataset (it is useful if COG model does not converge) [Y/N]? :  ")
   else:
      file = sys.argv[1]
      dumpdata =  sys.argv[2]

   dumpdata = checkYNinput(dumpdata)

   # create an input file that can be used to automatically re-run the script
   inputs = open('inputs','w')
   os.system("rm allmag allcoo")

   # open the list of fits files on which photometry is to be performed
   checkfile = 0
   while checkfile == 0:
      try:
         inputfitslist = numpy.loadtxt(file,dtype="str")
         checkfile = 1
      except IOError:
         file = raw_input("Invalid file name! What is the name of the file that contains the list of FITS file names?:  ")

   try:
      length = len(inputfitslist)
   except TypeError, e:
      templist = str(inputfitslist)
      inputfitslist = []
      inputfitslist.append(str(templist))
   
   fitslist = []
   trigger = imutil.hselect(images = inputfitslist[0], fields = 'TRIGGER', expr = 'yes',Stdout=1)
   if str(trigger[0]) == '"External Start"':
      newlist = open('newlist','w')
      for i in range (1,len(inputfitslist)):
         fitslist.append(inputfitslist[i])
         print >> newlist, inputfitslist[i]
      newlist.close()
   else:
      fitslist = inputfitslist

   cubenumber = str(fitslist[0].split('.')[1])
   startFITS = str(fitslist[0])

   # Allow the user to determine a star-free region on their initial image
   print "###########################################################################"
   print "#  Determine the parameters [x1:x2,y1:y2] for a box without stars         #"
   print "#  from the image that has been opened for you in DS9 to help you.        #"
   print "#                                                                         #"
   print "#  The box is defined by its four corners:                                #"
   print "#                                                                         #"
   print "#                  (x1,y2)_________________(x2,y2)                        #"
   print "#                        |                 |                              #"
   print "#                  (x1,y1)_________________(x2,y1)                        #"
   print "#                                                                         #"
   print "#  It will help you to determine the standard deviation of the background #"
   print "#  which are required inputs for the IRAF tasks 'daofind' and 'phot'      #"
   print "###########################################################################"
   if dumpdata in ('N','n'):
      os.system("ds9 "+fitslist[0]+"&")
   skybox = raw_input("Enter coordinates of a box without stars in the format [x1:x2,y1:y2] : ") 
   if skybox != '':  
      while skybox.count('[')<1 or skybox.count(']')<1 or skybox.count(':')<2 or skybox.count(',')<1:
         skybox = raw_input("The correct format is [x1:x2,y1:y2] , with all the brackets and punctuation included. Please try again: ")
   print >> inputs, skybox
   # Determine the standard deviation in the backgound
   stddev = imutil.imstat(images = fitslist[0]+skybox , mode = "h", fields = 'image,mean,stddev',Stdout=1)[1].split()[-1]
   print 'STDDEV in the background is :', stddev
   
   # Allow the user to accept the values of the parameter file, revert to default or exit to adjust the file before runnning PHOTscript
   print "###########################################################################"
   print "CONTENTS OF THE 'parameters' FILE IN THIS DIRECTORY IS:"
   print "###########################################################################"
   print "   "
   os.system('cat parameters')
   print "###########################################################################"
   print "   "
   promtpar = raw_input("Do you wish to continue with the photometry using the parameters listed above (Y/N)? ")
   promtpar = checkYNinput(promtpar)
   print >> inputs, promtpar
   if promtpar not in ('Y','y',''):
      print "###########################################################################"
      print "CONTENTS OF THE 'defaultparameters' FILE IS:"
      print "###########################################################################"
      print "   "
      os.system('cat ../defaultparameters')
      print "###########################################################################"
      print "   "
      promtpardefault = raw_input("Do you wish to revert back to the default parameters (Y/N)? ")
      promtpardefault = checkYNinput(promtpardefault)
      print >> inputs, promtpardefault
      if promtpardefault in ('Y','y'):
         os.system("cp ../defaultparameters parameters")
      else:
         print "##################################################################################################"
         #print "#  You have elected to quit the program and edit the 'parameters' file before running it again. #"
         print "#  Adjust the parameters in the open 'gedit' window. SAVE and CLOSE it to continue further here. #"
         print "##################################################################################################"
         os.system("gedit parameters")
         #sys.exit()

   os.system('cp parameters parameters'+cubenumber)

   # Extract parameter values from the 'parameters' file (which the user should edit with the appropriate values for their field)
   parameters = numpy.loadtxt('parameters',dtype="str")
   ApertureList = parameters[0]
   InnerBackgroundAnnulus = float(parameters[1])
   OuterBackgroundAnnulus = float(parameters[2])
   CentroidBoxSize = parameters[3]
   MaximumShift = parameters[4]
   edgemargin = parameters[5]
   crowdmargin = parameters[6]
   if len(parameters)>7:
      maxMAGerr = parameters[7]
   else:
      maxMAGerr = 0.1
   if len(parameters)>9:
      fwhm = parameters[9]
   else:
      fwhm = 3

# determine if a 'windows' file was provided with the target and comparisons' X and Y coordinates in 2 column ASCII format
try:
    coordinates = numpy.loadtxt('windows',dtype="float",unpack=True)
    Xcoord = coordinates[0]
    Ycoord = coordinates[1] 
    print "###################################################################################"
    print "# Coordinates are based on the following positions supplied in the 'windows' file #"
    print "###################################################################################"
    os.system('cat windows')
    print "###################################################################################"
    print "# Coordinates specified in this way are only relevant if observations were GUIDED #"
    print "###################################################################################"
    usewindow = raw_input("Is this correct? (Y/N) :   ")
    usewindow = checkYNinput(usewindow)
    if usewindow in ('Y','y'):
       fromwindows = 1
       print >> inputs, 'Y'
    else:
       fromwindows = 0      
       print >> inputs, 'N' 
except IOError, e:
    fromwindows = 0

######################
######################
#  Photometry TASKS  #
######################
######################

from pyraf.iraf import noao 
from pyraf.iraf import digiphot
from pyraf.iraf import daophot

###########
# DAOFIND #
###########

# Set data parameters to FIND all stars above a certain threshold
daophot.datapars.scale = 1
daophot.datapars.fwhmpsf = fwhm
daophot.datapars.emission = "yes"
daophot.datapars.sigma = stddev
daophot.datapars.datamin = "INDEF"
daophot.datapars.datamax = "INDEF"
daophot.datapars.noise = "poisson"
daophot.datapars.ccdread = "RON"
daophot.datapars.gain = "gain"
daophot.datapars.readnoise = 0
daophot.datapars.epadu = 1
daophot.datapars.exposure = "exposure"
daophot.datapars.airmass = "airmass"
daophot.datapars.filter = "filter"
daophot.datapars.obstime = "utc-obs"
daophot.datapars.itime = 1
daophot.datapars.xairmass = "INDEF"
daophot.datapars.ifilter = "INDEF"
daophot.datapars.otime = "INDEF"
daophot.datapars.mode = "h"

# Set the THRESHOLD for source detection if the user hasn't specified specific locations for sources in a 'windows' file
crowdeddrift = 0

if fromwindows == 1:
    os.system("cp windows allcoo")
else:
    significance = raw_input("Required significance level (n) for detection (default:10) ?  :  ")
    if significance not in (''):
        significance = checkNUMBERinput(significance)
    else:
        significance = 10
    print >> inputs, significance
    print "#######################################################################################################"
    print "#  Star positions will be determined for sources above the threshold ("+str(significance)+"xSTDDEV) in the first frame.  #"
    print "#######################################################################################################"
    print "#  The IRAF task 'daofind' (from noao digiphot daophot) is used to determine the centroid positions   #"
    print "#######################################################################################################"
    # Allow the user to choose whether positions should be determined on every frame (for drift) or only on the first frame (for guided)
    promt = raw_input("Is there a significant drift of sources from their initial positions? (Y/N): ")
    promt = checkYNinput(promt)

    # Set the parameters for FINDING sources     
    if promt in ('Y','y'):
        crowdeddrift = 1
        os.system('rm *.coo.*')
        print >> inputs, 'Y'
    else:
        crowdeddrift = 0
        print >> inputs, 'N'
    daophot.findpars.threshold = significance
    daophot.findpars.nsigma = 1.5
    daophot.findpars.ratio = 1.
    daophot.findpars.theta = 0.
    daophot.findpars.sharplo = 0.2
    daophot.findpars.sharphi = 1.
    daophot.findpars.roundlo = -1.
    daophot.findpars.roundhi = 1.
    daophot.findpars.mkdetections = "no"
    daophot.findpars.mode = "h" 

    # Run DAOFIND to find sources above the stipulated threshold
    if crowdeddrift == 1:
        if str(trigger[0]) == '"External Start"': 
            daophot.daofind.image = "@"+'newlist'
        else:
            daophot.daofind.image = "@"+file
        daophot.daofind.output = "default"
    else:
        daophot.daofind.image = fitslist[0]
        daophot.daofind.output = "allcoo" 
    daophot.daofind.boundary = "nearest"
    daophot.daofind.constant = 0.
    daophot.daofind.interactive = "no"
    daophot.daofind.mode = "h"
    daophot.daofind()

    # Give the user feedback on the sources that have been detected above the threshold
    if crowdeddrift == 1:
        os.system('ls *.coo.* > allcoolist')
        print "#######################################################################################################"
        print "#  Star positions were determined for sources above the threshold ("+str(significance)+"xSTDDEV) in EACH frame.  #"
        print "#######################################################################################################"
        try:
            coordinatefiles = numpy.loadtxt('allcoolist',dtype="str",unpack=True)
            determinedcoordinates = numpy.loadtxt(coordinatefiles[0],dtype="str",unpack=True)
            numberextracted = len(determinedcoordinates[0])
            os.system("cat "+fitslist[0].replace('ReducedData/','')+'.coo.1')
        except IOError, e:
            print "######################################################################"
            print "#  No positions were determined for sources on the first FITS file.  #"
            print "######################################################################"
            sys.exit("Suggestion: Set the significance level required for detection LOWER.")
    else:
        try:
            determinedcoordinates = numpy.loadtxt('allcoo',dtype="str",unpack=True)
            try:
                numberextracted = len(determinedcoordinates[0])
                os.system('cat allcoo')
                print "#######################################################################################################"
                print "#  Star positions were determined for sources above the threshold ("+str(significance)+"xSTDDEV) in the FIRST frame.  #"
                print "#######################################################################################################"
            except IndexError, e:
                print "######################################################################"
                print "#  No positions were determined for sources on the first FITS file.  #"
                print "######################################################################"
                os.system('rm allcoo')
                sys.exit("Suggestion: Set the significance level required for detection LOWER.")
        except IOError, e:
            print "#######################################################################################################"
            print "#  No 'allcoo' file was created, so no positions were determined for sources on the first FITS file.  #"
            print "#######################################################################################################"
            sys.exit("Suggestion: Set the significance level required for detection LOWER or provide the source coordinates in a 'windows' file.")

    if numberextracted == 0:
        print "#######################################################################################"
        print "#  Stars could not be extracted above the threshold ("+str(significance)+"xSTDDEV) from the first frame  #"
        print "#######################################################################################"
        os.system('rm allcoo')
        os.system('rm *.coo.*')
        sys.exit("Suggestion: Set the significance level required for detection LOWER or provide the source coordinates in a 'windows' file.")
    else:
        if dumpdata in ('n','N'): 
            try:
                promtcontinue = raw_input("Is your target among these sources (Y/N)? ")
                promtcontinue = checkYNinput(promtcontinue)
            except EOFError: promtcontinue = 'Y'
        else:
            promtcontinue = 'Y'
        print >> inputs, promtcontinue
        if promtcontinue not in ('Y','y'):
            os.system('rm allcoo')
            os.system('rm *.coo.*')
            print "###################################################################################################################"
            print "# Re-run the program using different parameters by typing in the command-line:   ../Photometry.py "+file+" N"
            print "###################################################################################################################"
            sys.exit()

    # Allow the user to automatically eliminate sources that are too close to eachother or the edge
    if numberextracted > 10 and crowdeddrift == 0:
            print "############################################################################################"
            print "#  More than 10 stars were extracted above the threshold ("+str(significance)+"xSTDDEV) from the first frame  #"
            print "############################################################################################"
            os.system('cp allcoo allcoo'+cubenumber+'original')         
            os.system("../construct_windows.py allcoo "+startFITS)
            promtcontinued = raw_input("Do you wish to continue the photometry on the sources contained in windows"+cubenumber+" (Y/N)? ")
            promtcontinued = checkYNinput(promtcontinued)
            print >> inputs, promtcontinued
            if promtcontinued in ('Y','y'):
                os.system("cp windows"+cubenumber+" allcoo")
            else:
                promtcontinuedon = raw_input("Do you wish to re-run the program using different parameters (Y/N)? ")
                promtcontinuedon = checkYNinput(promtcontinuedon)
                print >> inputs, promtcontinuedon                
                if promtcontinuedon in ('Y','y'):
                    os.system('rm allcoo')
                    print "###################################################################################################################"
                    print "# Re-run the program using different parameters by typing in the command-line:   ../Photometry.py "+file+" N"
                    print "###################################################################################################################"
                    sys.exit()
                else:
                    print "##############################################################################################################"
                    print "# You have elected to do photometry on all the sources identified (more than 10). It will take some time.... #"
                    print "##############################################################################################################"

inputs.close()
os.system('mv inputs inputs'+cubenumber)

########
# PHOT #
########

# Run the IRAF task DAOPHOT PHOT for every trial perture listed in the 'parameter' file
if len(str(ApertureList).split(',')) > 0:

    # Set centroiding parameters for IRAF task PHOT
    daophot.centerpars.calgorithm = "centroid"
    daophot.centerpars.cbox = CentroidBoxSize
    daophot.centerpars.cthreshold = 2.
    daophot.centerpars.minsnratio = 1.
    daophot.centerpars.cmaxiter = 10
    daophot.centerpars.maxshift = MaximumShift
    daophot.centerpars.clean = "no"
    daophot.centerpars.rclean = 1.
    daophot.centerpars.rclip = 2.
    daophot.centerpars.kclean = 3.
    daophot.centerpars.mkcenter = "no"
    daophot.centerpars.mode = "h"       

    # Set sky parameters for IRAF task PHOT
    daophot.fitskypars.salgorithm = "mode"
    daophot.fitskypars.annulus = InnerBackgroundAnnulus
    daophot.fitskypars.dannulus = OuterBackgroundAnnulus-InnerBackgroundAnnulus
    daophot.fitskypars.skyvalue = 0.
    daophot.fitskypars.smaxiter = 10
    daophot.fitskypars.sloclip = 3.
    daophot.fitskypars.shiclip = 3.
    daophot.fitskypars.snreject = 50
    daophot.fitskypars.sloreject = 3.
    daophot.fitskypars.shireject = 3.
    daophot.fitskypars.khist = 3.
    daophot.fitskypars.binsize = 0.1
    daophot.fitskypars.smooth = "no"
    daophot.fitskypars.rgrow = 0.
    daophot.fitskypars.mksky = "no"
    daophot.fitskypars.mode = "h"

    # Set photometry parameters for IRAF task PHOT
    daophot.photpars.weighting = "constant"
    daophot.photpars.apertures = ApertureList
    daophot.photpars.zmag = 0.
    daophot.photpars.mkapert = "no"
    daophot.photpars.mode = "h" 

    # Do photometry on all the stars that have been identified by IRAF task DAOFIND or supplied by user in 'windows' file
    print "####################################################################################"
    print "#  The IRAF task 'phot' (from noao digiphot daophot) is used for the phototmetry   #"
    print "####################################################################################"
    if str(trigger[0]) == '"External Start"':
        daophot.phot.image = "@"+'newlist'
    else:
        daophot.phot.image = "@"+file
    if crowdeddrift == 1:
        daophot.phot.coords = "@allcoolist"
    else:
        daophot.phot.coords = "allcoo"
    daophot.phot.output = "allmag"
    daophot.phot.interactive = "no"
    daophot.phot.radplots = "no"
    daophot.phot.mode = "h"
    daophot.phot()

# Open script file for lightcurve extraction and PLOTTING
PLOTscript = open('PLOTscript','w')
print >> PLOTscript, "#! /bin/bash"   
os.system('chmod a+x PLOTscript')

# Do Aperture corrected photometry (Curve of growth fitting [COG model] to determine the apertures for which S/N is optimized)
if len(str(ApertureList).split(',')) > 1:    
    print "##################################################################################################################"
    print "#  The IRAF task 'mkapfile' (from noao digiphot photcal) is used to extract the aperture corrected phototmetry   #"
    print "##################################################################################################################"
    from pyraf.iraf import photcal
    photcal.mkapfile.photfiles = "allmag"
    photcal.mkapfile.naperts = len(str(ApertureList).split(',')) 
    photcal.mkapfile.apercors = "apcor.allmag"
    photcal.mkapfile.smallap = 1
    photcal.mkapfile.largeap = len(str(ApertureList).split(','))
    photcal.mkapfile.magfile = "apcor.out"
    photcal.mkapfile.logfile = ""
    photcal.mkapfile.plotfile = ""
    photcal.mkapfile.obscolumns = "2 3 4 5"
    photcal.mkapfile.append = "no"
    photcal.mkapfile.maglim = maxMAGerr
    photcal.mkapfile.nparams = 3
    photcal.mkapfile.swings = 1.2
    photcal.mkapfile.pwings = 0.1
    photcal.mkapfile.pgauss = 0.5
    photcal.mkapfile.rgescale = 0.9
    photcal.mkapfile.xwings = 0.
    photcal.mkapfile.interactive = "no"
    photcal.mkapfile.graphics = "stdgraph"
    photcal.mkapfile.verify = "no"
    photcal.mkapfile.mode = "h"
    photcal.mkapfile() 

    os.system('mv apcor.out apcor.out'+cubenumber)
    os.system('mv apcor.allmag apcor.allmag'+cubenumber)

    # Populate script for lightcurve extraction and PLOTTING
    print >> PLOTscript, "../extract_lcs.py apcor.out"+(str(file).lstrip('reduced')).split('to')[0]+" "+startFITS.replace('ReducedData/','')
    print >> PLOTscript, "../plot_lcs.py lightcurves_based_on_"+startFITS.replace('.fits','').replace('ReducedData/','')
else:
# Go an alternate route if a user specified a single aperture
    dumpdata = 'Y'
    print "########################################################################################"
    print "#  You have chosen NOT to attempt aperture-corrected photometry (which optimizes S/N), #"
    print "#  but opted for fixed aperture photometry instead. Please run ./PLOTscript next.      #"
    print "########################################################################################"
    #print >> PLOTscript, "echo '###############'"
    #print >> PLOTscript, "echo '# PLEASE WAIT #'"
    #print >> PLOTscript, "echo '###############'"
    #print >> PLOTscript, "../Photometry.py "+str(file)+" Y <inputs"+cubenumber+" >outputs"+cubenumber
    print >> PLOTscript, "../extract_txdump.py outputs"+cubenumber+" "+ApertureList
    print >> PLOTscript, "../extract_lcs.py extracted_outputs"+cubenumber+" "+startFITS.replace('ReducedData/','')
    print >> PLOTscript, "../plot_lcs.py lightcurves_based_on_"+startFITS.replace('.fits','').replace('ReducedData/','')
PLOTscript.close()

# DUMP the results from PHOT if requested to do so
if dumpdata == 'Y' :
    # IRAF txdump task: 
    # To select the fields ID, XCENTER, YCENTER and the first three magnitudes from the output of the APPHOT PHOT task.
    #        pt> pdump image.mag.3 "ID,XCEN,YCEN,MAG[1],MAG[2],MAG[3]" yes
    #        pt> txdump image.mag.2 "ID,XCEN,YCEN,MAG[1-3]" yes

    dumpfile = open('outputs'+cubenumber,'w')
    from pyraf.iraf import ptools
    print "###################################################################################################"
    print "#  The IRAF task 'txdump' (from noao digiphot ptools) is used to dump the data produced by phot   #"
    print "###################################################################################################"
    print >> dumpfile, "###################################################################################################"
    print >> dumpfile, "#  IMAGE           IFILTER  ITIME  XAIRMASS  OTIME         XCENTER YCENTER  MAG    MERR   RAPERT  #"
    print >> dumpfile, "###################################################################################################"
    ptools.txdump.textfiles = "allmag"
    ptools.txdump.expr = "yes"
    ptools.txdump.mode = "h"

    for i in range(1,1+len(str(ApertureList).split(','))):
        ptools.txdump.fields = "IMAGE,IFILTER,ITIME,XAIRMASS,OTIME,XCENTER,YCENTER,MAG["+str(i)+"],MERR["+str(i)+"],RAPERT["+str(i)+"]"
        #ptools.txdump()
        dumpeddata = ptools.txdump(Stdout=1)
        for j in range(len(dumpeddata)):
            print >> dumpfile, dumpeddata[j]

os.system('rm allmag')

# Save coordinate files for future re-use
if crowdeddrift == 1:
    os.system("mv "+fitslist[0].replace('ReducedData/','')+'.coo.1'+ ' allcoo'+cubenumber)
    os.system('rm *.coo.*')
else:
    os.system('mv allcoo allcoo'+cubenumber)

if str(trigger[0]) == '"External Start"':
    print 'Skipped the first file in ',str(file), 'for the TRIGGER scenario:', str(trigger[0])
