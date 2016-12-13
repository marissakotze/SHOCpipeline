#! /usr/bin/env python

##########################################################################
##########################################################################
# Set up Data reduction Pipeline scripts for multi-filter SHOC data #
##########################################################################
##########################################################################

# IMPORT Python plug-ins
import sys
import numpy
import os


if __name__=='__main__':
   _nargs = len(sys.argv)
   ################
   #  User inputs #
   ################
   # Prompt user for inputs
   if _nargs == 1:
      TARGETSfile = raw_input("File containing the list of raw TARGET files (0 if none or the name of a single fits file):  ")
      FILTERS = raw_input("Give list of all filters used (, separated with no spaces):  ")

   # Inputs from arguments in command line
   else:
      TARGETSfile = sys.argv[1]
      FILTERS = sys.argv[2]

FILTERlist = FILTERS.split(',')
numberfilters = len(FILTERlist)

datalist = numpy.loadtxt(TARGETSfile,dtype="str")
numberfiles = len(datalist)
basefilename = datalist[0].split('.')[0]
startnumber = int(float(datalist[0].split('.')[1]))
cycles = int(numberfiles/numberfilters)

filterforfile = []
filenumbers = []
for i in range(cycles):
   for j in range(len(FILTERlist)):
      filenumber = str(basefilename)+'.0'+str(startnumber+j+numberfilters*i)+'.fits'
      print filenumber, FILTERlist[j]
      filenumbers.append(filenumber)
      filterforfile.append(FILTERlist[j])

for k in range(len(FILTERlist)):
   filterfilelists = open(FILTERlist[k]+'filter','w')
   for l in range(len(datalist)):
      if FILTERlist[k] == filterforfile[l]:
         print >> filterfilelists, filenumbers[l]
