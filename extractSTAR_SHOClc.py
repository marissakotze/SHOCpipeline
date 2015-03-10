#! /usr/bin/env python

###########################################################
# Extract data for a star from lightcurve files for SHOC  #
###########################################################

import sys
import numpy

##################
#  MAIN PROGRAM  #
##################

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Enter the name of the file containing the data (lightcurve_based_on_....) :  ")
      starnumber = raw_input("What is the number of the star you wish to extract? :  ")
      complist = raw_input("Give the list of comparison stars (, separated with no spaces) or enter ALL to use all stars identified: ")
   else:
      file = sys.argv[1]
      starnumber = sys.argv[2]
      complist = sys.argv[3]
    
#   RAWlightcurve = open(file+'_rawLC_star_'+str(starnumber),'w') 
#   COMPlightcurve = open(file+'_compsLC_star_'+str(starnumber),'w')
   differential = open(file+'_diffLC_star_'+str(starnumber),'w')
   
   # filenamelist = loadtxt(file,dtype="str",usecols=(0),delimiter=' ',unpack=True)
   datalist = numpy.loadtxt(file,dtype="float",usecols=(0,1,2,3,4,5,6),unpack=True)
   extdatalist = numpy.loadtxt(file,dtype="str",usecols=(7,8,9),unpack=True)

   comparisons = []
   target = []   
   for i in range(len(datalist[0])):     
      hjdtemp = datalist[3][i]
      #hjdvalue = str(int(hjdtemp))+'.'+str(hjdtemp-int(hjdtemp)).lstrip('0.')
      hjdvalue = hjdtemp
      if datalist[0][i] == float(starnumber):        
#          print >> RAWlightcurve, datalist[0][i], datalist[1][i], datalist[2][i], hjdvalue, datalist[4][i], datalist[5][i], "#"     
          target.append((hjdvalue, datalist[4][i], datalist[5][i], datalist[0][i], datalist[1][i], datalist[2][i], datalist[6][i], extdatalist[0][i], extdatalist[1][i], extdatalist[2][i]))
      else:
          comparisons.append((int(datalist[0][i]), hjdvalue, datalist[4][i], datalist[5][i], datalist[0][i], datalist[1][i], datalist[2][i], datalist[6][i], extdatalist[0][i], extdatalist[1][i], extdatalist[2][i]))
   
   comparisonlist = []
   if complist == 'ALL':
      for m in range(int(max(datalist[0]))):
          comparisonlist.append(m+1)
      comparisonlist.remove(int(starnumber))
   else:
      templist = complist.split(',')
      for l in range(len(templist)):
          comparisonlist.append(int(templist[l]))

   diffphot = []
   rawcomp = []

   for j in range(len(target)):
       allcomparisons = 0
       n = 0
       for k in range(len(comparisons)):
           if target[j][0] == comparisons[k][1] and comparisonlist.count(comparisons[k][0]) > 0:
               allcomparisons = allcomparisons + comparisons[k][2]
               n = n+1
       if n > 0:
           diffphot.append([target[j][0], target[j][1]/(allcomparisons/n),target[j][2],target[j][3],target[j][4],target[j][5],target[j][6],target[j][7],target[j][8],target[j][9]])
           rawcomp.append([target[j][0], allcomparisons/n])
   overallsum = 0
   for m in range(len(rawcomp)):
       overallsum = overallsum + rawcomp[m][1]
   overallaverage = overallsum/len(rawcomp)
   #print >> differential, '# Source Nr   ', 'X   ','Y   ','HJD   ','MAG   ','MAGerr   ','Optimal Aperture'
   print >> differential, '# Source Nr  ', 'X  ','Y  ','Seconds since 00:00   ','MAG   ','MAGerr   ','Optimal Aperture   ', 'File name   ', 'Start of exposure (UTC)', 'HMJD'
   for k in range(len(diffphot)):
       print >> differential, int(float(diffphot[k][3])), diffphot[k][4], diffphot[k][5], round(float(diffphot[k][0]),6), diffphot[k][1]*overallaverage, diffphot[k][2], diffphot[k][6], diffphot[k][7], diffphot[k][8], diffphot[k][9]
#       print >> COMPlightcurve, rawcomp[k][0], rawcomp[k][1]
