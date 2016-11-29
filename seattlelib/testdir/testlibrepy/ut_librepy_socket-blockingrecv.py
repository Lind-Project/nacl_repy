"""
This unit test checks that a blocking recv
methods of the RepySocket works.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

def incoming(sock):
  # Do a blocking recv
  data = sock.recv(4)

  # Send back
  sock.send("test")

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
s = openconn(ip, listen_port, localip=ip, localport=client_port)

# Wait a bit...
sleep(0.4)

# Send some data
s.send("test")

# Recv some now
data = s.recv(4)

# Close and cleanup
s.close()
stop_func()

