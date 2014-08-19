"""
Test to make sure specifying that modules have a shared mycontext 
"""

import repyhelper
import test_utils


TESTFILE1 = "rhtest_mycontext_shared1.repy"
TESTFILE2 = "rhtest_mycontext_shared2.repy"

test_utils.cleanup_translations([TESTFILE1, TESTFILE2])

modname1 = repyhelper.translate(TESTFILE1, shared_mycontext=True)
mod1 = __import__(modname1)
reload(mod1)

modname2 = repyhelper.translate(TESTFILE2, shared_mycontext=True)
mod2 = __import__(modname2)
reload(mod2)

result = mod2.foo()
if result == 'bar':
  pass
else:
  print "Context sharing failed! foo returned", mod2.foo()
  print "mod1's mycontext =", mod1.mycontext
  print "mod2's mycontext =", mod2.mycontext

test_utils.cleanup_translations([TESTFILE1, TESTFILE2])
