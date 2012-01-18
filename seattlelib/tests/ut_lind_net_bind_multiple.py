import wrapped_lind_net_calls as lind_net_calls


from lind_net_constants import *

SyscallError = lind_net_calls.SyscallError


sockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_STREAM, 0)

# should work...
lind_net_calls.bind_syscall(sockfd,'127.0.0.1',50102)


# let's try to bind another to the same IP /port...
sockfd2 = lind_net_calls.socket_syscall(AF_INET, SOCK_STREAM, 0)

# let's set them to allow port reuse
lind_net_calls.setsockopt_syscall(sockfd, SOL_SOCKET, SO_REUSEPORT, 1)
lind_net_calls.setsockopt_syscall(sockfd2, SOL_SOCKET, SO_REUSEPORT, 1)

# should work...
lind_net_calls.bind_syscall(sockfd2,'127.0.0.1',50102)

# now let's try to listen on both... (should fail on the second)

lind_net_calls.listen_syscall(sockfd,10)

try:
  lind_net_calls.listen_syscall(sockfd2,10)
except SyscallError, e:
  pass
else:
  print 'double listen allowed!!!'

sockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_DGRAM, 0)
# however, UDP should work...
lind_net_calls.bind_syscall(sockfd,'127.0.0.1',50102)
