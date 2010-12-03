import test_utils
import repyhelper

TESTFILE = "rhtest_callargs.repy"
#Make sure we have fresh translations per test run

test_utils.cleanup_translations([TESTFILE])


#Now test that the string escaping works properly
modname = repyhelper.translate(TESTFILE, callargs=["\"a\"", "samoas", "\\\'b\"\\", ""])
mod = __import__(modname)


if mod.callargs[0] != "\"a\"":
  print "double quotes not properly escaped:", mod.callargs[0]
if mod.callargs[1] != "samoas":
  print "simple string badly escaped:", mod.callargs[2]
if mod.callargs[2] != "\\\'b\"\\":
  print "double/single quotes not escaped properly:", mod.callargs[1]
if mod.callargs[3] != "":
  print "empty string improperly passed:", mod.callargs[1]

test_utils.cleanup_translations([TESTFILE])
import time
time.sleep(1)
