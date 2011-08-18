import sys
import time

dy_import_module_symbols("shimstackinterface")


SERVER_IP = getmyip()
SERVER_PORT_NODEA = 36829
SERVER_PORT_NODEB = 35349

MSG_TO_SEND = "HelloWorld" * 1024 * 1024  # 10MB of Data
DATA_RECV_BYTES = 2**16

MSG_DICT = {}


def launch_server(shim_str, listen_ip, listen_port, out_port, msg_dict, server_name, echo_msg=False):

  def _server_helper():
    log("\nLaunching server %s on port %d" % (server_name, listen_port))
    sys.stdout.flush()
    shim_obj = ShimStackInterface(shim_str)

    tcpserver_socket = shim_obj.listenforconnection(listen_ip, listen_port)

    while True:
      try:
        rip, rport, sockobj = tcpserver_socket.getconnection()
      except SocketWouldBlockError:
        pass
      except (SocketClosedLocal, SocketClosedRemote):
        log("[ FAIL ]")
        raise Exception("Unable to get connection from client.")
      else:
        log("\nServer %s got connection on port: %d." % (server_name, listen_port))
        msg_dict[server_name]['recv_socket'] = sockobj
        msg_dict[server_name]['remoteip'] = rip
        # The rport here should be off by 1 due to the way the test
        # was designed.
        msg_dict[server_name]['remoteport'] = rport
        break


    # If we are going to return the msg, we create a new connection.
    sock_return = None
    if echo_msg:
      try:
        # We have to open a connection to the specified out port rather then the rip received.
        # This is due to the fact we have two servers running on the same machine, so we are not
        # allowed to openconnection() and getconnection() on the same port on the same machine.
        sock_return = shim_obj.openconnection(rip, out_port, listen_ip, listen_port + 50, 10)
      except Exception, err:
        raise Exception("Unable to make connection to the echo server. " + str(err))
      else:
        log("\nOpenconnection made on server %s on port %d" % (server_name, out_port))
        sys.stdout.flush()
        msg_dict[server_name]['send_socket'] = sock_return
        msg_dict[server_name]['localip'] = listen_ip
        msg_dict[server_name]['localport'] = listen_port + 50
        


    start_time = time.time()
    log("\nServer %s starting to recv msg." % server_name)
    while True:
      try:
        msg_recv = sockobj.recv(DATA_RECV_BYTES)
      except SocketWouldBlockError:
        pass
      
      except SocketClosedRemote:
        # We want to close the ougoing connection.
        if sock_return:
          sock_return.close()
        break
      except SocketClosedLocal:
        raise Exception("Socket should not have been closed locally.")
      else:
        msg_dict[server_name]['recv'] += msg_recv

        # If we are going to echo the message.
        if echo_msg:
          while msg_recv:
            try:
              data_sent = sock_return.send(msg_recv)
            except SocketWouldBlockError:
              pass
            except SocketClosedLocal:
              break
            except SocketClosedRemote:
              raise Exception("Socket should not have been closed remotely.")
            else:
              msg_dict[server_name]['sent'] += data_sent
              msg_recv = msg_recv[data_sent:]

    if echo_msg:
      log("\nTime taken to recv msg on %s and echo it back: %f" % (server_name, (time.time() - start_time)))
    else:
      log("\nTime taken to recv msg on %s : %f" % (server_name, (time.time() - start_time)))
    msg_dict[server_name]['Finished_recv'] = True

  return _server_helper





# The test launching point.
def launch_test(multipath_shim_str='', leftover_shim_str=''):

  for node in ["NodeA", "NodeB"]:
    MSG_DICT[node] = {}
    MSG_DICT[node]['sent'] = 0
    MSG_DICT[node]['recv'] = ''
    MSG_DICT[node]['Finished_recv'] = False
    MSG_DICT[node]['send_socket'] = None
    MSG_DICT[node]['recv_socket'] = None
    MSG_DICT[node]['localip'] = None
    MSG_DICT[node]['localport'] = None
    MSG_DICT[node]['remoteip'] = None
    MSG_DICT[node]['remoteport'] = None

  server_A = launch_server(multipath_shim_str + leftover_shim_str, SERVER_IP, SERVER_PORT_NODEA, SERVER_PORT_NODEB + 1, MSG_DICT, "NodeA", False)
  server_B = launch_server(multipath_shim_str + leftover_shim_str, SERVER_IP, SERVER_PORT_NODEB, SERVER_PORT_NODEA, MSG_DICT, "NodeB", True)

  createthread(server_A)
  createthread(server_B)

  sleep(5)

  shim_obj = ShimStackInterface(multipath_shim_str + leftover_shim_str)
  
  try:
    log("\nNodeA making connection on port: %d" % SERVER_PORT_NODEB)
    sockobj = shim_obj.openconnection(SERVER_IP, SERVER_PORT_NODEB, SERVER_IP, SERVER_PORT_NODEA+50, 10)
  except Exception, err:
    raise Exception("Unable to make connection to NodeB.")
  else:
    MSG_DICT["NodeA"]['send_socket'] = sockobj
    MSG_DICT["NodeA"]['localip'] = SERVER_IP
    MSG_DICT["NodeA"]['localport'] = SERVER_PORT_NODEA +50
    
  

  msg = MSG_TO_SEND

  start_time = time.time()
  while msg:
    try:
      data_sent = sockobj.send(msg)
    except SocketWouldBlockError:
      pass
    except (SocketClosedLocal, SocketClosedRemote):
      raise Exception("Socket closed error raised unexpectedly.")
    else:
      MSG_DICT["NodeA"]['sent'] += data_sent
      msg = msg[data_sent:]

  log("\nTime taken to send msg on NodeA: " + str(time.time() - start_time))
  # After we are done sending the message we will close the socket.    
  sockobj.close()

  while True:
    if MSG_DICT["NodeA"]['Finished_recv'] and MSG_DICT["NodeB"]['Finished_recv']:
      break
    sleep(0.01)

  assert_server_msg(MSG_DICT)




def assert_server_msg(msg_dict):
  """
  <Purpose>
    Test that everything checks out.
  """

  first_server = msg_dict["NodeA"]
  second_server = msg_dict["NodeB"]

  display_node(msg_dict)

  # Message sanity checks.
  log("\n\nMessage sanity check: ")
  try:
    assert(first_server['recv'] == MSG_TO_SEND)
    assert(second_server['recv'] == MSG_TO_SEND)
    assert(first_server['sent'] == len(MSG_TO_SEND))
    assert(second_server['sent'] == len(MSG_TO_SEND))
  except AssertionError:
    log("[ FAIL ]")
    raise
  else:
    log("[ PASS ]")

  # IP check
  log("\nIP address sanity check: ")
  try:
    assert(first_server['localip'] == SERVER_IP)
    assert(second_server['localip'] == SERVER_IP)
    assert(first_server['remoteip'] == SERVER_IP)
    assert(second_server['remoteip'] == SERVER_IP)
  except AssertionError:
    log("[ FAIL ]")
    raise
  else:
    log("[ PASS ]")

  # Port sanity checks.
  log("\nPort sanity check: ")
  try:
    assert(first_server['remoteport'] == second_server['localport'])
    assert(second_server['remoteport'] == first_server['localport'])
  except AssertionError:
    log("[ FAIL ]")
    raise
  else:
    log("[ PASS ]")

  for node in msg_dict.keys():
    log("\nChecking %s send_socket closed: " % node)
    try:
      msg_dict[node]['send_socket'].send("randomword")
    except SocketClosedLocal:
      log("[ PASS ]")
    except SocketClosedRemote:
      log("[ FAIL ]")
      raise Exception("Send socket should not have been closed remotely.")
    else:
      log("[ FAIL ]")
      raise Exception("Failed at closing socket for %s" % node)

    log("\nChecking %s recv_socket closed: " % node)
    try:
      msg_dict[node]['recv_socket'].recv(1024)
    except SocketClosedRemote:
      log("[ PASS ]")
    except SocketClosedLocal:
      log("[ FAIL ]")
      raise Exception("Recv socket should not have been closed locally.")
    else:
      log("[ FAIL ]")
      raise Exception("Failed at closing socket for %s" % node)





  for node in msg_dict.keys():
    log("\nChecking data distribution send for %s: " % node)
    data_distribution_send = msg_dict[node]['send_socket'].get_stats()
    total_sent = 0

    for cur_shim_socket in data_distribution_send.keys():
      total_sent += data_distribution_send[cur_shim_socket]['send']

    try:
      assert(total_sent == len(MSG_TO_SEND))
    except AssertionError:
      log("[ FAIL ]")
      raise
    else:
      log("[ PASS ]")

    log("\nChecking data distribution recv for %s: " % node)
    data_distribution_recv = msg_dict[node]['recv_socket'].get_stats()
    total_recv = 0

    for cur_shim_socket in data_distribution_recv.keys():
      total_recv += data_distribution_recv[cur_shim_socket]['recv']
    
    try:
      assert(total_recv == len(MSG_TO_SEND))
    except AssertionError:
      log("[ FAIL ]")
      raise
    else:
      log("[ PASS ]")
    

  #log("\n" + str(MSG_DICT)) 




def display_node(msg_dict):

  for node in msg_dict.keys():
    log("\n\nServer Name: " + node)
    log("\nLocalip: " + msg_dict[node]['localip'])
    log("\nLocalport: " + str(msg_dict[node]['localport']))
    log("\nRemoteip: " + msg_dict[node]['remoteip'])
    log("\nRemoteport: " + str(msg_dict[node]['remoteport']))
    log("\nSend length: " + str(msg_dict[node]['sent']))
    log("\nRecv length: " + str(len(msg_dict[node]['recv'])))
    log("\nData distribution send: " + str(msg_dict[node]['send_socket'].get_stats()))
    log("\nData distribution recv: " + str(msg_dict[node]['recv_socket'].get_stats()))
