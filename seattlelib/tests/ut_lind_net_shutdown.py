import wrapped_lind_net_calls as lind_net_calls

from emultimer import createthread as createthread

from emulmisc import exitall

from time import sleep

from lind_net_constants import *

SyscallError = lind_net_calls.SyscallError

# I'll listen, accept, and connect...

serversockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_STREAM, 0)

clientsockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_STREAM, 0)


# bind to a socket
lind_net_calls.bind_syscall(serversockfd,'127.0.0.1',50300)

lind_net_calls.listen_syscall(serversockfd,10)

def do_server():
  
  newsocketfd = lind_net_calls.accept_syscall(serversockfd)
  try:
    lind_net_calls.send_syscall(serversockfd,'jhasdfhjsa',0)
    lind_net_calls.shutdown_syscall(serversockfd,SHUT_RDWR)

    try:
      # should fail!!!
      lind_net_calls.send_syscall(serversockfd,'jhasdfhjsa',0)
    except: 
      pass
    else:
      print "send after shutdown didn't fail!!!"

  finally:
    exitall()


createthread(do_server)


# wait for the server to run...
sleep(.1)

# should be okay...
lind_net_calls.connect_syscall(clientsockfd,'127.0.0.1',50300)
assert(lind_net_calls.getpeername_syscall(clientsockfd) == ('127.0.0.1',50300))



