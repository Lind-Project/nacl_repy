"""
File : ut_lind_net_recvfrom.py

Unit test for recvfrom_syscall(), this applies for recv_sycall() as well,
since recv_syscall() calls recvfrom_syscall(). This test is for TCP only.
Tests include both reads & peeks from socket in recvfrom_syscall().
Test 1# write 100 bytes --> peek 100 bytes, read 100 bytes.
Test 2# write 100 bytes --> read 20 bytes, peek 20, read 80.
Test 3# wrtie 100 bytes --> repeated peeks of {10, 20, 30 , 40}bytes, read 100
Test 4# write  50 bytes --> peek 100 bytes.

"""

import lind_test_server
import emultimer

from lind_net_constants import *

SyscallError = lind_test_server.SyscallError

#Both client and server are run from this file, hence opening sockets for both
serversockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)
clientsockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)

#Bind & listen with backlog of 1, since I am creating only 1 client. 
lind_test_server.bind_syscall(serversockfd, '127.0.0.1', 50300)
lind_test_server.listen_syscall(serversockfd, 1)


def process_request():
  """
  <Purpose>
    Process the incoming data using above specifed tests
  """

  rip, rport, newsockfd = lind_test_server.accept_syscall(serversockfd)  
  
  #Process first test...
  try:
    msg = lind_test_server.recvfrom_syscall(newsockfd, 100, MSG_PEEK)
    assert len(msg[2]) == 100, "Length expected 100 bytes to peek, but only" \
      + " got " + str(len(msg[2])) + " bytes."
    msg = lind_test_server.recvfrom_syscall(newsockfd, 100, 0)
    assert len(msg[2]) == 100, "Length expected 100 bytes to read, but only" \
      + " got " + str(len(msg[2])) + " bytes."
  except Exception, e:
    print 'TEST:- W:100, P:100, R:100 : ', e

  emultimer.sleep(0.2)

  #Process second test...
  try:
    msg = lind_test_server.recvfrom_syscall(newsockfd, 20, 0)
    assert len(msg[2]) == 20, "Length expected 20 bytes to read, but only" \
      + " got " + str(len(msg[2])) + " bytes."
    msg = lind_test_server.recvfrom_syscall(newsockfd, 20, MSG_PEEK)
    assert len(msg[2]) == 20, "Length expected 20 bytes to peek, but only" \
      + " got " + str(len(msg[2])) + " bytes."
    msg = lind_test_server.recvfrom_syscall(newsockfd, 80, 0)
    assert len(msg[2]) == 80, "Length expected 80 bytes to read, but only" \
      + " got " + str(len(msg[2])) + " bytes."
  except Exception, e:
    print 'Test:- W:100, R:20, P:20, R:80 : ', e

  emultimer.sleep(0.2)

  #Process thrid test...
  try:
    for i in range(0,4):
      msg = lind_test_server.recvfrom_syscall(newsockfd, 10, MSG_PEEK)
      assert len(msg[2]) == 10, "Length expected 10 bytes to peek, but only" \
        + " got " + str(len(msg[2])) + " bytes."
    for i in range(0,4):
      msg = lind_test_server.recvfrom_syscall(newsockfd, 20, MSG_PEEK)
      assert len(msg[2]) == 20, "Length expected 20 bytes to peek, but only" \
        + " got " + str(len(msg[2])) + " bytes."
    for i in range(0,4):
      msg = lind_test_server.recvfrom_syscall(newsockfd, 30, MSG_PEEK)
      assert len(msg[2]) == 30, "Length expected 30 bytes to peek, but only" \
        + " got " + str(len(msg[2])) + " bytes."
    for i in range(0,4):
      msg = lind_test_server.recvfrom_syscall(newsockfd, 40, MSG_PEEK)
      assert len(msg[2]) == 40, "Length expected 40 bytes to peek, but only" \
        + " got " + str(len(msg[2])) + " bytes."
    msg = lind_test_server.recvfrom_syscall(newsockfd, 100, 0)
    assert len(msg[2]) == 100, "Length expected 100 bytes to read, but only" \
      + " got " + str(len(msg[2])) + " bytes."
  except Exception, e:
    print 'Test:- W:100, Peek several times : ', e

  emultimer.sleep(0.2)

  #Process fourth test...
  try:
    msg = lind_test_server.recvfrom_syscall(newsockfd, 100, MSG_PEEK)
    assert len(msg[2]) == 50, "Length expected 50 bytes to peek, but only" \
      + " got " + str(len(msg[2])) + " bytes."
  except Exception, e:
    print 'Test:- W:100 P:50 : ', e
  
  #Gracefully close the socket
  lind_test_server.close_syscall(newsockfd)

#Run the server in a seperate thread, since client/server should be started
#simultaneously.
emultimer.createthread(process_request)

#connect to server
lind_test_server.connect_syscall(clientsockfd, '127.0.0.1', 50300)

#send each test with some delay, so that server processes each test cleanly.
lind_test_server.send_syscall(clientsockfd, "A" * 100, 0)
emultimer.sleep(0.1)
lind_test_server.send_syscall(clientsockfd, "A" * 100, 0)
emultimer.sleep(0.1)
lind_test_server.send_syscall(clientsockfd, "A" * 100, 0)
emultimer.sleep(0.1)
lind_test_server.send_syscall(clientsockfd, "A" * 50, 0)
emultimer.sleep(0.1)

#close the client & server sockets...  
lind_test_server.close_syscall(clientsockfd)
lind_test_server.close_syscall(serversockfd)
