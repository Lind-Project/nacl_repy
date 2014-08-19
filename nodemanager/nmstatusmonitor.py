""" 
Author: Justin Cappos

Module: Node Manager status monitor.   This thread checks the status of the
    running experiments.   This thread updates the status information about
    the vessels.

Start date: September 1st, 2008

The design goals of this version are to be secure, simple, and reliable (in 
that order).   

I'll do this by instrumenting the vessel to indicate its status.   These 
are likely needed anyways for things like CPU and memory resource restrictions
on platforms that don't support correct thread / signaling interaction.
"""

import sys

import traceback

import threading

import statusstorage

import time

import servicelogger

# This is used to handle a vesseling having a 
# ThreadErr status
import nmthreadingerror

# The amount of time we allow without an update before we declare a vessel 
# dead...
updatebound = 15

timestampdict = {}

# I use this lock to prevent multiple checks of the status timestamp, etc.
statuslock = threading.Lock()


def update_status(statusdict, vesselname, status, timestamp):

  # always acquire the lock and then release when done...
  statuslock.acquire()

  try:

    # If this is older than the previous, we're done...
    if vesselname in timestampdict and timestamp < timestampdict[vesselname]:
      return

    timestampdict[vesselname] = timestamp

    try:
      # set the status
      statusdict[vesselname]['status'] = status
    except KeyError:
      # It must have been deleted in the meantime... (see race notes below)
      return
  finally:
    statuslock.release()
  





class statusthread(threading.Thread):

  # Note: This will get updates from the main program because the dictionary
  # isn't a copy, but a reference to the same data structure
  statusdict = None
  sleeptime = None
  
  # Set tracks timestamps at which vessels encountered a threading error
  # This is uses so that the error is only handled once
  threadErrSet = None

  def __init__(self, statusdictionary, sleeptime, nmAPI):
    self.statusdict = statusdictionary
    self.sleeptime = sleeptime
    self.threadErrSet = set()
    self.nmAPI = nmAPI
    threading.Thread.__init__(self,name = "Status Monitoring Thread")

  def run(self):
    try:
      while True:

        # the race condition here is that they might delete something and I will
        # check it.   This is okay.   I'll end up getting a KeyError when trying
        # to update the dictionary (checked below) or look at the old entry.
        for vesselname in self.statusdict.keys()[:]:

          try:
            statusfilename = self.statusdict[vesselname]['statusfilename']
            oldstatus = self.statusdict[vesselname]['status']
          except KeyError:
            # race condition, this was removed in the meantime.
            continue
  
  
          # there should be a status file (assuming we've inited)
  
          try: 
            status,timestamp = statusstorage.read_status(statusfilename)
          except IOError, e:
            # if the file exists, raise the exception since we don't know what
            # it is about.
            if e[0] != 2:
              raise

            # file not found.   This means it is fresh...
            status = 'Fresh'
            timestamp = time.time()
               
          
          # Armon: Check if status is ThreadErr, this is a critical error condition
          # that requires lowering the global thread count, and reseting all vessels
          if status == "ThreadErr":
            # Check if this is the first time for this timestamp
            # Since the status file is not removed, this is necessary so that we do not
            # continuously trigger the error handling code
            if not timestamp in self.threadErrSet:
              # Add the timestamp
              self.threadErrSet.add(timestamp)
              
              # Call the error handling module
              nmthreadingerror.handle_threading_error(self.nmAPI)
          
          # The status has a timestamp in case the process is killed harshly and 
          # needs to be restarted.   This allows ordering of status reports
          staleness = time.time() - timestamp
  
          if staleness < 0:
            # time is running backwards, likely a NTP update (allow it)...
#            print "Time is running backwards by increment '"+str(staleness)+"', allowing this"
            newstatus = status
         
          elif staleness > updatebound:  
            # stale?
            newstatus = oldstatus

            if oldstatus == 'Started':
  
              # BUG: What happens if we're wrong and it's alive?   What do we do?
              # How do we detect and fix this safely?
              newstatus = 'Stale'
              # We set the timestamp so that our update happens in the table...
              timestamp = time.time() - updatebound
  
          else:
            # it seems to be okay.   Use the given status
            newstatus = status
            
          update_status(self.statusdict, vesselname, newstatus, timestamp)
  
        time.sleep(self.sleeptime)
    
    except Exception,e:
      servicelogger.log_last_exception()
      raise e
