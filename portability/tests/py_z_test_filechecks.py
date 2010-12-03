"""
Author: Andreas Sekine
Description:
  Tests the checks performed to determine whether or not a file needs to be
  retranslated.
  
  No output indicates success
  
"""

import os
import repyhelper
import test_utils
  
#The (preexisting) repy file to use as a reference for translating
SRCFILE = "rhtest_filetests.repy"

#The temporary file to create to perform checks against
TESTFILE = "rhtest_filetests_new.repy"

#The translation name corresponding to TESTFILE
TESTFILE_TR = repyhelper._get_module_name(TESTFILE) + ".py"



def create_testfile(filename, contents):
  """
  Create a file in the current directory with a specified translation tagline file tag
  returns the name of the created file
  """
  fh = open(filename, 'w')
  print >> fh, contents
  fh.close()
  return filename
  
  
create_testfile(TESTFILE, repyhelper.TRANSLATION_TAGLINE)

### Test Nonexistant Files ###

if repyhelper._translation_is_needed(SRCFILE, "file_doesnt_exist'"):
  pass
else:
  print "Test failed for translation path that doesn't exist'"

test_utils.cleanup_file(TESTFILE_TR)

#Test source (repy) file
try: 
  repyhelper._translation_is_needed("random_file246565324", TESTFILE)
except repyhelper.TranslationError:
  pass
else:
  print "Didnt raise exception when provided nonexistant souce file"

test_utils.cleanup_file(TESTFILE_TR)

create_testfile(TESTFILE, repyhelper.TRANSLATION_TAGLINE)

#Test directory...
try: 
  repyhelper._translation_is_needed("..", TESTFILE)
except repyhelper.TranslationError:
  pass
else:
  print "Directory passed test as file needing to be read"

test_utils.cleanup_file(TESTFILE_TR)



### Now test the tagline test ###

#Create a file without the tagline, to see if an anonomous file would get clobbered
create_testfile(TESTFILE, "gibberish!\n")
try:
  repyhelper._translation_is_needed(SRCFILE, TESTFILE)
except repyhelper.TranslationError:
  pass
else:
  print "Tagline detection incorrectly passed, would have clobbered file"

test_utils.cleanup_file(TESTFILE_TR)


#Now see if a translation from a different source path prompts a regen
create_testfile(TESTFILE, repyhelper.TRANSLATION_TAGLINE + " " + os.path.abspath('./foo'))
if repyhelper._translation_is_needed(SRCFILE, TESTFILE):
  pass
else:
  print "Mismatched absolute source path of regen didn't prompt a new generation!"

test_utils.cleanup_file(TESTFILE_TR)


### Test the filetime modification checks ###

#create a fake translation with the correct tagline, and a newer modification time
#on the source. This means regen should be required
create_testfile(TESTFILE, repyhelper.TRANSLATION_TAGLINE)

#touch the source file so it thinks translation is needed
os.utime(SRCFILE, None)

if repyhelper._translation_is_needed(SRCFILE, TESTFILE):
  pass
else:
  print "File modification time test incorrectly failed! Didn't detect change in source file"
  
test_utils.cleanup_file(TESTFILE_TR)


#Perform the same tests as last (valid translation file), but keep modtime of
#translation newer, so test should fail.
create_testfile(TESTFILE, repyhelper.TRANSLATION_TAGLINE + "\ndef foo():\n  pass\n")

if repyhelper._translation_is_needed(SRCFILE, TESTFILE):
  pass
else:
  print "File modification time test failed! Thought regeneration was needed when it wasn't!"

test_utils.cleanup_file(TESTFILE_TR)

