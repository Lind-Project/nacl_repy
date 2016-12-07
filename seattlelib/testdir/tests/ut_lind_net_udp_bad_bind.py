import lind_test_server

from lind_net_constants import *

SyscallError = lind_test_server.SyscallError

# let's do a few basic things with connect.   This will be UDP only for now...

sockfd = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, 0)

lind_test_server.bind_syscall(sockfd, '127.0.0.1', 50102)
# should be okay...
lind_test_server.connect_syscall(sockfd,'127.0.0.1',50300)

# bind will not be interesting...
try:
  lind_test_server.bind_syscall(sockfd,'127.0.0.1',50102)
except SyscallError:
  pass
else:
  print "=============="
  print "TEST Failed..."
  print "=============="

lind_test_server.close_syscall(sockfd)


