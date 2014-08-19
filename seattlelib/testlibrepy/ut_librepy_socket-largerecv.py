"""
This unit test checks that we can send a large amount
of data correctly using the RepySocket.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

def incoming(sock):
  bytes = 1024 * 20 # We need to read this much
  read_data = ""

  while len(read_data) < bytes:
    read_data += sock.recv(512) # Read in 512 byte blocks
 
  # Check if we read the right data back
  if read_data != original_data:
    print "Data does not match what was sent!"

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
original_data = data

# Send all the data
while len(data) > 0:
  sent = s.send(data)
  data = data[sent:]

# Close and cleanup
sleep(0.5)
s.close()
stop_func()

