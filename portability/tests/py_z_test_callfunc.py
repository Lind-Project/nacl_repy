"""
Test the callfunc arg of the translations, to make sure it actually
gets used

"""

import repyhelper
import test_utils

TESTFILE = 'rhtest_callfunc.repy'

#Make sure we have fresh translations per test run
test_utils.cleanup_translations([TESTFILE])

modname = repyhelper.translate(TESTFILE, callfunc='plankton')
a = __import__(modname)


### Try again with translate_and_import
#Allow retranslation
test_utils.cleanup_translations([TESTFILE])

repyhelper.translate_and_import(TESTFILE, callfunc='plankton')

test_utils.cleanup_translations([TESTFILE])
