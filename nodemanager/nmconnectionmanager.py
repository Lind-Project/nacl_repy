""" 
Author: Justin Cappos

Module: Node Manager connection handling.   This does everything up to handling
        a request (i.e. accept connections, handle the order they should be
        processed in, etc.)   Requests will be handled one at a time.

Start date: August 28th, 2008

This is the node manager for Seattle.   It ensures that sandboxes are correctly
assigned to users and users can manipulate those sandboxes safely.   

The design goals of this version are to be secure, simple, and reliable (in 
that order).   

The basic design of the node manager is that the accept portion (implemented
using waitforconn) accepts 
connections and checks basic things about them such as there aren't too many 
connections from a single source.   This callback places valid connections into
an ordered list.   This callback handles meta information like sceduling 
requests and preventing DOS attacks that target admission.

Another thread (the worker thread) processes the first element in the list.  
The worker thread is responsible for handling an individual request.   This
ensures that the request is validly signed, prevents slow connections from 
clogging the request stream, etc.


Right now I ensure that only one worker thread is active at a time.   In the 
future, it would be possible to have multiple threads that are performing 
disjoint operations to proceed in parallel.   This may allow starvation attacks
if it involves reordering the list of connections.   As a result, it is punted 
to future work.

I'm going to use "polling" by the worker thread.   I'll sleep when the 
list is empty and periodically look to see if a new element was added.
"""

# Need to have a separate threads for the worker and the accepter
import threading

# need to get connections, etc.
import socket

# needed for sleep
import time

# does the actual request handling
import nmrequesthandler

import sys

import traceback

import servicelogger

from repyportability import *
_context = locals()
add_dy_support(_context)

dy_import_module_symbols("sockettimeout.r2py")

connectionlock = createlock()
  

def connection_handler(IP, port, socketobject):
 
  # prevent races when adding connection information...   We don't process
  # the connections here, we just categorize them...
  connectionlock.acquire(True)
 
  # always release the lock...
  try:
    # it's not in the list, let's initialize!
    if IP not in connection_dict_order:
      connection_dict_order.append(IP)
      connection_dict[IP] = []

    # we're rejecting lots of connections from the same IP to limit DOS by 
    # grabbing lots of connections
    if len(connection_dict[IP]) > 3:
      # Armon: Avoid leaking sockets
      socketobject.close()
      return

    # don't allow more than 100 connections regardless of source...
    if _get_total_connection_count() > 100:
      socketobject.close()
      return

    # we should add this connection to the list
    connection_dict[IP].append(socketobject)

  finally:
    connectionlock.release()


def _get_total_connection_count():
  totalconnections = 0
  for srcIP in connection_dict:
    totalconnections = totalconnections + len(connection_dict[srcIP])

  return totalconnections




# This thread takes an active ServerSocket, and waits for incoming connections 
class AccepterThread(threading.Thread):
  serversocket = None
  
  def __init__(self, serversocket):
    log("AccepterThread inits")
    threading.Thread.__init__(self, name="AccepterThread")
    self.serversocket = serversocket
    log("AccepterThread inited.")
  
  def run(self):
    # Run indefinitely.
    # This is on the assumption that getconnection() blocks, and so this won't consume an inordinate amount of resources.
    while True:
      try:
        ip, port, client_socket = self.serversocket.getconnection()
        connection_handler(ip, port, client_socket)
      except SocketWouldBlockError:
        sleep(0.5)
      except SocketTimeoutError:
        sleep(0.5)
      except Exception, e:
        servicelogger.log("FATAL error in AccepterThread: " + 
            traceback.format_exc())
        return

  def close_serversocket(self):
    # Close down the serversocket.
    self.serversocket.close()
    # We sleep for half a second to give the OS some time
    # to clean things up.
    sleep(0.5)


##### ORDER IN WHICH CONNECTIONS ARE HANDLED

# Each connection should be handled after all other IP addresses with this
# number of connections.   So if the order of requests is IP1, IP1, IP2 then 
# the ordering should be IP1, IP2, IP1.   
# For example, if there are IP1, IP2, IP3, IP1, IP3, IP3 then IP4 should be
# handled after the first IP3.   If IP2 adds a request, it should go in the 
# third to last position.   IP3 cannot currently queue another request since 
# it has 3 pending.



# This is a list that has the order connections should be handled in.   This
# list contains IP addresses (corresponding to the keys in the connection_dict)
connection_dict_order = []

# this is dictionary that contains a list per IP.   Each key in the dict 
# maps to a list of connections that are pending for that IP.
connection_dict = {}



# get the first request
def pop_request():

  # Acquire a lock to prevent a race (#993)...
  connectionlock.acquire(True)

  # ...but always release it.
  try:
    if len(connection_dict)==0:
      raise ValueError, "Internal Error: Popping a request for an empty connection_dict"

    # get the first item of the connection_dict_order... 
    nextIP = connection_dict_order[0]
    del connection_dict_order[0]

    # ...and the first item of this list
    therequest = connection_dict[nextIP][0]
    del connection_dict[nextIP][0]

    # if this is the last connection from this IP, let's remove the empty list 
    # from the dictionary
    if len(connection_dict[nextIP]) == 0:
      del connection_dict[nextIP]
    else:
      # there are more.   Let's append the IP to the end of the dict_order
      connection_dict_order.append(nextIP)

  finally:
    # if there is a bug in the above code, we still want to prevent deadlock...
    connectionlock.release()

  # and return the request we removed.
  return therequest
  


# this class is the worker thread.   It processes connections
class WorkerThread(threading.Thread):
  sleeptime = None
  def __init__(self,st):
    self.sleeptime = st
    threading.Thread.__init__(self, name="WorkerThread")

  def run(self):
    try: 

      while True:
        
        if len(connection_dict)>0:
          # get the "first" request
          conn = pop_request()
# Removing this logging which seems excessive...          
#          servicelogger.log('start handle_request:'+str(id(conn)))
          nmrequesthandler.handle_request(conn)
#          servicelogger.log('finish handle_request:'+str(id(conn)))
        else:
          # check at most twice a second (if nothing is new)
          time.sleep(self.sleeptime)

    except:
      servicelogger.log_last_exception()
      raise
   
  
