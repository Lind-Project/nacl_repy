"""
Verify that we can catch an excpetion defined in an imported library 
and raised in another.
"""
#pragma out Successfully caught Lib1Error().

from repyportability import *
add_dy_support(locals())

lib1 = dy_import_module("portability_testlib1.repy") # defines the exception
lib2 = dy_import_module("portability_testlib2.repy") # raises it

try:
  lib2.raise_lib1error()
except lib1.Lib1Error:
  log("Successfully caught Lib1Error().\n")
except Exception, e:
  log("Error: Expected Lib1Error() with id " + str(id(lib1.Lib1Error)) + 
      " but caught '" + repr(e) + "' with id " + str(id(e)) + " \n")

