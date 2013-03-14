#! /usr/bin/env python
import sys
import os

if __name__=='__main__':
   _nargs = len(sys.argv)
   if _nargs == 1:
      targetfile = raw_input("Name of the datacube containing TARGET data:  ")
      masterbias = raw_input("Name of master BIASfile: ")
   else:
      targetfile = sys.argv[1]
      masterbias = sys.argv[2]

print "######################################################################################################################################"
print "# PLEASE be PATIENT: The IRAF task 'imarith' (from images immatch imutil) is subtracting the master bias files from the target files #"
print "######################################################################################################################################"

import pyraf
from pyraf import iraf
from pyraf.iraf import images
from pyraf.iraf import immatch
from pyraf.iraf import imutil

imutil.imarith.operand1 = "@"+targetfile
imutil.imarith.op = "-"
imutil.imarith.operand2 = masterbias
imutil.imarith.result = "b//@"+targetfile
imutil.imarith.mode = "h"
imutil.imarith()

#Binary image arithmetic (images.imutil.imarith) is performed of the form:   operand1 op operand2 = result
#where  the  operators  are  addition,  subtraction,  multiplication, division, and minimum and maximum.  The division operator checks for nearly  zero  denominators  and  replaces  the  ratio  by  the value specified by the parameter  divzero.   The  operands  are  lists  of images  and  numerical constants and the result is a list of images.   The number of elements in an operand list  must  either  be  one  or   equal  the  number of elements in the resultant list.  If the number of elements is one then it is used for  each  resultant  image.   If the  number  is  equal  to  the  number of resultant images then the elements in the operand list are matched with the  elements  in  the resultant  list.   The  only limitation on the combination of images and constants in the operand lists  is  that  both  operands  for  a given  resultant  image  may not be constants.  The resultant images may have the same name as one of the operand images in which case  a temporary  image  is created and after the operation is successfully completed the image to be replaced is overwritten by  the  temporary image.    
#If  both operands are images the lengths of each axis for the common dimensions must be the same though the dimensions need  not  be  the same.   The  resultant  image  header  will be a copy of the operand image with the greater dimension.  If the dimensions  are  the  same then  image  header for the resultant image is copied from operand1.
#HOWEVER, the headers from Operand2 seems to be the one copied, NOT operand1 (as we would prefer)!!!
