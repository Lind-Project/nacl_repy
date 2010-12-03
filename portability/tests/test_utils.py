"""
A series of utility helpers for running the repyhelper tests.

"""


import os
import repyhelper

#Given a filename, return the corresponding translation filename
def get_translation_filename(filename):
  return repyhelper._get_module_name(filename) + '.py'

#Given a list of python files, return a list of the corresponding translated filenames
def get_translation_filenames(filenames):
  return map(get_translation_filename, filenames)


#Given a list of repy files, remove the corresponding translations if they exist
def cleanup_translations(files):
  translations = get_translation_filenames(files)
  for translation in translations:
    cleanup_file(translation)
  
  
def cleanup_file(filename):
  """
    Remove filename if it exists
  """
  if os.path.isfile(filename):
    try:
      #print "erasing ", filename #DEBUG
      os.remove(filename)
    except (OSError, IOError):
      raise
