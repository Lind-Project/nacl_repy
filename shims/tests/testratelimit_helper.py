import sys
import time

dy_import_module_symbols("shimstackinterface")

SERVER_IP = getmyip()
SERVER_PORT = 34829
UPLOAD_RATE = 1024 * 1024 * 15 # 15MB/s
DOWNLOAD_RATE = 1024 * 1024 * 128 # 15MB/s
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

  log("\nSetting upload rate to %dbytes/s. \nSetting download rate to %dbytes/s" % (UPLOAD_RATE, DOWNLOAD_RATE))
  # Launch the server and sleep for couple of seconds.
  createthread(launchserver)
  sleep(3)

  shim_obj = ShimStackInterface("(RateLimitShim,%s,%s)" % (UPLOAD_RATE, DOWNLOAD_RATE))

  try:
    sockobj = shim_obj.openconnection(SERVER_IP, SERVER_PORT, SERVER_IP, SERVER_PORT + 1, 10)
  except Exception, err:
    print "Found error: " + str(err)
    exitall()


  msg_to_send = DATA_TO_SEND + END_TAG



# --------------------- Testing Upload --------------------------------
  cur_data_sent = 0

  log("\nStarting to send msg.")
  starttime = getruntime()

  while msg_to_send:
    try:
      data_sent = sockobj.send(msg_to_send)
    except SocketWouldBlockError, err:
      pass
    else:
      msg_to_send = msg_to_send[data_sent:]
      cur_data_sent += data_sent

  elapsed_time = getruntime() - starttime

  log("\nTime to upload: %fs. Upload rate: %fbytes/s" % (elapsed_time, len(DATA_TO_SEND + END_TAG)*1.0 / elapsed_time))  
  log("\nTesting upload rate with 10% error")

  rate_over_percent = ((len(DATA_TO_SEND + END_TAG)*1.0 / elapsed_time) - UPLOAD_RATE) / UPLOAD_RATE

  if rate_over_percent > 0.10:
    log("[ FAIL ]")
    sys.stdout.flush()
    exitall()
  else:
    log("[ PASS ]")


# -------------------------- Testing Download ------------------------------
  msg_received = ''
  

  log("\nStarting to recv echo msg.")
  starttime = getruntime()
  while True:
    try:
      data_received = sockobj.recv(RECV_SIZE)
    except SocketWouldBlockError, err:
      pass
    else:
      msg_received += data_received
      if END_TAG in data_received:
        break

  elapsed_time = getruntime() - starttime

  sockobj.close()

  log("\nTime to download: %fs. Download rate: %fbytes/s" % (elapsed_time, len(msg_received)*1.0 / elapsed_time))  

  log("\nTesting download rate with 10% error")
  
  rate_over_percent = ((len(msg_received)*1.0 / elapsed_time) - DOWNLOAD_RATE) / DOWNLOAD_RATE

  if rate_over_percent > 0.10:
    log("[ FAIL ]")
    sys.stdout.flush()
    exitall()
  else:
    log("[ PASS ]")

  log("\nChecking message received len: ")
  try:
    assert(len(msg_received) == len(DATA_TO_SEND + END_TAG))
  except AssertionError:
    log("[ FAIL ]")
    sys.stdout.flush()
    exitall()
  else:
    log("[ PASS ]")

