"""
Test if a call to importcachedir is handled well.

"""

import repyhelper

import os

import sys

import shutil

# clean up any left over data...
try:
  shutil.rmtree('importcachetest')
except (OSError, IOError):
  # it's okay if it doesn't exist...
  pass

os.mkdir('importcachetest')

# append this to the Python path...
sys.path = sys.path +  ['importcachetest']

# write files there
repyhelper.set_importcachedir('importcachetest')

repyhelper.translate_and_import('rhtestrecursion_1.repy')

# This should work...
try:
  # note: this is a function from rhtest_recursion_1.   I'm not calling it...
  one
except NameError:
  print "Failed to import rhtest_recursion_1 when using importcachetest"

# This should work...
try:
  # note: this is a function from rhtest_recursion_2.   I'm not calling it...
  two
except NameError:
  print "Failed to import rhtest_recursion_2 when using importcachetest"

# and the files should be in importcachetest...
if not os.path.exists('importcachetest/rhtestrecursion_1_repy.py'):
  print "The rhtest_recursion_1.repy file was not preprocessed to importcache test because 'importcachetest/rhtest_recursion_1_repy.py' does not exist"

if not os.path.exists('importcachetest/rhtestrecursion_2_repy.py'):
  print "The rhtest_recursion_2.repy file was not preprocessed to importcache test because 'importcachetest/rhtest_recursion_2_repy.py' does not exist"
