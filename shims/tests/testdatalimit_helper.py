import sys
import time

dy_import_module_symbols("shimstackinterface")

SERVER_IP = getmyip()
SERVER_PORT = 34829
UPLOAD_LIMIT = 1024 * 1024 * 128 # 128MB
DOWNLOAD_LIMIT = 1024 * 1024 * 128 # 128MB
TIME_LIMIT = 60
DATA_TO_SEND = "HelloWorld" * 1024 * 1024

RECV_SIZE = 2**14 # 16384 bytes.
MSG_RECEIVED = ''
END_TAG = "@@END"


def launchserver():
  """
  <Purpose>
    Launch a server that receives and echos the message back.

  <Arguments>
    None

  <Side Effects>
    None

  <Exceptions>
    None

  <Return>
    None
  """

  shim_object = ShimStackInterface("(NoopShim)")

  tcpserver_socket = shim_object.listenforconnection(SERVER_IP, SERVER_PORT)

  while True:
    try:
      rip, rport, sockobj = tcpserver_socket.getconnection()
      break
    except SocketWouldBlockError:
      pass
    except (SocketClosedLocal, SocketClosedRemote):
      break

  msg_received = ''
  recv_closed = False
  send_closed = False

  # Echo back all the message that we receive. Exit out of the 
  # loop once we get socket closed error.
  while True:
    try:
      msg_received += sockobj.recv(RECV_SIZE)
    except SocketWouldBlockError:
      pass
    except (SocketClosedLocal, SocketClosedRemote):
      break
    

    try:
      if len(msg_received) > 0:
        data_sent = sockobj.send(msg_received)
        msg_received = msg_received[data_sent : ]
    except SocketWouldBlockError:
      pass
    except (SocketClosedLocal, SocketClosedRemote):
      break






def launch_test():

  # Launch the server and sleep for couple of seconds.
  createthread(launchserver)
  sleep(3)

  shim_obj = ShimStackInterface("(DataLimitShim,%s,%s,%s)" % (UPLOAD_LIMIT, DOWNLOAD_LIMIT, TIME_LIMIT))

  try:
    sockobj = shim_obj.openconnection(SERVER_IP, SERVER_PORT, SERVER_IP, SERVER_PORT + 1, 10)
  except Exception, err:
    print "Found error: " + str(err)
    exitall()


  msg_to_send = DATA_TO_SEND + END_TAG



# --------------------- Testing Upload --------------------------------
  cur_data_sent = 0
  check_sock_blocked = True
  first_sent_time_list = []

  log("\nStarting to send msg.")
  log("\nChecking individual upload limit ")
  while msg_to_send:
    try:
      data_sent = sockobj.send(msg_to_send)
      if check_sock_blocked:
        first_sent_time_list.append(getruntime())
        check_sock_blocked = False
    except SocketWouldBlockError, err:
      # Check if we are blocking because we reached upload limit.
      if "Reached maximum data upload limit" in str(err):
        check_sock_blocked = True
        try:
          assert(cur_data_sent <= UPLOAD_LIMIT)
        except AssertionError:
          log("[ FAIL ]")
          exitall()
        cur_data_sent = 0
      pass
    else:
      msg_to_send = msg_to_send[data_sent:]
      cur_data_sent += data_sent
  else:
    log("[ PASS ]")


  if len(first_sent_time_list) > 1:
    first_time = first_sent_time_list.pop()
    second_time = None

    log("\nChecking weather message uploaded exceeded limit ")
    try:
      for i in range(len(first_sent_time_list)):
        second_time = first_time
        first_time = first_sent_time_list.pop()
        assert((second_time - first_time) < (TIME_LIMIT + 1))
    except AssertionError:
      log("[ FAIL ]")
      exitall()
    else:
      log("[ PASS ]")




# -------------------------- Testing Download ------------------------------
  msg_received = ''
  cur_data_recv_buf = ''
  
  check_sock_blocked = True 
  first_recv_time_list = []

  log("\nStarting to recv echo msg.")
  log("\nChecking individual download limit ")
  while True:
    try:
      data_received = sockobj.recv(RECV_SIZE)
      if check_sock_blocked:
        first_recv_time_list.append(getruntime())
        check_sock_blocked = False
    except SocketWouldBlockError, err:
      # Check to see if we are blocking because we reached the data limit.
      if "Reached maximum data download limit" in str(err):
        check_sock_blocked = True
        try:
          assert(len(cur_data_recv_buf) <= DOWNLOAD_LIMIT)
        except AssertionError:
          log("[ FAIL ]")
          exitall()
        cur_data_recv_buf = ''
      pass
    else:
      msg_received += data_received
      cur_data_recv_buf += data_received
      if END_TAG in data_received:
        break
  else:
    log("[ PASS ]")

  sockobj.close()

  if len(first_recv_time_list) > 1:
    first_time = first_recv_time_list.pop()
    second_time = None

    log("\nChecking weather message downloaded exceeded limit ")
    try:
      for i in range(len(first_recv_time_list)):
        second_time = first_time
        first_time = first_recv_time_list.pop()
        assert((second_time - first_time) < (TIME_LIMIT + 1))
    except AssertionError:
      log("[ FAIL ]")
      exitall()
    else:
      log("[ PASS ]")


  log("\nChecking message received len: ")
  try:
    assert(len(msg_received) == len(DATA_TO_SEND + END_TAG))
  except AssertionError:
    log("[ FAIL ]")
    exitall()
  else:
    log("[ PASS ]")

