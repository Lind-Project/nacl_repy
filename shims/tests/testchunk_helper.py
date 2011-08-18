import sys
import time

dy_import_module_symbols("msg_chunk_lib")

SERVER_IP = getmyip()
SERVER_PORT = 60606
DATA_RECV = 2**16
CHUNK_SIZE_SEND = 2**16
CHUNK_SIZE_RECV = 2**20
DATA_TO_SEND = "HelloWorld" * 1024 * 1024 * 5 # 50MB of data

MSG_RECEIVED = ''
FINISHED_RECEIVING = False

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
  tcpserver_socket = listenforconnection(SERVER_IP, SERVER_PORT)

  while True:
    try:
      rip, rport, sockobj = tcpserver_socket.getconnection()
    except SocketWouldBlockError:
      pass
    except (SocketClosedLocal, SocketClosedRemote):
      break
    else:
      chunk_object = ChunkMessage(CHUNK_SIZE_SEND,CHUNK_SIZE_RECV)
      chunk_object.add_socket(sockobj)
      createthread(handle_connection(chunk_object))
      #createthread(handle_connection(sockobj))

      # We want only one connection.
      break





def handle_connection(chunk_object):
  """
  Continluously receive data.
  """

  def _connection_handle_helper():
    global MSG_RECEIVED 
    global FINISHED_RECEIVING

    msg_recv = ''
    start_time = time.time()
    while True:
      try:
        msg_recv += chunk_object.recvdata(DATA_RECV)
        #msg_recv += chunk_object.recv(DATA_RECV)
        sys.stdout.flush()
      except SocketWouldBlockError:
        pass
      except (SocketClosedLocal, SocketClosedRemote):
        break

    log("\nTime taken to receive message: " + str(time.time() - start_time))
    MSG_RECEIVED = msg_recv
    FINISHED_RECEIVING = True

  return _connection_handle_helper



def launch_test():
  
  createthread(launchserver)
  # Sleep to let the server kick up.
  sleep(2)
  
  try:
    sockobj = openconnection(SERVER_IP, SERVER_PORT, SERVER_IP, SERVER_PORT+1, 10)
  except Exception, err:
    log("\nError occured making connection" + str(err))
    exitall()


  chunk_object = ChunkMessage(CHUNK_SIZE_SEND,CHUNK_SIZE_RECV)
  chunk_object.add_socket(sockobj)

  msg = DATA_TO_SEND
  total_data_sent = 0


  start_time = time.time()
  while msg:
    try:
      data_sent = chunk_object.senddata(msg)
      #data_sent = sockobj.send(msg)
    except SocketWouldBlockError:
      sleep(0.1)
    except (SocketClosedLocal, SocketClosedRemote):
      log("Socket closed too early")
      exitall()
    else:
      msg = msg[data_sent:]
      total_data_sent += data_sent

  log("\nTime taken to send message: " + str(time.time() - start_time))
  chunk_object.close()

  log("\nMessage sent length matches: ")
  try:
    assert(total_data_sent == len(DATA_TO_SEND))
  except AssertionError:
    log("[ FAIL ]")
    raise Exception("Message sent length doesn't match")
  else:
    log("[ PASS ]")

  data_distribution = chunk_object.get_data_sent_distribution()
  log("\nData distrubtion lenght check: ")

  try:
    assert(data_distribution[repr(sockobj)] == len(DATA_TO_SEND))
  except AssertionError:
    log("[ FAIL ]")
    raise Exception("Data distribution length doesn't check out.")
  else:
    log("[ PASS ]")

  # Wait till all message has been received.
  while not FINISHED_RECEIVING:
    sleep(0.1)

  log("\nMessage received length check: ")
  try:
    assert(MSG_RECEIVED == DATA_TO_SEND)
  except AssertionError:
    log("[ FAIL ]")
    raise Exception("Message received length doesn't check out.")
  else:
    log("[ PASS ]")
  sys.stdout.flush()

  exitall()




      
  
