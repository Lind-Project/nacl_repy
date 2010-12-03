#!/usr/bin/python
"""
<Program>
  Seattle Test Framework


<Author>
  Vjekoslav Brajkovic


<Started>
  2009-07-11
  

<Requirements>

  <Naming Convention>

    Required naming convention for every test file:

    ut_MODULE{_DESCRIPTOR].py

    There can be multiple descriptors associated with a module.

    <Example>
      ut_semaphore_simple_create.py
      ut_semaphore_simple_destroy.py
    
  <Pragma Directives>

    The token-string is a series of characters that gives a specific framework 
    instruction and arguments, if any. The number sign (#) must be the first 
    non-white-space character on the line containing the pragma; white-space 
    characters can separate the number sign and the word pragma. Following 
    #pragma, write any text that the translator can parse as preprocessing 
    tokens.
    
    <Example>
      #pragma repy [RESTRITIONS]
      #pragma out [TEXT]
      #pragma error [TEXT]

    The parser throws on unrecognized pragmas. 
"""


import glob
import optparse
import os
import signal
import subprocess
import sys
import time

import utfutil


# Valid prefix and suffix.
SYNTAX_PREFIX = 'ut_'
SYNTAX_SUFFIX = '.py'




# Acceptable pragma directives.
REPY_PRAGMA = 'repy'
ERROR_PRAGMA = 'error'
OUT_PRAGMA = 'out'




# UTF Exceptions.
class InvalidTestFileError(Exception): 
  pass
class InvalidPragmaError(Exception): 
  pass




def main():
  """
  <Purpose>
    Executes the main program that is the unit testing framework.
    Tests different modules, files, capabilities, dependent on command
    line arguments.
    
  <Arguments>
    None

  <Exceptions>
    None.
    
  <Side Effects>
    None

  <Returns>
    None
  """
  ###
  ### Define allowed arguments.
  ###
  parser = optparse.OptionParser()

  ### Generic Option Category.
  group_generic = optparse.OptionGroup(parser, "Generic")
  
  # Verbose flag.
  group_generic.add_option("-v", "--verbose",
                    action="store_true", dest="verbose", default=False,
                    help="verbose output")

  parser.add_option_group(group_generic)

  ### Testing Option Category.
  group_test = optparse.OptionGroup(parser, "Testing")
  
  # Test for a specific module.
  group_test.add_option("-m", "--module", dest="module",
                        help="run tests for a specific module", 
                        metavar="MODULE")

  # Run a specific test file.
  group_test.add_option("-f", "--file", dest="file",
                        help="execute a specific test file", 
                        metavar="FILE")

  parser.add_option_group(group_test)
  
  # All files in the current working directory.
  all_files = glob.glob("*")

  # Valid test files in the current working directory.
  valid_files = filter_files(all_files)

  ###
  # Parse the arguments.
  ###
  (options, args) = parser.parse_args()

  # Test for mutual exclusion.
  if (options.module and options.file):
    parser.error("Options are mutually exclusive!")
    

  if (options.file): # Single file.

    file_path = options.file
    test_single(file_path)

  elif (options.module): # Entire module.
    
    # Retrieve the module name.
    module_name = options.module
    
    module_file_list = filter_files(valid_files, module = module_name)
    test_module(module_name, module_file_list)
    
  else: # If no options are present, run all tests.
    
    test_all(valid_files)




def test_single(file_path):
  """
  <Purpose>
    Given the test file path, this function will execute the test using the test framework.
    
  <Arguments>
    Test file path.

  <Exceptions>
    None.
    
  <Side Effects>
    None

  <Returns>
    None
  """
  file_path = os.path.normpath(file_path)
  testing_monitor(file_path)




def test_module(module_name, module_file_list):
  """
  <Purpose>
    Execute all test files contained within module_file_list matching the
    module_name in the form of each test file name 'ut_<module_name>_<descriptor>.py'

  <Arguments>
    module_name: module name to be tested
    module_file_list: a list of files to be filtered by module name and ran through
      the testing framework

  <Exceptions>
    None

  <Side Effects>
    None
  
  <Returns>
    None
  """
  print 'Testing module:', module_name
  
  setup_file = None
  
  # Given all test files for the specified module name, find the file whose
  # descriptor equals 'setup' (there can be only one such file name).
  filtered_files = filter_files(module_file_list, descriptor = 'setup')
  
  if filtered_files:
    setup_file = filtered_files.pop()
    module_file_list.remove(setup_file)

  subprocess_file = None
  
  filtered_files = filter_files(module_file_list, descriptor = 'subprocess')
  if filtered_files:
    subprocess_file = filtered_files.pop()
    module_file_list.remove(subprocess_file)
  
  shutdown_file = None
  
  # Given all test files for the specified module name, find the file whose
  # descriptor equals 'shutdown' (there can be only one such file name).
  
  filtered_files = filter_files(module_file_list, descriptor = 'shutdown')
  if filtered_files:
    shutdown_file = filtered_files.pop()
    module_file_list.remove(shutdown_file)

  
  sub = None
  # If we must open a process to run concurrently with the tests 
  if subprocess_file:
    print "Now starting subprocess: " + subprocess_file
    sub = subprocess.Popen(['python', subprocess_file])
    # Give the process time to start
    time.sleep(30)

  if setup_file:
    print "Now running setup script: " + setup_file
    test_single(setup_file)    

  module_file_list.sort()
  for test_file in module_file_list: 
    test_single(test_file)

  if shutdown_file:
    print "Now running shutdown script: " + shutdown_file
    test_single(shutdown_file)

  #If we opened a subprocess, we need to be sure to kill it
  if sub:
    print "Now killing subprocess: " + subprocess_file    
    if sys.version_info < (2, 6):
      os.kill(sub.pid, signal.SIGTERM)
    else: 
      sub.kill()

def test_all(file_list):
  """
  <Purpose>
    Given the list of valid test files, this function will test each module
    within the test file list
    
  <Arguments> 
    file_list: List of test files to be ran

  <Exceptions>
    None
    
  <Side Effects>
    None

  <Returns>
    None
  """
  module_dictionary = { }

  # Map test files to their respective modules.
  # dictionary[module name] -> list(test files)
  for test_file in file_list: 
    (module, descriptor) = parse_file_name(test_file)
    
    if module_dictionary.has_key(module):
      module_dictionary[module].append(test_file)
    else:
      module_dictionary[module] = [test_file]
  
  # Test each module.
  for module_name, module_file_list in module_dictionary.iteritems():
    test_module(module_name, module_file_list)




def testing_monitor(file_path):
  """
  <Purpose>
    Executes and prints the results of the unit test contained within 'file_path'
    
 
  <Arguments>
    file_path: File to be used within the testing_monitor

  <Exceptions>
    InvalidPragmaError: if there is an invalid pragma within the source file

  <Side Effects>
    None

  <Returns>
    None
  """

  # Source the file.
  file_object = open(file_path)
  source = file_object.read()

  (tail, head) = os.path.split(file_path)

  (module, descriptor) = parse_file_name(head)
  print "\tRunning: %-50s" % head,

  # Parse all pragma directives for that file.
  try: 
    pragmas = parse_pragma(source)
  except InvalidPragmaError:
    print '[ ERROR ]'
    print_dashes()
    print 'Invalid pragma directive.'
    print_dashes()
    
    return

  # Now, execute the test file.
  report = execution_monitor(file_path, pragmas)

  if report:
    print '[ FAIL ]'
    print_dashes()
    
    for key, value in report.items():
      print 'Standard', key, ': (Produced, Expected):'
      print value
      print_dashes()
    
  else:
    print '[ PASS ]'




def execution_monitor(file_path, pragma_dictionary):
  """
  <Purpose>
    Executes a unit test written with a source contained in file_path. If the source
    contains any pragmas (#pragma out, #pragma repy, #pragma err), the unit testing
    framework creates the report differently. If there is a repy pragma, the test
    executes in repy, not python. If there is an out or err pragma, the unit testing
    framework will include that there was to be output in the report.
 
  <Arguments>
    file_path: file to be executed under the framework
    pragma_dictionary: dictionary of pragmas within this test file

  <Exceptions>
    None

  <Side Effects>
    None

  <Returns>
    A report containing information about any unexpected output:
    { Pragma Type : (Produced, Expected), ... }
  """

  # Status report.
  report = { }

  executable = 'python'
  popen_args = [ executable ]

  if pragma_dictionary.has_key(REPY_PRAGMA):
    repy = 'repy.py'
    default_restriction = 'restrictions.default'
    
    # Did the user specify a non-default restrictions file?
    repyArgs = pragma_dictionary[REPY_PRAGMA]
    if not repyArgs: 
      repyArgs = default_restriction
   
    popen_args.append(repy)

    # For tests requiring repy arguments besides restrictions.default
    # the user must specify them after the pragma
    arguments = repyArgs.split(" ")
    for element in arguments:
      popen_args.append(element)
  
  popen_args.append(file_path)

  # Execute the program.
  (out, error) = utfutil.execute(popen_args)
  
  # Is this executable suppose to produce any output on standard out?
  if pragma_dictionary.has_key(OUT_PRAGMA):
    expected_out = pragma_dictionary[OUT_PRAGMA]
    
    if not expected_out and not out: # pragma out
      report[OUT_PRAGMA] = (None, expected_out)
    elif not expected_out in out: # pragma out [ARGUMENT]
      report[OUT_PRAGMA] = (out, expected_out)
    
  elif out: # If not, make sure the standard out is empty.
    report[ERROR_PRAGMA] = (out, None)


  # Is this executable suppose to produce any output on standard error?
  if pragma_dictionary.has_key(ERROR_PRAGMA):
    expected_error = pragma_dictionary[ERROR_PRAGMA]
    
    if not expected_error and not  error: # pragma error
      report[ERROR_PRAGMA] = (None, expected_error)
    elif not expected_error in error: # pragma error [ARGUMENT]
      report[ERROR_PRAGMA] = (error, expected_error)
      
  elif error: # If not, make sure the standard error is empty.
    report[ERROR_PRAGMA] = (error, None)


  return report

 

def parse_pragma(source_text):
  """
  <Purpose>
    Parses pragma directives which are contained within a source code file.
    Possible pragmas inside of a source code include:
      #pragma out arg
      #pragma err arg
      #pragma repy arg
 
  <Arguments>
    source_text: the content of a particular file

  <Exceptions>
    InvalidPragmaError: When a pragma of an unrecognizable format is used
      (i.e. none of the above)

  <Side Effects>
    None

  <Returns>
    Parsed pragma directives:
    { Pragma Type : Argument, ... }
  """
  directive  = 'pragma'
  pragma_directives = utfutil.parse_directive(source_text, directive)
  pragma_dictionary = { }

  for (directive, pragma_type, arg) in pragma_directives:
    if pragma_type in (OUT_PRAGMA, ERROR_PRAGMA, REPY_PRAGMA):
      pragma_dictionary[pragma_type] = arg
    else: 
      raise InvalidPragmaError(pragma_type)

  return pragma_dictionary




def parse_file_name(file_name):
  """
  <Purpose>
    Parses a file name to identify its module and its descriptor
 
  <Arguments> 
    file_name: the name of the test file

  <Exceptions>
    InvalidTestFileError: if you provide a test file which does not follow the
      naming convention of 'ut_<module>_<descriptor>.py'
      
  <Side Effects>
    None

  <Returns>
    A tuple containing (module, descriptor) in the file's naming convention of 
      'ut_<module>_<descriptor>.py'
    
  """
  if not file_name.startswith(SYNTAX_PREFIX):
    raise InvalidTestFileError(file_name)
  if not file_name.endswith(SYNTAX_SUFFIX):
    raise InvalidTestFileError(file_name)
  
  # Remove prefix and suffix.
  stripped = file_name[len(SYNTAX_PREFIX):-len(SYNTAX_SUFFIX)]
  # Partition the string.
  (module, separator, descriptor) = stripped.partition('_')

  # Empty module name is not allowed.
  if not module:
    raise InvalidTestFileError(file_name)

  return (module, descriptor)




def filter_files(file_list, module = None, descriptor = None):
  """
  <Purpose>
    Given the list of files 'file_list', filter out all invalid test files, that is,
    test files which do not have a module name of 'module' or a descriptor of 'descriptor'
    in the form of 'ut_<module>_<descriptor>.py. 
 
  <Arguments> 
    Module name.
    Descriptor.

  <Exceptions>
    InvalidTestFileError--Raised if you provide a test file of incorrect format
      (all files must follow name convention of ut_<module>_<descriptor>.py).

  <Side Effects>
    None

  <Returns>
    A list of all filtered file names:
    [Filtered File Name list]
  """
  result = []
  
  for file_name in file_list:
    
    try:
      (file_module, file_descrriptor) = parse_file_name(file_name)
    except InvalidTestFileError: # This is not a valid test file.
      continue
    
    # Filter based on the module name.
    if module and file_module != module:
      continue
    # Filter based on the descriptor.
    if descriptor and file_descrriptor != descriptor:
      continue
    
    result.append(file_name) 
  
  return result




def print_dashes(): 
  print '-' * 80




if __name__ == "__main__":
  try:
    main()
  except IOError:
    raise
  except InvalidTestFileError, e:
    print 'Invalid file name syntax:', e
  except:
    print 'Internal error. Trace:'
    print_dashes()
    raise

