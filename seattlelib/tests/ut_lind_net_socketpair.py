"""
File : ut_lind_net_socketpair.py

Unit test for socketpair_syscall(), it's used to check if a pair of sockets
are returned successfully with two-way communication. Works for both TCP/UDP.
"""

import lind_test_server
import emultimer

from lind_net_constants import *

SyscallError = lind_test_server.SyscallError

# other end of communicator...
def helper():
  msg = None
  msg = lind_test_server.recv_syscall(sockets[0], 1024, 0)
  assert msg != None, "Sockpair recv failed in helper..."

  lind_test_server.send_syscall(sockets[0], "SocketPair test.", 0)

  return

# one end of communicator...
def tester():
  # need simultaneous communication...
  emultimer.createthread(helper)
  emultimer.sleep(0.1)

  lind_test_server.send_syscall(sockets[1], "SocketPair test.", 0)

  msg = None
  msg = lind_test_server.recv_syscall(sockets[1], 1024, 0)
  assert msg != None, "Sockpair recv failed in tester..."

  emultimer.sleep(0.1)

  lind_test_server.close_syscall(sockets[1])
  lind_test_server.close_syscall(sockets[0])

  return

# Let's get a piar of sockets and check if a two way communication
# is possible. This is TCP sockpair.
sockets = lind_test_server.socketpair_syscall(AF_INET, SOCK_STREAM, 0)[1]

# performs message passing among the sockets...
tester()

# Test for UDP connection...
sockets = lind_test_server.socketpair_syscall(AF_INET, SOCK_DGRAM, 0)[1]

# performs message passing among the sockets...
tester()
