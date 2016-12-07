"""
Test to see if restrictions can be initialized and restored from within Python.

"""
from repyportability import *

initialize_restrictions("restrictions.veryslowread")

import repyhelper


import sys

# in the call to this, it will do 'exitall' if the restrictions are in place
repyhelper.translate_and_import("rhtest_printifreadisfast.repy")


# We need to flush stdout (this won't be done for us unless it goes to the 
# terminal).
sys.stdout.flush()
