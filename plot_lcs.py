#! /usr/bin/env python

####################################################################################################
#  Plot all Extracted lightcurves for targets on which aperture corrected photometry as been done. #
####################################################################################################

import sys
import os
import numpy

#################
#  MAIN PROGRAM #
#################
if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      file = raw_input("Name of the file that contains the extracted lightcurves:  ")

   else:
      file = sys.argv[1]

   try:
      # filenamelist = loadtxt(file,dtype="str",usecols=(0),delimiter=' ',unpack=True)
      datalist = numpy.loadtxt(file,dtype="float",usecols=(0,1,2,3,4,5,6),unpack=True) 
   except IOError, e:
      sys.exit(file+" does not exist.")
   # Open OUTPUT files
   MULTIscript = open('MULTIscript_'+file,'w')
   print >> MULTIscript, '#! /bin/bash'
   coordinates = open('coordinates_'+file,'w')

   # Clear previous plots
   os.system('rm MULTIgnuplotscript*'+file)
   os.system('rm Lightcurves_*_'+file+'.eps')


   star = []
   star.append(int(datalist[0][0]))
   for i in range(1,len(datalist[0])):
       if datalist[0][i] != datalist[0][i-1]:
          star.append(int(datalist[0][i]))
   entries = len(star)
   minTIME = min(datalist[3])
   startTIME = str(minTIME)
   maxTIME = max(datalist[3])
   endTIME = str(maxTIME)
   if minTIME > 1000000:
       startTIMEsec = str((minTIME-minTIME)*24*60*60)
       endTIMEsec = str((maxTIME-minTIME)*24*60*60)
       factor = 24*60*60
   else:
       startTIMEsec = str((minTIME-minTIME))
       endTIMEsec = str((maxTIME-minTIME))
       factor = 1
   
   times10 = int(float(entries)/10)+1 
   if 10*(times10-1) == entries:
          times10 = times10 -1


   plotscale = raw_input("What is the plot scale [mag] (default:0.25)?  ")
   if plotscale in (''):
       plotscale = 0.25
   else:
       plotscale = float(plotscale)

   targetnumber = []
   Xcoord = []
   Ycoord = []
   lowerlimit = []
   upperlimit = []
   center = []
   flux = []
   apertures = []
   optimalaperture = []
   
   targetnumber.append(datalist[0][0])
   Xcoord.append(datalist[1][0])
   Ycoord.append(datalist[2][0])
   flux.append(datalist[4][0])
   apertures.append(datalist[6][0])
   for k in range(1,len(datalist[0])):
          if datalist[0][k] == datalist[0][k-1]:
               flux.append(datalist[4][k])
               apertures.append(datalist[6][k])
          else:
               targetnumber.append(datalist[0][k])
               Xcoord.append(datalist[1][k])
               Ycoord.append(datalist[2][k])
               if len(flux)>1:
                  #ymax = min(flux)
                  #ymin = max(flux)
                  average = numpy.mean(flux)
                  averageaperture = numpy.mean(apertures)
               else:
                  #ymax = datalist[4][k-1]
                  #ymin = datalist[4][k-1]
                  average = datalist[4][k-1]
                  averageaperture = datalist[6][k-1]
               #lowerlimit.append(ymin+(ymin-ymax))
               #upperlimit.append(ymax-(ymin-ymax))
               lowerlimit.append(average-plotscale*2)
               upperlimit.append(average+plotscale)
               center.append(average)
               flux = []
               optimalaperture.append(averageaperture)
               apertures = []
   #ymax = min(flux)
   #ymin = max(flux)
   average = numpy.mean(flux)
   averageaperture = numpy.mean(apertures)
#   lowerlimit.append(ymin+(ymin-ymax))
#   upperlimit.append(ymax-(ymin-ymax))
   lowerlimit.append(average-plotscale*2)
   upperlimit.append(average+plotscale)
   center.append(average)
   optimalaperture.append(averageaperture)
   print "                                                                         "
   if file.count('differential') > 0:
       print "###############################################################################################################"
       print "# Differential lightcurves have been extracted from "+file.replace('differential_lightcurves_based_on_','')[:-5]+".fits"+" for all the sources listed below:    #"
       print "###############################################################################################################"
   else:
       print "###################################################################################################################################"
       print "# Lightcurves have been extracted from "+file.replace('lightcurves_based_on_','')[:-5]+".fits"+" for all the sources listed below:    #"
       print "###################################################################################################################################"
   print 'Target', '\t', 'X', '\t', 'Y', '\t', 'Average Mag', '\t', 'Average Optimal Aperture'
   print >> coordinates, '#Target', '  X', '\t', '  Y', '\t', 'Average Mag', '\t', 'Average Optimal Aperture'
   for j in range(len(targetnumber)):
          print int(targetnumber[j]),'\t', Xcoord[j], '\t', Ycoord[j], '\t', round(center[j],2), '\t\t', round(optimalaperture[j],2)
          print >> coordinates, int(targetnumber[j]),'\t', Xcoord[j], '\t', Ycoord[j], '\t', round(center[j],2), '\t\t', round(optimalaperture[j],2)
#          print >> coordinates, 'Target ', int(targetnumber[j]), '           X = ', Xcoord[j], '      Y = ', Ycoord[j],  '      Average Mag: ', center[j], '      Optimal Aperture: ', optimalaperture[j]
          
   ##################################
   # MULTI PLOTS  - GNUPLOT scripts #   PORTRAIT
   ##################################
   timespan = float(endTIMEsec) - float(startTIMEsec)
   if timespan > 20000:
         scale = 5000
   elif timespan > 10000:
         scale = 2000
   elif timespan > 5000:
         scale = 1000
   elif timespan > 2000:
         scale = 500
   elif timespan > 1000:
         scale = 200
   else:
         scale = 100
         
   # FOR loop START       
   for i in range(times10):
          MULTIgnuplotscript = open('MULTIgnuplotscript'+str(i)+'_'+file,'w') 
          print >> MULTIscript, 'gnuplot<' + str('MULTIgnuplotscript'+str(i)+'_'+file) 
          print >> MULTIgnuplotscript, "set output 'Lightcurves_"+str(i)+'_'+file+".eps'"
          print >> MULTIgnuplotscript, "set terminal postscript portrait" 
          if file.count('differential') > 0:
              print >> MULTIgnuplotscript, "set multiplot layout 11,1 title 'DIFFERENTIAL lightcurves for "+file.replace('differential_lightcurves_based_on_','')[:-5]+".fits'"
          else:
              print >> MULTIgnuplotscript, "set multiplot layout 11,1 title 'RAW lightcurves for "+file.replace('lightcurves_based_on_','')[:-5]+".fits'"
          #print >> MULTIgnuplotscript, "set multiplot layout 11,1"
          print >> MULTIgnuplotscript, "set tmargin 0.25"
          print >> MULTIgnuplotscript, "set bmargin 0"
          print >> MULTIgnuplotscript, "set lmargin at screen 0.15"
          print >> MULTIgnuplotscript, "set rmargin at screen 0.98"
          print >> MULTIgnuplotscript, "set pointsize 0.3"
          print >> MULTIgnuplotscript, "unset xtics"  
          print >> MULTIgnuplotscript, "set ytics font "+'"Helvetica,7"'
          if file.count('differential') > 0:
              print  '###################################################################################################################################'
              print  'To view the DIFFERENTIAL lightcurves, type:        gs ' + 'Lightcurves_'+str(i)+'_'+file+'.eps &'
              print  '###################################################################################################################################'
              #print >> MULTIgnuplotscript, "set title 'DIFFERENTIAL lightcurves for "+file.replace('differential_lightcurves_based_on_','')[:-5]+".fits'"
          else:
              print  '########################################################################################################################'
              print  'To view RAW lightcurves, type:        gs ' + 'Lightcurves_'+str(i)+'_'+file+'.eps &'
              print  '########################################################################################################################'
              #print >> MULTIgnuplotscript, "set title 'RAW lightcurves for "+file.replace('lightcurves_based_on_','')[:-5]+".fits'"
          print >> MULTIgnuplotscript, "set ylabel '  ' font "+'"Helvetica,14"'       
          print >> MULTIgnuplotscript, "set label 'Instrumental Magnitude' font "+'"Helvetica,14" at screen 0.02,0.5 rotate by 90'

          if i*10+0 < entries:
              if i*10+0 == entries-1:
                  print >> MULTIgnuplotscript, "set xlabel 'Time [seconds]'"#+startTIME+"'"
                  print >> MULTIgnuplotscript, "set xtics 0,"+str(scale)+",100000 font "+'"Helvetica,9"' 
              print >> MULTIgnuplotscript, "set yrange ["+str(upperlimit[i*10+0])+":"+str(lowerlimit[i*10+0])+"] reverse"
              print >> MULTIgnuplotscript, "plot ["+startTIMEsec+":"+endTIMEsec+"] "+"[] '"+str(file).replace('.fits','')+"' using ($4-"+startTIME+")*"+str(factor)+":5:($1=="+str(star[i*10+0])+" ? $1:(1/0)) pt 7 title 'Source: "+str(star[i*10+0])+"  at X = "+str(Xcoord[i*10+0])+"  Y = "+str(Ycoord[i*10+0])
              print >> MULTIgnuplotscript, "unset label"
          print >> MULTIgnuplotscript, "unset title"
          print >> MULTIgnuplotscript, "set tmargin 0"

          if i*10+1 < entries:
              if i*10+1 == entries-1:
                  print >> MULTIgnuplotscript, "set xlabel 'Time [seconds]'"#+startTIME+"'"
                  print >> MULTIgnuplotscript, "set xtics 0,"+str(scale)+",100000 font "+'"Helvetica,9"' 
              print >> MULTIgnuplotscript, "set yrange ["+str(upperlimit[i*10+1])+":"+str(lowerlimit[i*10+1])+"] reverse"
              print >> MULTIgnuplotscript, "plot ["+startTIMEsec+":"+endTIMEsec+"] "+"[] '"+str(file).replace('.fits','')+"' using ($4-"+startTIME+")*"+str(factor)+":5:($1=="+str(star[i*10+1])+" ? $1:(1/0)) pt 7 title 'Source: "+str(star[i*10+1])+"  at X = "+str(Xcoord[i*10+1])+"  Y = "+str(Ycoord[i*10+1])
              print >> MULTIgnuplotscript, "unset label"

                    
          if i*10+2 < entries:
              if i*10+2 == entries-1:
                  print >> MULTIgnuplotscript, "set xlabel 'Time [seconds]'"#+startTIME+"'"
                  print >> MULTIgnuplotscript, "set xtics 0,"+str(scale)+",100000 font "+'"Helvetica,9"' 
              print >> MULTIgnuplotscript, "set yrange ["+str(upperlimit[i*10+2])+":"+str(lowerlimit[i*10+2])+"] reverse"
              print >> MULTIgnuplotscript, "plot ["+startTIMEsec+":"+endTIMEsec+"] "+"[] '"+str(file).replace('.fits','')+"' using ($4-"+startTIME+")*"+str(factor)+":5:($1=="+str(star[i*10+2])+" ? $1:(1/0)) pt 7 title 'Source: "+str(star[i*10+2])+"  at X = "+str(Xcoord[i*10+2])+"  Y = "+str(Ycoord[i*10+2])
              print >> MULTIgnuplotscript, "unset label"

                
          if i*10+3 < entries:
              if i*10+3 == entries-1:
                  print >> MULTIgnuplotscript, "set xlabel 'Time [seconds]'"#+startTIME+"'"
                  print >> MULTIgnuplotscript, "set xtics 0,"+str(scale)+",100000 font "+'"Helvetica,9"' 
              print >> MULTIgnuplotscript, "set yrange ["+str(upperlimit[i*10+3])+":"+str(lowerlimit[i*10+3])+"] reverse"
              print >> MULTIgnuplotscript, "plot ["+startTIMEsec+":"+endTIMEsec+"] "+"[] '"+str(file).replace('.fits','')+"' using ($4-"+startTIME+")*"+str(factor)+":5:($1=="+str(star[i*10+3])+" ? $1:(1/0)) pt 7 title 'Source: "+str(star[i*10+3])+"  at X = "+str(Xcoord[i*10+3])+"  Y = "+str(Ycoord[i*10+3])
              print >> MULTIgnuplotscript, "unset label"

                    
          if i*10+4 < entries:
              if i*10+4 == entries-1:
                  print >> MULTIgnuplotscript, "set xlabel 'Time [seconds]'"#+startTIME+"'"
                  print >> MULTIgnuplotscript, "set xtics 0,"+str(scale)+",100000 font "+'"Helvetica,9"' 
              print >> MULTIgnuplotscript, "set yrange ["+str(upperlimit[i*10+4])+":"+str(lowerlimit[i*10+4])+"] reverse"
              print >> MULTIgnuplotscript, "plot ["+startTIMEsec+":"+endTIMEsec+"] "+"[] '"+str(file).replace('.fits','')+"' using ($4-"+startTIME+")*"+str(factor)+":5:($1=="+str(star[i*10+4])+" ? $1:(1/0)) pt 7 title 'Source: "+str(star[i*10+4])+"  at X = "+str(Xcoord[i*10+4])+"  Y = "+str(Ycoord[i*10+4])
              print >> MULTIgnuplotscript, "unset label"

          
          if i*10+5 < entries:
              if i*10+5 == entries-1:
                  print >> MULTIgnuplotscript, "set xlabel 'Time [seconds]'"#+startTIME+"'"
                  print >> MULTIgnuplotscript, "set xtics 0,"+str(scale)+",100000 font "+'"Helvetica,9"' 
              print >> MULTIgnuplotscript, "set yrange ["+str(upperlimit[i*10+5])+":"+str(lowerlimit[i*10+5])+"] reverse"
              print >> MULTIgnuplotscript, "plot ["+startTIMEsec+":"+endTIMEsec+"] "+"[] '"+str(file).replace('.fits','')+"' using ($4-"+startTIME+")*"+str(factor)+":5:($1=="+str(star[i*10+5])+" ? $1:(1/0)) pt 7 title 'Source: "+str(star[i*10+5])+"  at X = "+str(Xcoord[i*10+5])+"  Y = "+str(Ycoord[i*10+5])
              print >> MULTIgnuplotscript, "unset label"
         
          if i*10+6 < entries:
              if i*10+6 == entries-1:
                  print >> MULTIgnuplotscript, "set xlabel 'Time [seconds]'"#+startTIME+"'"
                  print >> MULTIgnuplotscript, "set xtics 0,"+str(scale)+",100000 font "+'"Helvetica,9"' 
              print >> MULTIgnuplotscript, "set yrange ["+str(upperlimit[i*10+6])+":"+str(lowerlimit[i*10+6])+"] reverse"
              print >> MULTIgnuplotscript, "plot ["+startTIMEsec+":"+endTIMEsec+"] "+"[] '"+str(file).replace('.fits','')+"' using ($4-"+startTIME+")*"+str(factor)+":5:($1=="+str(star[i*10+6])+" ? $1:(1/0)) pt 7 title 'Source: "+str(star[i*10+6])+"  at X = "+str(Xcoord[i*10+6])+"  Y = "+str(Ycoord[i*10+6])
              print >> MULTIgnuplotscript, "unset label"
        
          if i*10+7 < entries:
              if i*10+7 == entries-1:
                  print >> MULTIgnuplotscript, "set xlabel 'Time [seconds]'"#+startTIME+"'"
                  print >> MULTIgnuplotscript, "set xtics 0,"+str(scale)+",100000 font "+'"Helvetica,9"' 
              print >> MULTIgnuplotscript, "set yrange ["+str(upperlimit[i*10+7])+":"+str(lowerlimit[i*10+7])+"] reverse"
              print >> MULTIgnuplotscript, "plot ["+startTIMEsec+":"+endTIMEsec+"] "+"[] '"+str(file).replace('.fits','')+"' using ($4-"+startTIME+")*"+str(factor)+":5:($1=="+str(star[i*10+7])+" ? $1:(1/0)) pt 7 title 'Source: "+str(star[i*10+7])+"  at X = "+str(Xcoord[i*10+7])+"  Y = "+str(Ycoord[i*10+7])
              print >> MULTIgnuplotscript, "unset label"

          if i*10+8 < entries:
              if i*10+8 == entries-1:
                  print >> MULTIgnuplotscript, "set xlabel 'Time [seconds]'"#+startTIME+"'"
                  print >> MULTIgnuplotscript, "set xtics 0,"+str(scale)+",100000 font "+'"Helvetica,9"' 
              print >> MULTIgnuplotscript, "set yrange ["+str(upperlimit[i*10+8])+":"+str(lowerlimit[i*10+8])+"] reverse"
              print >> MULTIgnuplotscript, "plot ["+startTIMEsec+":"+endTIMEsec+"] "+"[] '"+str(file).replace('.fits','')+"' using ($4-"+startTIME+")*"+str(factor)+":5:($1=="+str(star[i*10+8])+" ? $1:(1/0)) pt 7 title 'Source: "+str(star[i*10+8])+"  at X = "+str(Xcoord[i*10+8])+"  Y = "+str(Ycoord[i*10+8])
              print >> MULTIgnuplotscript, "unset label"

          print >> MULTIgnuplotscript, "set xlabel 'Time [seconds]'"#+startTIME+"'"
          print >> MULTIgnuplotscript, "set xtics 0,"+str(scale)+",100000 font "+'"Helvetica,9"'          
          if i*10+9 < entries:
              if i*10+9 == entries-1:
                  print >> MULTIgnuplotscript, "set xlabel 'Time [seconds]'"#+startTIME+"'"
                  print >> MULTIgnuplotscript, "set xtics 0,"+str(scale)+",100000 font "+'"Helvetica,9"' 
              print >> MULTIgnuplotscript, "set yrange ["+str(upperlimit[i*10+9])+":"+str(lowerlimit[i*10+9])+"] reverse"
              print >> MULTIgnuplotscript, "plot ["+startTIMEsec+":"+endTIMEsec+"] "+"[] '"+str(file).replace('.fits','')+"' using ($4-"+startTIME+")*"+str(factor)+":5:($1=="+str(star[i*10+9])+" ? $1:(1/0)) pt 7 title 'Source: "+str(star[i*10+9])+"  at X = "+str(Xcoord[i*10+9])+"  Y = "+str(Ycoord[i*10+9])
              print >> MULTIgnuplotscript, "unset label"
          print >> MULTIgnuplotscript, "unset multiplot"
          print >> MULTIgnuplotscript, "exit"
          MULTIgnuplotscript.close()
   # FOR loop END 
   MULTIscript.close()   

os.system("chmod a+x ./MULTIscript_"+file)
#print "chmod a+x ./MULTIscript_"+file
os.system("./MULTIscript_"+file)
#print "./MULTIscript_"+file

print "##################################################################################"
print "#  If you want to replot using a different scale, run it by:                     #"
print "#   ../plot_lcs.py "+file
print "##################################################################################"
