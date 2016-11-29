"""
This unit test checks the getpeername() and getsockname()
methods of the RepySocket.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

def incoming(sock):
  # Check the names
  if sock.getsockname() != (ip, listen_port):
    print "Server socket name is not correct! Got: "+str(sock.getsockname())
  if sock.getpeername() != (ip, client_port):
    print "Server's peer name is not correct! Got: "+str(sock.getpeername())
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

# Check everything
if s.getsockname() != (ip, client_port):
  print "Client socket name is not correct! Got: "+str(s.getsockname())

if s.getpeername() != (ip, listen_port):
  print "Client's peer name is not correct! Got: "+str(s.getpeername())

# Close and cleanup
s.close()
stop_func()

