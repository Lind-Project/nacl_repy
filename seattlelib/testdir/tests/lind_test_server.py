"""
  Author: Justin Cappos
  Module: Lind test server.   This allows python code to call any function in 
          any of the modules and for the modules to call each other.

  Start Date: February 25th, 2012


"""

# This file sets up the different lind modules that need to call each other.   
# It imports everything and then monkey-patches a few references so that 
# everything points to everything else correctly.

# We want all of the following in the main namespace
from repy_workarounds import *
from lind_fs_constants import *
from lind_net_constants import *

def log(msg):
    print msg

# execute these as scripts.   This means importing them into the current 
# namespace as though they were included here...
execfile('lind_fs_calls.py')
execfile('lind_net_calls.py')

