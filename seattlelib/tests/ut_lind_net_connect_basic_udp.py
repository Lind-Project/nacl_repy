import lind_test_server


from lind_net_constants import *

SyscallError = lind_test_server.SyscallError

# let's do a few basic things with connect.   This will be UDP only for now...

sockfd = lind_test_server.get_net_call(-1,"socket_syscall")(AF_INET, SOCK_DGRAM, 0)

# should be okay...
lind_test_server.get_net_call(-1,"connect_syscall")(sockfd,'127.0.0.1',50103)

# bind will not be interesting...
#lind_test_server.bind_syscall(sockfd,'127.0.0.1',50102)


# I should be able to retarget it...
lind_test_server.get_net_call(-1,"connect_syscall")(sockfd,'127.0.0.1',50104)


