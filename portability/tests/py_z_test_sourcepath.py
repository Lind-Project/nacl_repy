"""
Test if files are written to the directory they came from by default

"""

import repyhelper

import os

import sys

import shutil

# clean up any left over data...
try:
  shutil.rmtree('sourcepathtest')
except (OSError, IOError):
  # it's okay if it doesn't exist...
  pass

os.mkdir('sourcepathtest')

# prepend this to the Python path...
sys.path = ['sourcepathtest'] + sys.path

# remove the file if it's there...
if os.path.exists('rhtest_filetests_repy.py'):
  os.remove('rhtest_filetests_repy.py')

# write files there
repyhelper.translate_and_import('rhtest_filetests.repy')

# This should work...
try:
  rhtest_filetests_exists()
except NameError:
  print "Failed to import rhtest_filetests when using sourcepath test"

# and the file should be in the current directory.
if not os.path.exists('rhtest_filetests_repy.py'):
  print "The rhtest_filetests.repy file was not preprocessed to the current directory because 'rhtest_filetests_repy.py' does not exist"
