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

   os.system("rm SHOCscript PHOTscript PLOTscript 0*fits > log")

   try:
      os.system("../SHOCpipeline.py "+TARGETSfile+" 0 0 QuickLook 0 0 2000 0 0 0 88")
      print "RUNNING....:    "+"./SHOCscript"
      os.system("./SHOCscript")
      print "RUNNING....:    "+"./PHOTscript"
      os.system("./PHOTscript")
      print "RUNNING....:    "+"./PLOTscript"
      os.system("./PLOTscript")
   except IOError:
      print "SHOCpipeline failed to execute. Please take note of the errors listed."
