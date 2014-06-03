#! /usr/bin/env python

########################################
# Differential photometry lightcurves  #
########################################

import sys
import os
import numpy

####################
##################
#  MAIN PROGRAM  #
##################
####################

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Enter the name of the file containing the data (lightcurves_based_on_....) :  ")
      starnumber = raw_input("What is the number of the star you wish to extract? :  ")
      complist = raw_input("Give the list of comparison stars (, separated with no spaces) or enter ALL to use all stars identified: ")
   else:
      file = sys.argv[1]
      starnumber = sys.argv[2]
      complist = sys.argv[3]

   # Open inputfile
   DIFFscript = open('DIFFscript','w')
   print >> DIFFscript, '#! /bin/bash'
   datalist = numpy.loadtxt(file.replace('differential_',''),dtype="float",usecols=(0,1),unpack=True)
   comparisonlist = []
   if complist == 'ALL':
      for m in range(int(max(datalist[0]))):
          comparisonlist.append(m+1)
      comparisonlist.remove(int(starnumber))
   else:
      templist = complist.split(',')
      for l in range(len(templist)):
          comparisonlist.append(int(templist[l]))

   os.system("rm "+file+"_diffLC*")
   print "RUNNING....:    "+"../extractSTAR_SHOClc.py "+file+" "+starnumber+" "+complist
   os.system("../extractSTAR_SHOClc.py "+file+" "+starnumber+" "+complist)
   print >> DIFFscript, "../extractSTAR_SHOClc.py "+file+" "+starnumber+" "+complist
   if len(comparisonlist) >1:
       print "##################################################################################################################"
       print "# The differential lightcurve for the target was produced and they will now be produced for all the comparisons. #"
       print "##################################################################################################################"
       for star in comparisonlist:    
           trimcomplist = str(comparisonlist).replace(' ','').lstrip('[').rstrip(']').split(',')
           #trimcomplist.remove(str(star))
           finalcomplist = str(trimcomplist).replace(' ','').lstrip('[').rstrip(']').replace("'",'')
           print "RUNNING....:    "+"../extractSTAR_SHOClc.py "+file+" "+str(star)+" "+finalcomplist
           os.system("../extractSTAR_SHOClc.py "+file+" "+str(star)+" "+finalcomplist)
           print >> DIFFscript, "../extractSTAR_SHOClc.py "+file+" "+str(star)+" "+finalcomplist
   else:
       print "#################################################################"
       print "# Only the differential lightcurve for the target was produced. #"
       print "#################################################################"
   os.system("cat "+file+"_diffLC* > differential_"+file)
   print >> DIFFscript, "cat "+file+"_diffLC* > differential_"+file
   print "RUNNING....:    "+"../plot_lcs.py differential_"+file
   os.system("../plot_lcs.py differential_"+file)
   print >> DIFFscript, "../plot_lcs.py differential_"+file
   os.system("chmod a+x DIFFscript")
#   os.system("chmod a+x ./MULTIscript_differential_"+file)
#   os.system("./MULTIscript_differential_"+file)
