import lind_test_server


from lind_net_constants import *

SyscallError = lind_test_server.SyscallError


sockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)

# should work...
lind_test_server.bind_syscall(sockfd,'127.0.0.1',50102)



# let's set some options!!!    I'll check for function in different tests...
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_REUSEPORT)==0)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_LINGER)==0)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_KEEPALIVE)==0)


# reuseport
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_REUSEPORT)==0)
lind_test_server.setsockopt_syscall(sockfd, SOL_SOCKET, SO_REUSEPORT, 1)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_REUSEPORT)==1)

assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_LINGER)==0)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_KEEPALIVE)==0)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_REUSEPORT)==1)


# linger
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_LINGER)==0)
lind_test_server.setsockopt_syscall(sockfd, SOL_SOCKET, SO_LINGER, 1)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_LINGER)==1)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_REUSEPORT)==1)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_LINGER)==1)


# keepalive
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_KEEPALIVE)==0)
lind_test_server.setsockopt_syscall(sockfd, SOL_SOCKET, SO_KEEPALIVE, 1)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_KEEPALIVE)==1)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_REUSEPORT)==1)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_LINGER)==1)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_KEEPALIVE)==1)


# let's set some options!!!
lind_test_server.setsockopt_syscall(sockfd, SOL_SOCKET, SO_SNDBUF, 1000)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_SNDBUF)==1000)

lind_test_server.setsockopt_syscall(sockfd, SOL_SOCKET, SO_RCVBUF, 2000)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_RCVBUF)==2000)


assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_REUSEPORT)==1)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_LINGER)==1)
assert(lind_test_server.getsockopt_syscall(sockfd, SOL_SOCKET, SO_KEEPALIVE)==1)
