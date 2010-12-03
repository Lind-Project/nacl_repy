"""
Author: Andreas Sekine
Description
  Tests various file name formats for calls to translate
  
  No output indicates success

"""

import os
import repyhelper
import test_utils

def prepare_file(filename):
  #make an empty test file of name filename
  try:
    fh = open(filename, "w")
    fh.close()
    return True
  except IOError, e:
    print "Error opening file for test:", filename
    return False
    
    
def test_name(name, expected):
  if prepare_file(name):
    translation_name = repyhelper.translate(name)
    
    if translation_name != expected:
      print "ERROR: expected:", expected, " but translation name was:", translation_name
      
    test_utils.cleanup_file(name)
    test_utils.cleanup_file(translation_name + ".py")
  else:
    print "Couldn't prepare test for filename test:", name


test_name("rhtestname_file1.repy", "rhtestname_file1_repy")
test_name("rhtestname_file2.py", "rhtestname_file2_py")
test_name("rhtestname.file3.py", "rhtestname_file3_py")
test_name("rhtestname.file4.repy", "rhtestname_file4_repy")
test_name("rhtestname file5.repy", "rhtestname file5_repy")
test_name("./rhtestname_file6.repy", "rhtestname_file6_repy")

