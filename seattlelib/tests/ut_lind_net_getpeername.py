import lind_test_server


from lind_net_constants import *

SyscallError = lind_test_server.SyscallError

# let's do a few basic things with connect.   This will be UDP only for now...

sockfd = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, 0)

# should be okay...
lind_test_server.connect_syscall(sockfd,'127.0.0.1',50103)

assert(lind_test_server.getpeername_syscall(sockfd) == ('127.0.0.1', 50103))


# I should be able to retarget it...
lind_test_server.connect_syscall(sockfd,'127.0.0.1',50104)

# now should change...
assert(lind_test_server.getpeername_syscall(sockfd) == ('127.0.0.1', 50104))
