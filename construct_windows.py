#! /usr/bin/env python

####################################################################
#  Construct a 'windows' file that eliminates sources at the edges #
####################################################################

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
      file = raw_input("Name of the file that contains the positions of all the extracted sources:  ")
      startFITS = raw_input("Name of FITS file to base positions of sources on:  ")
#      edgemargin = raw_input("What is the minimum distance [pixels] a source is allowed to be from the edge?:  ")
#      crowdmargin = raw_input("What is the minimum distance [pixels] a source is allowed to be from another source?:  ")

   else:
      file = sys.argv[1]
      startFITS = sys.argv[2].replace('ReducedData/','')
#      edgemargin = sys.argv[3]
#      crowdmargin = sys.argv[4]

   # Extract parameter values from the 'parameters' file (which the user may edit)
   parameters = numpy.loadtxt('parameters',dtype="str")
   edgemargin = parameters[5]
   crowdmargin = parameters[6]
   promtedgemargin = raw_input("What is the minimum distance [pixels] a source is allowed to be from the edge? (default:"+edgemargin+"):  ")
   promtcrowdmargin = raw_input("What is the minimum seperation distance [pixels] between sources? (default:"+crowdmargin+"):  ")
   if promtedgemargin not in (''):
      edgemargin = promtedgemargin
   if promtcrowdmargin not in (''):
      crowdmargin = promtcrowdmargin
   
   edgemargin = float(edgemargin)
   crowdmargin = float(crowdmargin)
   cubenumber = str(startFITS.split('.')[1])
   windows = open('windows'+cubenumber,'w')

   # filenamelist = loadtxt(file,dtype="str",usecols=(0),delimiter=' ',unpack=True)
   datalist = numpy.loadtxt(file,dtype="float",unpack=True) 

   X = datalist[0]
   Y = datalist[1]
   Mag = datalist[2]

   firstframe = pyfits.open('ReducedData/'+startFITS)
   sizex = float(firstframe[0].header['NAXIS1'])
   sizey = float(firstframe[0].header['NAXIS2'])

   centralX = []
   centralY = []
   centralMag = []
   originalNr = []

   print " The following eliminated sources are situated within "+str(edgemargin)+" pixels of the edges:"
   for i in range(len(X)):
       if X[i] < sizex-edgemargin and Y[i] < sizey-edgemargin and X[i] > 0+edgemargin and Y[i] > 0+edgemargin:
          centralX.append(X[i])
          centralY.append(Y[i])
          centralMag.append(Mag[i])
          originalNr.append(i+1)   
       else:
          print X[i], Y[i],  '  Nr.',i+1

   print " The following eliminated sources are situated within "+str(crowdmargin)+" pixels from one another:"
   crowdflag = []
   singleX = []
   singleY = []
   singleMag = []
   singleNr = []
   crowdlist = []
   for j in range(len(centralX)):
       flag = 0
       for k in range(j+1,len(centralX)):
           if (centralX[j] < centralX[k]+crowdmargin and centralX[j] > centralX[k]-crowdmargin) and (centralY[j] < centralY[k]+crowdmargin and centralY[j] > centralY[k]-crowdmargin):
               flag = 1
               crowdlist.append(originalNr[j])
               crowdlist.append(originalNr[k])
               print centralX[j], centralY[j], centralMag[j], '  Nr.',originalNr[j], '\t', 'vs', '\t', centralX[k], centralY[k], centralMag[k], '  Nr.', originalNr[k]

       crowdflag.append(flag)

   for l in range(len(centralX)):
       if crowdflag[l] == 0:
           singleX.append(centralX[l])
           singleY.append(centralY[l])
           singleMag.append(centralMag[l])
           singleNr.append(originalNr[l])

   print " The following sources are suitable for aperture corrected photometry and has been written to 'windows"+cubenumber+"' :"
   for i in range(len(singleX)): 
       if singleNr[i] not in crowdlist:
           print singleX[i],singleY[i],singleMag[i], '  Nr.',singleNr[i]
           print >> windows, singleX[i],singleY[i]
   
