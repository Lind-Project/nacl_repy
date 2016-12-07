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

# needed to have a separate thread for the worker
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


# the global list of connections waiting to be serviced
# each item is a tuple of (socketobj, IP)
connection_list = []

  
def connection_handler(IP, port, socketobject, thiscommhandle, maincommhandle):
  # we're rejecting lots of connections from the same IP to limit DOS by 
  # grabbing lots of connections
  try:
    if len(connection_dict[IP]) > 3:
      # Armon: Avoid leaking sockets
      socketobject.close()
      return
  except KeyError:
    # It's okay, they aren't added yet...
    pass

  connection_list.append((socketobject,IP))
  
  
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


# I look at the connection_list and add the new items to the connection_dict
# and connection_dict_order
def add_requests():
  while len(connection_list) > 0:
    # items are added to the back (and removed from the front)
    thisconn, thisIP = connection_list[0]

    # it's not in the list, let's initialize!
    if thisIP not in connection_dict_order:
      connection_dict_order.append(thisIP)
      connection_dict[thisIP] = []

    # we should add this connection to the list
    connection_dict[thisIP].append(thisconn)
    
    # I've finished processing and can safely remove the item.  If I removed it 
    # earlier, they might be able to get more than 3 connections because they
    # might not have seen it in the connection_list or the connection_dict)
    del connection_list[0]
  

# get the first request
def pop_request():
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

  # and return the request we removed.
  return therequest
  


# this class is the worker thread.   It pulls connections off of the 
# connection_list and categorizes them.   
class WorkerThread(threading.Thread):
  sleeptime = None
  def __init__(self,st):
    self.sleeptime = st
    threading.Thread.__init__(self, name="WorkerThread")

  def run(self):
    try: 

      while True:
        # if there are any requests, add them to the dict.
        add_requests()
        
        if len(connection_dict)>0:
          # get the "first" request
          conn = pop_request()
          nmrequesthandler.handle_request(conn)
        else:
          # check at most twice a second (if nothing is new)
          time.sleep(self.sleeptime)

    except:
      servicelogger.log_last_exception()
      raise
   
  
