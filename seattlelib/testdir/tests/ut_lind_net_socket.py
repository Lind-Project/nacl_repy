import lind_test_server



from lind_net_constants import *

SyscallError = lind_test_server.SyscallError

sockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)
sockfd2 = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, IPPROTO_TCP)

sockfd3 = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, 0)
sockfd4 = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, IPPROTO_UDP)


try:
  # let's try to use an incorrect setting
  lind_test_server.socket_syscall(AF_UNIX, SOCK_DGRAM, 0)

except:
  pass
else:
  print "Should be an error"

sockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)

lind_test_server.close_syscall(sockfd)
