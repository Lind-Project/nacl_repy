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

# NOTICE THE RELATIVE PATH NAME!!!
repyhelper.translate_and_import('./rhtest_filetests.repy')

# This should work...
try:
  rhtest_filetests_exists()
except NameError:
  print "Failed to import rhtest_filetests when using importcachetest"

# and the file should be in importcachetest...
if not os.path.exists('importcachetest/rhtest_filetests_repy.py'):
  print "The rhtest_filetests.repy file was not preprocessed to importcache test because 'importcachetest/rhtest_filetests_repy.py' does not exist"
