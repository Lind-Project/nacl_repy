""" 
Author: Justin Cappos

Start Date: Sept 1st, 2008

Description:
The advertisement functionality for the node manager

"""

# needed for getruntime
from repyportability import *
_context = locals()
add_dy_support(_context)

# needed to convert keys to strings
dy_import_module_symbols('rsa.r2py')

# Comment out following line by Danny Y. Huang. Potentially unsafe operation if it contains repy-specific symbols like mycontext.
# include advertise.r2py

import sys
import time
import threading
import traceback
import servicelogger

dy_import_module_symbols('listops.r2py')
dy_import_module_symbols("advertise.r2py")


# The frequency of updating the advertisements
adfrequency = 300

# the TTL of those adverts
adTTL = 750

# This is how many seconds we'll wait between checks to see if there are new 
# keys that need to be advertised.
adsleepfrequency = 5

# Log after 'N' advertise errors 
error_skip_count = 100

myname = None

# This dictionary holds the last time an address was advertised.   This is used
# to allow us to quickly re-advertise when a key changes.
# If the elapsed time between now and when we advertised is greater than the 
# adfrequency, we'll advertise.   
# I'll clean this up periodically using clean_advertise_dict()
# NOTE: This contains keys that are converted to strings because a dictionary
# isn't hashable!
lastadvertisedict = {}


# removes old items from the advertise dictionary.
def clean_advertise_dict():
  now = getruntime()
  # must copy because we're removing items
  for advertisekey in lastadvertisedict.copy():
    if now - lastadvertisedict[advertisekey] > adfrequency:
      # remove outdated item
      del lastadvertisedict[advertisekey]
      


class advertthread(threading.Thread):

  # Note: This will get updates from the main program because the dictionary
  # isn't a copy, but a reference to the same data structure
  addict = None


  def __init__(self, advertisementdictionary, nodekey):
    self.addict = advertisementdictionary
    self.nodekey = nodekey
    self.error_count = 0
    self.is_offline = False
    threading.Thread.__init__(self, name = "Advertisement Thread")


  def run(self):
    # Put everything in a try except block so that if badness happens, we can
    # log it before dying.
    try:
      while True:
        # remove stale items from the advertise dict.   This is important because
        # we're using membership in the dict to indicate a need to advertise
        clean_advertise_dict()

        # this list contains the keys we will advertise
        advertisekeylist = []

        # JAC: advertise under the node's key
        if rsa_publickey_to_string(self.nodekey) not in lastadvertisedict and self.nodekey not in advertisekeylist:
          advertisekeylist.append(self.nodekey)


        # make a copy so there isn't an issue with a race
        for vesselname in self.addict.keys()[:]:

          try:
            thisentry = self.addict[vesselname].copy()
          except KeyError:
            # the entry must have been removed in the meantime.   Skip it!
            continue

          # if I advertise the vessel...
          if thisentry['advertise']:
            # add the owner key if not there already...
            if rsa_publickey_to_string(thisentry['ownerkey']) not in lastadvertisedict and thisentry['ownerkey'] not in advertisekeylist:
              advertisekeylist.append(thisentry['ownerkey'])

            # and all user keys if not there already
            for userkey in thisentry['userkeys']:
              if rsa_publickey_to_string(userkey) not in lastadvertisedict and userkey not in advertisekeylist:
                advertisekeylist.append(userkey)


        # there should be no dups.   
        assert(advertisekeylist == listops_uniq(advertisekeylist))

        # now that I know who to announce to, send messages to annouce my IP and 
        # port to all keys I support
        for advertisekey in advertisekeylist:
          try:
            advertise_announce(advertisekey, str(myname), adTTL)
            # mark when we advertise
            lastadvertisedict[rsa_publickey_to_string(advertisekey)] = getruntime()
         
            # If the announce succeeded, and node was offline, log info message
            # and switch it back to online mode.
            if self.is_offline:
              info_msg = 'Node is back online.'
              if self.error_count:
                info_msg += ' (Encountered ' + str(self.error_count) + \
                              ' advertise errors)'
              servicelogger.log('[INFO]: ' + info_msg)
              self.error_count = 0
              self.is_offline = False
          
          except AdvertiseError, e:
            # If all announce requests failed, assume node has
            # gone offline, 
            if str(e) == "None of the advertise services could be contacted":
              self.is_offline = True
              # Log an error message after every 'N' failures
              if (self.error_count % error_skip_count == 0):
                servicelogger.log('AdvertiseError occured, continuing: '+str(e))
              self.error_count += 1
            # Log all other types of errors
            else:
              servicelogger.log('AdvertiseError occured, continuing: '+str(e))
          except Exception, e:
            servicelogger.log_last_exception()
            # an unexpected exception occured, exit and restart
            return
           

        # wait to avoid sending too frequently
        time.sleep(adsleepfrequency)
    except Exception, e:
      exceptionstring = "[ERROR]:"
      (etype, value, tb) = sys.exc_info()
    
      for line in traceback.format_tb(tb):
        exceptionstring = exceptionstring + line
  
      # log the exception that occurred.
      exceptionstring = exceptionstring + str(etype)+" "+str(value)+"\n"

      servicelogger.log(exceptionstring)
      raise e




