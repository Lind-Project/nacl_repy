import lind_test_server


from lind_net_constants import *

SyscallError = lind_test_server.SyscallError


sockfd = lind_test_server.get_fscall_obj(-1).socket_syscall(AF_INET, SOCK_STREAM, 0)

assert(lind_test_server.get_fscall_obj(-1).getsockname_syscall(sockfd) == ('0.0.0.0', 0))


# should work...
lind_test_server.get_fscall_obj(-1).bind_syscall(sockfd,'127.0.0.1',50102)

assert(lind_test_server.get_fscall_obj(-1).getsockname_syscall(sockfd) == ('127.0.0.1', 50102))

try:
  lind_test_server.get_fscall_obj(-1).bind_syscall(sockfd,'127.0.0.1',50103)

except SyscallError:
  # should fail (already bound)
  pass
else:
  print "Should be an error (already bound)"

# should not change...
assert(lind_test_server.get_fscall_obj(-1).getsockname_syscall(sockfd) == ('127.0.0.1', 50102))

