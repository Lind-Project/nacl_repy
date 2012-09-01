import lind_test_server
from emultimer import sleep
from emultimer import createthread as createthread
from lind_net_constants import *

SyscallError = lind_test_server.SyscallError


def log(*args):
  print ' '.join(args)



# let's do a few basic things with connect.   This will be UDP only for now...

listensockfd = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, 0)
sendsockfd = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, 0)

def recvmessages():
  # let's wait for packets here...
  lind_test_server.bind_syscall(listensockfd,'127.0.0.1',50102)
  assert lind_test_server.recv_syscall(listensockfd,10000,0) == 'test',\
    "UDP recv test 1 failed."
  lind_test_server.recv_syscall(listensockfd,10000,0) == 'test2',\
    "UDP recv test 2 failed."

# I need a thread...
createthread(recvmessages)

# let's wait for it to start...
sleep(.1)

# send a message
lind_test_server.sendto_syscall(sendsockfd,'test','127.0.0.1',50102,0)

# get another socket, bind and then send
sendsockfd2 = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, 0)
lind_test_server.bind_syscall(sendsockfd2,'127.0.0.1',50992)
lind_test_server.sendto_syscall(sendsockfd2,'test2','127.0.0.1',50102,0)

sleep(0.1)
lind_test_server.close_syscall(sendsockfd2)
lind_test_server.close_syscall(sendsockfd)
lind_test_server.close_syscall(listensockfd)
