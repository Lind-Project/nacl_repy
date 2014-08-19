""" 
Author: Justin Cappos
  Modified by Brent Couvrette to make use of circular logging.
  Modified by Eric Kimbrel to add NAT traversal


Module: Node Manager main program.   It initializes the other modules and
        doesn't do much else.

Start date: September 3rd, 2008

This is the node manager for Seattle.   It ensures that sandboxes are correctly
assigned to users and users can manipulate those sandboxes safely.   

The design goals of this version are to be secure, simple, and reliable (in 
that order).   

The node manager has several different threads.   

   An advertisement thread (nmadverise) that inserts entries into OpenDHT so 
that users and owners can locate their vessels.
   A status thread (nmstatusmonitor) that checks the status of vessels and 
updates statuses in the table used by the API.
   An accepter (nmconnectionmanager) listens for connections (preventing
simple attacks) and puts them into a list.
   A worker thread (used in the nmconnectionmanager, nmrequesthandler, nmAPI)
handles enacting the appropriate actions given requests from the user.
   The main thread initializes the other threads and monitors them to ensure
they do not terminate prematurely (restarting them as necessary).

"""

# Let's make sure the version of python is supported
import checkpythonversion
checkpythonversion.ensure_python_version_is_supported()

import daemon
import os
import sys

import repyhelper #used to bring in NAT Layer

# I need to make a cachedir for repyhelper...
if not os.path.exists('nodemanager.repyhelpercache'):
  os.mkdir('nodemanager.repyhelpercache')

# prepend this to my python path
sys.path = ['nodemanager.repyhelpercache'] + sys.path
repyhelpercachedir = repyhelper.set_importcachedir('nodemanager.repyhelpercache')



# Armon: Prevent all warnings
import warnings
# Ignores all warnings
warnings.simplefilter("ignore")

from repyportability import *

import time

import threading

import nmadvertise

import nmstatusmonitor
# Needed for use of the status monitor thread:
import nmAPI

import nmconnectionmanager

# need to initialize the name, key and version (for when we return information
# about us).   Also we need the dictionary of vessel state so that the threads
# can update / read it.
import nmrequesthandler

import persist

import misc

import runonce

# for getruntime...
import nonportable

# for harshexit
import harshexit

import traceback

import servicelogger



# import the natlayer for use
# this requires all NATLayer dependincies to be in the current directory
repyhelper.translate_and_import('NATLayer_rpc.repy')
repyhelper.translate_and_import('sha.repy')
repyhelper.translate_and_import('rsa.repy')



# Armon: To handle user preferrences with respect to IP's and Interfaces
# I will re-use the code repy uses in emulcomm
import emulcomm


# One problem we need to tackle is should we wait to restart a failed service
# or should we constantly restart it.   For advertisement and status threads, 
# I've chosen to wait before restarting...   For worker and accepter, I think
# it's essential to keep restarting them as often as we can...
#
# these variables help us to track when we've started and whether or not we
# should restart

# the last time the thread was started
thread_starttime = {}

# the time I should wait
thread_waittime = {}

# never wait more than 5 minutes
maxwaittime = 300.0

# or less than 2 seconds
minwaittime = 2.0

# multiply by 1.5 each time...
wait_exponent = 1.5

# and start to decrease only after a reasonable run time...
reasonableruntime = 30

# and drop by
decreaseamount = .5


# log a liveness message after this many iterations of the main loop
LOG_AFTER_THIS_MANY_ITERATIONS = 600  # every 10 minutes

# BUG: what if the data on disk is corrupt?   How do I recover?   What is the
# "right thing"?   I could run nminit again...   Is this the "right thing"?

version = "0.1e"

# Our settings
configuration = {}

# Lock and condition to determine if the acceptor thread has started
acceptor_state = {'lock':getlock(),'started':False}

# whether or not to use the natlayer, this option is passed in via command line
# -nat
AUTO_USE_NAT = False
FOREGROUND = False


# Initializes emulcomm with all of the network restriction information
# Takes configuration, which the the dictionary stored in nodeman.cfg
def initialize_ip_interface_restrictions(configuration):
  # Armon: Check if networking restrictions are enabled, appropriately generate the list of usable IP's
  # If any of our expected entries are missing, assume that restrictions are not enabled
  if 'networkrestrictions' in configuration and 'nm_restricted' in configuration['networkrestrictions'] \
    and configuration['networkrestrictions']['nm_restricted'] and 'nm_user_preference' in configuration['networkrestrictions']:
    # Setup emulcomm to generate an IP list for us, setup the flags
    emulcomm.user_ip_interface_preferences = True
    
    # Add the specified IPs/Interfaces
    emulcomm.user_specified_ip_interface_list = configuration['networkrestrictions']['nm_user_preference']

# has the thread started?
def should_start_waitable_thread(threadid, threadname):
  # first time!   Let's init!
  if threadid not in thread_starttime:
    thread_waittime[threadid] = minwaittime
    thread_starttime[threadid] = 0.0

  # If it has been started, and the elapsed time is too short, always return
  # False to say it shouldn't be restarted
  if thread_starttime[threadid] and nonportable.getruntime() - thread_starttime[threadid] < thread_waittime[threadid]:
    return False
    
  for thread in threading.enumerate():
    if threadname in str(thread):
      # running now.   If it's run for a reasonable time, let's reduce the 
      # wait time...
      if nonportable.getruntime() - thread_starttime[threadid] > reasonableruntime:
        thread_waittime[threadid] = max(minwaittime, thread_waittime[threadid]-decreaseamount)
      return False
  else:
    return True

# this is called when the thread is started...
def started_waitable_thread(threadid):
  thread_starttime[threadid] = nonportable.getruntime()
  thread_waittime[threadid] = min(maxwaittime, thread_waittime[threadid] ** wait_exponent)

  


# has the thread started?
def is_accepter_started():
  acceptor_state['lock'].acquire()
  result = acceptor_state['started']
  acceptor_state['lock'].release()
  return result


def start_accepter():
  

  if AUTO_USE_NAT == False:
    # check to see if we should use the nat layer
    try:
      # see if we can currently have a bi-directional connection
      use_nat = nat_check_bi_directional(getmyip(), configuration['ports'][0])
    except Exception,e:
      servicelogger.log("Exception occurred trying to contact forwarder to detect nat "+str(e))
      use_nat = False
  else:
    use_nat = True
    
  
  # do this until we get the accepter started...
  while True:

    if is_accepter_started():
      # we're done, return the name!
      return myname

    else:
      # Just use getmyip(), this is the default behavior and will work if we have preferences set
      # We only want to call getmyip() once, rather than in the loop since this potentially avoids
      # rebuilding the allowed IP cache for each possible port
      bind_ip = emulcomm.getmyip()
        
      for possibleport in configuration['ports']:
        try:
          
          if use_nat:
            # use the sha hash of the nodes public key with the vessel
            # number as an id for this node
            unique_id = rsa_publickey_to_string(configuration['publickey'])
            unique_id = sha_hexhash(unique_id)
            unique_id = unique_id+str(configuration['service_vessel'])
            servicelogger.log("[INFO]: Trying NAT wait")
            nat_waitforconn(unique_id, possibleport,
                    nmconnectionmanager.connection_handler)

          # do a local waitforconn (not using a forowarder)
          # this makes the node manager easily accessible locally
          waitforconn(bind_ip, possibleport, 
                    nmconnectionmanager.connection_handler)
        
        except Exception, e:
          servicelogger.log("[ERROR]: when calling waitforconn for the connection_handler: " + str(e))
          servicelogger.log_last_exception()
        else:
          # the waitforconn was completed so the acceptor is started
          acceptor_state['lock'].acquire()
          acceptor_state['started']= True
          acceptor_state['lock'].release()

          # assign the nodemanager name
          # if NAT is being used NAT$ will tell the connection client
          # to use nat_openconn with unique_id to contact this node
          if use_nat: 
            myname = 'NAT$'+unique_id+":"+str(possibleport)
          else: 
            myname = str(bind_ip) + ":" + str(possibleport)
          break

      else:
        servicelogger.log("[ERROR]: cannot find a port for recvmess")

    # check infrequently
    time.sleep(configuration['pollfrequency'])
  






# has the thread started?
def is_worker_thread_started():
  for thread in threading.enumerate():
    if 'WorkerThread' in str(thread):
      return True
  else:
    return False



def start_worker_thread(sleeptime):

  if not is_worker_thread_started():
    # start the WorkerThread and set it to a daemon.   I think the daemon 
    # setting is unnecessary since I'll clobber on restart...
    workerthread = nmconnectionmanager.WorkerThread(sleeptime)
    workerthread.setDaemon(True)
    workerthread.start()


# has the thread started?
def is_advert_thread_started():
  for thread in threading.enumerate():
    if 'Advertisement Thread' in str(thread):
      return True
  else:
    return False


def start_advert_thread(vesseldict, myname, nodekey):

  if should_start_waitable_thread('advert','Advertisement Thread'):
    # start the AdvertThread and set it to a daemon.   I think the daemon 
    # setting is unnecessary since I'll clobber on restart...
    advertthread = nmadvertise.advertthread(vesseldict, nodekey)
    nmadvertise.myname = myname
    advertthread.setDaemon(True)
    advertthread.start()
    started_waitable_thread('advert')
  


def is_status_thread_started():
  for thread in threading.enumerate():
    if 'Status Monitoring Thread' in str(thread):
      return True
  else:
    return False


def start_status_thread(vesseldict,sleeptime):

  if should_start_waitable_thread('status','Status Monitoring Thread'):
    # start the StatusThread and set it to a daemon.   I think the daemon 
    # setting is unnecessary since I'll clobber on restart...
    statusthread = nmstatusmonitor.statusthread(vesseldict, sleeptime, nmAPI)
    statusthread.setDaemon(True)
    statusthread.start()
    started_waitable_thread('status')
  


# lots of little things need to be initialized...   
def main():

  global configuration

  if not FOREGROUND:
    # Background ourselves.
    daemon.daemonize()

  # ensure that only one instance is running at a time...
  gotlock = runonce.getprocesslock("seattlenodemanager")
  if gotlock == True:
    # I got the lock.   All is well...
    pass
  else:
    if gotlock:
      servicelogger.log("[ERROR]:Another node manager process (pid: " + str(gotlock) + 
          ") is running")
    else:
      servicelogger.log("[ERROR]:Another node manager process is running")
    return

  
  # I'll grab the necessary information first...
  servicelogger.log("[INFO]:Loading config")
  # BUG: Do this better?   Is this the right way to engineer this?
  configuration = persist.restore_object("nodeman.cfg")
  
  # Armon: initialize the network restrictions
  initialize_ip_interface_restrictions(configuration)
  
  
  
  # ZACK BOKA: For Linux and Darwin systems, check to make sure that the new
  #            seattle crontab entry has been installed in the crontab.
  #            Do this here because the "nodeman.cfg" needs to have been read
  #            into configuration via the persist module.
  if nonportable.ostype == 'Linux' or nonportable.ostype == 'Darwin':
    if 'crontab_updated_for_2009_installer' not in configuration or \
          configuration['crontab_updated_for_2009_installer'] == False:
      try:
        import update_crontab_entry
        modified_crontab_entry = \
            update_crontab_entry.modify_seattle_crontab_entry()
        # If updating the seattle crontab entry succeeded, then update the
        # 'crontab_updated_for_2009_installer' so the nodemanager no longer
        # tries to update the crontab entry when it starts up.
        if modified_crontab_entry:
          configuration['crontab_updated_for_2009_installer'] = True
          persist.commit_object(configuration,"nodeman.cfg")

      except Exception,e:
        exception_traceback_string = traceback.format_exc()
        servicelogger.log("[ERROR]: The following error occured when " \
                            + "modifying the crontab for the new 2009 " \
                            + "seattle crontab entry: " \
                            + exception_traceback_string)
  


  # get the external IP address...
  # BUG: What if my external IP changes?   (A problem throughout)
  myip = None
  while True:
    try:
      # Try to find our external IP.
      myip = emulcomm.getmyip()
    except Exception, e:
      # If we aren't connected to the internet, emulcomm.getmyip() raises this:
      if len(e.args) >= 1 and e.args[0] == "Cannot detect a connection to the Internet.":
        # So we try again.
        pass
      else:
        # It wasn't emulcomm.getmyip()'s exception. re-raise.
        raise
    else:
      # We succeeded in getting our external IP. Leave the loop.
      break
    time.sleep(0.1)

  vesseldict = nmrequesthandler.initialize(myip, configuration['publickey'], version)

  # Start accepter...
  myname = start_accepter()
  
  #send our advertised name to the log
  servicelogger.log('myname = '+str(myname))

  # Start worker thread...
  start_worker_thread(configuration['pollfrequency'])

  # Start advert thread...
  start_advert_thread(vesseldict, myname, configuration['publickey'])

  # Start status thread...
  start_status_thread(vesseldict,configuration['pollfrequency'])


  # we should be all set up now.   

  servicelogger.log("[INFO]:Started")

  # I will count my iterations through the loop so that I can log a message
  # periodically.   This makes it clear I am alive.
  times_through_the_loop = 0

  # BUG: Need to exit all when we're being upgraded
  while True:

    # E.K Previous there was a check to ensure that the acceptor
    # thread was started.  There is no way to actually check this
    # and this code was never executed, so i removed it completely

        
    if not is_worker_thread_started():
      servicelogger.log("[WARN]:At " + str(time.time()) + " restarting worker...")
      start_worker_thread(configuration['pollfrequency'])

    if should_start_waitable_thread('advert','Advertisement Thread'):
      servicelogger.log("[WARN]:At " + str(time.time()) + " restarting advert...")
      start_advert_thread(vesseldict, myname, configuration['publickey'])

    if should_start_waitable_thread('status','Status Monitoring Thread'):
      servicelogger.log("[WARN]:At " + str(time.time()) + " restarting status...")
      start_status_thread(vesseldict,configuration['pollfrequency'])

    if not runonce.stillhaveprocesslock("seattlenodemanager"):
      servicelogger.log("[ERROR]:The node manager lost the process lock...")
      harshexit.harshexit(55)

    time.sleep(configuration['pollfrequency'])

    # if I've been through the loop enough times, log this...
    times_through_the_loop = times_through_the_loop + 1
    if times_through_the_loop % LOG_AFTER_THIS_MANY_ITERATIONS == 0:
      servicelogger.log("[INFO]: node manager is alive...")
      
    


if __name__ == '__main__':
  
  for arg in sys.argv[1:]:
    # take a command line argument to force use of natlayer
    if arg == '-nat':
      AUTO_USE_NAT = True

    # take a command line argument to force foreground
    if arg == '--foreground':
      FOREGROUND = True

  # Initialize the service logger.   We need to do this before calling main
  # because we want to print exceptions in main to the service log
  servicelogger.init('nodemanager')

  # Armon: Add some logging in case there is an uncaught exception
  try:
    main() 
  except Exception,e:
    # If the servicelogger is not yet initialized, this will not be logged.
    servicelogger.log_last_exception()

    # Since the main thread has died, this is a fatal exception,
    # so we need to forcefully exit
    harshexit.harshexit(15)


