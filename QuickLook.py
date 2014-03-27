#! /usr/bin/env python

#####################################
# Data reduction Pipeline for SHOC  #
#####################################

import sys
import os

####################
##################
#  MAIN PROGRAM  #
##################
####################

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      TARGETSfile = raw_input("File containing the fits filenames of raw TARGET files (or the name of the fits file if only one cube):  ")
   else:
      TARGETSfile = sys.argv[1]

   # Open inputfile
   quicklookinputs = open('quicklookinputs','w')
   print >> quicklookinputs, "../SHOCpipeline.py "+TARGETSfile+" 0 0 QuickLook 0 0 2000 0 0 0 88"
   quicklookinputs.close()

   os.system("rm SHOCscript PHOTscript PLOTscript 0*fits")

   try:
      os.system("../SHOCpipeline.py "+TARGETSfile+" 0 0 QuickLook 0 0 2000 0 0 0 88")
      try:
         testSHOCscript = open('SHOCscript','r')
         print "RUNNING....:    "+"./SHOCscript"
         testSHOCscript.close()
         os.system("./SHOCscript")
      except IOError:
         print "SHOCscript was not created. Please take note of the errors listed above."
      try:
         testPHOTscript = open('PHOTscript','r')
         print "RUNNING....:    "+"./PHOTscript"
         testPHOTscript.close()
         os.system("./PHOTscript")
      except IOError:
         print "PHOTscript was not created. Please take note of the errors listed above."
      try:
         testPLOTscript = open('PLOTscript','r')
         print "RUNNING....:    "+"./PLOTscript"
         testPLOTscript.close()
         os.system("./PLOTscript")
      except IOError:
         print "PLOTscript was not created. Please take note of the errors listed above."
   except IOError:
      print "SHOCpipeline failed to execute. Please take note of the errors listed above."
