import sys
import traceback
import time

dy_import_module_symbols("msg_chunk_lib")

SERVER_IP = getmyip()
SERVER_PORT = 60606
DATA_RECV = 1024
CHUNK_SIZE_SEND = 2**16
CHUNK_SIZE_RECV = 2**20
DATA_TO_SEND = "HelloWorld" * 1024 * 1024 * 5 # 50MB of data

def launchserver():
  """
  <Purpose>
    Launch a server that waits for connection from client.

  <Arguments>
    None

  <Side Effects>
    None

  <Exceptions>
    None

  <Return>
    None
  """
  log("\nMultisocket server launched")
  sys.stdout.flush()
  tcpserver_socket_one = listenforconnection(SERVER_IP, SERVER_PORT)
  tcpserver_socket_two = listenforconnection(SERVER_IP, SERVER_PORT+1)
  tcpserver_socket_three = listenforconnection(SERVER_IP, SERVER_PORT+2)

  while True:
    try:
      rip, rport, sockobj_one = tcpserver_socket_one.getconnection()
      rip, rport, sockobj_two = tcpserver_socket_two.getconnection()
      rip, rport, sockobj_three = tcpserver_socket_three.getconnection()
    except SocketWouldBlockError:
      sleep(0.1)
    except (SocketClosedLocal, SocketClosedRemote):
      break
    else:
      log("\nServer received connection on all sockets")
      sys.stdout.flush()
      chunk_object = ChunkMessage(CHUNK_SIZE_SEND,CHUNK_SIZE_RECV)
      chunk_object.add_socket(sockobj_one)
      chunk_object.add_socket(sockobj_two)
      chunk_object.add_socket(sockobj_three)
      createthread(handle_connection(chunk_object))
      #createthread(handle_connection(sockobj))
      break




def handle_connection(chunk_object):
  """
  Continluously receive data.
  """

  def _connection_handle_helper():
    msg_recv = ''
    start_time = time.time()
    while True:
      try:
        msg_recv += chunk_object.recvdata(DATA_RECV)
        #msg_recv += chunk_object.recv(DATA_RECV)
      except SocketWouldBlockError:
        sleep(0.1)
      except (SocketClosedLocal, SocketClosedRemote):
        exitall()
    log("\nTime taken to recv msg: " + str(time.time() - start_time))
    assert(msg_recv == DATA_TO_SEND)
    log("\nMessage received: [ PASS ]")
    sys.stdout.flush()
    exitall()

  return _connection_handle_helper



if callfunc == 'initialize':
  
  createthread(launchserver)
  # Sleep to let the server kick up.
  sleep(10)
  
  try:
    sockobj_one = openconnection(SERVER_IP, SERVER_PORT, SERVER_IP, SERVER_PORT+10, 10)
    sockobj_two = openconnection(SERVER_IP, SERVER_PORT+1, SERVER_IP, SERVER_PORT+11, 10)
    sockobj_three = openconnection(SERVER_IP, SERVER_PORT+2, SERVER_IP, SERVER_PORT+12, 10)
  except Exception, err:
    print "Error occured" + str(err)
    sys.stdout.flush()
  log("Opened a connection on all sockets")

  chunk_object = ChunkMessage(CHUNK_SIZE_SEND,CHUNK_SIZE_RECV)
  chunk_object.add_socket(sockobj_one)
  chunk_object.add_socket(sockobj_two)
  chunk_object.add_socket(sockobj_three)

  msg = DATA_TO_SEND
  total_data_sent = 0


  start = time.time()
  while msg:
    try:
      data_sent = chunk_object.senddata(msg)
      #data_sent = sockobj.send(msg)
    except SocketWouldBlockError:
      sleep(0.1)
    except (SocketClosedLocal, SocketClosedRemote):
      log("Socket closed too early")
      chunk_object.close()
      exitall()
    else:
      msg = msg[data_sent:]
      total_data_sent += data_sent

  log("\nTotal time taken to send msg: " + str(time.time() - start))
  chunk_object.close()
  assert(total_data_sent == len(DATA_TO_SEND))
  log("\nMessage sent length matches: [ PASS ]")

  data_distribution = chunk_object.get_data_sent_distribution()

  total_data_sent = data_distribution[repr(sockobj_one)] + data_distribution[repr(sockobj_two)] + data_distribution[repr(sockobj_three)]
  assert(total_data_sent == len(DATA_TO_SEND))
  log("\nData distrubtion lenght check: [ PASS ]")
  sys.stdout.flush()

  exitall()
      
  
