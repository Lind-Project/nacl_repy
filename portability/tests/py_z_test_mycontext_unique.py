"""
Test to make sure specifying that modules have a unique mycontext works
"""

import repyhelper
import test_utils


TESTFILE1 = "rhtest_mycontext_unique1.repy"
TESTFILE2 = "rhtest_mycontext_unique2.repy"

test_utils.cleanup_translations([TESTFILE1, TESTFILE2])


modname1 = repyhelper.translate(TESTFILE1, shared_mycontext=False)
mod1 = __import__(modname1)

modname2 = repyhelper.translate(TESTFILE2, shared_mycontext=False)
mod2 = __import__(modname2)

if mod2.foo() is None:
  pass
else:
  print "Context sharing wasn't unique'! foo returned", mod2.foo()

test_utils.cleanup_translations([TESTFILE1, TESTFILE2])
