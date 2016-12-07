import lind_test_server


from lind_net_constants import *

SyscallError = lind_test_server.SyscallError


sockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)

# should work...
lind_test_server.bind_syscall(sockfd,'127.0.0.1',50102)

try:
  lind_test_server.bind_syscall(sockfd,'127.0.0.1',50103)

except SyscallError:
  # should fail (already bound)
  pass
else:
  print "Should be an error (already bound)"


# let's try to bind another to the same IP /port...
sockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)

try:
  # should fail...
  lind_test_server.bind_syscall(sockfd,'127.0.0.1',50102)

except SyscallError:
  # should fail another socket is already bound here...
  pass
else:
  print "Should be an error (already bound)"


sockfd = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, 0)
# however, UDP should work...
lind_test_server.bind_syscall(sockfd,'127.0.0.1',50102)
