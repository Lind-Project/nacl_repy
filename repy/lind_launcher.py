# Copyright (c) 2011 The Native Client Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Modified by Chris Matthews. 2011

""" This module loads a Native Client instance and establishes connections
on the file descriptors to send data in and out.

Chris Matthews 2011 <cmatthew@cs.uvic.ca>

"""

import os
import subprocess
import struct
import sys
import traceback
import threading
import time
import repy_constants
import safebinary
import naclimc
from thread import start_new_thread


def is_fast_lind():
    return 


if is_fast_lind():
    import nacl

RECV_SOCKET = None
SEND_SOCKET = None


def getrecv():
    """ Get the inbound channel for this NaCl instance."""
    assert(RECV_SOCKET != None)
    return RECV_SOCKET


def getsend():
    """ Get the outbound channel for this NaCl instance."""
    assert(SEND_SOCKET != None)
    return SEND_SOCKET


def _pack_string_list(strings):
    """ Convert the command line args into a null separated
    string version to send into NaCl"""
    return "".join(arg + "\0" for arg in strings)


def _pack_args_message(argv, envv):
    """ build the struct with commadn line arguments to send into NaCl."""
    return (struct.pack("4sII", "ARGS", len(argv), len(envv))
            + _pack_string_list(argv)
            + _pack_string_list(envv))


def _spawn_sel_ldr(args, fd_slots, **kwargs):
    """ do the actual NaCl launch.

    First, setup the in and out file descriptors,
    add them to the command line arguements passed to sel_ldr
    then fork and launch sel_ldr.

    """
    sockets = [(fd_slot, naclimc.os_socketpair())
               for fd_slot in fd_slots]
    extra_args = []
    for fd_slot, (child_fd, parent_fd) in sockets:
        extra_args.extend(["-i", "%i:%i" % (fd_slot, child_fd)])

    def _pre_exec():
        """ before we run, close off the other ends of the FDs so we can't
        use them."""
        for _, (_, parent_fd) in sockets:
            os.close(parent_fd)

    cmd = [repy_constants.NACL_ENV["NACL_SEL_LDR"]] + extra_args + args
 
    proc = subprocess.Popen(cmd, preexec_fn=_pre_exec, **kwargs)
    start_new_thread(nacl_watchdog, (proc,))
    for fd_slot, (child_fd, parent_fd) in sockets:
        os.close(child_fd)
    result_sockets = [naclimc.from_os_socket(parent_fd)
                      for fd_slot, (child_fd, parent_fd) in sockets]
    return proc, result_sockets


def _spawn_internal_sel_ldr(args, fd_slots, **kwargs):
    # prepare the UD socket
    sockets = [(fd_slot, naclimc.os_socketpair())
               for fd_slot in fd_slots]
    extra_args = []
    for fd_slot, (child_fd, parent_fd) in sockets:
        extra_args.extend(["-i", "%i:%i" % (fd_slot, child_fd)])

    cmd = [repy_constants.NACL_ENV["NACL_SEL_LDR"]] + extra_args + args

    nacl.call_native_launch(cmd)
    
    result_sockets = [naclimc.from_os_socket(parent_fd)
                      for fd_slot, (child_fd, parent_fd) in sockets]


    return None, result_sockets


def nacl_watchdog(proc):
    """Watch a nacl process. Has it died? """
    rc = proc.wait()
    if rc != 0:
        print "NaCl process return with:", rc


def launch_nacl(nacl_env, program, args):
    """wrapper to setup a NaCl enviroement given the locations of all the files
    and the arugmetns"""

    lib_dir = nacl_env["NACL_LIBRARY_DIR"] + ":/home/lind/tmp/lind/sdk/linux_x86/nacl64/lib/"
    sel_ldr_args = [
        "-s", "-a", "-l", "lind.log",
        "--", nacl_env["NACL_DYN_LOADER"]]

    fast_mode = is_fast_lind()
    args = [item for item in args if '--fast' not in item]

    if fast_mode:
        proc, [fd1, recv, send] = _spawn_internal_sel_ldr(sel_ldr_args,
                                                          [repy_constants.NACL_PLUGIN_BOUND_SOCK,
                                                           repy_constants.NACL_PLUGIN_ASYNC_FROM_CHILD_FD,
                                                           repy_constants.NACL_PLUGIN_ASYNC_TO_CHILD_FD])
    else:
        proc, [fd1, recv, send] = _spawn_sel_ldr(sel_ldr_args,
                                                 [repy_constants.NACL_PLUGIN_BOUND_SOCK,
                                                  repy_constants.NACL_PLUGIN_ASYNC_FROM_CHILD_FD,
                                                  repy_constants.NACL_PLUGIN_ASYNC_TO_CHILD_FD])

    your_program = safebinary.NaClRuntime(proc, fd1, recv, send)
    argv = ["unused-argv0", "--library-path", lib_dir] + [program] + args
    envv = ["NACL_FILE_RPC=1"]
    rc = send.imc_sendmsg(_pack_args_message(argv, envv), tuple([]))
    return your_program

if __name__ == "__main__":
    launch_nacl(sys.argv[1], sys.argv[2:], [])
