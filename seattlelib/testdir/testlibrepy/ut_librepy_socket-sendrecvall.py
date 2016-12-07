"""
This unit test checks sendall() and recvall() methods of
RepySocket.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

def incoming(sock):
  bytes = 1024 * 20 # We need to read this much
  read = sock.recvall(bytes)

  if read != data:
    print "Recv'ed data does not match what was sent!"

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

# Generate some random data
data = (randombytes() + randombytes()) * 10 # 20K of data

# Send all the data
sent = s.sendall(data)

if sent != len(data):
  print "Did not send all the data!"

# Close and cleanup
sleep(0.5)
s.close()
stop_func()

