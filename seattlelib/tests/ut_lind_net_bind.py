import wrapped_lind_net_calls as lind_net_calls


from lind_net_constants import *

SyscallError = lind_net_calls.SyscallError


sockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_STREAM, 0)

# should work...
lind_net_calls.bind_syscall(sockfd,'127.0.0.1',50102)

try:
  lind_net_calls.bind_syscall(sockfd,'127.0.0.1',50103)

except SyscallError:
  # should fail (already bound)
  pass
else:
  print "Should be an error (already bound)"


# let's try to bind another to the same IP /port...
sockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_STREAM, 0)

try:
  # should fail...
  lind_net_calls.bind_syscall(sockfd,'127.0.0.1',50102)

except SyscallError:
  # should fail another socket is already bound here...
  pass
else:
  print "Should be an error (already bound)"


sockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_DGRAM, 0)
# however, UDP should work...
lind_net_calls.bind_syscall(sockfd,'127.0.0.1',50102)
