"""
Test the filename parameter of the translation calls, to make sure errors are
handled well.

"""

import repyhelper



try:
  repyhelper.translate_and_import('asdkfjaNONEXISTANT_FILEkasfj')
except ValueError:
  pass
else:
  print "Was able to import a nonexistant file (no dir)..."



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

