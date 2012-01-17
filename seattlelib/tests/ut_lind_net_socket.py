import wrapped_lind_net_calls as lind_net_calls


from lind_net_constants import *

SyscallError = lind_net_calls.SyscallError

sockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_STREAM, 0)
sockfd2 = lind_net_calls.socket_syscall(AF_INET, SOCK_STREAM, IPPROTO_TCP)

sockfd3 = lind_net_calls.socket_syscall(AF_INET, SOCK_DGRAM, 0)
sockfd4 = lind_net_calls.socket_syscall(AF_INET, SOCK_DGRAM, IPPROTO_UDP)


try:
  # let's try to use an incorrect setting
  lind_net_calls.socket_syscall(AF_UNIX, SOCK_DGRAM, 0)

except:
  pass
else:
  print "Should be an error"

