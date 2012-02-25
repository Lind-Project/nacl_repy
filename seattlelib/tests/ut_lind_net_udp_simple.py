import lind_test_server

from time import sleep

from lind_net_constants import *

from emulmisc import exitall

SyscallError = lind_test_server.SyscallError


from emultimer import createthread as createthread

def log(*args):
  print ' '.join(args)



# let's do a few basic things with connect.   This will be UDP only for now...

listensockfd = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, 0)

sendsockfd = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, 0)


def recvmessages():
  # let's wait for packets here...
  lind_test_server.bind_syscall(listensockfd,'127.0.0.1',50102)

  lind_test_server.recv_syscall(listensockfd,10000,0)

  lind_test_server.recv_syscall(listensockfd,10000,0)
  # we should get two and exit...
  exitall()


# I need a thread...
createthread(recvmessages)

# let's wait for it to start...
sleep(.1)


# send a message
lind_test_server.sendto_syscall(sendsockfd,'hi','127.0.0.1',50102,0)


# get another socket, bind and then send
sendsockfd2 = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, 0)
lind_test_server.bind_syscall(sendsockfd2,'127.0.0.1',50992)
lind_test_server.sendto_syscall(sendsockfd2,'yo','127.0.0.1',50102,0)

# let's wait for it to happen...
sleep(10)

log('fail!!!')
exitall()
