import lind_test_server
from emultimer import sleep
from emultimer import createthread
from lind_net_constants import AF_INET, SOCK_STREAM, SHUT_RDWR

SyscallError = lind_test_server.SyscallError

# I'll listen, accept, and connect...

serversockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)
clientsockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)


# bind to a socket
lind_test_server.bind_syscall(serversockfd, '127.0.0.1', 50431)
lind_test_server.listen_syscall(serversockfd, 10)


def do_server():
    newsocketfd = lind_test_server.accept_syscall(serversockfd)
    fd = newsocketfd[2]
    lind_test_server.send_syscall(fd, 'jhasdfhjsa', 0)
    lind_test_server.setshutdown_syscall(fd, SHUT_RDWR)

    try:
        # should fail!!!
        lind_test_server.send_syscall(fd, 'jhasdfhjsa', 0)
    except:
        pass
    else:
        print "send after shutdown didn't fail!!!"



createthread(do_server)


# wait for the server to run...
sleep(.1)

# should be okay...

lind_test_server.connect_syscall(clientsockfd, '127.0.0.1', 50431)
assert(lind_test_server.getpeername_syscall(clientsockfd) == \
       ('127.0.0.1', 50431))
