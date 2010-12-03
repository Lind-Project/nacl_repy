""" See if I can import a relative path... """

import repyhelper

import os
# to clean up...
import shutil
import sys

os.mkdir('testdirforrepyhelper')
os.mkdir('testdirforrepyhelper/child')

# The test file we'll use.
fo = file('testdirforrepyhelper/footest.repy','w')
fo.write('flibble = False')
fo.flush()
fo.close()
fo = file('testdirforrepyhelper/footest2.repy','w')
fo.write('flibble2 = 7')
fo.close()


# always clean up
try:
  repyhelper.translate_and_import('testdirforrepyhelper/footest.repy')

  try:
    if flibble:
      # this print shouldn't happen.   If it fails we should see the name error
      print "The first import failed (but oddly didn't give a name error)."
  except NameError:
    print "The first import failed"

  repyhelper.translate_and_import('testdirforrepyhelper/child/../footest2.repy')

  try:
    if flibble2 != 7:
      # this print shouldn't happen.   On failure we should see the name error
      print "The second import failed (but oddly didn't give a name error)."
  except NameError:
    print "The second import failed"
    

finally:
  shutil.rmtree('testdirforrepyhelper')
  pass

