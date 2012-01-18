import wrapped_lind_net_calls as lind_net_calls


from lind_net_constants import *

SyscallError = lind_net_calls.SyscallError


sockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_STREAM, 0)

assert(lind_net_calls.getsockname_syscall(sockfd) == ('0.0.0.0', 0))


# should work...
lind_net_calls.bind_syscall(sockfd,'127.0.0.1',50102)

assert(lind_net_calls.getsockname_syscall(sockfd) == ('127.0.0.1', 50102))

try:
  lind_net_calls.bind_syscall(sockfd,'127.0.0.1',50103)

except SyscallError:
  # should fail (already bound)
  pass
else:
  print "Should be an error (already bound)"

# should not change...
assert(lind_net_calls.getsockname_syscall(sockfd) == ('127.0.0.1', 50102))

