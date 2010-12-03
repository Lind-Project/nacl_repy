"""
Test if bad calls to importcachedir are handled.

"""

import repyhelper



try:
  repyhelper.set_importcachedir(153)
except TypeError:
  pass
else:
  print "Was able to set the cache dir to be something besides a string..."


try:
  repyhelper.set_importcachedir('asdkfjaNONEXISTANT_DIRasfj')
except TypeError:
  pass
else:
  print "Was able to set my cache to a nonexistant dir..."


try:
  repyhelper.set_importcachedir('..')
except ValueError:
  pass
else:
  print "Was able to set my cache to be a dir that's not in the python path..."



try:
  repyhelper.translate_and_import('./asdkfjaVALID_DIR_NONEXISTANT_FILEkasfj')
except ValueError:
  pass
else:
  print "Was able to import a nonexistant file in a valid dir..."


try: 
  repyhelper.translate_and_import('asaINVALID_DIRkasd/adjNONEXISTANT_FILEkaj')
except ValueError:
  pass
else:
  print "Was able to import a nonexistant file in an invalid dir..."

