"""
This unit test checks that a non-blocking recv
methods of the RepySocket works.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

CONNECTED_LOCK = Lock()

def incoming(sock):
  # Set to non-blocking
  sock.settimeout(0)

  # Do a non-blocking recv, this
  # should give SocketWouldBlockError
  try:
    data = sock.recv(4)
  except SocketWouldBlockError:
    pass
  else:
    print "Should get SocketWouldBlockError!"
 
  # Release the lock
  CONNECTED_LOCK.release()
  sleep(0.2) 

  # Do a non-blocking recv, this
  # should not timeout
  data = sock.recv(4)

  sleep(0.2)
  sock.close()


# Get the IP, and some ports
ip = getmyip()
free_ports = libsocket.get_connports(ip)
listen_port = free_ports[0]
client_port = free_ports[1]

# Setup a listener
stop_func = waitforconn(listen_port, incoming, ip)

# Connect now
CONNECTED_LOCK.acquire()
s = openconn(ip, listen_port, localip=ip, localport=client_port)
CONNECTED_LOCK.acquire()

# Send some data
s.send("test")

# Close and cleanup
sleep(0.4)
s.close()
stop_func()

