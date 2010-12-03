"""
Test if files are written to the first path if a relative path name is used.

"""

import repyhelper

import os

import sys

import shutil

# clean up any left over data...
try:
  shutil.rmtree('firstpathtest')
except (OSError, IOError):
  # it's okay if it doesn't exist...
  pass

os.mkdir('firstpathtest')

# prepend this to the Python path...
sys.path = ['firstpathtest'] + sys.path

# A RELATIVE IMPORT...   SHOULD BE WRITTEN TO sys.path[0]
repyhelper.translate_and_import('./rhtest_filetests.repy')

# This should work...
try:
  rhtest_filetests_exists()
except NameError:
  print "Failed to import rhtest_filetests when using firstpath test"

# and the file should be in the current directory.
if not os.path.exists('firstpathtest/rhtest_filetests_repy.py'):
  print "The rhtest_filetests.repy file was not preprocessed to the correct directory because 'firstpathtest/rhtest_filetests_repy.py' does not exist"
