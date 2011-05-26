""" 
<Author>
  Chris Matthews (cmatthew@cs.uvic.ca)
<Start Date>
  Dececmber 2010

<Description>
  Based off Repy.py, build a backend for a C program to bind to.

"""


# Let's make sure the version of python is supported
import checkpythonversion
checkpythonversion.ensure_python_version_is_supported()

import idhelper
import safe
import sys
import getopt
import emulcomm
import namespace
import nanny
import time
import threading
import loggingrepy
import nmstatusinterface
import harshexit
import statusstorage
import repy_constants   
import os
# Armon: Using VirtualNamespace as an abstraction around direct execution
import virtual_namespace
## we'll use tracebackrepy to print our exceptions
import tracebackrepy
import traceback
import nonportable
from exception_hierarchy import *
# BAD: REMOVE these imports after we remove the API calls
import emulfile
import emulmisc
import emultimer
import repy
import naclimc
import subprocess
import struct


def NaclRPCServer(recv_socket, send_socket):
  pass
  while True:
    try:
      message, fds = recv_socket.imc_recvmsg(1024)
    # TODO(mseaborn): When the Python bindings raise a specific
    # exception type, we should test for that for EOF instead.
    except Exception:
      break
 
    method_id = message[:4]
    message_body = message[4:]
 
    print >> sys.stderr, "Message: ", method_id, message_body
    if method_id == "Open":
      # TODO(mseaborn): When we handle more types of request, we can
      # factor out the unmarshalling code.
      format = "ii"
      flags, mode = struct.unpack_from(format, message_body)
      filename = message_body[struct.calcsize(format):]
      try:
        fd = os.open(filename, flags)
      except OSError:
        send_socket.imc_sendmsg("Fail", tuple([]))
      else:
        desc = naclimc.from_os_file_descriptor(fd)
        send_socket.imc_sendmsg("Okay", tuple([desc]))
