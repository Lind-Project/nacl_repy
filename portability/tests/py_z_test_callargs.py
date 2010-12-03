"""
Test the callargs parameter of the translation calls, to make sure it actually
gets used

"""

import repyhelper
import test_utils

TESTFILE = "rhtest_callargs.repy"

#Make sure we have fresh translations per test run
test_utils.cleanup_translations([TESTFILE])


modname = repyhelper.translate(TESTFILE, callargs=["", "samoas"])
mod = __import__(modname)

if mod.num_callargs() is not 2:
  print "translate had wrong number of callargs:", mod.num_callargs()
  print "callargs =", mod.callargs

test_utils.cleanup_translations([TESTFILE])
import time
time.sleep(1)