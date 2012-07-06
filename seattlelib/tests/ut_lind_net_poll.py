"""
File : ut_lind_net_poll.py

Unit test for poll_syscall(), the poll checks between file, and 2 sockets
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

#Create a file, to read/write using poll.
filefd = lind_test_server.open_syscall('/foo.txt', O_CREAT | O_EXCL | O_RDWR, S_IRWXA)
 
#Create a socket, to handle incomming connections.
serversockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)
clientsockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)
client2sockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)

#Bind and listen the socket to a particular address.
lind_test_server.bind_syscall(serversockfd, '127.0.0.1', 50300)
lind_test_server.listen_syscall(serversockfd, 4)

#Will contain list of sockets that poll needs to watch for. The first is
#the server socket for handling incomming new connections.

server_poll = {'fd': serversockfd,
                            'events': lind_test_server.POLLIN,
                            'revents': 0}

client_poll = {'fd': clientsockfd,
                            'events': lind_test_server.POLLIN,
                            'revents': 0}

file_poll = {'fd': filefd,
                            'events': lind_test_server.POLLIN | lind_test_server.POLLOUT,
                            'revents': 0}

inputs = [file_poll, client_poll, server_poll]




def process_request():
  """
  <Purpose>
    Server thread for processing connections using poll ...
  """
  while True:
    #Pass list of Inputs, Outputs for poll which returns if any activity
    #occurs on any socket.
    poll_vals = lind_test_server.poll_syscall(inputs, 0)
    ret = [0,[],[],[]]
    ret[1] = [x['fd'] for x in poll_vals[1] if x['revents'] & lind_test_server.POLLIN]
    ret[2] = [x['fd'] for x in poll_vals[1] if x['revents'] & lind_test_server.POLLOUT]

    #Check for any activity in any of the Input sockets...
    for sock in ret[1]:
      
      #If the socket returned was listerner socket, then there's a new conn.
      #so we accept it, and put the client socket in the list of Inputs.
      if sock is serversockfd:
        newsockfd = lind_test_server.accept_syscall(sock)
        try:
          new_poll =  {'fd':newsockfd[2], 'events':lind_test_server.POLLIN|lind_test_server.POLLOUT, 'revents':0}
          inputs.append(new_poll)
        except Exception, e:
          print "Note:", e
      #Write to a file...
      elif sock is filefd:
        assert lind_test_server.write_syscall(filefd, 'test') == 4, \
          "Failed to write into a file..."
        lind_test_server.lseek_syscall(filefd,0,SEEK_SET)
      #If the socket is in established conn., then we recv the data, if
      #there's no data, then close the client socket.
      else:
        data = lind_test_server.recv_syscall(sock, 100, 0)
        if data:
          assert data == "test", "Recv failed in poll..."
          #We make the ouput ready, so that it sends out data... 
          if len([x for x in inputs if x['fd'] == sock]) == 0:
            inputs.append({'fd':sock, 'events':lind_test_server.POLLOUT,'revents':0})
        else:          
          lind_test_server.close_syscall(sock)
          to_go = [x for x in inputs if x['fd'] == sock]
          map(inputs.remove, to_go)
    
    #Check for any activity in any of the output sockets...
    for sock in ret[2]:
      if sock is filefd:
        assert lind_test_server.read_syscall(sock, 4) == "test", \
          "Failed to read from a file..."
        to_go = [x for x in inputs if x['fd'] == sock]
        map(inputs.remove, to_go)
      else:
        lind_test_server.send_syscall(sock, data, 0)
        to_go = [x for x in inputs if x['fd'] == sock]
        map(inputs.remove, to_go)



  lind_test_server.close_syscall(serversockfd)

#Thread for running server ...
emultimer.createthread(process_request)
emultimer.sleep(1)

def client1():
  """
  <Purpose>
    Thread for client 1 to connect to server, and send/recv data...
  """
  lind_test_server.connect_syscall(clientsockfd, '127.0.0.1', 50300)
  
  lind_test_server.send_syscall(clientsockfd, "test", 0)
  #Short sleeps are not working, give enough time...
  emultimer.sleep(1)
  ret = lind_test_server.recv_syscall(clientsockfd, 100, 0)
  assert ret  == "test", \
     "Write failed in poll while processing client 1... got:%s"%(str(ret))

  lind_test_server.close_syscall(clientsockfd)

#Thread for running client 1, I did so because to show that server can handle
#multiple connections simultaneously...
emultimer.createthread(client1)
emultimer.sleep(.1)

#Client 2 connects to server, and send/recv data...
lind_test_server.connect_syscall(client2sockfd, '127.0.0.1', 50300)

lind_test_server.send_syscall(client2sockfd, "test", 0)
#Short sleeps are not working, give enough time...
emultimer.sleep(1)
assert lind_test_server.recv_syscall(client2sockfd, 100, 0) == "test", \
  "Write failed in poll while processing client 2..."

lind_test_server.close_syscall(client2sockfd)

#Exit all threads, no better way to close server thread which is in infinity
#loop...
emulmisc.exitall()
