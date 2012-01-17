import wrapped_lind_net_calls as lind_net_calls

from time import sleep

from lind_net_constants import *

from emulmisc import exitall

SyscallError = lind_net_calls.SyscallError


from emultimer import createthread as createthread

def log(*args):
  print ' '.join(args)



# let's do a few basic things with connect.   This will be UDP only for now...

listensockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_DGRAM, 0)

sendsockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_DGRAM, 0)


def recvmessages():
  # let's wait for packets here...
  lind_net_calls.bind_syscall(listensockfd,'127.0.0.1',50102)

  lind_net_calls.recv_syscall(listensockfd,10000,0)

  lind_net_calls.recv_syscall(listensockfd,10000,0)
  # we should get two and exit...
  exitall()


# I need a thread...
createthread(recvmessages)

# let's wait for it to start...
sleep(.1)


# send a message
lind_net_calls.sendto_syscall(sendsockfd,'hi','127.0.0.1',50102,0)


# get another socket, bind and then send
sendsockfd2 = lind_net_calls.socket_syscall(AF_INET, SOCK_DGRAM, 0)
lind_net_calls.bind_syscall(sendsockfd2,'127.0.0.1',50992)
lind_net_calls.sendto_syscall(sendsockfd2,'yo','127.0.0.1',50102,0)

# let's wait for it to happen...
sleep(10)

log('fail!!!')
exitall()
