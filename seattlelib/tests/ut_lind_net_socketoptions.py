import wrapped_lind_net_calls as lind_net_calls


from lind_net_constants import *

SyscallError = lind_net_calls.SyscallError


sockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_STREAM, 0)

# should work...
lind_net_calls.bind_syscall(sockfd,'127.0.0.1',50102)


# let's set some options!!!    I'll check for function in different tests...

# reuseport
assert(lind_net_calls.getsockopt_syscall(sockfd, SOL_SOCKET, SO_REUSEPORT)==0)
lind_net_calls.setsockopt_syscall(sockfd, SOL_SOCKET, SO_REUSEPORT, 1)
assert(lind_net_calls.getsockopt_syscall(sockfd, SOL_SOCKET, SO_REUSEPORT)==1)

# linger
assert(lind_net_calls.getsockopt_syscall(sockfd, SOL_SOCKET, SO_LINGER)==0)
lind_net_calls.setsockopt_syscall(sockfd, SOL_SOCKET, SO_LINGER, 1)
assert(lind_net_calls.getsockopt_syscall(sockfd, SOL_SOCKET, SO_LINGER)==1)


# keepalive
assert(lind_net_calls.getsockopt_syscall(sockfd, SOL_SOCKET, SO_KEEPALIVE)==0)
lind_net_calls.setsockopt_syscall(sockfd, SOL_SOCKET, SO_KEEPALIVE, 1)
assert(lind_net_calls.getsockopt_syscall(sockfd, SOL_SOCKET, SO_KEEPALIVE)==1)


# let's set some options!!!
lind_net_calls.setsockopt_syscall(sockfd, SOL_SOCKET, SO_SNDBUF, 1000)
assert(lind_net_calls.getsockopt_syscall(sockfd, SOL_SOCKET, SO_SNDBUF)==1000)

lind_net_calls.setsockopt_syscall(sockfd, SOL_SOCKET, SO_RCVBUF, 2000)
assert(lind_net_calls.getsockopt_syscall(sockfd, SOL_SOCKET, SO_RCVBUF)==2000)

