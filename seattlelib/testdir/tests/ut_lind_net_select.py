"""
File : ut_lind_net_select.py

Unit test for select_syscall(), the select checks between file, and 2 sockets
of a client. 
"""
import lind_test_server
import emultimer
import emulmisc

from lind_net_constants import *
from lind_fs_constants import *

SyscallError = lind_test_server.SyscallError

#Try read/write of a file and see if it works.
lind_test_server._blank_fs_init()

#Create a file, to read/write using select.
filefd = lind_test_server.open_syscall('/foo.txt', O_CREAT | O_EXCL | O_RDWR, S_IRWXA)
 
#Create 3 socket, one for server and two client sockets.
serversockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)
clientsockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)
client2sockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)

#Bind and listen the socket to a particular address.
lind_test_server.bind_syscall(serversockfd, '127.0.0.1', 50300)
lind_test_server.listen_syscall(serversockfd, 4)

#Will contain list of sockets that select needs to watch for. By default we
#provide server socket and file, new sockets will be added to monitor by server. 
inputs = [serversockfd, filefd]
outputs = [filefd]
excepts = []

def process_request():
  """
  <Purpose>
    Server thread for processing connections using select ...
  """
  while True:
    #Pass list of Inputs, Outputs for select which returns if any activity
    #occurs on any socket.
    ret = lind_test_server.select_syscall(11, inputs, outputs, excepts, 5)

    #Check for any activity in any of the Input sockets...
    for sock in ret[1]:
      #If the socket returned was listerner socket, then there's a new conn.
      #so we accept it, and put the client socket in the list of Inputs.
      if sock is serversockfd:
        newsockfd = lind_test_server.accept_syscall(sock)
        inputs.append(newsockfd[2])
      #Write to a file...
      elif sock is filefd:
        emultimer.sleep(1)
        assert lind_test_server.write_syscall(sock, 'test') == 4, \
          "Failed to write into a file..."
        lind_test_server.lseek_syscall(sock, 0, SEEK_SET)
        inputs.remove(sock)
      #If the socket is in established conn., then we recv the data, if
      #there's no data, then close the client socket.
      else:
        data = lind_test_server.recv_syscall(sock, 100, 0)
        if data:
          assert data == "test", "Recv failed in select..."
          #We make the ouput ready, so that it sends out data... 
          if sock not in outputs:
            outputs.append(sock)
        else:         
          #No data means remote socket closed, hence close the client socket
          #in server, also remove this socket from readfd's. 
          lind_test_server.close_syscall(sock)
          inputs.remove(sock)
    
    #Check for any activity in any of the output sockets...
    for sock in ret[2]:
      if sock is filefd:
        assert lind_test_server.read_syscall(sock, 4) == "test", \
          "Failed to read from a file..."
        #test for file finished, remove from monitoring.
        outputs.remove(sock)
      else:
        lind_test_server.send_syscall(sock, data, 0)
        #Data is sent out this socket, it's no longer ready for writing
        #remove this socket from writefd's. 
        outputs.remove(sock)

  lind_test_server.close_syscall(serversockfd)

#Thread for running server ...
emultimer.createthread(process_request)
emultimer.sleep(.1)

def client1():
  """
  <Purpose>
    Thread for client 1 to connect to server, and send/recv data...
  """
  lind_test_server.connect_syscall(clientsockfd, '127.0.0.1', 50300)
  
  lind_test_server.send_syscall(clientsockfd, "test", 0)
  #Short sleeps are not working, give enough time...
  emultimer.sleep(1)
  assert lind_test_server.recv_syscall(clientsockfd, 100, 0) == "test", \
     "Write failed in select while processing client 1..."

  lind_test_server.close_syscall(clientsockfd)

#Thread for running client 1, I did so because to show that server can handle
#multiple connections simultaneously...
emultimer.createthread(client1)
emultimer.sleep(.1)

#Client 2 connects to server, and send/recv data...
lind_test_server.connect_syscall(client2sockfd, '127.0.0.1', 50300)

lind_test_server.send_syscall(client2sockfd, "test", 0)
#Short sleeps are not working, give enough time...
emultimer.sleep(.1)
assert lind_test_server.recv_syscall(client2sockfd, 100, 0) == "test", \
  "Write failed in select while processing client 2..."

lind_test_server.close_syscall(client2sockfd)

#Exit all threads, no better way to close server thread which is in infinity
#loop...
emulmisc.exitall()
