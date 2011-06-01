# Copyright (c) 2011 The Native Client Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import subprocess
import struct
import sys
import thread
import threading
import repy_constants
import safebinary
import naclimc

#socks_cond = threading.Condition()
recv_socket = None
send_socket = None

def getrecv():
  assert(recv_socket != None)
  return recv_socket

def getsend():
  assert(send_socket != None)
  return send_socket


def PackStringList(strings):
  return "".join(arg + "\0" for arg in strings)


def PackArgsMessage(argv, envv):
  return (struct.pack("4sII", "ARGS", len(argv), len(envv))
          + PackStringList(argv)
          + PackStringList(envv))


def SpawnSelLdrWithSockets(args, fd_slots, **kwargs):
  sockets = [(fd_slot, naclimc.os_socketpair())
             for fd_slot in fd_slots]
  extra_args = []
  for fd_slot, (child_fd, parent_fd) in sockets:
    extra_args.extend(["-i", "%i:%i" % (fd_slot, child_fd)])

  def PreExec():
    for fd_slot, (child_fd, parent_fd) in sockets:
      os.close(parent_fd)

  cmd = [repy_constants.NACL_ENV["NACL_SEL_LDR"]] + extra_args + args
  proc = subprocess.Popen(cmd, preexec_fn=PreExec, **kwargs)
  for fd_slot, (child_fd, parent_fd) in sockets:
    os.close(child_fd)
  result_sockets = [naclimc.from_os_socket(parent_fd)
                    for fd_slot, (child_fd, parent_fd) in sockets]
  return proc, result_sockets


def launch_nacl(nacl_env, program, args):
  
  lib_dir = nacl_env["NACL_LIBRARY_DIR"]

  sel_ldr_args = [
      "-s","-a","-l","lind.log",
      "--", nacl_env["NACL_DYN_LOADER"] ]

  # print "[Lind] Starting sel_ldr with lib_dir=", lib_dir, " and args ", sel_ldr_args

  proc, [fd1, recv, send] = SpawnSelLdrWithSockets(
      sel_ldr_args,
      [repy_constants.NACL_PLUGIN_BOUND_SOCK,
       repy_constants.NACL_PLUGIN_ASYNC_FROM_CHILD_FD,
       repy_constants.NACL_PLUGIN_ASYNC_TO_CHILD_FD])
  print type(recv)
  #your_program = emulcomm.NaClRuntime(proc, fd1, 1, 2)
  your_program = safebinary.NaClRuntime(proc, fd1, recv, send)

  argv = ["unused-argv0", "--library-path", lib_dir] + [program] + args
  envv = ["NACL_FILE_RPC=1"]

  # print "[Lind]",argv, envv

  send.imc_sendmsg(PackArgsMessage(argv, envv), tuple([]))

  return your_program

if __name__ == "__main__":
  print launch_nacl(sys.argv[1],sys.argv[2:])
