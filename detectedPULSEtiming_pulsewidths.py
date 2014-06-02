#! /usr/bin/env python
import sys
import os
import numpy

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      observedpulsefile = raw_input("Name of the file that contains PULSE timing PYRAF info:  ")  
      predictedpulsefile = raw_input("Name of the file that contains PULSE predictions:  ") 
      exposure = raw_input("What was the exposure time [s]?   ") 
      increment = raw_input("Incremental time step [s]?   ") 
      detectionlevel = raw_input("At what counts are pulses detected?   ")
      factor = raw_input("What factor of EXPTIME forms the range investigated?   ")
      pulsewidth = raw_input("What is the average pulse width of second pulses [s]?   ")
   else:
      observedpulsefile = sys.argv[1]
      predictedpulsefile = sys.argv[2]
      exposure = sys.argv[3]
      increment = sys.argv[4]
      detectionlevel = sys.argv[5]
      factor = sys.argv[6]
      pulsewidth = sys.argv[7]

# determine the significant figures
if float(increment) < 1:
   sigfig = len(increment.split('.')[1])
else:
   sigfig = 0

pulsetimingaccuracy = open('pulsetimingaccuracy','w')
pulsetiminganalysis = open('pulsetiminganalysis','w')

exposure = float(exposure)
print 'Exposure: ', exposure
print >> pulsetiminganalysis, 'Exposure: ', exposure

factor =float(factor)
absoffset = round(exposure*factor,sigfig)
pulsewidth =float(pulsewidth)

corr = 0
offset = -absoffset

# 1 second pulses have width 100 ms
#pulsewidth = 0.1   -  INPUT ITEM
# margin should be allowed (10ms) - NO the HIPPO tests shows rise-time of ~1 ms
margin = 0

observedpulse = numpy.loadtxt(observedpulsefile,dtype="str", unpack = 'True')
predictedpulse = numpy.loadtxt(predictedpulsefile,dtype="str", unpack = 'True')

predictedtime = predictedpulse[0]
predictedheight = predictedpulse[1]
observedtime = observedpulse[0]
observedheight = observedpulse[1]

offsetperoffset = []
detectionsperoffset = []
detectedpercentageperoffset = []
secondpulses = []
secframe = []
minframe = []
minutepulses = []
temp = []
tempframe = []
pulselength = 0

# Identify all detections
for z in range(len(observedtime)):
   if float(observedheight[z]) > float(detectionlevel):
      secondpulses.append(round(float(observedtime[z]),5))
      secframe.append(z+1)

# Test pulse widths to distinguish minute pulses from second pulses
flag = 0
for zz in range(1,len(secondpulses)-1):
   if secondpulses[zz] - secondpulses[zz-1] <= 2*pulsewidth:
      temp.append(secondpulses[zz-1])
      tempframe.append(secframe[zz-1])
   else:
      temp = []
      tempframe = []
      flag = 0
   if len(temp)>2*pulsewidth/exposure and flag==0:
      minutepulses.append(round(temp[0],5))
      minframe.append(tempframe[0])
      flag = 1

if minframe[0] == 1:         
   print "Minute pulses occur at: ", minutepulses[1:]     
   print "On frames: ", minframe[1:]  
   print >> pulsetiminganalysis, "Minute pulses occur at: ", minutepulses[1:]  
   print >> pulsetiminganalysis,  "On frames: ", minframe[1:] 
else:
   print "Minute pulses occur at: ", minutepulses[:]     
   print "On frames: ", minframe[:]  
   print >> pulsetiminganalysis, "Minute pulses occur at: ", minutepulses[:]  
   print >> pulsetiminganalysis,  "On frames: ", minframe[:] 

while offset < absoffset+float(increment):
   detections = 0
   exposures = 0 
   print >> pulsetimingaccuracy, '======================================    Offset: ', offset, '    ================================'
   for i in range(len(predictedtime)):
      for j in range(1,len(observedtime)-1):
         if float(observedtime[j])+corr+offset <= float(predictedtime[i])+margin < float(observedtime[j])+corr+offset+exposure:
              print >> pulsetimingaccuracy, predictedtime[i], round(float(observedtime[j])+corr,3), round(float(observedtime[j])+corr-float(predictedtime[i]),3), '\t\t', observedheight[j], '\t\t',round(float(observedtime[j+1])-float(observedtime[j]),3)
              if float(observedheight[j]) > float(detectionlevel):
                  # count only the start of the observed pulse (especially relevant if pulsewidth > exposure)
                  if pulsewidth > exposure:
                     if float(observedheight[j-1]) < float(detectionlevel):
                        detections = detections + 1
                  else:
                     detections = detections + 1
              else:
                  print >> pulsetimingaccuracy, "##############"
                  print >> pulsetimingaccuracy, 'Missed UTC-OBS: ', predictedtime[i], round(float(observedtime[j])+corr,3), round(float(observedtime[j])+corr-float(predictedtime[i]),3), '\t\t', observedheight[j], '\t\t',round(float(observedtime[j+1])-float(observedtime[j]),3)
              exposures = exposures + 1 
   print 'Offset: ', offset
   print 'Detections: ', detections, ' out of ', exposures, ' exposures.', 'Percentage:', 100*float(detections)/float(exposures), ' %'
   print 'Total number of pulses:  ', len(predictedtime)
   print >> pulsetiminganalysis, 'Offset: ', offset
   percentagedetected = 100*float(detections)/float(exposures)
   print >> pulsetiminganalysis, 'Detections: ', detections, ' out of ', exposures, ' exposures.', 'Percentage:', percentagedetected, ' %'
   print >> pulsetiminganalysis, 'Total number of pulses:  ', len(predictedtime)
   offsetperoffset.append(offset)  
   detectionsperoffset.append(detections)
   detectedpercentageperoffset.append(percentagedetected)
   offset = round(offset + float(increment),sigfig)

print '===================================================================================================='
print >> pulsetiminganalysis, '===================================================================================================='

for k in range(len(offsetperoffset)):
   if detectionsperoffset[k] == max(detectionsperoffset) or detectedpercentageperoffset[k] == max(detectedpercentageperoffset):
      print 'Max Detections: ', detectionsperoffset[k], '('+str(detectedpercentageperoffset[k])+'%)', 'for Offset: ', offsetperoffset[k]
      print >> pulsetiminganalysis, 'Max Detections: ', detectionsperoffset[k], '('+str(detectedpercentageperoffset[k])+'%)', 'for Offset: ', offsetperoffset[k]
