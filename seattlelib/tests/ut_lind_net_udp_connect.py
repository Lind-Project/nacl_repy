"""
File : ut_lind_net_udp.py

Unit test for UDP in connection mode, i.e using connect_syscall() to connect
to peer and sending a msg using send_syscall() instead of sendto_sycall(). 
"""
import lind_test_server
import emultimer

from lind_net_constants import *

SyscallError = lind_test_server.SyscallError

#Both client and server are run from this file, hence opening sockets for both
listensockfd = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, 0)
sendsockfd = lind_test_server.socket_syscall(AF_INET, SOCK_DGRAM, 0)

#Bind the socket to an address, this is important in repy, because the recvfrom
#_syscall() doesn't work properly without binding the address first.
lind_test_server.bind_syscall(listensockfd, '127.0.0.1', 50300)

def process_request():
  msg = None
  # Read the data in the socket.
  try:
    msg = lind_test_server.recvfrom_syscall(listensockfd, 1024, 0)
    assert msg != None, "Socket failed to recv message."
  except Exception, e:
    print "UDP Connect Test : ", e

#Run the listen socket in seperate thread, since send/listen should be started
#simultaneously.
emultimer.createthread(process_request)

emultimer.sleep(0.1)

#This is another way to send message in UDP, instead of sendto_syscall().
lind_test_server.connect_syscall(sendsockfd, '127.0.0.1', 50300)
lind_test_server.send_syscall(sendsockfd, "UDP Connect Test", 0)

#close send & listen sockets...
lind_test_server.close_syscall(listensockfd)
lind_test_server.close_syscall(sendsockfd)
