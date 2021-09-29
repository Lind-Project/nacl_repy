import lind_test_server

from emultimer import createthread as createthread

from emulmisc import exitall

from time import sleep

from lind_net_constants import *

SyscallError = lind_test_server.SyscallError

# I'll listen, accept, and connect...

serversockfd = lind_test_server.get_fscall_obj(-1).socket_syscall(AF_INET, SOCK_STREAM, 0)

clientsockfd = lind_test_server.get_fscall_obj(-1).socket_syscall(AF_INET, SOCK_STREAM, 0)


# bind to a socket
lind_test_server.get_fscall_obj(-1).bind_syscall(serversockfd,'127.0.0.1',50300)

lind_test_server.get_fscall_obj(-1).listen_syscall(serversockfd,10)

def do_server():
  
  newsocketfd = lind_test_server.get_fscall_obj(-1).accept_syscall(serversockfd)


createthread(do_server)


# wait for the server to run...
sleep(.1)

# should be okay...
lind_test_server.get_fscall_obj(-1).connect_syscall(clientsockfd,'127.0.0.1',50300)
assert(lind_test_server.get_fscall_obj(-1).getpeername_syscall(clientsockfd) == ('127.0.0.1',50300))



