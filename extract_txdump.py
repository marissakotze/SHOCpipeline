#! /usr/bin/env python

######################################################################
#  Extract txdump data from the STDOUT of the Photometry.py secript. #
######################################################################

import sys

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Name of the file that contains the txdump info:  ")
      aperture =  raw_input("Please specify the size [pixels] of the aperture you want to use:  ")
   else:
      file = sys.argv[1]
      aperture = sys.argv[2]


   try:
      f = open(file,'r')
   except IOError, e:
      print 'Failed to open '+file

   extracted = open('extracted_'+file,'w')

   # read in the file (as a list of lines for which each line is a string) 
   s = f.readlines()
   rows = len(s)
   flag = 0
   # FOR loop START
   for n in range(rows):
      # read in each line and split the string into a list of entries
      col = s[n].split(' ')
      # remove all list items that are unwanted
      while col.count('\n')>=1: 
         col.remove('\n')
      while col.count('')>=1: 
         col.remove('')
 
      if s[n].count('ok\n') == 1:
         flag = 1 
      if flag == 1 and len(col) == 10 and float(col[-1])==float(aperture):
         if col[7].count('INDEF') == 0:
            print >> extracted, s[n].replace('\n','')

   print "###################################################################"
   print "Output is available in :  extracted_"+file
   print "###################################################################"
