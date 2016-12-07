"""
Author: Armon Dadgar
Start Date: March 31st, 2009
Description:
  When a vessel is terminated with the ThreadErr status, this file contains the code necessary to reduce the global
  event limit by 50%, and to restart all vessels that are running.

"""

import servicelogger

# This allows us to get the system thread count
import nonportable

# This allows us to access the NM configuration
import persist

import nmAPI

# needed to read and write resource files
import resourcemanipulation


EVENT_SCALAR = 0.5 # Scalar number of threads, relative to current
HARD_MIN = 1 # Minimum number of events

# If repy's allocated 
DEFAULT_NOOP_THRESHOLD = .10
NOOP_CONFIG_KEY = "threaderr_noop_thres" # The key used in the NM config file


      
# BUG: I make the assumption that there isn't a race condition with the worker
# thread!!!   This should only really matter if splits / joins are happening.
def handle_threading_error():
  """
  <Purpose>
    Handles a repy node failing with ThreadErr. If repy is allowed to use
    more than 10% of the current threads, reduce the global thread count by 50%
    and stop all existing vessels

  <Arguments>
    None
  
  <Exceptions>
    None

  <Side Effects>
    May re-write all resource files and stop all vessels

  <Returns>
    None
  """
  # Make a log of this
  servicelogger.log("[ERROR]:A Repy vessel has exited with ThreadErr status. Checking to determine next step")

  # Get all the names of the vessels
  vesselnamelist = nmAPI.vesseldict.keys()
  
  # read in all of the resource files so that we can look at and possibly 
  # manipulate them.
  resourcedicts = {}
  for vesselname in vesselnamelist:
    resourcedicts[vesselname] = resourcemanipulation.read_resourcedict_from_file('resource.'+vesselname)
  
  # Get the number of threads Repy has allocated
  allowedthreadcount = 0
  for vesselname in vesselnamelist:
    allowedthreadcount = allowedthreadcount + resourcedicts[vesselname]['events']
  
  # Get the total number os system threads currently used 
  totalusedthreads = nonportable.os_api.get_system_thread_count()
  
  # Log this information
  servicelogger.log("[WARNING]:System Threads: "+str(totalusedthreads)+"  Repy Allocated Threads: "+str(allowedthreadcount))
  
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
  if allowedthreadcount < totalusedthreads * threshold:
    return
  
  servicelogger.log("[ERROR]:Reducing number of system threads!")



  #### We are above the threshold!   Let's cut everything by 1/2

  # First, update the resource files
  for vesselname in vesselnamelist:
    # cut the events by 1/2
    resourcedicts[vesselname]['events'] = resourcedicts[vesselname]['events'] / 2
    # write out the new resource files...
    resourcemanipulation.write_resourcedict_to_file(resourcedicts[vesselname], 'resource.'+vesselname)
  

  
  
  # Create the stop tuple, exit code 57 with an error message
  stoptuple = (57, "Fatal system-wide threading error! Stopping all vessels.")
  
  # Stop each vessel
  for vesselname in vesselnamelist:
    try:
      # Stop each vessel, using our stoptuple
      nmAPI.stopvessel(vesselname,stoptuple)
    except Exception, exp:
      # Forge on, regardless of errors
      servicelogger.log("[ERROR]:Failed to reset vessel (Handling ThreadErr). Exception: "+str(exp))
      servicelogger.log_last_exception()
