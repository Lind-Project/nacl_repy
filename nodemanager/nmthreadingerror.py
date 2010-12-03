"""
Author: Armon Dadgar
Start Date: March 31st, 2009
Description:
  When a vessel is terminated with the ThreadErr status, this file contains the code necessary to reduce the global
  event limit by 50%, and to restart all vessels that are running.

"""

# Use this for generic processing
import nmrestrictionsprocessor
    
import servicelogger

# This allows us to get the system thread count
import nonportable

# This allows us to access the NM configuration
import persist

EVENT_SCALAR = 0.5 # Scalar number of threads, relative to current
HARD_MIN = 1 # Minimum number of events

# If repy's allocated 
DEFAULT_NOOP_THRESHOLD = .10
NOOP_CONFIG_KEY = "threaderr_noop_thres" # The key used in the NM config file

# Updates the restrictions files, to use 50% of the threads
def update_restrictions():
  # Create an internal handler function, takes a resource line and returns the new number of threads
  def _internal_func(lineContents):
    try:
      threads = float(lineContents[2])
      threads = threads * EVENT_SCALAR
      threads = int(threads)
      threads = max(threads, HARD_MIN) # Set a hard minimum
      return threads
    except:
      # On failure, return the minimum
      return HARD_MIN
      
  
  # Create a task that uses our internal function
  task = ("resource","events",_internal_func,True)
  taskList = [task]
  
  # Process all the resource files
  errors = nmrestrictionsprocessor.process_all_files(taskList)
  
  # Log any errors we encounter
  if errors != []:
    for e in errors:
      print e
      servicelogger.log("[ERROR]:Unable to patch events limit in resource file "+ e[0] + ", exception " + str(e[1]))

# Store the threads
_allocatedThreads = 0
      
# Gets our allocated thread count
def get_allocated_threads():
  global _allocatedThreads
  
  # Create an internal handler function, takes a resource line and stores the allocated threads
  # Makes no changes
  def _internal_func(lineContents):
    global _allocatedThreads
    try:
      threads = int(float(lineContents[2]))
      _allocatedThreads += threads
      return lineContents[2]
    except Exception, e:
      # On failure, return the initial value
      return lineContents[2]
  
  # Reset the thread count
  _allocatedThreads = 0
  
  # Create a task that uses our internal function, which will tally up the allocated threads
  task = ("resource","events",_internal_func,True)
  taskList = [task]
  
  # Process all the resource files
  errors = nmrestrictionsprocessor.process_all_files(taskList)
  
  return _allocatedThreads

def handle_threading_error(nmAPI):
  """
  <Purpose>
    Handles a repy node failing with ThreadErr. Reduces global thread count by 50%.
    Restarts all existing vesselts

  <Arguments>
    nmAPI: the nmAPI module -- passed to the function to avoid import loops;
           see ticket #590 for more information about this.
  """
  # Make a log of this
  servicelogger.log("[ERROR]:A Repy vessel has exited with ThreadErr status. Patching restrictions and reseting all vessels.")
  
  # Get the number of threads Repy has allocated
  allocatedThreads = get_allocated_threads()
  
  # Get the number os system threads currently
  systemThreads = nonportable.os_api.get_system_thread_count()
  
  # Log this information
  servicelogger.log("[ERROR]:System Threads: "+str(systemThreads)+"  Repy Allocated Threads: "+str(allocatedThreads))
  
  # Get the NM configuration
  configuration = persist.restore_object("nodeman.cfg")
  
  # Check if there is a threshold configuration,
  # otherwise add the default configuration
  if NOOP_CONFIG_KEY in configuration:
    threshold = configuration[NOOP_CONFIG_KEY]
  else:
    threshold = DEFAULT_NOOP_THRESHOLD
    configuration[NOOP_CONFIG_KEY] = threshold
    persist.commit_object(configuration, "nodeman.cfg")
  
  # Check if we are below the threshold, if so
  # then just return, this is a noop
  if allocatedThreads < systemThreads * threshold:
    return
  
  # We are continuing, so we are above the threshold!
  # First, update the restrictions
  update_restrictions()
  
  # Then, stop the vessels
  # Get all the vessels
  vessels = nmAPI.vesseldict.keys()
  
  # Create the stop tuple, exit code 57 with an error message
  stoptuple = (57, "Fatal system-wide threading error! Stopping all vessels.")
  
  # Stop each vessel
  for vessel in vessels:
    try:
      # Stop each vessel, using our stoptuple
      nmAPI.stopvessel(vessel,stoptuple)
    except Exception, exp:
      # Forge on, regardless of errors
      servicelogger.log("[ERROR]:Failed to reset vessel (Handling ThreadErr). Exception: "+str(exp))
      servicelogger.log_last_exception()
